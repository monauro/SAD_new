import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import numpy as np
import base64
from PIL import Image
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import tempfile
import plotly.io as pio
from scipy.stats import norm
import plotly.graph_objects as go
from scipy.stats import t

# Create tabs
# tab1, tab2 = st.tabs(["Signal Analyzer", "Monte Carlo Analysis"])

# Check if file_path is already in session state
if 'file_path' not in st.session_state:
    st.session_state.file_path = None

# Initialize show_table in session state
if 'show_table' not in st.session_state:
    st.session_state.show_table = False

# Function to create PDF report
def create_pdf_report(df_filtered2, metrics_data1, metrics_data2, selected_column1, selected_column2, chart_columns):
    try:
        st.text('Creating temporary directory...')
        # Create a temporary directory for images
        temp_dir = tempfile.mkdtemp()
        st.text(f'Temporary directory created at: {temp_dir}')
        
        st.text('Creating temporary file...')
        # Create a temporary file for the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            pdf_path = tmp_file.name
        
        st.text('Initializing PDF document...')
        # Create the PDF document with A4 size
        from reportlab.lib.pagesizes import A4
        doc = SimpleDocTemplate(pdf_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []
        
        st.text('Adding title...')
        # Add title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,  # Reduced font size for A4
            spaceAfter=20,
            alignment=1  # Center alignment
        )
        elements.append(Paragraph("Signal Analyzer Report", title_style))
        
        st.text('Creating filter information table...')
        # Create a table for filter information
        filter_data = [
            ["Filter Information", ""],
            ["Filter 1", selected_column1],
            ["Total Records", str(len(df_filtered2))],
            ["P(A)", f"{(len(df_filtered2)/len(df))*100:.2f}%"],
            ["Filter 2", selected_column2],
            ["P(B)", f"{(len(df_filtered2)/len(df))*100:.2f}%"],
            ["P(B|A)", f"{(len(df_filtered2)/len(df_filtered2))*100:.2f}%"]
        ]
        
        filter_table = Table(filter_data, colWidths=[150, 250])  # Adjusted widths for A4
        filter_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        elements.append(filter_table)
        elements.append(Spacer(1, 20))
        
        st.text('Adding metrics tables...')
        # Add metrics tables side by side
        if metrics_data1 and metrics_data2:
            # Create data for both tables
            metrics_table_data1 = [
                [Paragraph(f"Metrics for {selected_column1}", styles['Heading3']), ""],
                ["Win Rate", f"{metrics_data1['win_rate']:.2f}%"],
                ["Net Win", f"{metrics_data1['net_win']:.2f} R"],
                ["Total Win", f"{metrics_data1['total_win']:.2f} R"],
                ["Total Loss", f"{metrics_data1['total_loss']:.2f} R"],
                ["SQN", f"{metrics_data1['sqn']:.2f}"],
                ["StdDev", f"{metrics_data1['std_dev']:.2f}"],
                ["Median R", f"{metrics_data1['median_r']:.2f}"],
                ["Mode", f"{metrics_data1['mode_r']:.2f}"],
                ["Avrg R", f"{metrics_data1['avg_r']:.2f}"]
            ]
            
            metrics_table_data2 = [
                [Paragraph(f"Metrics for {selected_column2}", styles['Heading3']), ""],
                ["Win Rate", f"{metrics_data2['win_rate']:.2f}%"],
                ["Net Win", f"{metrics_data2['net_win']:.2f} R"],
                ["Total Win", f"{metrics_data2['total_win']:.2f} R"],
                ["Total Loss", f"{metrics_data2['total_loss']:.2f} R"],
                ["SQN", f"{metrics_data2['sqn']:.2f}"],
                ["StdDev", f"{metrics_data2['std_dev']:.2f}"],
                ["Median R", f"{metrics_data2['median_r']:.2f}"],
                ["Mode", f"{metrics_data2['mode_r']:.2f}"],
                ["Avrg R", f"{metrics_data2['avg_r']:.2f}"]
            ]
            
            # Create tables
            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ])
            
            table1 = Table(metrics_table_data1, colWidths=[120, 80])  # Adjusted widths for A4
            table1.setStyle(table_style)
            table2 = Table(metrics_table_data2, colWidths=[120, 80])  # Adjusted widths for A4
            table2.setStyle(table_style)
            
            # Create a table to hold both metrics tables side by side
            combined_table = Table([[table1, table2]], colWidths=[250, 250])  # Adjusted widths for A4
            combined_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(combined_table)
        
        st.text('Adding page break...')
        # Add page break before histograms
        elements.append(PageBreak())
        
        st.text('Adding histograms title...')
        # Add histograms title
        elements.append(Paragraph("Histograms", title_style))
        elements.append(Spacer(1, 20))
        
        st.text('Generating histograms...')
        # Create histograms (2 per row)
        for i in range(0, len(chart_columns), 2):
            hist_row = []
            for j in range(2):
                if i + j < len(chart_columns):
                    column = chart_columns[i + j]
                    if pd.api.types.is_numeric_dtype(df_filtered2[column]):
                        try:
                            st.text(f'Generating histogram for {column}...')
                            
                            # Create a simple histogram using matplotlib
                            import matplotlib.pyplot as plt
                            import io
                            import re
                            
                            # Clean column name for file name
                            safe_column_name = re.sub(r'[<>:"/\\|?*]', '_', column)
                            
                            plt.figure(figsize=(6, 3))  # Adjusted size for A4
                            plt.hist(df_filtered2[column].dropna(), bins=30, edgecolor='black')
                            plt.title(f'Distribution of "{column}"', fontsize=10)
                            plt.xlabel('Value', fontsize=8)
                            plt.ylabel('Frequency', fontsize=8)
                            plt.xticks(fontsize=7)
                            plt.yticks(fontsize=7)
                            
                            # Save plot to a bytes buffer
                            buf = io.BytesIO()
                            plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
                            plt.close()
                            
                            # Convert buffer to image
                            buf.seek(0)
                            img = Image.open(buf)
                            
                            # Save to temporary file in the temp directory
                            img_path = os.path.join(temp_dir, f"temp_histogram_{safe_column_name}.png")
                            img.save(img_path)
                            
                            # Add image to row with adjusted size for A4
                            hist_row.append(RLImage(img_path, width=250, height=150))
                            
                            # Clean up buffer
                            buf.close()
                            
                        except Exception as e:
                            st.error(f"Error generating histogram for {column}: {str(e)}")
                            continue
            
            if hist_row:
                # Add spacer if only one histogram in row
                if len(hist_row) == 1:
                    hist_row.append(Spacer(250, 150))
                
                # Create table for histogram row
                hist_table = Table([hist_row], colWidths=[250, 250])  # Adjusted widths for A4
                hist_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(hist_table)
                elements.append(Spacer(1, 20))
        
        st.text('Building PDF...')
        # Build PDF
        doc.build(elements)
        st.text('PDF generation completed!')
        
        # Clean up temporary directory
        import shutil
        shutil.rmtree(temp_dir)
        
        return pdf_path
        
    except Exception as e:
        st.error(f"Error in create_pdf_report: {str(e)}")
        raise e

# Function to get file path using tkinter
def get_file_path():
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = askopenfilename(filetypes=[("Excel files", "*.xlsx *.xlsm")])
    root.destroy()
    return file_path

# Add function to load and encode image
def get_image_base64(image_path):
    with Image.open(image_path) as img:
        # Convert to RGB if image is in RGBA format
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return base64.b64encode(buffer.getvalue()).decode()

# Custom CSS to make the select boxes and container wider
st.markdown(
    """
    <style>
    /* Center content and set max width */
    .main .block-container {
        max-width: 1200px !important;
        padding: 2rem 1rem !important;
        margin: 0 auto !important;
    }

    /* Make select boxes and containers full width */
    .stSelectbox, .stMultiSelect {
        width: 100% !important;
    }

    /* Custom style for the histogram count selector */
    div[data-testid="stSelectbox"]:has(div:contains("Number of Histograms")) {
        width: 50px !important;
    }

    /* Center the title and content */
    .stMarkdown {
        margin: 0 auto !important;
        text-align: center !important;
    }

    /* Style for buttons and file section */
    .button-container {
        display: flex;
        justify-content: center;
        width: 100%;
        margin: 1rem 0;
    }

    .file-section {
        display: flex;
        flex-direction: column;
        align-items: center;
        width: 100%;
        margin: 1rem 0;
    }

    .file-text {
        margin-top: 5px;
        text-align: center;
        width: 100%;
    }

    /* Divider styles */
    hr {
        margin: 1rem auto;
        border: none;
        height: 1px;
        background: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0));
        width: 80%;
    }

    /* Table styles */
    .custom-table {
        margin: 0 auto;
        padding: 0;
        font-size: 12px;
        width: 100%;
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

    /* Button styles */
    .stButton {
        width: 100%;
        display: flex;
        justify-content: center;
    }

    .stButton > button {
        width: auto;
    }

    /* Make sure all elements are centered */
    .element-container, .stMarkdown, .stDataFrame {
        margin-left: auto !important;
        margin-right: auto !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Show tabs only if a file is selected
if st.session_state.file_path:
    tab1, tab2 = st.tabs(["Signal Analyzer", "Monte Carlo Analysis"])
    
    with tab1:
        # Title and button in the same line
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown("# **Signal Analyzer Dashboard**")

        with col2:
            st.markdown('<div class="file-section">', unsafe_allow_html=True)
            container = st.container()
            with container:
                if st.button('Select Excel file', key='select_file'):
                    file_path = get_file_path()
                    if file_path:
                        st.session_state.file_path = file_path
                        file_name = os.path.basename(file_path)
                        st.markdown(f'<div class="file-text">Selected file: {file_name}</div>', unsafe_allow_html=True)
                elif st.session_state.file_path:
                    file_name = os.path.basename(st.session_state.file_path)
                    st.markdown(f'<div class="file-text">Selected file: {file_name}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Horizontal line with shadow
        st.markdown("<hr>", unsafe_allow_html=True)
        
        # Load the Excel file
        df = pd.read_excel(st.session_state.file_path, engine='openpyxl')
        
        # Display logo2 after loading Excel
        try:
            logo2_base64 = get_image_base64(r"C:\Users\monau\Downloads\logo2.png")
            st.markdown(f"""
                <div style='text-align: center; margin-top: -60px; margin-bottom: -40px; position: relative; z-index: 1;'>
                    <img src='data:image/png;base64,{logo2_base64}' alt='Logo2' style='width: 80px; height: 80px; object-fit: contain; border-radius: 50%; position: relative; z-index: 2;'>
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading logo2: {str(e)}")
        
        # Calculate total rows
        total_rows = len(df)
        
        # Initialize filtered dataframes
        df_filtered1 = df.copy()
        df_filtered2 = df.copy()

        # Create a row for section titles
        title_col1, title_col2, title_col3 = st.columns([0.9, 0.9, 1.2])
        
        with title_col1:
            st.markdown("### Filters")
        
        with title_col2:
            st.markdown("")  # Empty space to maintain alignment
        
        with title_col3:
            st.markdown("### Metrics")

        # Create columns for Filter 1 and Filter 2
        col1, col2, col3 = st.columns([0.9, 0.9, 1.2])

        with col1:
            # Dropdown to select the filter header for Filter 1
            filter_header_1 = st.selectbox('Select the header to filter 1', df.columns)

            if pd.api.types.is_datetime64_any_dtype(df[filter_header_1]):
                min_date = df[filter_header_1].min()
                max_date = df[filter_header_1].max()
                date_range = st.date_input(f'Select the date range for "{filter_header_1}"', [min_date, max_date])
                if len(date_range) == 2:
                    start_date = datetime.combine(date_range[0], datetime.min.time())
                    end_date = datetime.combine(date_range[1], datetime.min.time())
                    df_filtered1 = df[(df[filter_header_1] >= start_date) & (df[filter_header_1] <= end_date)]
                else:
                    df_filtered1 = df.copy()
            elif pd.api.types.is_numeric_dtype(df[filter_header_1]):
                min_value = float(round(df[filter_header_1].min(), 2))
                max_value = float(round(df[filter_header_1].max(), 2))
                
                # Initialize session state if not exists
                if f'number_min_1_{filter_header_1}' not in st.session_state:
                    st.session_state[f'number_min_1_{filter_header_1}'] = min_value
                if f'number_max_1_{filter_header_1}' not in st.session_state:
                    st.session_state[f'number_max_1_{filter_header_1}'] = max_value
                if f'range_slider_1_{filter_header_1}' not in st.session_state:
                    st.session_state[f'range_slider_1_{filter_header_1}'] = (min_value, max_value)
                
                # Callback functions for Filter 1
                def update_slider_1():
                    st.session_state[f'range_slider_1_{filter_header_1}'] = (
                        st.session_state[f'number_min_1_{filter_header_1}'],
                        st.session_state[f'number_max_1_{filter_header_1}']
                    )

                def update_inputs_1():
                    st.session_state[f'number_min_1_{filter_header_1}'] = st.session_state[f'range_slider_1_{filter_header_1}'][0]
                    st.session_state[f'number_max_1_{filter_header_1}'] = st.session_state[f'range_slider_1_{filter_header_1}'][1]
                
                col1_1, col1_2 = st.columns(2)
                
                with col1_1:
                    condition_min = st.selectbox('Condition (Min)', ['Greater than or equal to', 'Greater than'])
                    min_input = st.number_input(
                        f'Value ({min_value:.2f} : {max_value:.2f})', 
                        min_value=float(min_value),
                        max_value=float(max_value),
                        key=f'number_min_1_{filter_header_1}',
                        on_change=update_slider_1
                    )
                
                with col1_2:
                    condition_max = st.selectbox('Condition (Max)', ['Less than or equal to', 'Less than'])
                    max_input = st.number_input(
                        f'Value ({min_value:.2f} : {max_value:.2f})', 
                        min_value=float(min_value),
                        max_value=float(max_value),
                        key=f'number_max_1_{filter_header_1}',
                        on_change=update_slider_1
                    )
                
                # Add range slider without title and label
                min_val, max_val = st.slider(
                    " ",  # Empty space as label to maintain layout
                    min_value=float(min_value),
                    max_value=float(max_value),
                    key=f'range_slider_1_{filter_header_1}',
                    on_change=update_inputs_1
                )

                if condition_min == 'Greater than':
                    df_filtered1 = df[df[filter_header_1] > min_val]
                else:
                    df_filtered1 = df[df[filter_header_1] >= min_val]
                
                if condition_max == 'Less than':
                    df_filtered1 = df_filtered1[df_filtered1[filter_header_1] < max_val]
                else:
                    df_filtered1 = df_filtered1[df_filtered1[filter_header_1] <= max_val]
            else:
                unique_values = df[filter_header_1].unique()
                selected_values = st.multiselect(f'Select values for "{filter_header_1}"', unique_values)
                if selected_values:
                    df_filtered1 = df[df[filter_header_1].isin(selected_values)]
                else:
                    df_filtered1 = df.copy()

            # After filter 1 settings, display P(A)
            if not df_filtered1.empty:
                p_a = (len(df_filtered1)/total_rows)*100
                st.markdown(f"**P(A): {p_a:.2f}%**")
            else:
                st.markdown("**P(A): 0.00%**")

        st.markdown('<div class="vl"></div>', unsafe_allow_html=True)

        with col2:
            filter_header_2 = st.selectbox('Select the header to filter 2', df.columns)

            if pd.api.types.is_datetime64_any_dtype(df[filter_header_2]):
                min_date = df[filter_header_2].min()
                max_date = df[filter_header_2].max()
                date_range = st.date_input(f'Select the date range for "{filter_header_2}"', [min_date, max_date])
                if len(date_range) == 2:
                    start_date = datetime.combine(date_range[0], datetime.min.time())
                    end_date = datetime.combine(date_range[1], datetime.min.time())
                    df_filtered2 = df_filtered1[(df_filtered1[filter_header_2] >= start_date) & (df_filtered1[filter_header_2] <= end_date)]
                else:
                    df_filtered2 = df_filtered1.copy()
            elif pd.api.types.is_numeric_dtype(df[filter_header_2]):
                min_value = float(round(df[filter_header_2].min(), 2))
                max_value = float(round(df[filter_header_2].max(), 2))
                
                # Initialize session state if not exists
                if f'number_min_2_{filter_header_2}' not in st.session_state:
                    st.session_state[f'number_min_2_{filter_header_2}'] = min_value
                if f'number_max_2_{filter_header_2}' not in st.session_state:
                    st.session_state[f'number_max_2_{filter_header_2}'] = max_value
                if f'range_slider_2_{filter_header_2}' not in st.session_state:
                    st.session_state[f'range_slider_2_{filter_header_2}'] = (min_value, max_value)
                
                # Callback functions for Filter 2
                def update_slider_2():
                    st.session_state[f'range_slider_2_{filter_header_2}'] = (
                        st.session_state[f'number_min_2_{filter_header_2}'],
                        st.session_state[f'number_max_2_{filter_header_2}']
                    )

                def update_inputs_2():
                    st.session_state[f'number_min_2_{filter_header_2}'] = st.session_state[f'range_slider_2_{filter_header_2}'][0]
                    st.session_state[f'number_max_2_{filter_header_2}'] = st.session_state[f'range_slider_2_{filter_header_2}'][1]
                
                col2_1, col2_2 = st.columns(2)
                
                with col2_1:
                    condition_min = st.selectbox('Condition (Min)', ['Greater than or equal to', 'Greater than'], key='condition_min_2')
                    min_input = st.number_input(
                        f'Value ({min_value:.2f} : {max_value:.2f})', 
                        min_value=float(min_value),
                        max_value=float(max_value),
                        key=f'number_min_2_{filter_header_2}',
                        on_change=update_slider_2
                    )
                
                with col2_2:
                    condition_max = st.selectbox('Condition (Max)', ['Less than or equal to', 'Less than'], key='condition_max_2')
                    max_input = st.number_input(
                        f'Value ({min_value:.2f} : {max_value:.2f})', 
                        min_value=float(min_value),
                        max_value=float(max_value),
                        key=f'number_max_2_{filter_header_2}',
                        on_change=update_slider_2
                    )
                
                # Add range slider without title and label
                min_val, max_val = st.slider(
                    " ",  # Empty space as label to maintain layout
                    min_value=float(min_value),
                    max_value=float(max_value),
                    key=f'range_slider_2_{filter_header_2}',
                    on_change=update_inputs_2
                )

                if condition_min == 'Greater than':
                    df_filtered2 = df_filtered1[df_filtered1[filter_header_2] > min_val]
                else:
                    df_filtered2 = df_filtered1[df_filtered1[filter_header_2] >= min_val]
                
                if condition_max == 'Less than':
                    df_filtered2 = df_filtered2[df_filtered2[filter_header_2] < max_val]
                else:
                    df_filtered2 = df_filtered2[df_filtered2[filter_header_2] <= max_val]
            else:
                unique_values = df[filter_header_2].unique()
                selected_values = st.multiselect(f'Select values for "{filter_header_2}"', unique_values)
                if selected_values:
                    df_filtered2 = df_filtered1[df_filtered1[filter_header_2].isin(selected_values)]
                else:
                    df_filtered2 = df_filtered1.copy()

            # After filter 2 settings, display P(B) and P(B|A)
            if not df_filtered2.empty:
                p_b = (len(df_filtered2)/total_rows)*100
                if not df_filtered1.empty:
                    p_b_given_a = (len(df_filtered2) / len(df_filtered1)) * 100
                    st.markdown(f"""
                        <div style='display: flex; align-items: center; gap: 10px;'>
                            <span><strong>P(B): {p_b:.2f}%</strong></span>
                            <span style='color: #888; font-size: 18px;'>⚡</span>
                            <span><strong>P(B|A): {p_b_given_a:.2f}%</strong></span>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"**P(B): {p_b:.2f}%**")
            else:
                st.markdown("""
                    <div style='display: flex; align-items: center; gap: 10px;'>
                        <span><strong>P(B): 0.00%</strong></span>
                        <span style='color: #888; font-size: 18px;'>⚡</span>
                        <span><strong>P(B|A): 0.00%</strong></span>
                    </div>
                """, unsafe_allow_html=True)

        with col3:
            # Create two metrics controls side by side
            metrics_col1, metrics_col2 = st.columns(2)
            
            with metrics_col1:
                metrics_column1 = st.selectbox('Select column for metrics (No SC-In)', df.columns, key='metrics1')
                
                if pd.api.types.is_numeric_dtype(df[metrics_column1]):
                    # Calculate metrics for first column
                    total_elements = len(df_filtered2)
                    if total_elements > 0:
                        # Win Rate
                        wins = len(df_filtered2[df_filtered2[metrics_column1] > 0])
                        win_rate = (wins / total_elements) * 100
                        
                        # Total Win and Loss
                        total_win = df_filtered2[df_filtered2[metrics_column1] > 0][metrics_column1].sum()
                        total_loss = df_filtered2[df_filtered2[metrics_column1] < 0][metrics_column1].sum()
                        net_win = total_win + total_loss
                        
                        # Statistical metrics
                        std_dev = df_filtered2[metrics_column1].std()
                        median_r = df_filtered2[metrics_column1].median()
                        mode_r = df_filtered2[metrics_column1].mode().iloc[0] if not df_filtered2[metrics_column1].mode().empty else 0
                        avg_r = df_filtered2[metrics_column1].mean()
                        
                        # SQN calculation
                        sqn = (avg_r / std_dev) * np.sqrt(total_elements) if std_dev != 0 else 0
                        
                        # Create HTML for first metrics table
                        html1 = f"""
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <table class="custom-table" style="margin-right: 10px;">
                                <tr>
                                    <td class="bold-text">Win Rate</td>
                                    <td class="bold-text">{win_rate:.2f}%</td>
                                </tr>
                                 <tr>
                                    <td class="bold-text">Net Win</td>
                                    <td class="bold-text">{net_win:.2f} R</td>
                                </tr>
                                <tr>
                                    <td>Total Win</td>
                                    <td>{total_win:.2f} R</td>
                                </tr>
                                <tr>
                                    <td>Total Loss</td>
                                    <td>{total_loss:.2f} R</td>
                                </tr>                           
                            </table>
                            <table class="custom-table">
                              <tr>
                                    <td class="bold-text">SQN</td>
                                    <td class="bold-text">{sqn:.2f}</td>
                                </tr>
                                <tr>
                                    <td>StdDev</td>
                                    <td>{std_dev:.2f}</td>
                                </tr>
                                <tr>
                                    <td>Median R</td>
                                    <td>{median_r:.2f}</td>
                                </tr>
                                <tr>
                                    <td>Mode</td>
                                    <td>{mode_r:.2f}</td>
                                </tr>
                                <tr>
                                    <td>Avrg R</td>
                                    <td>{avg_r:.2f}</td>
                                </tr>                          
                            </table>
                        </div>
                        """
                        st.markdown(html1, unsafe_allow_html=True)
                    else:
                        st.write("No data available")
                else:
                    st.write("Select numeric column")

            with metrics_col2:
                metrics_column2 = st.selectbox('Select column for metrics (SC-In)', df.columns, key='metrics2')
                
                if pd.api.types.is_numeric_dtype(df[metrics_column2]):
                    # Calculate metrics for second column
                    total_elements = len(df_filtered2)
                    if total_elements > 0:
                        # Win Rate
                        wins = len(df_filtered2[df_filtered2[metrics_column2] > 0])
                        win_rate = (wins / total_elements) * 100
                        
                        # Total Win and Loss
                        total_win = df_filtered2[df_filtered2[metrics_column2] > 0][metrics_column2].sum()
                        total_loss = df_filtered2[df_filtered2[metrics_column2] < 0][metrics_column2].sum()
                        net_win = total_win + total_loss
                        
                        # Statistical metrics
                        std_dev = df_filtered2[metrics_column2].std()
                        median_r = df_filtered2[metrics_column2].median()
                        mode_r = df_filtered2[metrics_column2].mode().iloc[0] if not df_filtered2[metrics_column2].mode().empty else 0
                        avg_r = df_filtered2[metrics_column2].mean()
                        
                        # SQN calculation
                        sqn = (avg_r / std_dev) * np.sqrt(total_elements) if std_dev != 0 else 0
                        
                        # Create HTML for second metrics table
                        html2 = f"""
                        <div style="display: flex; justify-content: space-between; margin-top: 10px;">
                            <table class="custom-table" style="margin-right: 10px;">
                                <tr>
                                    <td class="bold-text">Win Rate</td>
                                    <td class="bold-text">{win_rate:.2f}%</td>
                                </tr>
                                <tr>
                                    <td class="bold-text">Net Win</td>
                                    <td class="bold-text">{net_win:.2f} R</td>
                                </tr>
                                <tr>
                                    <td>Total Win</td>
                                    <td>{total_win:.2f} R</td>
                                </tr>
                                <tr>
                                    <td>Total Loss</td>
                                    <td>{total_loss:.2f} R</td>
                                </tr>                            
                            </table>
                            <table class="custom-table">
                            <tr>
                                    <td class="bold-text">SQN</td>
                                    <td class="bold-text">{sqn:.2f}</td>
                                </tr>
                                <tr>
                                    <td>StdDev</td>
                                    <td>{std_dev:.2f}</td>
                                </tr>
                                <tr>
                                    <td>Median R</td>
                                    <td>{median_r:.2f}</td>
                                </tr>
                                <tr>
                                    <td>Mode</td>
                                    <td>{mode_r:.2f}</td>
                                </tr>
                                <tr>
                                    <td>Avrg R</td>
                                    <td>{avg_r:.2f}</td>
                                </tr>                            
                            </table>
                        </div>
                        """
                        st.markdown(html2, unsafe_allow_html=True)
                    else:
                        st.write("No data available")
                else:
                    st.write("Select numeric column")

        # Create columns for the table and charts
        if not df_filtered2.empty:
            # Add button to show/hide DataFrame
            if st.button('Show/Hide Data Table'):
                st.session_state.show_table = not st.session_state.show_table
            
            # Show DataFrame if button was clicked
            if st.session_state.show_table:
                st.dataframe(df_filtered2)

            # Add horizontal line before Histograms title
            st.markdown("<hr>", unsafe_allow_html=True)

            # Create a row for the title and histogram count selector
            title_col, selector_col = st.columns([14, 1])
            
            with title_col:
                st.markdown("### Histograms")
            
            with selector_col:
                st.markdown('<div class="histogram-count-selector">', unsafe_allow_html=True)
                num_histograms = st.selectbox(
                    "Num of Charts",
                    options=[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                    index=4,
                    key="num_histograms"
                )
                st.markdown('</div>', unsafe_allow_html=True)

            # Get numeric columns for charts
            chart_columns = [col for col in df_filtered2.columns if pd.api.types.is_numeric_dtype(df_filtered2[col])]

            # Calculate number of rows needed
            num_rows = (num_histograms + 5) // 6  # Round up division
            
            # Create rows of charts
            for row in range(num_rows):
                # Calculate how many charts in this row
                charts_in_row = min(6, num_histograms - (row * 6))
                
                # Create columns for this row
                cols = st.columns(6)  # Always create 6 columns
                
                # Process each column in this row
                for i in range(charts_in_row):
                    with cols[i]:
                        selected_column = st.selectbox(f'Chart {row*6 + i + 1}', chart_columns, key=f'chart_{row*6 + i}')
                        
                        if pd.api.types.is_numeric_dtype(df_filtered2[selected_column]):
                            # Freedman-Diaconis rule to determine bin width
                            n = len(df_filtered2[selected_column])
                            iqr = df_filtered2[selected_column].quantile(0.75) - df_filtered2[selected_column].quantile(0.25)
                            bin_width = 2 * iqr * (n ** (-1/3))
                            
                            if bin_width == 0:
                                data_range = df_filtered2[selected_column].max() - df_filtered2[selected_column].min()
                                bin_width = data_range / 10 if data_range > 0 else 1
                            
                            if bin_width == 0:
                                st.write("Data is constant")
                            else:
                                data_range = df_filtered2[selected_column].max() - df_filtered2[selected_column].min()
                                num_bins = max(1, int(np.ceil(data_range / bin_width)))
                                bins = np.linspace(df_filtered2[selected_column].min(), df_filtered2[selected_column].max(), num_bins + 1)
                                bin_labels = [f"[{bins[i]:.1f}, {bins[i+1]:.1f})" for i in range(len(bins) - 1)]
                                df_filtered2['bin'] = pd.cut(df_filtered2[selected_column], bins=bins, labels=bin_labels, right=False)
                                bin_counts = df_filtered2['bin'].value_counts().sort_index().reset_index()
                                bin_counts.columns = ['bin', 'count']

                                # Extract numeric values from bin labels for coloring
                                bin_counts['bin_start'] = bin_counts['bin'].str.extract(r'\[([-\d.]+),').astype(float)
                                
                                fig = px.bar(bin_counts, x='bin', y='count',
                                           labels={'bin': '', 'count': 'Frequency'})
                                
                                # Color bars based on bin values
                                fig.update_traces(
                                    marker_color=['#FF8989' if val < 0 else '#1f77b4' for val in bin_counts['bin_start']],
                                    width=0.5
                                )
                                
                                fig.update_layout(
                                    title={
                                        'text': f'Distribution of "{selected_column}"',
                                        'y': 0.95,
                                        'x': 0.5,
                                        'xanchor': 'center',
                                        'yanchor': 'top',
                                        'font': {'size': 14}
                                    },
                                    xaxis_tickangle=-45,
                                    height=400,
                                    margin=dict(l=20, r=20, t=60, b=80),
                                    showlegend=False,
                                    bargap=0.1
                                )
                                
                                # Display the plot
                                container = st.container()
                                with container:
                                    st.markdown('<div style="width: 80%; margin: 0 auto;">', unsafe_allow_html=True)
                                    st.plotly_chart(fig, use_container_width=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
            
            # Add horizontal line before report buttons
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Add report type selector and buttons
            report_col1, report_col2, report_col3 = st.columns([1, 1, 1])
            
            with report_col1:
                # Add report type selector
                report_type = st.selectbox(
                    "Report Type",
                    ["Visible Histograms Only", "All Numeric Columns"],
                    help="Choose whether to include only the visible histograms or all numeric columns in the report"
                )
            
            with report_col2:
                if st.button('Generate PDF Report'):
                    try:
                        with st.spinner('Generating PDF report...'):
                            # Prepare metrics data
                            st.text('Preparing metrics data...')
                            metrics_data1 = None
                            metrics_data2 = None
                            
                            if pd.api.types.is_numeric_dtype(df[metrics_column1]):
                                total_elements = len(df_filtered2)
                                if total_elements > 0:
                                    wins = len(df_filtered2[df_filtered2[metrics_column1] > 0])
                                    win_rate = (wins / total_elements) * 100
                                    total_win = df_filtered2[df_filtered2[metrics_column1] > 0][metrics_column1].sum()
                                    total_loss = df_filtered2[df_filtered2[metrics_column1] < 0][metrics_column1].sum()
                                    net_win = total_win + total_loss
                                    std_dev = df_filtered2[metrics_column1].std()
                                    median_r = df_filtered2[metrics_column1].median()
                                    mode_r = df_filtered2[metrics_column1].mode().iloc[0] if not df_filtered2[metrics_column1].mode().empty else 0
                                    avg_r = df_filtered2[metrics_column1].mean()
                                    sqn = (avg_r / std_dev) * np.sqrt(total_elements) if std_dev != 0 else 0
                                    
                                    metrics_data1 = {
                                        'win_rate': win_rate,
                                        'net_win': net_win,
                                        'total_win': total_win,
                                        'total_loss': total_loss,
                                        'sqn': sqn,
                                        'std_dev': std_dev,
                                        'median_r': median_r,
                                        'mode_r': mode_r,
                                        'avg_r': avg_r
                                    }
                            
                            if pd.api.types.is_numeric_dtype(df[metrics_column2]):
                                total_elements = len(df_filtered2)
                                if total_elements > 0:
                                    wins = len(df_filtered2[df_filtered2[metrics_column2] > 0])
                                    win_rate = (wins / total_elements) * 100
                                    total_win = df_filtered2[df_filtered2[metrics_column2] > 0][metrics_column2].sum()
                                    total_loss = df_filtered2[df_filtered2[metrics_column2] < 0][metrics_column2].sum()
                                    net_win = total_win + total_loss
                                    std_dev = df_filtered2[metrics_column2].std()
                                    median_r = df_filtered2[metrics_column2].median()
                                    mode_r = df_filtered2[metrics_column2].mode().iloc[0] if not df_filtered2[metrics_column2].mode().empty else 0
                                    avg_r = df_filtered2[metrics_column2].mean()
                                    sqn = (avg_r / std_dev) * np.sqrt(total_elements) if std_dev != 0 else 0
                                    
                                    metrics_data2 = {
                                        'win_rate': win_rate,
                                        'net_win': net_win,
                                        'total_win': total_win,
                                        'total_loss': total_loss,
                                        'sqn': sqn,
                                        'std_dev': std_dev,
                                        'median_r': median_r,
                                        'mode_r': mode_r,
                                        'avg_r': avg_r
                                    }
                            
                            st.text('Creating PDF report...')
                            # Generate PDF with selected report type
                            if report_type == "Visible Histograms Only":
                                # Get the number of histograms from session state
                                num_histograms = st.session_state.get("num_histograms", 6)
                                # Get the selected columns for visible histograms
                                visible_columns = [st.session_state.get(f'chart_{i}') for i in range(num_histograms)]
                                visible_columns = [col for col in visible_columns if col and pd.api.types.is_numeric_dtype(df_filtered2[col])]
                                pdf_path = create_pdf_report(df_filtered2, metrics_data1, metrics_data2, metrics_column1, metrics_column2, visible_columns)
                            else:
                                # Get all numeric columns
                                all_numeric_columns = [col for col in df_filtered2.columns if pd.api.types.is_numeric_dtype(df_filtered2[col])]
                                pdf_path = create_pdf_report(df_filtered2, metrics_data1, metrics_data2, metrics_column1, metrics_column2, all_numeric_columns)
                            
                            st.text('Preparing download...')
                            # Create download button for PDF
                            with open(pdf_path, "rb") as pdf_file:
                                PDFbyte = pdf_file.read()
                                
                            st.session_state.pdf_ready = True
                            st.session_state.pdf_data = PDFbyte
                            
                            # Clean up temporary file
                            os.unlink(pdf_path)
                            
                            st.success('PDF report generated successfully!')
                    except Exception as e:
                        st.error(f'Error generating PDF report: {str(e)}')
                        st.info('Please make sure you have installed the required package: pip install kaleido')
            
            with report_col3:
                if 'pdf_ready' in st.session_state and st.session_state.pdf_ready:
                    st.download_button(
                        label="Download PDF Report",
                        data=st.session_state.pdf_data,
                        file_name="signal_analyzer_report.pdf",
                        mime='application/octet-stream'
                    )
        else:
            st.write("No data matches the selected filters")

    # Monte Carlo Analysis tab content
    with tab2:
        # Title and warning icon in the same line
        st.markdown("""
        <style>
        .tooltip {
            position: relative;
            display: inline-block;
            cursor: pointer;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 1200px;
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
        </style>
        
        <div style="display: flex; align-items: center;">
            <h1 style="margin: 0;">Monte Carlo Analysis</h1>
            <span style="margin-left: 10px;" class="tooltip">⚠️
                <span class="tooltiptext">
                    <strong style="font-size: 20px; font-family: Arial, sans-serif;">Problems with Monte Carlo Simulation</strong><br><br>
                    <strong>Market Cycle-Driven SQN</strong><br>
                    It is important to know the relationship between risk adjusted return and time in trade.<br><br>
                    1. Your system is based on price structure: Order of trades are important in price-action based systems; randomizing order will invalidate your strategy.<br><br>
                    2. High win rate and curve-fitted systems: The strategy is accurate enough to be considered "curve fitted" and as a result, has a high win rate.<br><br>
                    3. Self-correcting systems: your system is always in the market and closes a long by opening a new short position. So, at no point in time, two consequent long or two consequent short trades happen. Randomizing order of trades will break the system.<br><br>
                    4. Long-term trend following systems: You cannot change the order of trades without changing the system, because long term systems are dependent on fundamentals. Randomization does not make sense because fundamentals change over long periods of time.<br><br>
                    5. Large original set: If the sample size is too big, there is high portability of generating trade sequences with drawdown levels equal to the initial capital.<br><br>
                    6. Strategy dynamics depend on position sizing: Systems that scale in and out of trades to increase their probability of success cannot be stress tested by a Monte Carlo analyzer, because sequence of trades is a system edge that contributes to the expectancy of the system.<br><br>
                    <strong>General Guideline</strong><br>
                    • If your system's edge depends on the order of trades in any form, Monte Carlo analysis will likely give you incorrect information and should not be used.<br>
                    • If your system is simple with no such dependency then you can probably use a Monte Carlo analyzer to estimate worst case drawdowns and performance envelope of its equity curve.<br><br>
                </span>
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Horizontal line with shadow
        st.markdown("<hr>", unsafe_allow_html=True)
        
        try:
            # Load the Excel file
            data = pd.read_excel(st.session_state.file_path, engine='openpyxl')
            
            # Create columns for controls
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                # Dropdown to select the column for Monte Carlo simulation
                selected_column = st.selectbox('Select column for Monte Carlo simulation', 
                                             [col for col in data.columns if pd.api.types.is_numeric_dtype(data[col])])
            
            with col2:
                # Distribution type selector
                dist_type = st.selectbox('Distribution Type', 
                                       ['Gaussian Normal', 'Student T', 'Raw Data'],
                                       help='Select the distribution type for the simulation')
            
            with col3:
                # Number of steps input
                num_steps = st.number_input('Number of steps', min_value=10, max_value=1000, value=100)
            
            with col4:
                # Initial value input
                initial_value = st.number_input('Initial value', min_value=0.1, max_value=100.0, value=1.0, step=0.1)
            
            with col5:
                # Number of simulations input
                num_simulations = st.number_input('Number of simulations', min_value=100, max_value=100000, value=10000, step=1000)
            
            # Run simulation button in a new row
            if st.button('Run Monte Carlo Simulation'):
                with st.spinner('Running Monte Carlo simulation...'):
                    # Extract the selected column data
                    column_data = data[selected_column].dropna()
                    
                    def simulate_monte_carlo(num_simulations, dist_type):
                        trajectories = []
                        
                        if dist_type == 'Gaussian Normal':
                            # Fit Gaussian distribution to the data
                            mu, sigma = norm.fit(column_data)
                            
                            for _ in range(num_simulations):
                                steps = np.random.normal(mu, sigma, size=num_steps)
                                trajectory = [initial_value]
                                for step in steps:
                                    trajectory.append(trajectory[-1] * (1 + step / 100))
                                trajectories.append(trajectory)
                                
                        elif dist_type == 'Student T':
                            # Fit Student's T distribution to the data
                            df, loc, scale = t.fit(column_data)
                            
                            for _ in range(num_simulations):
                                steps = t.rvs(df=df, loc=loc, scale=scale, size=num_steps)
                                trajectory = [initial_value]
                                for step in steps:
                                    trajectory.append(trajectory[-1] * (1 + step / 100))
                                trajectories.append(trajectory)
                                
                        else:  # Raw Data
                            # Use bootstrap sampling from the actual data
                            for _ in range(num_simulations):
                                steps = np.random.choice(column_data, size=num_steps)
                                trajectory = [initial_value]
                                for step in steps:
                                    trajectory.append(trajectory[-1] * (1 + step / 100))
                                trajectories.append(trajectory)
                        
                        return pd.DataFrame(trajectories).T
                    
                    # Run simulation with selected distribution type
                    trajectories = simulate_monte_carlo(num_simulations, dist_type)
                    
                    # Calculate statistics
                    mean_trajectory = trajectories.mean(axis=1)
                    min_trajectory = trajectories.min(axis=1)
                    max_trajectory = trajectories.max(axis=1)
                    
                    # Display statistics in a row above the plot
                    stats_col1, stats_col2, stats_col3 = st.columns(3)
                    
                    with stats_col1:
                        st.metric("Maximum Drawdown", f"{min_trajectory.min():.2f}")
                    with stats_col2:
                        st.metric("Median Value", f"{mean_trajectory.median():.2f}")
                    with stats_col3:
                        st.metric("Mean Value", f"{mean_trajectory.mean():.2f}")
                    
                    # Create the plot using plotly
                    fig = go.Figure()
                    
                    # Add individual trajectories
                    for i in range(min(100, num_simulations)):  # Show only first 100 trajectories
                        fig.add_trace(go.Scatter(
                            y=trajectories[i],
                            mode='lines',
                            line=dict(color='gray', width=0.5),
                            opacity=0.1,
                            showlegend=False
                        ))
                    
                    # Add mean trajectory
                    fig.add_trace(go.Scatter(
                        y=mean_trajectory,
                        mode='lines',
                        name='Most Likely Range',
                        line=dict(color='blue', width=2)
                    ))
                    
                    # Add min and max trajectories
                    fig.add_trace(go.Scatter(
                        y=min_trajectory,
                        mode='lines',
                        name='Worst Case',
                        line=dict(color='red', width=1, dash='dash')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        y=max_trajectory,
                        mode='lines',
                        name='Best Case',
                        line=dict(color='green', width=1, dash='dash')
                    ))
                    
                    # Add area between min and max
                    fig.add_trace(go.Scatter(
                        x=list(range(len(min_trajectory))),
                        y=min_trajectory,
                        fill=None,
                        mode='lines',
                        line_color='rgba(0,0,0,0)',
                        showlegend=False
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=list(range(len(max_trajectory))),
                        y=max_trajectory,
                        fill='tonexty',
                        mode='lines',
                        line_color='rgba(0,0,0,0)',
                        fillcolor='rgba(0,0,255,0.2)',
                        name='Range'
                    ))
                    
                    #Update layout
                    fig.update_layout(
                        xaxis_title="Trade #",
                        yaxis_title="Equity",
                        showlegend=True,
                        legend=dict(
                            yanchor="top",
                            y=0.99,
                            xanchor="left",
                            x=0.01
                        ),
                        height=600,
                        margin=dict(l=50, r=50, t=50, b=50)
                    )
                    
                    # Add grid
                    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGrey')
                    
                    # Display the plot
                    container = st.container()
                    with container:
                        st.markdown('<div style="width: 80%; margin: 0 auto;">', unsafe_allow_html=True)
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error running Monte Carlo simulation: {str(e)}")
else:
    # Title and button in the same line when no file is selected
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("# **Signal Analyzer Dashboard**")

    with col2:
        st.markdown('<div class="file-section">', unsafe_allow_html=True)
        container = st.container()
        with container:
            if st.button('Select Excel file', key='select_file'):
                file_path = get_file_path()
                if file_path:
                    st.session_state.file_path = file_path
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Horizontal line with shadow
    st.markdown("<hr>", unsafe_allow_html=True)

    # Show logo when no file is selected
    try:
        logo_base64 = get_image_base64(r"C:\Users\monau\Downloads\logo.png")
        st.markdown(f"""
            <div style='text-align: center; padding: 20px 0;'>
                <img src='data:image/png;base64,{logo_base64}' alt='Logo' style='width: 80%; max-width: 1500px; object-fit: contain; border-radius: 15px;'>
            </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading logo: {str(e)}")

# To run the code, use the following command in the terminal:
# streamlit run FilteredData_v8.py

#También, para futuras referencias, el proceso completo para ejecutar la aplicación es:
#conda activate datavis_env
#cd "C:\Users\monau\Coding"
#streamlit run FilteredData_v19.py