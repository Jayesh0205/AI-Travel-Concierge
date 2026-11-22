import json
import logging
from collections import deque
from datetime import datetime, timezone
from time import perf_counter

from fastapi import FastAPI, HTTPException, Depends, Query
# from streamlit import user
from backend.auth import require_admin
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from backend.auth import get_current_user
from database.pg_models import User

logger = logging.getLogger(__name__)


# Monitoring statistics (stored in memory)
monitoring_stats = {
    "total_requests": 0,
    "failed_requests": 0,
    "total_response_time_ms": 0.0,
}

recent_activity = deque(maxlen=20)

process_started_at = perf_counter()
server_started_at = datetime.now(timezone.utc)

app = FastAPI(
    title="NovaTrip API",
    description="AI-powered Travel Concierge Backend",
    version="1.0.0"
)

# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    
allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://novatrip-frontend.vercel.app",
    "https://novatrip-frontend-psgxniydv-jayesh0205.vercel.app",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# API Monitoring Middleware
@app.middleware("http")
async def monitor_requests(request, call_next):
    start_time = perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response

    finally:
        duration_ms = (perf_counter() - start_time) * 1000

        monitoring_stats["total_requests"] += 1
        monitoring_stats["total_response_time_ms"] += duration_ms

        if status_code >= 400:
            monitoring_stats["failed_requests"] += 1

        recent_activity.appendleft({
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "response_time_ms": round(duration_ms, 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })



# Request models
class TravelPlanRequest(BaseModel):
    user_request: str = Field(
        min_length=3,
        max_length=5000,
        description="Describe your travel requirements"
    )
    uploaded_text: str = Field(default="", max_length=20000)
    origin: str = Field(default="", max_length=150)
    destination: str = Field(default="", max_length=150)
    departure_date: str = Field(default="", max_length=30)


# Response models
class HomeResponse(BaseModel):
    message: str
    status: str
    version: str


class HealthResponse(BaseModel):
    status: str
    service: str


class TravelPlanResponse(BaseModel):
    status: str
    message: str
    itinerary: str


class SavedTripSummary(BaseModel):
    id: int
    query: str
    created_at: datetime


class SavedTripsResponse(BaseModel):
    status: str
    trips: list[SavedTripSummary]


class SavedTripDetail(BaseModel):
    id: int
    query: str
    response: str
    created_at: datetime


class SavedTripDetailResponse(BaseModel):
    status: str
    trip: SavedTripDetail

# Profile response model
class ProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str | None
    avatar_url: str | None
    role: str
    created_at: datetime


class ProfileResponseEnvelope(BaseModel):
    status: str
    profile: ProfileResponse


# Profile update request model
class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=150)
    avatar_url: str | None = Field(default=None, max_length=500)


# Saved Places request model
class SavedPlaceCreate(BaseModel):
    place_name: str = Field(min_length=1, max_length=150)
    country: str = Field(min_length=1, max_length=100)
    image_url: str | None = Field(default=None, max_length=1000)
    tag: str | None = Field(default=None, max_length=100)



@app.get("/", response_model=HomeResponse)
def home():
    return {
        "message": "Welcome to NovaTrip API!",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "service": "NovaTrip Backend"
    }

@app.post("/api/travel/plan", response_model=TravelPlanResponse)
def plan_travel(
    request: TravelPlanRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate an itinerary using the existing LangGraph workflow."""

    try:
        from agent.workflow import run_travel_workflow

        itinerary = run_travel_workflow(
            user_request=request.user_request,
            uploaded_text=request.uploaded_text,
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            user_id=current_user.id,
        )

        if not itinerary or not itinerary.strip():
            raise HTTPException(
                status_code=500,
                detail="The travel workflow returned an empty itinerary."
            )

        return {
            "status": "success",
            "message": "Travel itinerary generated successfully.",
            "itinerary": itinerary
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("NovaTrip travel planning failed")
        raise HTTPException(
            status_code=500,
            detail="Travel planning failed. Check the backend logs."
        )

@app.post("/api/travel/plan/stream")
def plan_travel_stream(
    request: TravelPlanRequest,
    current_user: User = Depends(get_current_user),
):
    """Stream real-time progress from the NovaTrip LangGraph workflow."""

    # Store the authenticated user's database ID
    user_id = current_user.id

    def event_generator():
        try:
            from agent.workflow import stream_travel_workflow

            for event in stream_travel_workflow(
                user_request=request.user_request,
                uploaded_text=request.uploaded_text,
                origin=request.origin,
                destination=request.destination,
                departure_date=request.departure_date,
                user_id=user_id,
            ):
                yield f"data: {json.dumps(event)}\n\n"

        except Exception:
            logger.exception("NovaTrip streaming workflow failed")

            error_event = {
                "type": "error",
                "message": "NovaTrip could not complete your travel plan. Please try again."
            }

            yield f"data: {json.dumps(error_event)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/trips", response_model=SavedTripsResponse)
def get_saved_trips(
    current_user: User = Depends(get_current_user),
):
    """Retrieve only the authenticated user's saved itineraries."""

    try:
        from database.pg_database import SessionLocal
        from database.pg_models import SavedSearch

        with SessionLocal() as session:
            records = (
                session.query(SavedSearch)
                .filter(SavedSearch.user_id == current_user.id)
                .order_by(SavedSearch.created_at.desc())
                .limit(100)
                .all()
            )

            trips = [
                {
                    "id": record.id,
                    "query": record.query,
                    "created_at": record.created_at,
                }
                for record in records
            ]

        return {"status": "success", "trips": trips}

    except Exception:
        logger.exception("Failed to retrieve saved trips")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve saved trips. Check backend logs."
        )


@app.get(
    "/api/trips/{trip_id}",
    response_model=SavedTripDetailResponse
)
def get_saved_trip(
    trip_id: int,
    current_user: User = Depends(get_current_user),
):
    """Retrieve one saved itinerary belonging to the authenticated user."""

    try:
        from database.pg_database import SessionLocal
        from database.pg_models import SavedSearch

        with SessionLocal() as session:
            record = (
                session.query(SavedSearch)
                .filter(
                    SavedSearch.id == trip_id,
                    SavedSearch.user_id == current_user.id,
                )
                .first()
            )

            if record is None:
                raise HTTPException(
                    status_code=404,
                    detail="Saved trip not found."
                )

            trip = {
                "id": record.id,
                "query": record.query,
                "response": record.response,
                "created_at": record.created_at,
            }

        return {
            "status": "success",
            "trip": trip
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Failed to retrieve saved trip")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve saved trip. Check backend logs."
        )

    # Get authenticated user's profile
@app.get(
    "/api/profile",
    response_model=ProfileResponseEnvelope
)
def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Retrieve the authenticated user's profile."""

    try:
        from database.pg_database import SessionLocal

        with SessionLocal() as session:
            user = session.get(User, current_user.id)

            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User profile not found."
                )

            profile = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "role": user.role,
                "created_at": user.created_at,
            }

        return {
            "status": "success",
            "profile": profile
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Failed to retrieve user profile")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve profile."
        )
    # Update authenticated user's profile

@app.put(
    "/api/profile",
    response_model=ProfileResponseEnvelope
)
def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
):
    """Update authenticated user's profile information."""

    try:
        from database.pg_database import SessionLocal

        updates = request.model_dump(exclude_unset=True)

        if not updates:
            raise HTTPException(
                status_code=400,
                detail="Please provide at least one profile field."
            )

        if "full_name" in updates and updates["full_name"] is not None:
            updates["full_name"] = updates["full_name"].strip()

            if not updates["full_name"]:
                raise HTTPException(
                    status_code=400,
                    detail="Full name cannot be empty."
                )

        if "avatar_url" in updates and updates["avatar_url"] is not None:
            updates["avatar_url"] = updates["avatar_url"].strip()

            if not updates["avatar_url"].startswith(("https://", "http://")):
                raise HTTPException(
                    status_code=400,
                    detail="Profile image must use a valid HTTP or HTTPS URL."
                )

        with SessionLocal() as session:
            user = session.get(User, current_user.id)

            if user is None:
                raise HTTPException(
                    status_code=404,
                    detail="User profile not found."
                )

            for field, value in updates.items():
                setattr(user, field, value)

            session.commit()
            session.refresh(user)

            profile = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "role": user.role,
                "created_at": user.created_at,
            }

        return {
            "status": "success",
            "profile": profile
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Failed to update user profile")
        raise HTTPException(
            status_code=500,
            detail="Could not update profile."
        )
# Monitoring Dashboard API
@app.get("/api/monitoring/overview")
def monitoring_overview(
    admin=Depends(require_admin),
):
    total = monitoring_stats["total_requests"]
    failed = monitoring_stats["failed_requests"]

    average_response_time = (
        monitoring_stats["total_response_time_ms"] / total
        if total > 0 else 0
    )

    return {
        "status": "success",
        "uptime_seconds": round(
            perf_counter() - process_started_at, 2
        ),
        "started_at": server_started_at.isoformat(),
        "total_requests": total,
        "failed_requests": failed,
        "successful_requests": total - failed,
        "average_response_time_ms": round(
            average_response_time, 2
        ),
        "recent_activity": list(recent_activity),
    }


# PostgreSQL Database Health Monitoring
@app.get("/api/monitoring/database")
def database_health(
    admin=Depends(require_admin),
):
    start_time = perf_counter()

    try:
        from database.pg_database import check_postgres_connection

        check_postgres_connection()

        response_time = (perf_counter() - start_time) * 1000

        return {
            "status": "success",
            "database": "PostgreSQL",
            "connection_status": "online",
            "response_time_ms": round(response_time, 2),
            "message": "Database connection is healthy."
        }

    except Exception:
        response_time = (perf_counter() - start_time) * 1000

        logger.exception("PostgreSQL health check failed")

        return {
            "status": "degraded",
            "database": "PostgreSQL",
            "connection_status": "offline",
            "response_time_ms": round(response_time, 2),
            "message": "Database connection is unavailable."
        }


# ==========================================
# ADMIN PANEL - USER MANAGEMENT
# ==========================================

@app.get("/api/admin/users")
def get_admin_users(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    admin: User = Depends(require_admin),
):
    """Retrieve registered users. Admin access only."""

    try:
        from database.pg_database import SessionLocal

        with SessionLocal() as session:
            total_users = session.query(User).count()

            records = (
                session.query(User)
                .order_by(User.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            users = [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                    "avatar_url": user.avatar_url,
                    "role": user.role,
                    "created_at": user.created_at,
                }
                for user in records
            ]

        return {
            "status": "success",
            "total_users": total_users,
            "limit": limit,
            "offset": offset,
            "users": users,
        }

    except Exception:
        logger.exception("Failed to retrieve admin user list")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve users. Check backend logs."
        )


# ==========================================
# SAVED PLACES - USER MANAGEMENT
# ==========================================

@app.get("/api/saved-places")
def get_saved_places(
    current_user: User = Depends(get_current_user),
):
    """Get only the logged-in user's saved places."""

    try:
        from database.pg_database import SessionLocal
        from database.pg_models import SavedPlace

        with SessionLocal() as session:
            records = (
                session.query(SavedPlace)
                .filter(SavedPlace.user_id == current_user.id)
                .order_by(SavedPlace.created_at.desc())
                .all()
            )

            places = [
                {
                    "id": place.id,
                    "place_name": place.place_name,
                    "country": place.country,
                    "image_url": place.image_url,
                    "tag": place.tag,
                    "created_at": place.created_at,
                }
                for place in records
            ]

        return {
            "status": "success",
            "total": len(places),
            "places": places,
        }

    except Exception:
        logger.exception("Failed to retrieve saved places")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve saved places."
        )


@app.post("/api/saved-places")
def create_saved_place(
    request: SavedPlaceCreate,
    current_user: User = Depends(get_current_user),
):
    """Save a place for the authenticated user."""

    try:
        from sqlalchemy.exc import IntegrityError
        from database.pg_database import SessionLocal
        from database.pg_models import SavedPlace

        place_name = request.place_name.strip()
        country = request.country.strip()

        if not place_name or not country:
            raise HTTPException(
                status_code=400,
                detail="Place name and country are required."
            )

        if request.image_url and not request.image_url.startswith(
            ("https://", "http://")
        ):
            raise HTTPException(
                status_code=400,
                detail="Image URL must use HTTP or HTTPS."
            )

        with SessionLocal() as session:
            place = SavedPlace(
                user_id=current_user.id,
                place_name=place_name,
                country=country,
                image_url=request.image_url,
                tag=request.tag,
            )

            session.add(place)

            try:
                session.commit()
                session.refresh(place)
            except IntegrityError:
                session.rollback()
                raise HTTPException(
                    status_code=409,
                    detail="This place is already saved."
                )

            result = {
                "id": place.id,
                "place_name": place.place_name,
                "country": place.country,
                "image_url": place.image_url,
                "tag": place.tag,
                "created_at": place.created_at,
            }

        return {
            "status": "success",
            "message": "Place saved successfully.",
            "place": result,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Failed to save place")
        raise HTTPException(
            status_code=500,
            detail="Could not save place."
        )


@app.delete("/api/saved-places/{place_id}")
def delete_saved_place(
    place_id: int,
    current_user: User = Depends(get_current_user),
):
    """Delete only a place owned by the authenticated user."""

    try:
        from database.pg_database import SessionLocal
        from database.pg_models import SavedPlace

        with SessionLocal() as session:
            place = (
                session.query(SavedPlace)
                .filter(
                    SavedPlace.id == place_id,
                    SavedPlace.user_id == current_user.id,
                )
                .first()
            )

            if place is None:
                raise HTTPException(
                    status_code=404,
                    detail="Saved place not found."
                )

            session.delete(place)
            session.commit()

        return {
            "status": "success",
            "message": "Saved place removed successfully.",
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Failed to delete saved place")
        raise HTTPException(
            status_code=500,
            detail="Could not delete saved place."
        )


# ==========================================
# ADMIN PANEL - SAVED PLACES OVERVIEW
# ==========================================

@app.get("/api/admin/saved-places")
def get_admin_saved_places(
    limit: int = Query(default=100, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    admin: User = Depends(require_admin),
):
    """Admin-only overview of all users' saved places."""

    try:
        from database.pg_database import SessionLocal
        from database.pg_models import SavedPlace

        with SessionLocal() as session:
            total = session.query(SavedPlace).count()

            records = (
                session.query(SavedPlace, User.username, User.email)
                .join(User, SavedPlace.user_id == User.id)
                .order_by(SavedPlace.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )

            places = [
                {
                    "id": place.id,
                    "user_id": place.user_id,
                    "username": username,
                    "email": email,
                    "place_name": place.place_name,
                    "country": place.country,
                    "image_url": place.image_url,
                    "tag": place.tag,
                    "created_at": place.created_at,
                }
                for place, username, email in records
            ]

        return {
            "status": "success",
            "total": total,
            "places": places,
        }

    except Exception:
        logger.exception("Failed to retrieve admin saved places")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve saved places."
        )
