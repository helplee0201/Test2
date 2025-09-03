import streamlit as st
import networkx as nx
from web_data import PARSED_DATA
import network_graph_cycles as ngc
from streamlit.components.v1 import html
import pandas as pd
import random
from pyvis.network import Network
from collections import defaultdict

# Custom CSS inspired by https://www.coocon.net/main_0001_t5.act
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    body {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        background-color: #FFFFFF;
        font-size: 16px;
        line-height: 1.6;
        color: #666666;
    }
    .stApp {
        max-width: 1400px;
        margin: 0 auto;
        background-color: #FFFFFF;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        padding: 40px;
        transition: all 0.3s ease;
    }
    h1 {
        color: #000000;
        font-size: 2.8em;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5em;
    }
    h2 {
        color: #000000;
        font-size: 2.0em;
        font-weight: 600;
        margin-bottom: 1.2em;
    }
    h3 {
        color: #000000;
        font-size: 1.6em;
        font-weight: 500;
        margin-bottom: 1em;
    }
    .stSelectbox, .stTextInput, .stMultiselect {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 12px;
        font-size: 1.0em;
        border: 1px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    .stSelectbox:hover, .stTextInput:hover, .stMultiselect:hover {
        border-color: #00AEEF;
        box-shadow: 0 0 8px rgba(0, 174, 239, 0.3);
    }
    .stButton>button {
        background-color: #00AEEF;
        color: white;
        border-radius: 12px;
        padding: 12px 24px;
        border: none;
        font-size: 1.0em;
        font-weight: 500;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0099CC;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-1px);
    }
    .stDataFrame {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        overflow: hidden;
        background-color: #FFFFFF;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
        font-size: 1.0em;
    }
    .stDataFrame th {
        background-color: #00AEEF;
        color: white;
        padding: 14px;
        text-align: left;
        font-weight: 500;
    }
    .stDataFrame td {
        padding: 14px;
        border-bottom: 1px solid #e0e0e0;
        font-size: 1.0em;
    }
    .stDataFrame tr:hover {
        background-color: #f5f7fa;
        transform: scale(1.02);
        transition: all 0.2s ease;
    }
    .sidebar .sidebar-content {
        background-color: #1f2937;
        color: white;
        border-radius: 12px;
        padding: 24px;
        font-size: 1.0em;
    }
    .stCheckbox {
        margin: 8px 0;
    }
    /* Custom checkbox and multiselect checkmark color */
    .stCheckbox > div[data-baseweb="checkbox"],
    .stMultiSelect [role="option"] > div[data-baseweb="checkbox"] {
        background-color: rgba(0, 174, 239, 0.7) !important;
        border-color: #00AEEF !important;
    }
    .stCheckbox > div[data-baseweb="checkbox"] input:checked ~ div,
    .stMultiSelect [role="option"] > div[data-baseweb="checkbox"] input:checked ~ div {
        background-color: #00AEEF !important;
        border-color: #00AEEF !important;
    }
    .stCheckbox > div[data-baseweb="checkbox"] input:checked ~ div:after,
    .stMultiSelect [role="option"] > div[data-baseweb="checkbox"] input:checked ~ div:after {
        border-color: white !important;
    }
    .fraud-warning {
        color: #e74c3c;
        font-weight: 600;
        font-size: 1.1em;
        background-color: #ffe6e6;
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #e74c3c;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .no-fraud {
        color: #16a34a;
        font-weight: 600;
        font-size: 1.1em;
        background-color: rgba(220, 252, 231, 0.9);
        padding: 12px;
        border-radius: 12px;
        border: 1px solid #16a34a;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stMarkdown p {
        font-size: 1.0em;
        line-height: 1.6;
    }
    .graph-container {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        background-color: #FFFFFF;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    .graph-container:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Extract unique seller (no_biz) and buyer (no_bisocial) data
insured_dict = {entry['no_biz']: entry['nm_krcom'] for entry in PARSED_DATA}
contractor_dict = {entry['no_bisocial']: entry['nm_trade'] for entry in PARSED_DATA}

# Sorted options for selectboxes
insured_options = sorted([f"{num} - {name} (판매자)" for num, name in insured_dict.items()])
contractor_options = sorted([f"{num} - {name} (구매자)" for num, name in contractor_dict.items()])

# Set page config for wide layout
st.set_page_config(layout="wide")

# App title
st.title("사기거래 분석 대시보드")

# Pair Management Section
st.header("피보험자-계약자 입력")

# Add New Pair Section
st.subheader("사업자번호 조회 및 선택")
col_select1, col_select2 = st.columns([1, 1])

with col_select1:
    insured_selections = st.multiselect(
        "판매자 선택 (판매자)",
        options=insured_options,
        key="insured_select"
    )

with col_select2:
    contractor_selections = st.multiselect(
        "구매자 선택 (구매자)",
        options=contractor_options,
        key="contractor_select"
    )

# Initialize session state for pairs
if 'pairs' not in st.session_state:
    st.session_state.pairs = []
if 'delete_checks' not in st.session_state:
    st.session_state.delete_checks = []

if st.button("사업자번호 추가", key="add_pair"):
    if insured_selections and contractor_selections:
        # Create all possible pairs from selected sellers and buyers
        new_pairs = []
        for insured_selection in insured_selections:
            for contractor_selection in contractor_selections:
                insured_num = insured_selection.split(' - ')[0]
                contractor_num = contractor_selection.split(' - ')[0]
                new_pairs.append((insured_num, contractor_num))
        # Add new pairs to session state
        st.session_state.pairs.extend(new_pairs)
        st.session_state.delete_checks.extend([False] * len(new_pairs))
        st.success(f"{len(new_pairs)} 쌍이 추가되었습니다!")
        st.rerun()
    else:
        st.warning("판매자와 구매자를 하나 이상 선택해주세요.")

# Selected Pairs Section
st.subheader("선택된 사업자번호 조합")
if st.session_state.pairs:
    # Ensure delete_checks matches pairs length
    if len(st.session_state.delete_checks) != len(st.session_state.pairs):
        st.session_state.delete_checks = [False] * len(st.session_state.pairs)

    # Create table data with checkboxes
    table_data = []
    for i, (seller, buyer) in enumerate(st.session_state.pairs):
        table_data.append({
            "삭제": st.session_state.delete_checks[i],
            "판매자": f"{seller} - {insured_dict.get(seller, '알 수 없음')} (판매자)",
            "구매자": f"{buyer} - {contractor_dict.get(buyer, '알 수 없음')} (구매자)"
        })

    # Display table with integrated checkboxes
    df = pd.DataFrame(table_data)
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "삭제": st.column_config.CheckboxColumn(
                "삭제",
                default=False,
                help="삭제할 쌍을 선택하세요"
            ),
            "판매자": "판매자",
            "구매자": "구매자"
        }
    )

    # Update session state based on table checkbox changes
    for i, row in df.iterrows():
        st.session_state.delete_checks[i] = row["삭제"]

    # Delete button
    if st.button("선택된 쌍 삭제", key="delete_selected"):
        new_pairs = [pair for i, pair in enumerate(st.session_state.pairs) if not st.session_state.delete_checks[i]]
        st.session_state.pairs = new_pairs
        st.session_state.delete_checks = [False] * len(new_pairs)
        st.success("선택된 쌍이 삭제되었습니다!")
        st.rerun()
else:
    st.info("아직 쌍이 추가되지 않았습니다.")

# Network Analysis Section
st.header("2. 네트워크 분석을 실행하는 영역")
cycle_lengths = st.multiselect(
    "찾을 사이클 길이 선택",
    options=[3, 4, 5, 6],
    default=[3],
    key="cycle_lengths"
)

# Initialize session state for network analysis results
if 'network_run' not in st.session_state:
    st.session_state.network_run = False
if 'htmls' not in st.session_state:
    st.session_state.htmls = []
if 'overall_html' not in st.session_state:
    st.session_state.overall_html = None
if 'extended_overall_html' not in st.session_state:
    st.session_state.extended_overall_html = None
if 'show_sales_details' not in st.session_state:
    st.session_state.show_sales_details = [False] * 100  # Support multiple subgraphs
if
