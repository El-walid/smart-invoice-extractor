import streamlit as st
import requests
import pandas as pd

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
# TAB 1: THE UPLOAD DASHBOARD (YOUR OLD CODE)
# ==========================================
with tab1:
    uploaded_file = st.file_uploader("Drag and drop your PDF invoice here", type="pdf")

    if uploaded_file is not None:
        if st.button("🚀 Extract & Save to Database", type="primary", use_container_width=True):
            with st.spinner("Connecting to Azure and processing PDF..."):
                api_url = "http://127.0.0.1:8000/extract_and_save"
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
                    st.error("🚨 Could not connect to the Backend API!")

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
                # 1. Trigger the GET request we just built!
                response = requests.get("http://127.0.0.1:8000/history")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "error" in data:
                        st.error(data["error"])
                    else:
                        # 2. Extract the list from the JSON response
                        history_list = data.get("history", [])
                        
                        if len(history_list) > 0:
                            # 3. Magic! Pandas turns the JSON list into a DataFrame (table)
                            df = pd.DataFrame(history_list)
                            
                            # 4. Streamlit renders the DataFrame as a beautiful UI component
                            st.dataframe(df, hide_index=True, use_container_width=True)
                        else:
                            st.info("No invoices found in the database yet.")
                else:
                    st.error("Failed to fetch history from the server.")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the Backend API!")