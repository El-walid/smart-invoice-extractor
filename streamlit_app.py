import streamlit as st
import requests

# Set the page style
st.set_page_config(page_title="Smart Invoice Extractor", page_icon="🧾", layout="centered")

# Header Section
st.title("🧾 Smart Invoice Extractor")
st.markdown("Automated data entry pipeline for Moroccan industrial zones. Upload a PDF invoice to instantly extract and sync data to Azure SQL.")
st.divider()

# File Uploader
uploaded_file = st.file_uploader("Drag and drop your PDF invoice here", type="pdf")

if uploaded_file is not None:
    # Button to trigger the API
    if st.button("🚀 Extract & Save to Database", type="primary", use_container_width=True):
        
        with st.spinner("Connecting to Azure and processing PDF..."):
            # The URL of your FastAPI server (running locally or in Docker)
            api_url = "http://127.0.0.1:8000/extract_and_save"
            
            # Package the file to send over HTTP
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
            
            try:
                # Send the POST request to our backend
                response = requests.post(api_url, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if our FastAPI sent back an error string
                    if "error" in data:
                        st.error(f"Extraction Failed: {data['error']}")
                    else:
                        st.success("Success! Invoice successfully parsed and committed to Azure SQL.")
                        st.balloons() # A fun little animation!
                        
                        # Display the extracted data in 3 neat columns
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.caption("🏢 Client Name")
                            st.subheader(data.get("client","Unknown"))
                            
                        # Keep the numbers as metrics!
                        col2.metric(label="💰 Total (TTC)",value=f"{data.get("total_saved_ttc",0)} DH")
                        col3.metric(label="📦 Items Processed", value=data.get("items_processed", 0))
                else:
                    st.error(f"Server Error: {response.status_code} - {response.text}")
                    
            except requests.exceptions.ConnectionError:
                st.error("🚨 Could not connect to the Backend API! Is your FastAPI server or Docker container running on port 8000?")