import streamlit as st
import asyncio
import os
from Recruiter import audit_candidate

st.set_page_config(page_title="AI Recruitment Audit", page_icon="🤖")

st.title("🤖 AI Recruitment Audit Agent")
st.markdown("Upload a candidate's resume to perform a deep-dive background audit.")

# Sidebar for inputs
with st.sidebar:
    st.header("Project Info")
    st.info("This agent uses Gemini 1.5 Flash and Tavily Search to verify candidate claims.")

# Form inputs
name = st.text_input("Candidate Full Name")
role = st.text_input("Target Position")
uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

if st.button("🚀 Run Deep Audit"):
    if not name or not role or not uploaded_file:
        st.error("Please provide the name, role, and resume.")
    else:
        with st.status("🕵️ Agent researching...", expanded=True) as status:
            # Save PDF temporarily
            temp_name = f"temp_{uploaded_file.name}"
            with open(temp_name, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                # Fix for 'Event loop is closed' error in Streamlit
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                report = loop.run_until_complete(audit_candidate(name, role, temp_name))
                
                status.update(label="✅ Audit Complete!", state="complete")
                st.subheader(f"Results for {name}")
                st.markdown(report)
                
            except Exception as e:
                st.error(f"Error during audit: {e}")
            finally:
                if 'loop' in locals():
                    loop.close()
                if os.path.exists(temp_name):
                    os.remove(temp_name)