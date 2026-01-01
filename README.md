
# 👁️ VIZON (Visionlytics AI)

> **The Universal AI Data Analyst.** > *Turn any input—Image, URL, or CSV—into a "Tableau-Killer" Dashboard instantly.*

## 🚀 Overview
VIZON is a next-generation Business Intelligence tool powered by **Gemini 1.5 Flash**. Unlike traditional tools that require manual data entry, VIZON uses multi-modal AI to "see" documents, scrape websites, and read raw files, automatically converting them into structured insights and interactive dashboards.

**Current Version:** v0.2 (Architect MVP)  
**Status:** In Development / Stealth Mode

## ✨ Key Features
* **Universal Input:**
    * 📄 **Files:** Drag-and-drop CSV/Excel processing.
    * 📷 **Vision Analysis:** Upload photos of receipts, invoices, or menus; VIZON extracts the data to JSON/Table.
    * 🌐 **Web Scraper:** Input a URL to extract tabular data instantly.
* **The Data Refinery:** Automatically cleans and structures unstructured inputs into Pandas DataFrames.
* **Interactive Dashboard:**
    * Automatic Metric Cards (Total Sales, Items, etc.).
    * Sunburst & Treemap charts for hierarchical data.
    * AI-Powered Insights via Chat.
* **"Vi" Assistant:** Context-aware Q&A about your data.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **AI Engine:** Google Gemini 1.5 Flash
* **Data Processing:** Pandas, NumPy
* **Visualization:** Plotly Express
* **Utilities:** BeautifulSoup4 (Scraping), OpenPyxl (Excel)

## 💻 Local Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/vizon-ai.git](https://github.com/your-username/vizon-ai.git)
    cd vizon-ai
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Credentials:**
    * Create a folder named `.streamlit` in the root directory.
    * Create a file `.streamlit/secrets.toml` and add your key:
        ```toml
        GOOGLE_API_KEY = "your_actual_api_key_here"
        ```

4.  **Run the App:**
    ```bash
    streamlit run app.py
    ```

## 🔒 Security Note
This project uses `.gitignore` to prevent API keys from being uploaded to GitHub. Never commit your `secrets.toml` file.

---
© 2026 Visionlytics AI. All Rights Reserved.
