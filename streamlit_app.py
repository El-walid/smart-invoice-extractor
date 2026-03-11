import streamlit as st
import requests
import pandas as pd

# Set the page style
st.set_page_config(page_title="SmartExtract", page_icon="📄", layout="wide")

# --- CUSTOM CSS INJECTION ---
# This forces Streamlit to use the exact styling from your mockup
st.markdown("""
<style>
    /* Hide Streamlit's default top menu and footer for a cleaner look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Design for the 3 KPI Cards */
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 0.5rem;
        padding: 1.5rem;
        height: 100%;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        color: #f8fafc;
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1.2;
    }
    
    /* Design for the Green Success Banner */
    .success-banner {
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid #10b981;
        color: #10b981;
        padding: 1rem 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER LOGIC ---
col1, col2 = st.columns([1, 4])
with col1:
    st.markdown("### 📄 SmartExtract")
with col2:
    pass # Pushes the title to the left

st.markdown("<h1 style='text-align: center; margin-top: 2rem;'>Automate Your Invoicing Pipeline</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 3rem;'>Eliminate hours of manual data entry. Our AI-powered engine extracts high-fidelity data for factory and logistics managers in seconds.</p>", unsafe_allow_html=True)

# --- TABS ---
tab1, tab2 = st.tabs(["Dashboard", "History"])

# ==========================================
# TAB 1: UPLOAD DASHBOARD
# ==========================================
with tab1:
    st.write("") # Spacing
    uploaded_file = st.file_uploader("", type="pdf")

    if uploaded_file is not None:
        if st.button("Extract & Save to Database", type="primary", use_container_width=True):
            with st.spinner("Extracting data and syncing to Azure SQL..."):
                api_url = "http://127.0.0.1:8000/extract_and_save"
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                
                try:
                    response = requests.post(api_url, files=files)
                    if response.status_code == 200:
                        data = response.json()
                        if "error" in data:
                            st.error(data['error'])
                        else:
                            # --- CUSTOM HTML DASHBOARD OUTPUT ---
                            # 1. The Success Banner
                            st.markdown("""
                                <div class="success-banner">
                                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                                    Invoice Processed Successfully
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # 2. The Three Cards
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown(f"""
                                    <div class="metric-card">
                                        <div class="metric-label">CLIENT</div>
                                        <div class="metric-value">{data.get('client', 'Unknown')}</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                            with col2:
                                st.markdown(f"""
                                    <div class="metric-card">
                                        <div class="metric-label">TOTAL AMOUNT (TTC)</div>
                                        <div class="metric-value">{data.get('total_saved_ttc', 0):,.2f} DH</div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                            with col3:
                                st.markdown(f"""
                                    <div class="metric-card">
                                        <div class="metric-label">ITEMS PROCESSED</div>
                                        <div class="metric-value">{data.get('items_processed', 0)} <span style="font-size: 0.9rem; font-weight: 400; color: #94a3b8;">Line items</span></div>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.error("Server Error.")
                except requests.exceptions.ConnectionError:
                    st.error("🚨 Could not connect to the Backend API!")

# ==========================================
# TAB 2: INVOICE HISTORY
# ==========================================
with tab2:
    st.write("") # Spacing
    col_a, col_b = st.columns([3, 1])
    
    with col_a:
        st.markdown("### Invoice History")
        st.markdown("<p style='color: #94a3b8;'>Audit and manage your digitized procurement documents.</p>", unsafe_allow_html=True)
    
    with col_b:
        refresh = st.button("🔄 Refresh Data", use_container_width=True)
    
    if refresh:
        with st.spinner("Fetching data..."):
            try:
                response = requests.get("http://127.0.0.1:8000/history")
                if response.status_code == 200:
                    data = response.json()
                    if "error" in data:
                        st.error(data["error"])
                    else:
                        df = pd.DataFrame(data.get("history", []))
                        if not df.empty:
                            # Streamlit allows you to customize the dataframe rendering
                            st.dataframe(
                                df, 
                                hide_index=True, 
                                use_container_width=True,
                                height=400
                            )
                        else:
                            st.info("No invoices found.")
            except:
                st.error("API connection failed.")