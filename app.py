import streamlit as st

from rag.qa import answer_question


st.set_page_config(
    page_title="NovaTrip",
    page_icon="✈️",
    layout="wide"
)


st.title("✈️ NovaTrip")

st.write(
    "Your intelligent AI travel planning assistant."
)


user_message = st.text_input(
    "What can I help you with?"
)


if st.button("Ask AI"):

    if not user_message.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Searching travel knowledge and thinking..."):

            try:

                response = answer_question(user_message)

                st.subheader("AI Response")

                st.markdown(response)

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )