import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import stats
from scipy.stats import norm, t
import io
from PIL import Image
import plotly.io as pio
from datetime import datetime
import os

# Set page config
st.set_page_config(
    page_title="Signal Analyzer Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to make the select boxes and container wider
st.markdown(
    """
    <style>
    /* Main container styles */
    .main .block-container {
        max-width: 1200px !important;
        padding: 1rem !important;
        margin: 0 auto !important;
        width: 100% !important;
    }

    /* Override Streamlit's default container width */
    .css-1y4p8pa {
        max-width: 1200px !important;
        padding: 1rem !important;
        margin: 0 auto !important;
        width: 100% !important;
    }

    .css-1y4p8pa > div {
        max-width: 1200px !important;
        width: 100% !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Ensure full width for all main elements */
    .element-container, .stMarkdown, .stDataFrame {
        width: 100% !important;
        max-width: 1200px !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Force width on all Streamlit elements */
    .stSelectbox, .stMultiSelect, .stNumberInput, .stDateInput, .stTextInput {
        width: 100% !important;
        max-width: 1200px !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Override any potential max-width constraints */
    .stApp {
        max-width: 1200px !important;
        width: 100% !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    .stApp > div {
        max-width: 1200px !important;
        width: 100% !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Force width on plot containers */
    .plot-container, .js-plotly-plot {
        width: 100% !important;
        max-width: 1200px !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Ensure columns take full width */
    [data-testid="column"] {
        width: 100% !important;
        flex: 1 1 calc(33.333% - 1rem) !important;
        min-width: 200px !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Force width on metric containers */
    [data-testid="metric-container"] {
        width: 100% !important;
        max-width: 1200px !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Ensure horizontal blocks take full width */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 1rem !important;
        width: 100% !important;
        max-width: 1200px !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Override any potential container constraints */
    .container {
        max-width: 1200px !important;
        width: 100% !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Force width on all divs within the main container */
    .main .block-container > div {
        max-width: 1200px !important;
        width: 100% !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Ensure buttons take appropriate width */
    .stButton > button {
        width: auto !important;
        min-width: 150px !important;
        padding: 0.5rem 1rem !important;
        margin: 0.5rem !important;
    }

    /* Custom style for the histogram count selector */
    div[data-testid="stSelectbox"]:has(div:contains("Number of Histograms")) {
        width: 50px !important;
    }

    /* Button container styles */
    .button-container {
        display: flex;
        justify-content: flex-end;
        width: 100%;
        padding: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    /* File section styles */
    .file-section {
        display: flex;
        flex-direction: column;
        align-items: flex-end;
        width: 100%;
        padding: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    .file-text {
        margin-top: 5px;
        text-align: right;
        width: 100%;
    }

    /* Horizontal line styles */
    hr {
        margin: 1rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0));
        width: 100%;
        max-width: 1200px !important;
    }

    /* Vertical line styles */
    .vl {
        margin: 0 1rem;
        border: none;
        width: 1px;
        background: linear-gradient(to bottom, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0));
        height: 100%;
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
    }

    /* Table styles */
    .custom-table {
        margin: 0;
        padding: 0;
        font-size: 12px;
        width: 100%;
        max-width: 1200px !important;
    }

    .custom-table td {
        border: none !important;
        padding: 2px 10px !important;
    }

    .custom-table td:first-child {
        text-align: left;
    }

    .custom-table td:last-child {
        text-align: right;
    }

    .custom-table th {
        display: none;
    }

    .bold-text {
        font-weight: bold;
    }

    /* Chart container styles */
    .chart-container {
        width: 100%;
        margin: 0 auto;
        padding: 1rem !important;
        max-width: 1200px !important;
    }

    /* Metric container styles */
    [data-testid="metric-container"] {
        width: 100% !important;
        padding: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    /* Stacked columns fix */
    [data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 1rem !important;
        padding: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    /* Tooltip styles */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: pointer;
        padding: 1rem !important;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 300px;
        background-color: #f9f9f9;
        color: #333;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        top: 125%;
        left: 50%;
        margin-left: -150px;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }

    /* Streamlit elements width fix */
    .element-container, .stDateInput, .stNumberInput {
        width: 100% !important;
        padding: 1rem !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
    }

    /* Force full width on all Streamlit elements */
    .stMarkdown, .stDataFrame, .stSelectbox, .stMultiSelect, .stNumberInput, .stDateInput, .stTextInput, .stButton {
        width: 100% !important;
        max-width: 1200px !important;
        padding: 1rem !important;
        margin: 0 auto !important;
    }

    /* Ensure all containers take full width */
    .main .block-container, .stApp, .stApp > div, .element-container, .stMarkdown, .stDataFrame {
        width: 100% !important;
        max-width: 1200px !important;
        margin: 0 auto !important;
        padding: 1rem !important;
    }

    /* File uploader styles */
    .stFileUploader {
        width: 100% !important;
        padding: 1rem !important;
        margin: 0 auto !important;
        max-width: 1200px !important;
    }

    .stFileUploader > div {
        width: 100% !important;
        padding: 1rem !important;
        margin: 0 auto !important;
        max-width: 1200px !important;
    }

    /* Ensure buttons are visible */
    .stButton {
        width: auto !important;
        padding: 1rem !important;
        margin: 0.5rem !important;
        max-width: 1200px !important;
    }

    .stButton > button {
        width: auto !important;
        min-width: 150px !important;
        padding: 0.5rem 1rem !important;
        margin: 0.5rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Load and display the logo
logo_path = "logo.png"
if os.path.exists(logo_path):
    logo = Image.open(logo_path)
    st.image(logo, width=200)

# Create tabs
tab1, tab2 = st.tabs(["Signal Analyzer", "Monte Carlo Analysis"])

# Initialize session state for file upload
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

# File uploader in the main area
with tab1:
    st.title("Signal Analyzer Dashboard")
    
    # File uploader
    uploaded_file = st.file_uploader("Select Excel file", type=['xlsx', 'xls'])
    
    if uploaded_file is not None:
        st.session_state.uploaded_file = uploaded_file
        st.rerun()
    
    # Add horizontal line after title and file selection
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if st.session_state.uploaded_file is None:
        # Display the logo centered when no file is selected
        if os.path.exists(logo_path):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo, width=200)
    else:
        # Rest of your existing code for file processing...
        pass

# Monte Carlo Analysis tab
with tab2:
    st.title("Monte Carlo Analysis")
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Add warning icon with tooltip
    st.markdown(
        """
        <div class="tooltip">
            <span style="font-size: 24px;">⚠️</span>
            <span class="tooltiptext">
                <strong>Problems with Monte Carlo Simulation</strong><br><br>
                Market Cycle-Driven SQN is a measure of the quality of a trading system that takes into account both the risk-adjusted return and the time in trade. However, there are several problems with Monte Carlo simulation that should be considered:<br><br>
                1. Trade Order: The order of trades is important in price-action based systems, and Monte Carlo simulation may not capture this.<br>
                2. High Win Rate: Systems with high win rates may be curve-fitted and not representative of real market conditions.<br>
                3. Self-Correcting Systems: Systems that are self-correcting may not be properly simulated by Monte Carlo analysis.<br>
                4. Long-term Trend-following: Long-term trend-following systems may not be accurately represented by Monte Carlo simulation.<br>
                5. Original Set Size: The size of the original set can affect the drawdown levels in the simulation.<br>
                6. Position Sizing: The dynamics of the strategy can be dependent on position sizing.<br><br>
                <strong>General Guidelines:</strong><br>
                - Use Monte Carlo analysis for systems that are not dependent on trade order.<br>
                - Avoid using Monte Carlo analysis for systems with high win rates or that are self-correcting.<br>
                - Consider the size of the original set when interpreting results.<br>
                - Be aware of the impact of position sizing on the strategy dynamics.<br><br>
                Source: www.QuantSystems.ca
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Rest of your Monte Carlo Analysis code...
    pass 