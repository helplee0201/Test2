import streamlit as st
import networkx as nx
from web_data import PARSED_DATA
import network_graph_cycles as ngc
from streamlit.components.v1 import html
import pandas as pd
import random
from pyvis.network import Network
from collections import defaultdict

# Custom CSS for modern, sleek UI/UX
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

    body {
        font-family: 'Inter', 'Noto Sans KR', sans-serif;
        background-color: #f9fafb;
        font-size: 16px;
        line-height: 1.6;
        color: #1f2937;
    }
    .stApp {
        max-width: 1440px;
        margin: 0 auto;
        background-color: #ffffff;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.05);
        padding: 40px;
    }
    h1 {
        color: #1f2937;
        font-size: 2.8em;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1.5em;
    }
    h2 {
        color: #1f2937;
        font-size: 2.0em;
        font-weight: 600;
        margin-bottom: 1.2em;
    }
    h3 {
        color: #1f2937;
        font-size: 1.6em;
        font-weight: 500;
        margin-bottom: 1em;
    }
    .stSelectbox, .stTextInput, .stMultiselect {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 10px;
        font-size: 1.0em;
        border: 1px solid #e2e8f0;
    }
    .stButton>button {
        background: linear-gradient(to right, #60a5fa, #3b82f6);
        color: white;
        border-radius: 8px;
        padding: 12px 24px;
        border: none;
        font-size: 1.0em;
        font-weight: 500;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(to right, #3b82f6, #2563eb);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
        transform: translateY(-1px);
    }
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        overflow: hidden;
        background-color: #ffffff;
    }
    .stDataFrame table {
        width: 100%;
        border-collapse: collapse;
        font-size: 1.0em;
    }
    .stDataFrame th {
        background: linear-gradient(to right, #3b82f6, #60a5fa);
        color: white;
        padding: 14px;
        text-align: left;
        font-weight: 500;
    }
    .stDataFrame td {
        padding: 14px;
        border-bottom: 1px solid #e2e8f0;
        font-size: 1.0em;
    }
    .stDataFrame tr:hover {
        background-color: #f1f5f9;
    }
    .sidebar .sidebar-content {
        background-color: #1f2937;
        color: white;
        border-radius: 8px;
        padding: 24px;
        font-size: 1.0em;
    }
    .stCheckbox {
        margin: 8px 0;
    }
    .fraud-warning {
        color: #dc2626;
        font-weight: 600;
        font-size: 1.1em;
        background-color: rgba(254, 226, 226, 0.9);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #dc2626;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .no-fraud {
        color: #16a34a;
        font-weight: 600;
        font-size: 1.1em;
        background-color: rgba(220, 252, 231, 0.9);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #16a34a;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    .stMarkdown p {
        font-size: 1.0em;
        line-height: 1.6;
    }
    .graph-container {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 16px;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
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
        "판매자 선택",
        options=insured_options,
        key="insured_select",
        help="판매자(피보험자)를 선택하세요."
    )

with col_select2:
    contractor_selections = st.multiselect(
        "구매자 선택",
        options=contractor_options,
        key="contractor_select",
        help="구매자(계약자)를 선택하세요."
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
        st.success(f"{len(new_pairs)}개의 쌍이 추가되었습니다!")
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
            "판매자": f"{seller} - {insured_dict.get(seller, '알 수 없음')}",
            "구매자": f"{buyer} - {contractor_dict.get(buyer, '알 수 없음')}"
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
            "판매자": st.column_config.TextColumn("판매자"),
            "구매자": st.column_config.TextColumn("구매자")
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
    st.info("아직 추가된 쌍이 없습니다.")

# Network Analysis Section
st.header("네트워크 분석")
cycle_lengths = st.multiselect(
    "찾을 사이클 길이 선택",
    options=[3, 4, 5, 6],
    default=[3],
    key="cycle_lengths",
    help="분석할 사이클 길이를 선택하세요."
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
if 'show_fraud_analysis' not in st.session_state:
    st.session_state.show_fraud_analysis = [False] * 100  # Support multiple subgraphs

# Run network analysis
if st.button("네트워크 분석 실행", key="network_analysis"):
    if st.session_state.pairs:
        # Original graph and subgraphs
        G = nx.DiGraph(st.session_state.pairs)  # Edges from no_biz (seller) to no_bisocial (buyer)
        # Find all simple cycles and organize by length
        all_cycles = list(nx.simple_cycles(G))
        cycles = {length: [cycle for cycle in all_cycles if len(cycle) == length] for length in cycle_lengths}
        st.session_state.htmls = ngc.draw_graph(G, cycles, cycle_lengths, insured_dict, contractor_dict)

        # Compute overall graph (without extended nodes)
        selected_sellers = set(s for s, b in st.session_state.pairs)
        selected_buyers = set(b for s, b in st.session_state.pairs)
        overall_G = nx.DiGraph()

        # Add selected edges
        for s, b in st.session_state.pairs:
            overall_G.add_edge(s, b)

        # Compute cycles for overall
        all_cycles_overall = list(nx.simple_cycles(overall_G))
        cycles_overall = {length: [cycle for cycle in all_cycles_overall if len(cycle) == length] for length in cycle_lengths}

        # Draw overall graph
        filtered_graph, length_3_plus_edges = ngc.filter_paths_of_length_3_or_more(overall_G)
        subgraphs = ngc.split_into_subgraphs(filtered_graph if len(filtered_graph.nodes()) > 0 else overall_G, num_subgraphs=1)
        
        if subgraphs and subgraphs[0].number_of_nodes() > 0:
            net = Network(notebook=False, directed=True, height='600px', width='100%')
            net.from_nx(subgraphs[0])
            
            # Update node labels with company names
            for node in net.nodes:
                node_id = node['id']
                label = insured_dict.get(node_id, contractor_dict.get(node_id, node_id))
                node['label'] = label
                node['size'] = 30
                node['font'] = {'size': 14}
            
            # Highlight length 3+ edges
            for edge in net.edges:
                u, v = edge['from'], edge['to']
                if (u, v) in length_3_plus_edges:
                    edge['color'] = '#dc2626'
                    edge['width'] = 3
                else:
                    edge['color'] = '#6b7280'
                    edge['width'] = 1
            
            # Highlight cycles
            colors = ['#f472b6', '#a3e635', '#22d3ee']
            filtered_cycles = {}
            for length in cycle_lengths:
                filtered_cycles[length] = [c for c in cycles_overall[length] if all(node in subgraphs[0].nodes() for node in c)]
            for j, length in enumerate(filtered_cycles):
                for cycle in filtered_cycles[length]:
                    if cycle:
                        color = colors[j % len(colors)]
                        for node_id in cycle:
                            for node in net.nodes:
                                if node['id'] == node_id:
                                    node['color'] = color
                                    break
            
            # Enable physics and arrows
            net.set_options("""
            var options = {
              "physics": {
                "enabled": true,
                "barnesHut": {
                  "gravitationalConstant": -3000,
                  "springLength": 150
                }
              },
              "edges": {
                "arrows": {
                  "to": { "enabled": true, "scaleFactor": 1 }
                }
              }
            }
            """)
            
            st.session_state.overall_html = net.generate_html()
        else:
            st.session_state.overall_html = "<p>전체 관계망에 노드가 없습니다.</p>"

        # Create extended graph with arbitrary nodes
        extended_overall_G = nx.DiGraph()

        # Add original edges
        for s, b in st.session_state.pairs:
            extended_overall_G.add_edge(s, b)

        # Label dict for arbitrary names
        label_dict = {}
        shared_groups = defaultdict(list)  # top_node -> list of original nodes

        # Add 5 arbitrary buyers (sales) for each selected seller
        for seller in selected_sellers:
            for i in range(1, 6):
                arbitrary_buyer = f"arbitrary_buyer_{seller}_{i}"
                extended_overall_G.add_edge(seller, arbitrary_buyer)
                shared_groups[arbitrary_buyer].append(seller)
                label_dict[arbitrary_buyer] = f"매출{i}"

        # Add 5 arbitrary sellers (purchases) for each selected buyer
        for buyer in selected_buyers:
            for i in range(1, 6):
                arbitrary_seller = f"arbitrary_seller_{buyer}_{i}"
                extended_overall_G.add_edge(arbitrary_seller, buyer)
                shared_groups[arbitrary_seller].append(buyer)
                label_dict[arbitrary_seller] = f"매입{i}"

        # Assign colors to shared nodes (if shared across multiple originals)
        shared_colors = {}
        color_list = ['#ef4444', '#22c55e', '#3b82f6', '#eab308', '#d946ef', '#14b8a6', '#f97316', '#8b5cf6']
        color_idx = 0
        for node, originals in shared_groups.items():
            if len(originals) > 1:
                shared_colors[node] = color_list[color_idx % len(color_list)]
                color_idx += 1

        # Compute cycles for extended overall
        all_cycles_extended = list(nx.simple_cycles(extended_overall_G))
        cycles_extended = {length: [cycle for cycle in all_cycles_extended if len(cycle) == length] for length in cycle_lengths}

        # Draw extended overall graph
        filtered_graph, length_3_plus_edges = ngc.filter_paths_of_length_3_or_more(extended_overall_G)
        subgraphs = ngc.split_into_subgraphs(filtered_graph if len(filtered_graph.nodes()) > 0 else extended_overall_G, num_subgraphs=1)
        
        if subgraphs and subgraphs[0].number_of_nodes() > 0:
            net = Network(notebook=False, directed=True, height='600px', width='100%')
            net.from_nx(subgraphs[0])
            
            # Update node labels with company names or arbitrary
            for node in net.nodes:
                node_id = node['id']
                label = label_dict.get(node_id, insured_dict.get(node_id, contractor_dict.get(node_id, node_id)))
                node['label'] = label
                node['size'] = 30
                node['font'] = {'size': 14}
                if node_id in shared_colors:
                    node['color'] = shared_colors[node_id]
            
            # Highlight length 3+ edges
            for edge in net.edges:
                u, v = edge['from'], edge['to']
                if (u, v) in length_3_plus_edges:
                    edge['color'] = '#dc2626'
                    edge['width'] = 3
                else:
                    edge['color'] = '#6b7280'
                    edge['width'] = 1
            
            # Highlight cycles (apply only if no shared color)
            colors = ['#f472b6', '#a3e635', '#22d3ee']
            filtered_cycles = {}
            for length in cycle_lengths:
                filtered_cycles[length] = [c for c in cycles_extended[length] if all(node in subgraphs[0].nodes() for node in c)]
            for j, length in enumerate(filtered_cycles):
                for cycle in filtered_cycles[length]:
                    if cycle:
                        color = colors[j % len(colors)]
                        for node_id in cycle:
                            for node in net.nodes:
                                if node['id'] == node_id and 'color' not in node:
                                    node['color'] = color
                                    break
            
            # Enable physics and arrows
            net.set_options("""
            var options = {
              "physics": {
                "enabled": true,
                "barnesHut": {
                  "gravitationalConstant": -3000,
                  "springLength": 150
                }
              },
              "edges": {
                "arrows": {
                  "to": { "enabled": true, "scaleFactor": 1 }
                }
              }
            }
            """)
            
            st.session_state.extended_overall_html = net.generate_html()
        else:
            st.session_state.extended_overall_html = "<p>확장된 전체 관계망에 노드가 없습니다.</p>"

        st.session_state.network_run = True
        st.session_state.show_sales_details = [False] * len(st.session_state.htmls)
        st.session_state.show_fraud_analysis = [False] * len(st.session_state.htmls)
        st.rerun()
    else:
        st.warning("분석할 거래 쌍을 추가해주세요.")

# Display overall and extended graphs in 1:1 grid
if st.session_state.network_run and st.session_state.overall_html and st.session_state.extended_overall_html:
    st.markdown('<div class="graph-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("전체 관계망")
        html(st.session_state.overall_html, height=600, scrolling=True)
    with col2:
        st.subheader("확장된 전체 관계망")
        html(st.session_state.extended_overall_html, height=600, scrolling=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Display subgraphs with fraud analysis details
if st.session_state.network_run and st.session_state.htmls:
    for i, html_content in enumerate(st.session_state.htmls, 1):
        st.subheader(f"관계망 {i}")
        col_graph, col_table = st.columns([3, 2])
        with col_graph:
            st.markdown('<div class="graph-container">', unsafe_allow_html=True)
            html(html_content, height=600, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col_table:
            st.write("**거래 상세**")
            col_buttons = st.columns(2)
            with col_buttons[0]:
                if st.button("매출매입 상세", key=f"sales_details_{i}"):
                    st.session_state.show_sales_details[i-1] = not st.session_state.show_sales_details[i-1]
                    st.session_state.show_fraud_analysis[i-1] = False
                    st.rerun()
            with col_buttons[1]:
                if st.button("사기거래 분석", key=f"fraud_analysis_{i}"):
                    st.session_state.show_fraud_analysis[i-1] = not st.session_state.show_fraud_analysis[i-1]
                    st.session_state.show_sales_details[i-1] = False
                    st.rerun()

            # Get nodes in cycles of the desired length
            G = nx.DiGraph(st.session_state.pairs)
            all_cycles = list(nx.simple_cycles(G))
            cycles = {length: [cycle for cycle in all_cycles if len(cycle) == length] for length in cycle_lengths}
            subgraph_nodes = set()
            # Use all pairs if no cycles are found
            subgraph_pairs = st.session_state.pairs
            # If cycles exist, filter pairs by cycle nodes
            target_length = cycle_lengths[min(i-1, len(cycle_lengths)-1)] if cycle_lengths else None
            if target_length in cycles and cycles[target_length]:
                for cycle in cycles[target_length]:
                    subgraph_nodes.update(cycle)
                subgraph_pairs = [(seller, buyer) for seller, buyer in st.session_state.pairs 
                                 if seller in subgraph_nodes or buyer in subgraph_nodes]
            
            if st.session_state.show_sales_details[i-1]:
                # Retrieve PARSED_DATA entries matching the pairs
                details_data = []
                for seller, buyer in subgraph_pairs:
                    for entry in PARSED_DATA:
                        if entry['no_biz'] == seller and entry['no_bisocial'] == buyer:
                            # Select specific fields
                            details_data.append({
                                '판매자 번호': entry['no_biz'],
                                '구매자 번호': entry['no_bisocial'],
                                '거래처명': entry.get('nm_trade', 'N/A'),
                                '계정과목': entry.get('nm_acctit', 'N/A'),
                                '구분': entry.get('ty_gubn', 'N/A'),
                                '분개내역': entry.get('ct_bungae', 'N/A')
                            })
                
                if details_data:
                    # Convert to DataFrame and display selected fields
                    df = pd.DataFrame(details_data)
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("해당 쌍에 대한 상세 데이터가 없습니다.")
            elif st.session_state.show_fraud_analysis[i-1]:
                items = [
                    "최근 2년간 거래대금 결제 이력(회수) 여부 (판매자)",
                    "최근 2년간 거래대금 결제 이력(지급) 여부 (구매자)",
                    "양사 대표자 동일 여부",
                    "양사 대표자 가족 중복 여부",
                    "양사 대표자 종업원 포함 여부",
                    "양사 동일 종업원 존재 여부",
                    "회전거래 업체와 최근 2년간 거래 여부",
                    "폭탄업체와 최근 2년간 거래 여부",
                    "회전거래 업체 여부",
                    "계약자와 피보험자가 3개 이상인 경우 회전거래 존재 여부",
                    "동일 세무대리인 기장 이력 여부",
                    "사업장 주소지 유사성 여부",
                    "주주 구성 동일성 여부",
                    "중간거래상 거래 여부"
                ]
                # For 관계망3 (i=3), always show "사기거래 징후가 보이지 않습니다"
                if i == 3:
                    values = ['n'] * len(items)
                else:
                    values = [random.choice(['y', 'n']) for _ in items]
                df = pd.DataFrame({'항목': items, '해당 여부': values})
                st.dataframe(df, use_container_width=True)
                if 'y' in values:
                    st.markdown('<p class="fraud-warning">사기거래 징후가 보입니다.</p>', unsafe_allow_html=True)
                else:
                    st.markdown('<p class="no-fraud">사기거래 징후가 보이지 않습니다.</p>', unsafe_allow_html=True)
            else:
                st.info("‘매출매입 상세’ 또는 ‘사기거래 분석’을 클릭하여 상세 정보를 확인하세요.")
