
import logging
from collections import deque
from datetime import datetime, timezone
from time import perf_counter

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

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
def plan_travel(request: TravelPlanRequest):
    """Generate an itinerary using the existing LangGraph workflow."""

    try:
        from agent.workflow import run_travel_workflow

        itinerary = run_travel_workflow(
            user_request=request.user_request,
            uploaded_text=request.uploaded_text,
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date
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


@app.get("/api/trips", response_model=SavedTripsResponse)
def get_saved_trips():
    """Retrieve the latest saved itineraries."""

    try:
        from database.pg_database import SessionLocal
        from database.pg_models import SavedSearch

        with SessionLocal() as session:
            records = (
                session.query(SavedSearch)
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

        return {
            "status": "success",
            "trips": trips
        }

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
def get_saved_trip(trip_id: int):
    """Retrieve one saved itinerary."""

    try:
        from database.pg_database import SessionLocal
        from database.pg_models import SavedSearch

        with SessionLocal() as session:
            record = session.get(SavedSearch, trip_id)

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

    except Exception as exc:
        logger.exception("Failed to retrieve saved trip")

        error_message = str(exc).lower()

        if "503" in error_message or "unavailable" in error_message:
            raise HTTPException(
                status_code=503,
                detail="NovaTrip AI is temporarily busy. Please try again in a few minutes."
            )

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve saved trip. Check backend logs."
        )


# Monitoring Dashboard API
@app.get("/api/monitoring/overview")
def monitoring_overview():
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
def database_health():
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

