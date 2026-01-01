import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os
import json
import requests
from bs4 import BeautifulSoup
from PIL import Image
import io

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(
    page_title="VIZON | AI Architect",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Neon/Cyberpunk Theme
st.markdown("""
    <style>
        .main { background-color: #0E1117; }
        .stButton>button {
            background-color: #00FF94;
            color: #000000;
            border-radius: 8px;
            font-weight: bold;
            border: none;
        }
        .stMetric {
            background-color: #1E1E1E;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #333;
        }
        h1, h2, h3 { color: #FAFAFA; }
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #1E1E1E;
            border-radius: 5px;
            color: #FFF;
        }
        .stTabs [aria-selected="true"] {
            background-color: #6C63FF;
        }
    </style>
""", unsafe_allow_html=True)

# --- 2. API SETUP ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except (FileNotFoundError, KeyError):
    api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("⚠️ System Error: API Key missing.")
    st.stop()

genai.configure(api_key=api_key)

# Model config (JSON mode enforced via prompt engineering for simplicity in this version)
generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

# --- 3. HELPER FUNCTIONS ---

def clean_json_string(text):
    """Helper to strip markdown code blocks from LLM response"""
    text = text.replace("```json", "").replace("```", "").strip()
    return text

def gemini_data_extractor(prompt, content):
    """Generic function to send content to Gemini and get JSON back"""
    system_prompt = """
    You are a Data Extraction Engine. 
    Analyze the provided input and extract structured data.
    Output ONLY valid JSON. 
    Format: [{"Column1": "Value", "Column2": 10, ...}]
    If dates exist, format as YYYY-MM-DD.
    Ensure numeric fields are numbers, not strings.
    """
    
    try:
        response = model.generate_content([system_prompt, prompt, content])
        json_str = clean_json_string(response.text)
        data = json.loads(json_str)
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"AI Extraction Failed: {e}")
        return pd.DataFrame()

def scrape_url(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        # Get text, limit to first 10k chars to avoid token limits on free tier
        return soup.get_text(separator=' ', strip=True)[:10000] 
    except Exception as e:
        return f"Error scraping URL: {e}"

# --- 4. SIDEBAR: UNIVERSAL INPUT ---
with st.sidebar:
    st.title("👁️ VIZON")
    st.caption("AI Data Architect")
    
    st.subheader("1. Input Source")
    input_mode = st.radio("Select Source", ["Upload File (CSV/Excel)", "Image Analysis", "Website URL", "Video Intelligence"])
    
    df = None # Initialize empty dataframe
    
    if input_mode == "Upload File (CSV/Excel)":
        uploaded_file = st.file_uploader("Drop your dataset", type=["csv", "xlsx"])
        if uploaded_file:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

    elif input_mode == "Image Analysis":
        uploaded_file = st.file_uploader("Upload Receipt/Table/Chart", type=["jpg", "png", "jpeg"])
        if uploaded_file and st.button("Extract Data"):
            img = Image.open(uploaded_file)
            with st.spinner("Vi is scanning the image..."):
                prompt = "Extract all tabular data visible in this image. Focus on items, quantities, prices, categories, or dates."
                df = gemini_data_extractor(prompt, img)
    
    elif input_mode == "Website URL":
        url = st.text_input("Enter URL (e.g., product page, wiki table)")
        if url and st.button("Scrape & Structure"):
            with st.spinner("Vi is reading the website..."):
                raw_text = scrape_url(url)
                prompt = "Analyze this website text. Extract any lists, tables, or product data into a structured JSON."
                df = gemini_data_extractor(prompt, raw_text)

    elif input_mode == "Video Intelligence":
        # Note: Direct video upload to Gemini File API is complex for a single-file Streamlit app.
        # For this MVP, we will treat it as a placeholder or require the user to extract frames.
        # However, to satisfy the prompt, we will use a text simulation or inform user.
        st.info("Video API requires Google Cloud Storage linking in production. For MVP, please upload a key frame (Image) above.")
        # Alternatively, if you have a small video < 10MB, we could try processing, but Streamlit cloud limits apply.

    st.markdown("---")
    st.info("System Ready")

# --- 5. MAIN DASHBOARD ---

if df is not None and not df.empty:
    # --- DATA REFINERY ---
    st.toast("Data Successfully Extracted!")
    
    # Create Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Dashboard", "📄 Raw Data", "🤖 AI Insights"])
    
    # Identify Numeric and Categorical Columns for automation
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()

    with tab1:
        st.subheader("Executive Overview")
        
        # 1. Metric Cards
        if numeric_cols:
            cols = st.columns(min(len(numeric_cols), 4))
            for i, col in enumerate(numeric_cols[:4]):
                total = df[col].sum()
                cols[i].metric(label=col, value=f"{total:,.2f}")
        else:
            st.warning("No numeric data found for metrics.")
            
        st.divider()
        
        # 2. Visuals
        col_charts_1, col_charts_2 = st.columns(2)
        
        with col_charts_1:
            if len(categorical_cols) > 0 and len(numeric_cols) > 0:
                st.caption("Categorical Breakdown (Treemap)")
                fig_tree = px.treemap(df, path=[categorical_cols[0]], values=numeric_cols[0], color=categorical_cols[0])
                st.plotly_chart(fig_tree, use_container_width=True)
            else:
                st.info("Need categorical and numeric data for Treemap.")

        with col_charts_2:
            if len(categorical_cols) > 1 and len(numeric_cols) > 0:
                st.caption("Hierarchical View (Sunburst)")
                fig_sun = px.sunburst(df, path=[categorical_cols[0], categorical_cols[1]], values=numeric_cols[0])
                st.plotly_chart(fig_sun, use_container_width=True)
            elif len(numeric_cols) >= 2:
                st.caption("Correlation (Scatter)")
                fig_scatter = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], color=categorical_cols[0] if categorical_cols else None)
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Not enough data dimensions for secondary chart.")

    with tab2:
        st.subheader("Data Refinery")
        st.dataframe(df, use_container_width=True)
        
        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download CSV", data=csv, file_name="vizon_extracted_data.csv", mime="text/csv")

    with tab3:
        st.subheader("Vi Assistant")
        
        # Chat Interface
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).write(msg["content"])

        if prompt := st.chat_input("Ask about your data..."):
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)
            
            # Contextual AI Analysis
            data_context = df.to_string()
            ai_prompt = f"Data Context:\n{data_context}\n\nUser Question: {prompt}\nAnswer as a Data Analyst."
            
            try:
                response = model.generate_content(ai_prompt)
                st.session_state.chat_history.append({"role": "assistant", "content": response.text})
                st.chat_message("assistant").write(response.text)
            except Exception as e:
                st.error(f"Error: {e}")

else:
    # Landing Page State
    st.header("Welcome to VIZON")
    st.markdown("### The Universal AI Data Analyst")
    st.markdown("""
    To get started, open the sidebar and select a data source:
    * **Upload File:** Traditional CSV/Excel analysis.
    * **Image Analysis:** Take a photo of a bill, menu, or report.
    * **Website URL:** Paste a link to extract product or financial data.
    """)
