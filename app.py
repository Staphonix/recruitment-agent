import streamlit as st
import os
import asyncio
from Recruiter import audit_candidate

# UI Configuration
st.set_page_config(page_title="AI Recruitment Auditor", page_icon="🕵️‍♂️")
st.title("🕵️‍♂️ AI Recruitment Auditor")
st.info("Upload a resume to start the deep-dive verification process.")

# Input Section
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Full Name", placeholder="e.g., Mira Murati")
with col2:
    role = st.text_input("Target Position", placeholder="e.g., CTO")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if st.button("🚀 Start Audit"):
    if not name or not uploaded_file:
        st.error("Missing candidate name or resume file!")
    else:
        with st.status("🔍 Agent is scouring the web and reading PDF...", expanded=True) as status:
            # Create a temporary file path
            temp_name = f"temp_{uploaded_file.name}"
            with open(temp_name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                report = loop.run_until_complete(audit_candidate(name, role, temp_name))
            finally:
                loop.close()
                
                status.update(label="✅ Audit Complete!", state="complete")
                st.subheader(f"Verification Report: {name}")
                st.markdown(report)
                
            except Exception as e:
                st.error(f"Error during audit: {e}")
            finally:
                # Cleanup: Delete the temp file after processing
                if os.path.exists(temp_name):
                    os.remove(temp_name)