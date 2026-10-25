import streamlit as st
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

# Initialize SQLite without preventing the app from opening.
database_ready = True

try:
    initialize_database()
except Exception as e:
    database_ready = False
    print(f"Database initialization error: {e}")

# Display previously saved travel searches.
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
            print(f"Database history error: {e}")
    else:
        st.warning("Database is temporarily unavailable.")

st.subheader("📄 Upload Travel Information")
st.caption(
    "Optional: Upload a .txt document to help NovaTrip "
    "answer questions using your own travel information."
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
                response = run_agent(
                    user_message,
                    uploaded_text=uploaded_text,
                )

                st.subheader("Your Travel Plan")
                st.markdown(response)

                # Save the successful response to SQLite.
                if database_ready:
                    try:
                        save_search(user_message, response)
                        st.success("Travel request saved to your history.")
                    except Exception as e:
                        st.warning(
                            "Your travel plan was generated, "
                            "but it could not be saved."
                        )
                        print(f"Database save error: {e}")

            except Exception as e:
                error_message = str(e)

                if (
                    "RESOURCE_EXHAUSTED" in error_message
                    or "429" in error_message
                ):
                    st.warning(
                        "NovaTrip has reached its AI request limit. "
                        "Please try again after the quota resets."
                    )
                else:
                    st.error(
                        "NovaTrip encountered an error. Please try again."
                    )

                print(f"NovaTrip error: {e}")