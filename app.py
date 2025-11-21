import streamlit as st

from src.workflow import run_volunteer_agent_flow

# Page Config
st.set_page_config(page_title="Beacon - AI Volunteer Guide", page_icon="🕯️")

# Title and Header
st.title("Beacon 🕯️")
st.subheader("Find local volunteer opportunities in seconds.")

# User Input
user_request = st.text_input("What kind of volunteering are you looking for?",
                             placeholder="e.g., Animal welfare in Mumbai this weekend")

# Button to trigger the agent
if st.button("Find Opportunities"):
    if user_request:
        # Streamlit has a status container that is perfect for your sequential agents
        with st.status("Beacon is working...", expanded=True) as status:

            st.write("🤖 ResearchAgent is analyzing your request...")
            # In a real migration, you might want to yield status updates from your main.py
            # For now, we just run the full flow
            final_response = run_volunteer_agent_flow(user_request)

            st.write("✅ Search complete!")
            status.update(label="Mission Accomplished!",
                          state="complete", expanded=False)

        # Display Result
        st.markdown("### Here is what we found:")
        st.markdown(final_response)
    else:
        st.warning("Please enter a request first.")
