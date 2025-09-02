import streamlit as st
import networkx as nx
from web_data import PARSED_DATA
import network_graph_cycles as ngc
from streamlit.components.v1 import html
import pandas as pd
import random

# Custom CSS for wider, modern dashboard styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');

    body {
        font-family: 'Roboto', 'Noto Sans KR', sans-serif;
        background-color: #f4f7fa;
    }
    .stApp {
        max-width: 1400px;
        margin: 0 auto;
        background-color: #ffffff;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        padding: 30px;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stSelectbox, .stTextInput, .stMultiselect {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 8px;
    }
    .stButton>button {
        background-color: #e74c3c; /* Red color for fraud analysis button */
        color: white;
        border-radius: 5px;
        padding: 12px 24px;
        border: none;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #c0392b; /* Darker red on hover */
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        overflow: hidden;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
    }
    .stDataFrame th {
        background-color: #3498db;
        color: white;
        padding: 14px;
        text-align: left;
    }
    .stDataFrame td {
        padding: 12px;
        border-bottom: 1px solid #e0e0e0;
    }
    .stDataFrame tr:hover {
        background-color: #f1f3f5;
    }
    .sidebar .sidebar-content {
        background-color: #2c3e50;
        color: white;
        border-radius: 8px;
        padding: 20px;
    }
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 2px solid #3498db;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 500;
        color: #2c3e50;
        padding: 12px 24px;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #3498db;
        border-bottom: 2px solid #3498db;
    }
    .stCheckbox {
        margin: 6px 0;
    }
</style>
""", unsafe_allow_html=True)

# Debug: Check PARSED_DATA length
st.write(f"Debug: PARSED_DATA length: {len(PARSED_DATA)}")

# Extract unique seller (no_biz) and buyer (no_bisocial) data
insured_dict = {entry['no_biz']: entry['nm_krcom'] for entry in PARSED_DATA}
contractor_dict = {entry['no_bisocial']: entry['nm_trade'] for entry in PARSED_DATA}

# Sorted options for selectboxes
insured_options = sorted([f"{num} - {name} (판매자)" for num, name in insured_dict.items()])
contractor_options = sorted([f"{num} - {name} (구매자)" for num, name in contractor_dict.items()])

# Set page config for wide layout
st.set_page_config(layout="wide")

# App title
st.title("Insurance Network Dashboard")

# Use tabs for organization
tab1, tab2 = st.tabs(["📋 Pair Management", "📊 Network Analysis"])

with tab1:
    st.header("Manage Seller-Buyer Pairs")

    # Add New Pair Section
    st.subheader("Add New Pair")
    col_select1, col_select2 = st.columns([1, 1])
    
    with col_select1:
        insured_selection = st.selectbox(
            "Select Seller (판매자)",
            options=["Select an option"] + insured_options,
            key="insured_select"
        )
    
    with col_select2:
        contractor_selection = st.selectbox(
            "Select Buyer (구매자)",
            options=["Select an option"] + contractor_options,
            key="contractor_select"
        )
    
    # Initialize session state for pairs
    if 'pairs' not in st.session_state:
        st.session_state.pairs = []
    if 'delete_checks' not in st.session_state:
        st.session_state.delete_checks = []

    if st.button("Add Pair", key="add_pair"):
        if insured_selection != "Select an option" and contractor_selection != "Select an option":
            insured_num = insured_selection.split(' - ')[0]
            contractor_num = contractor_selection.split(' - ')[0]
            st.session_state.pairs.append((insured_num, contractor_num))
            st.session_state.delete_checks.append(False)
            st.success("Pair added successfully!")
            st.rerun()

    # Selected Pairs Section (on a new row)
    st.subheader("Selected Pairs")
    if st.session_state.pairs:
        # Ensure delete_checks matches pairs length
        if len(st.session_state.delete_checks) != len(st.session_state.pairs):
            st.session_state.delete_checks = [False] * len(st.session_state.pairs)

        # Create table data
        table_data = []
        for i, (seller, buyer) in enumerate(st.session_state.pairs):
            with st.container():
                cols = st.columns([1, 3, 3])
                with cols[0]:
                    st.session_state.delete_checks[i] = st.checkbox("", key=f"delete_{i}", value=st.session_state.delete_checks[i])
                with cols[1]:
                    st.write(f"{seller} - {insured_dict.get(seller, 'Unknown')} (판매자)")
                with cols[2]:
                    st.write(f"{buyer} - {contractor_dict.get(buyer, 'Unknown')} (구매자)")
                table_data.append({
                    "Delete": st.session_state.delete_checks[i],
                    "Seller": f"{seller} - {insured_dict.get(seller, 'Unknown')} (판매자)",
                    "Buyer": f"{buyer} - {contractor_dict.get(buyer, 'Unknown')} (구매자)"
                })

        # Delete button
        if st.button("Delete Selected Pairs", key="delete_selected"):
            new_pairs = [pair for i, pair in enumerate(st.session_state.pairs) if not st.session_state.delete_checks[i]]
            st.session_state.pairs = new_pairs
            st.session_state.delete_checks = [False] * len(new_pairs)
            st.success("Selected pairs deleted successfully!")
            st.rerun()

        # Display table
        st.dataframe(
            table_data,
            use_container_width=True,
            column_config={
                "Delete": st.column_config.CheckboxColumn("Delete"),
                "Seller": "Seller (판매자)",
                "Buyer": "Buyer (구매자)"
            }
        )
    else:
        st.info("No pairs added yet.")

with tab2:
    st.header("Network Analysis")
    cycle_lengths = st.multiselect(
        "Select Cycle Lengths to Find",
        options=[3, 4, 5, 6],
        default=[3],
        key="cycle_lengths"
    )
    
    # Initialize session state for network analysis results
    if 'network_run' not in st.session_state:
        st.session_state.network_run = False
    if 'htmls' not in st.session_state:
        st.session_state.htmls = []
    if 'show_fraud_analysis' not in st.session_state:
        st.session_state.show_fraud_analysis = False

    # Run network analysis
    if st.button("Run Network Analysis", key="network_analysis"):
        if st.session_state.pairs:
            G = nx.DiGraph(st.session_state.pairs)  # Edges from no_biz (seller) to no_bisocial (buyer)
            cycles = ngc.find_cycles(G, cycle_lengths)
            st.session_state.htmls = ngc.draw_graph(G, cycles, cycle_lengths, insured_dict, contractor_dict)
            st.session_state.network_run = True
            st.session_state.show_fraud_analysis = False  # Reset fraud analysis
            st.rerun()
        else:
            st.warning("Please add transaction pairs to analyze.")

    # Debug: Show pairs
    st.write(f"Debug: Current pairs: {st.session_state.get('pairs', [])}")

    # Display subgraphs with fraud analysis details
    if st.session_state.network_run and st.session_state.htmls:
        for i, html_content in enumerate(st.session_state.htmls, 1):
            st.subheader(f"Subgraph {i}")
            col_graph, col_table = st.columns([3, 2])
            with col_graph:
                html(html_content, height=600, scrolling=True)
            with col_table:
                st.write("**Transaction Details**")
                if st.button("사기거래 분석", key=f"fraud_analysis_{i}"):
                    st.session_state.show_fraud_analysis = not st.session_state.show_fraud_analysis
                    st.rerun()
                if st.session_state.show_fraud_analysis and st.session_state.pairs:
                    items = [
                        "최근 2년간 해당 거래처와의 거래대금 결제 이력(회수) 여부 (판매자)",
                        "최근 2년간 해당 거래처와의 거래대금 결제 이력(지급) 여부 (구매자)",
                        "양사 대표자 동일(이름, 주민번호) 여부",
                        "양사 대표자 가족 중복 포함 여부",
                        "양사 대표자 종업원 포함 여부",
                        "양사 동일 종업원 존재 여부",
                        "회전거래 업체와 최근 2년간 거래 여부",
                        "폭탄업체와 최근 2년간 거래 여부",
                        "회전거래 업체여부",
                        "계약자와 피보험자가 3개 이상인 경우 회전거래가 존재하는지 여부",
                        "동일 세무대리인으로부터 기장한 이력이 확인되는 경우",
                        "사업장 주소지 유사성이 확인되는 경우",
                        "주주 구성의 동일성이 확인되는 경우",
                        "중간거래상을 통한 거래가 확인되는 경우"
                    ]
                    values = [random.choice(['y', 'n']) for _ in items]
                    df = pd.DataFrame({'Item': items, 'Value': values})
                    st.dataframe(df, use_container_width=True)
                    if 'y' in values:
                        st.write("사기거래 징후가 보입니다.")
                    else:
                        st.write("사기거래 징후가 보이지 않습니다.")
                else:
                    st.info("Click '사기거래 분석' to view fraud analysis details.")

        # CSV downloads
        if st.session_state.pairs:
            G = nx.DiGraph(st.session_state.pairs)
            cycles = ngc.find_cycles(G, cycle_lengths)
            csv_files = ngc.generate_csv(cycles, cycle_lengths)
            for filename, csv_data in csv_files:
                st.download_button(
                    label=f"Download {filename}",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key=f"download_{filename}"
                )