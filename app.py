
import streamlit as st

from agent.agent import run_agent
from agent.tools import set_uploaded_document


st.set_page_config(
    page_title="NovaTrip",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ NovaTrip")
st.write("Your intelligent AI travel planning assistant.")

st.subheader("📄 Upload Travel Information")
st.caption(
    "Optional: Upload a .txt document to help NovaTrip answer "
    "questions using your own travel information."
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

# Make the uploaded text available to the agent's search tool.
set_uploaded_document(uploaded_text)

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
                response = run_agent(user_message)
                st.subheader("Your Travel Plan")
                st.markdown(response)

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

                # Print technical details in the terminal, not to users.
                print(f"NovaTrip error: {e}")