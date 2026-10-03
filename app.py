import streamlit as st

from agent.llm import get_llm


st.set_page_config(
    page_title="AI Travel Concierge",
    page_icon="✈️",
    layout="wide"
)


st.title("✈️ AI Travel Concierge")

st.write(
    "Your intelligent travel planning assistant."
)


user_message = st.text_input(
    "What can I help you with?"
)


if st.button("Ask AI"):

    if not user_message.strip():

        st.warning("Please enter a question.")

    else:

        with st.spinner("Thinking..."):

            try:

                llm = get_llm()

                response = llm.invoke(user_message)

                st.subheader("AI Response")

                if isinstance(response.content, list):

                    text_response = ""

                    for item in response.content:

                        if isinstance(item, dict) and item.get("type") == "text":
                            text_response += item.get("text", "")

                    st.markdown(text_response)

                else:

                    st.markdown(response.content)

            except Exception as e:

                st.error(
                    f"Something went wrong: {e}"
                )