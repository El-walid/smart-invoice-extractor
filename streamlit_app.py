import streamlit as st
import requests
import pandas as pd
import os

# --- DOCKER NETWORKING FIX ---
# If running in Docker Compose, it grabs "http://api:8000" from the environment.
# If running locally, it defaults to your local Uvicorn server.
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# Set the page style
st.set_page_config(page_title="Smart Invoice Extractor", page_icon="🧾", layout="wide")

# Header Section
st.title("🧾 Smart Invoice Extractor")
st.markdown("Automated data entry pipeline for Moroccan industrial zones. Upload a PDF invoice to instantly extract and sync data to Azure SQL.")
st.divider()

# --- CREATE TABS ---
# This splits your UI into two separate screens
tab1, tab2 = st.tabs(["🚀 Upload Dashboard", "📜 Invoice History"])

# ==========================================
# TAB 1: THE UPLOAD DASHBOARD
# ==========================================
with tab1:
    uploaded_file = st.file_uploader("Drag and drop your PDF invoice here", type="pdf")

    if uploaded_file is not None:
        if st.button("🚀 Extract & Save to Database", type="primary", use_container_width=True):
            with st.spinner("Connecting to Azure and processing PDF..."):
                # Use the dynamic base URL here
                api_url = f"{API_BASE_URL}/extract_and_save"
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                
                try:
                    response = requests.post(api_url, files=files)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if "error" in data:
                            st.error(f"Extraction Failed: {data['error']}")
                        else:
                            st.success("Success! Invoice successfully parsed and committed to Azure SQL.")
                            st.balloons() 
                            
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.caption("🏢 Client Name")
                                st.subheader(data.get("client", "Unknown"))
                                
                            col2.metric(label="💰 Total (TTC)", value=f"{data.get('total_saved_ttc', 0)} DH")
                            col3.metric(label="📦 Items Processed", value=data.get("items_processed", 0))
                    else:
                        st.error(f"Server Error: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("🚨 Could not connect to the Backend API! Is it running?")

# ==========================================
# TAB 2: THE INVOICE HISTORY
# ==========================================
with tab2:
    st.subheader("Invoice History")
    st.markdown("Audit and manage your digitized procurement documents.")
    
    # We use a button so it doesn't constantly spam your Azure database every time you click the screen
    if st.button("🔄 Refresh History", type="secondary"):
        with st.spinner("Fetching data from Azure SQL..."):
            try:
                # Use the dynamic base URL here too!
                history_url = f"{API_BASE_URL}/history"
                response = requests.get(history_url)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "error" in data:
                        st.error(data["error"])
                    else:
                        # Extract the list from the JSON response
                        history_list = data.get("history", [])
                        
                        if len(history_list) > 0:
                            # Magic! Pandas turns the JSON list into a DataFrame (table)
                            df = pd.DataFrame(history_list)
                            
                            # Streamlit renders the DataFrame as a beautiful UI component
                            st.dataframe(df, hide_index=True, use_container_width=True)
                        else:
                            st.info("No invoices found in the database yet.")
                else:
                    st.error("Failed to fetch history from the server.")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the Backend API! Is it running?")