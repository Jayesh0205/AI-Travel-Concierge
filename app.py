
import streamlit as st
import traceback 
from agent.agent import run_agent
from database.database import (
    initialize_database,
    save_search,
    get_recent_searches,
)

st.set_page_config(
    page_title="NovaTrip",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ NovaTrip")
st.write("Your intelligent AI travel planning assistant.")

# Initialize the existing SQLite database.
database_ready = True

try:
    initialize_database()
except Exception as e:
    database_ready = False
    print(f"SQLite initialization error: {e}")

# Sidebar: existing SQLite travel history.
with st.sidebar:
    st.header("📚 Travel History")

    if database_ready:
        try:
            history = get_recent_searches(10)

            if history:
                st.caption("Your 10 most recent searches")

                for item in history:
                    with st.expander(
                        f"Search #{item['id']} — {item['created_at']}"
                    ):
                        st.markdown("**Your request:**")
                        st.write(item["user_query"])

                        st.markdown("**Generated travel plan:**")
                        st.markdown(item["assistant_response"])
            else:
                st.info("Your saved searches will appear here.")
        except Exception as e:
            st.warning("Travel history is temporarily unavailable.")
            print(f"SQLite history error: {e}")
    else:
        st.warning("SQLite database is temporarily unavailable.")

# Upload travel information.
st.subheader("📄 Upload Travel Information")
st.caption(
    "Optional: Upload a .txt document to help NovaTrip "
    "answer using your own travel information."
)

uploaded_file = st.file_uploader(
    "Choose a text document",
    type=["txt"],
)

uploaded_text = ""

if uploaded_file is not None:
    try:
        file_bytes = uploaded_file.getvalue()

        try:
            uploaded_text = file_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            uploaded_text = file_bytes.decode("cp1252")

        if uploaded_text.strip():
            st.success(f"Uploaded: {uploaded_file.name}")
        else:
            st.warning("This text file is empty.")
            uploaded_text = ""

    except (UnicodeDecodeError, LookupError):
        st.error("Could not read this file. Please try another .txt file.")
        uploaded_text = ""

# Choose the agent execution mode.
st.subheader("⚙️ Agent Configuration")

agent_mode = st.radio(
    "Choose how NovaTrip should process your request:",
    ["Existing Agent", "LangGraph Workflow"],
    horizontal=True,
)

# Optional travel details for the LangGraph workflow.
origin = ""
destination = ""
departure_date = ""

if agent_mode == "LangGraph Workflow":
    st.info(
        "LangGraph coordinates travel research, available tools, "
        "itinerary generation, and PostgreSQL logging."
    )

    col1, col2 = st.columns(2)

    with col1:
        origin = st.text_input(
            "Starting city",
            placeholder="Example: Mumbai",
        )

    with col2:
        destination = st.text_input(
            "Destination city",
            placeholder="Example: Goa",
        )

    departure_date = st.date_input(
        "Departure date (optional)",
        value=None,
    )

    if departure_date is not None:
        departure_date = departure_date.isoformat()
    else:
        departure_date = ""

user_message = st.text_area(
    "Where would you like to go?",
    placeholder=(
        "Example: Plan a 3-day Goa trip with beaches, "
        "heritage sites, and a moderate budget."
    ),
    height=120,
)

if st.button("Plan My Trip", type="primary"):
    if not user_message.strip():
        st.warning("Please enter your travel request.")

    else:
        with st.spinner("NovaTrip is planning your trip..."):
            try:
                if agent_mode == "LangGraph Workflow":
                    # Initialize PostgreSQL only when this mode is used.
                    from database.pg_database import (
                        initialize_postgres,
                        check_postgres_connection,
                    )

                    if not check_postgres_connection():
                        raise RuntimeError(
                            "PostgreSQL connection could not be verified."
                        )

                    initialize_postgres()

                    # Run the LangGraph workflow.
                    from agent.workflow import run_travel_workflow

                    response = run_travel_workflow(
                        user_request=user_message,
                        uploaded_text=uploaded_text,
                        origin=origin.strip(),
                        destination=destination.strip(),
                        departure_date=departure_date,
                    )

                else:
                    # Preserve the existing agent as a fallback.
                    response = run_agent(
                        user_message,
                        uploaded_text=uploaded_text,
                    )

                if not response:
                    raise RuntimeError(
                        "The agent returned an empty travel plan."
                    )

                st.subheader("Your Travel Plan")
                st.markdown(response)

                # Continue saving successful searches to SQLite.
                if database_ready:
                    try:
                        save_search(user_message, response)
                        st.success(
                            "Travel request saved to SQLite history."
                        )
                    except Exception as e:
                        st.warning(
                            "Your plan was generated, but SQLite "
                            "could not save it."
                        )
                        print(f"SQLite save error: {e}")

                if agent_mode == "LangGraph Workflow":
                    st.success(
                        "LangGraph workflow completed. "
                        "Check PostgreSQL for saved workflow data "
                        "and API activity logs."
                    )

            except Exception as e:
                error_message = str(e)

                if any(
                    keyword in error_message.casefold()
                    for keyword in (
                        "resource_exhausted",
                        "429",
                        "quota exceeded",
                        "rate limit",
                    )
                ):
                    st.warning(
                        "NovaTrip has reached its AI request limit. "
                        "Please try again after the quota resets."
                    )
                else:
                    st.error(
                        "NovaTrip encountered an error. "
                        "Please check the terminal for details."
                    )
                    st.exception(e)  # temporary: shows full traceback in the app

                traceback.print_exc()
                print(f"NovaTrip error: {e}", flush=True)