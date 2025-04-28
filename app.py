import streamlit as st
import pandas as pd
import json
import io
import base64
from collections import Counter
from github import Github, GithubException

# CSS tối ưu cho giao diện
st.markdown("""
    <style>
    .main {
        background-color: #000000;
        padding: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: #FFFFFF;
        border-radius: 8px;
        font-size: 18px;
        padding: 10px;
        width: 100%;
        margin: 10px 0;
        transition: background-color 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput>label, .stNumberInput>label, .stSelectbox>label, .stFileUploader>label {
        font-weight: bold;
        color: #FFFFFF;
        font-size: 16px;
    }
    .stTextInput>input, .stNumberInput>input {
        font-size: 16px;
        padding: 10px;
        border-radius: 5px;
        background-color: #333333;
        color: #FFFFFF;
        border: 1px solid #555555;
    }
    .stSelectbox select {
        font-size: 16px;
        padding: 10px;
        border-radius: 5px;
        background-color: #333333;
        color: #FFFFFF;
        border: 1px solid #555555;
    }
    h1, h2, h3 {
        color: #FFFFFF;
    }
    h1 {
        text-align: center;
        font-size: 16px;
    }
    h2, h3 {
        font-size: 22px;
    }
    .stDataFrame {
        border: 1px solid #555555;
        border-radius: 5px;
        font-size: 14px;
        background-color: #000000;
        color: #FFFFFF;
    }
    .stDataFrame table {
        color: #FFFFFF;
    }
    .match-info {
        background-color: #333333;
        padding: 10px;
        border: 2px solid #555555;
        border-radius: 5px;
        margin-bottom: 15px;
        font-size: 16px;
        color: #FFFFFF;
    }
    .nav-buttons {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
    }
    @media (max-width: 600px) {
        .stButton>button {
            font-size: 16px;
            padding: 8px;
        }
        .stTextInput>input, .stNumberInput>input, .stSelectbox select {
            font-size: 14px;
        }
        h1 {
            font-size: 18px;
        }
        h2, h3 {
            font-size: 20px;
        }
        .stDataFrame {
            font-size: 12px;
        }
        .match-info {
            font-size: 14px;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    [data-testid="stToolbar"] {
            visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Danh sách 26 trận đấu
matches = [
    {"Ngày": "27/04/2025", "Thời gian": "7:00", "Bảng/Vòng": "Bảng A", "Trận đấu": "24DTH1D vs 22DKTPM1B", "Sân": "Sân 1", "Đội 1": "24DTH1D", "Đội 2": "22DKTPM1B"},
    {"Ngày": "27/04/2025", "Thời gian": "7:00", "Bảng/Vòng": "Bảng B", "Trận đấu": "22DTH1D vs 22DKTPM1D", "Sân": "Sân 2", "Đội 1": "22DTH1D", "Đội 2": "22DKTPM1D"},
    {"Ngày": "27/04/2025", "Thời gian": "8:00", "Bảng/Vòng": "Bảng C", "Trận đấu": "22DTH1A vs 24DTH1A + 23DKTPM1A", "Sân": "Sân 1", "Đội 1": "22DTH1A", "Đội 2": "24DTH1A + 23DKTPM1A"},
    {"Ngày": "27/04/2025", "Thời gian": "8:00", "Bảng/Vòng": "Bảng D", "Trận đấu": "23DTH1B vs 21DTH2C + 20DTH2A", "Sân": "Sân 2", "Đội 1": "23DTH1B", "Đội 2": "21DTH2C + 20DTH2A"},
    {"Ngày": "27/04/2025", "Thời gian": "16:00", "Bảng/Vòng": "Bảng C", "Trận đấu": "24DKTPM1A vs 23DTH2D", "Sân": "Sân 1", "Đội 1": "24DKTPM1A", "Đội 2": "23DTH2D"},
    {"Ngày": "27/04/2025", "Thời gian": "16:00", "Bảng/Vòng": "Bảng D", "Trận đấu": "22DKTPM1A + 24DTH2B vs 22DTH2C", "Sân": "Sân 2", "Đội 1": "22DKTPM1A + 24DTH2B", "Đội 2": "22DTH2C"},
    {"Ngày": "10/05/2025", "Thời gian": "7:00", "Bảng/Vòng": "Bảng A", "Trận đấu": "24DTH1D vs 24DTH2A_1D", "Sân": "Sân 1", "Đội 1": "24DTH1D", "Đội 2": "24DTH2A_1D"},
    {"Ngày": "10/05/2025", "Thời gian": "7:00", "Bảng/Vòng": "Bảng C", "Trận đấu": "22DTH1A vs 24DKTPM1A", "Sân": "Sân 2", "Đội 1": "22DTH1A", "Đội 2": "24DKTPM1A"},
    {"Ngày": "10/05/2025", "Thời gian": "8:00", "Bảng/Vòng": "Bảng B", "Trận đấu": "22DTH1D vs 22DTH3B_2D + 23DTH1A", "Sân": "Sân 1", "Đội 1": "22DTH1D", "Đội 2": "22DTH3B_2D + 23DTH1A"},
    {"Ngày": "10/05/2025", "Thời gian": "8:00", "Bảng/Vòng": "Bảng D", "Trận đấu": "23DTH1B vs 22DKTPM1A + 24DTH2B", "Sân": "Sân 2", "Đội 1": "23DTH1B", "Đội 2": "22DKTPM1A + 24DTH2B"},
    {"Ngày": "10/05/2025", "Thời gian": "16:00", "Bảng/Vòng": "Bảng C", "Trận đấu": "24DTH1A + 23DKTPM1A vs 23DTH2D", "Sân": "Sân 1", "Đội 1": "24DTH1A + 23DKTPM1A", "Đội 2": "23DTH2D"},
    {"Ngày": "10/05/2025", "Thời gian": "16:00", "Bảng/Vòng": "Bảng D", "Trận đấu": "21DTH2C + 20DTH2A vs 22DTH2C", "Sân": "Sân 2", "Đội 1": "21DTH2C + 20DTH2A", "Đội 2": "22DTH2C"},
    {"Ngày": "17/05/2025", "Thời gian": "7:00", "Bảng/Vòng": "Bảng C", "Trận đấu": "22DTH1A vs 23DTH2D", "Sân": "Sân 1", "Đội 1": "22DTH1A", "Đội 2": "23DTH2D"},
    {"Ngày": "17/05/2025", "Thời gian": "7:00", "Bảng/Vòng": "Bảng D", "Trận đấu": "23DTH1B vs 22DTH2C", "Sân": "Sân 2", "Đội 1": "23DTH1B", "Đội 2": "22DTH2C"},
    {"Ngày": "17/05/2025", "Thời gian": "8:00", "Bảng/Vòng": "Bảng C", "Trận đấu": "24DTH1A + 23DKTPM1A vs 24DKTPM1A", "Sân": "Sân 1", "Đội 1": "24DTH1A + 23DKTPM1A", "Đội 2": "24DKTPM1A"},
    {"Ngày": "17/05/2025", "Thời gian": "8:00", "Bảng/Vòng": "Bảng D", "Trận đấu": "21DTH2C + 20DTH2A vs 22DKTPM1A + 24DTH2B", "Sân": "Sân 2", "Đội 1": "21DTH2C + 20DTH2A", "Đội 2": "22DKTPM1A + 24DTH2B"},
    {"Ngày": "17/05/2025", "Thời gian": "16:00", "Bảng/Vòng": "Bảng A", "Trận đấu": "22DKTPM1B vs 24DTH2A_1D", "Sân": "Sân 1", "Đội 1": "22DKTPM1B", "Đội 2": "24DTH2A_1D"},
    {"Ngày": "17/05/2025", "Thời gian": "16:00", "Bảng/Vòng": "Bảng B", "Trận đấu": "22DKTPM1D vs 22DTH3B_2D + 23DTH1A", "Sân": "Sân 2", "Đội 1": "22DKTPM1D", "Đội 2": "22DTH3B_2D + 23DTH1A"},
    {"Ngày": "18/05/2025", "Thời gian": "7:00", "Bảng/Vòng": "Tứ kết 1", "Trận đấu": "Nhất A vs Nhì B", "Sân": "Sân 1", "Đội 1": "Nhất A", "Đội 2": "Nhì B"},
    {"Ngày": "18/05/2025", "Thời gian": "7:00", "Bảng/Vòng": "Tứ kết 2", "Trận đấu": "Nhất B vs Nhì A", "Sân": "Sân 2", "Đội 1": "Nhất B", "Đội 2": "Nhì A"},
    {"Ngày": "18/05/2025", "Thời gian": "8:00", "Bảng/Vòng": "Tứ kết 3", "Trận đấu": "Nhất C vs Nhì D", "Sân": "Sân 1", "Đội 1": "Nhất C", "Đội 2": "Nhì D"},
    {"Ngày": "18/05/2025", "Thời gian": "8:00", "Bảng/Vòng": "Tứ kết 4", "Trận đấu": "Nhất D vs Nhì C", "Sân": "Sân 2", "Đội 1": "Nhất D", "Đội 2": "Nhì C"},
    {"Ngày": "24/05/2025", "Thời gian": "7:00", "Bảng/Vòng": "Bán kết 1", "Trận đấu": "Thắng TK1 vs Thắng TK3", "Sân": "Sân 1", "Đội 1": "Thắng TK1", "Đội 2": "Thắng TK3"},
    {"Ngày": "24/05/2025", "Thời gian": "7:00", "Bảng/Vòng": "Bán kết 2", "Trận đấu": "Thắng TK2 vs Thắng TK4", "Sân": "Sân 2", "Đội 1": "Thắng TK2", "Đội 2": "Thắng TK4"},
    {"Ngày": "25/05/2025", "Thời gian": "8:00", "Bảng/Vòng": "Tranh hạng 3", "Trận đấu": "Thua BK1 vs Thua BK2", "Sân": "Sân 1", "Đội 1": "Thua BK1", "Đội 2": "Thua BK2"},
    {"Ngày": "25/05/2025", "Thời gian": "9:00", "Bảng/Vòng": "Chung kết", "Trận đấu": "Thắng BK1 vs Thắng BK2", "Sân": "Sân 1", "Đội 1": "Thắng BK1", "Đội 2": "Thắng BK2"}
]

# Cấu trúc bảng
groups = {
    "Bảng A": ["24DTH1D", "22DKTPM1B", "24DTH2A_1D"],
    "Bảng B": ["22DTH1D", "22DKTPM1D", "22DTH3B_2D + 23DTH1A"],
    "Bảng C": ["22DTH1A", "24DTH1A + 23DKTPM1A", "24DKTPM1A", "23DTH2D"],
    "Bảng D": ["23DTH1B", "21DTH2C + 20DTH2A", "22DKTPM1A + 24DTH2B", "22DTH2C"]
}

# Hàm lưu file lên GitHub
def save_to_github(file_name, file_content):
    try:
        g = Github(st.secrets["github"]["github_token"])
        repo = g.get_repo(f"{st.secrets['github']['github_owner']}/{st.secrets['github']['github_repo']}")
        file_path = f"data/{file_name}"
        try:
            contents = repo.get_contents(file_path)
            repo.update_file(file_path, f"Update {file_name}", file_content, contents.sha)
        except GithubException as e:
            if e.status == 404:
                repo.create_file(file_path, f"Create {file_name}", file_content)
            else:
                raise e
        return file_path
    except KeyError as e:
        st.error(f"Lỗi: Thiếu khóa {e} trong Streamlit Secrets. Vui lòng cấu hình github_token, github_owner, github_repo trong Secrets.")
        st.stop()
    except GithubException as e:
        st.error(f"Lỗi GitHub API: {str(e)}. Vui lòng kiểm tra github_token hoặc kho GitHub.")
        st.stop()

# Hàm tải file từ GitHub
@st.cache_data
def load_from_github(file_name):
    try:
        g = Github(st.secrets["github"]["github_token"])
        repo = g.get_repo(f"{st.secrets['github']['github_owner']}/{st.secrets['github']['github_repo']}")
        file_path = f"data/{file_name}"
        contents = repo.get_contents(file_path)
        return base64.b64decode(contents.content)
    except GithubException as e:
        if e.status == 404:
            return None
        st.error(f"Lỗi GitHub API: {str(e)}. Vui lòng kiểm tra github_token hoặc kho GitHub.")
        st.stop()
    except KeyError as e:
        st.error(f"Lỗi: Thiếu khóa {e} trong Streamlit Secrets. Vui lòng cấu hình github_token, github_owner, github_repo trong Secrets.")
        st.stop()

# Hàm tính bảng xếp hạng
def calculate_rankings(results):
    rankings = {team: {"Trận": 0, "Thắng": 0, "Hòa": 0, "Thua": 0, "Bàn thắng": 0, "Bàn thua": 0, "Điểm": 0} 
                for group in groups.values() for team in group}
    
    for match in results:
        if match["Bảng/Vòng"].startswith("Bảng"):
            team1, team2 = match["Đội 1"], match["Đội 2"]
            team1_score, team2_score = match["Đội 1 Tỷ số"], match["Đội 2 Tỷ số"]

            rankings[team1]["Trận"] += 1
            rankings[team2]["Trận"] += 1
            rankings[team1]["Bàn thắng"] += team1_score
            rankings[team2]["Bàn thắng"] += team2_score
            rankings[team1]["Bàn thua"] += team2_score
            rankings[team2]["Bàn thua"] += team1_score

            if team1_score > team2_score:
                rankings[team1]["Thắng"] += 1
                rankings[team1]["Điểm"] += 3
                rankings[team2]["Thua"] += 1
            elif team2_score > team1_score:
                rankings[team2]["Thắng"] += 1
                rankings[team2]["Điểm"] += 3
                rankings[team1]["Thua"] += 1
            else:
                rankings[team1]["Hòa"] += 1
                rankings[team2]["Hòa"] += 1
                rankings[team1]["Điểm"] += 1
                rankings[team2]["Điểm"] += 1

    group_rankings = []
    for group_name, teams in groups.items():
        group_teams = []
        for team in teams:
            stats = rankings[team]
            stats["Đội"] = team
            stats["Hiệu số"] = stats["Bàn thắng"] - stats["Bàn thua"]
            group_teams.append(stats)
        
        group_teams.sort(key=lambda x: (x["Điểm"], x["Hiệu số"], x["Bàn thắng"]), reverse=True)
        for rank, team_stats in enumerate(group_teams, 1):
            group_rankings.append({
                "Bảng": group_name,
                "Đội": team_stats["Đội"],
                "Trận": team_stats["Trận"],
                "Thắng": team_stats["Thắng"],
                "Hòa": team_stats["Hòa"],
                "Thua": team_stats["Thua"],
                "Bàn thắng": team_stats["Bàn thắng"],
                "Bàn thua": team_stats["Bàn thua"],
                "Hiệu số": team_stats["Hiệu số"],
                "Điểm": team_stats["Điểm"]
            })

    return group_rankings

# Hàm thống kê cá nhân
def calculate_player_stats(results):
    goals = Counter()
    yellow_cards = Counter()
    red_cards = Counter()

    for match in results:
        if match["Cầu thủ ghi bàn"]:
            for player in match["Cầu thủ ghi bàn"].split(','):
                player = player.strip()
                goals[player] += 1
        if match["Cầu thủ thẻ vàng"]:
            for player in match["Cầu thủ thẻ vàng"].split(','):
                player = player.strip()
                yellow_cards[player] += 1
        if match["Cầu thủ thẻ đỏ"]:
            for player in match["Cầu thủ thẻ đỏ"].split(','):
                player = player.strip()
                red_cards[player] += 1

    goal_stats = [{"Cầu thủ": player, "Số bàn": count} for player, count in goals.most_common()]
    yellow_stats = [{"Cầu thủ": player, "Số thẻ vàng": count} for player, count in yellow_cards.most_common()]
    red_stats = [{"Cầu thủ": player, "Số thẻ đỏ": count} for player, count in red_cards.most_common()]

    return goal_stats, yellow_stats, red_stats

# Hàm tạo link tải file
def get_binary_file_downloader_html(bin_file, file_label='File'):
    bin_str = base64.b64encode(bin_file).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}" style="color: #FFFFFF;">Tải {file_label}</a>'
    return href

# Giao diện Streamlit
st.title("🏆 Bóng đá Khoa CNTT 2025")

# Khởi tạo session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'current_match_index' not in st.session_state:
    st.session_state.current_match_index = 0
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None
if 'scorers' not in st.session_state:
    st.session_state.scorers = []
if 'yellow_cards' not in st.session_state:
    st.session_state.yellow_cards = []
if 'red_cards' not in st.session_state:
    st.session_state.red_cards = []
if 'scorer_input_value' not in st.session_state:
    st.session_state.scorer_input_value = ""
if 'yellow_input_value' not in st.session_state:
    st.session_state.yellow_input_value = ""
if 'red_input_value' not in st.session_state:
    st.session_state.red_input_value = ""
if 'scorer_team' not in st.session_state:
    st.session_state.scorer_team = None
if 'yellow_team' not in st.session_state:
    st.session_state.yellow_team = None
if 'red_team' not in st.session_state:
    st.session_state.red_team = None
if 'temp_reset' not in st.session_state:
    st.session_state.temp_reset = {"scorer": False, "yellow": False, "red": False}

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Nhập Kết quả", "Kết quả Trận đấu", "Bảng Xếp hạng", "Thống kê Cá nhân"])

# Tab 1: Nhập Kết quả
with tab1:
    st.header("Nhập Kết quả Trận đấu")
    
    # Reset trạng thái nếu được đánh dấu
    if st.session_state.temp_reset["scorer"]:
        st.session_state.scorer_input_value = ""
        st.session_state.scorer_team = None
        st.session_state.temp_reset["scorer"] = False
    if st.session_state.temp_reset["yellow"]:
        st.session_state.yellow_input_value = ""
        st.session_state.yellow_team = None
        st.session_state.temp_reset["yellow"] = False
    if st.session_state.temp_reset["red"]:
        st.session_state.red_input_value = ""
        st.session_state.red_team = None
        st.session_state.temp_reset["red"] = False
    
    match = matches[st.session_state.current_match_index]
    st.markdown(f"""
        <div class="match-info">
            <b>Trận {st.session_state.current_match_index + 1}</b><br>
            {match['Ngày']} {match['Thời gian']} - {match['Bảng/Vòng']}<br>
            {match['Trận đấu']} - {match['Sân']}
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Trận Trước", disabled=st.session_state.current_match_index == 0, key="prev_match"):
            st.session_state.current_match_index -= 1
            st.session_state.scorers = []
            st.session_state.yellow_cards = []
            st.session_state.red_cards = []
            st.session_state.scorer_input_value = ""
            st.session_state.yellow_input_value = ""
            st.session_state.red_input_value = ""
            st.session_state.scorer_team = None
            st.session_state.yellow_team = None
            st.session_state.red_team = None
            st.session_state.temp_reset = {"scorer": False, "yellow": False, "red": False}
            st.rerun()
    with col2:
        if st.button("Trận Sau", disabled=st.session_state.current_match_index == len(matches) - 1, key="next_match"):
            st.session_state.current_match_index += 1
            st.session_state.scorers = []
            st.session_state.yellow_cards = []
            st.session_state.red_cards = []
            st.session_state.scorer_input_value = ""
            st.session_state.yellow_input_value = ""
            st.session_state.red_input_value = ""
            st.session_state.scorer_team = None
            st.session_state.yellow_team = None
            st.session_state.red_team = None
            st.session_state.temp_reset = {"scorer": False, "yellow": False, "red": False}
            st.rerun()

    st.subheader("Cầu thủ Ghi bàn")
    scorer_input = st.text_input("Tên cầu thủ (ví dụ: Nguyễn Văn A)", value=st.session_state.scorer_input_value, key="scorer_input")
    team_options = [match["Đội 1"], match["Đội 2"]]
    scorer_team = st.selectbox("Chọn đội", team_options, 
                             index=team_options.index(st.session_state.scorer_team) if st.session_state.scorer_team in team_options else 0, 
                             key="scorer_team")
    col_scorer1, col_scorer2 = st.columns(2)
    with col_scorer1:
        if st.button("Thêm Cầu thủ Ghi bàn", key="add_scorer"):
            if scorer_input.strip() and scorer_team:
                st.session_state.scorers.append(f"{scorer_input.strip()} - {scorer_team}")
                st.session_state.temp_reset["scorer"] = True
                st.success("Đã thêm cầu thủ ghi bàn!")
                st.rerun()
            else:
                st.warning("Vui lòng nhập tên cầu thủ và chọn đội.")
    with col_scorer2:
        if st.button("Xóa Danh sách Ghi bàn", key="clear_scorers"):
            st.session_state.scorers = []
            st.session_state.temp_reset["scorer"] = True
            st.success("Đã xóa danh sách ghi bàn!")
            st.rerun()
    if st.session_state.scorers:
        st.write("Danh sách ghi bàn: " + ", ".join(st.session_state.scorers))

    st.subheader("Cầu thủ Thẻ vàng")
    yellow_input = st.text_input("Tên cầu thủ (ví dụ: Lê Văn C)", value=st.session_state.yellow_input_value, key="yellow_input")
    yellow_team = st.selectbox("Chọn đội", team_options, 
                             index=team_options.index(st.session_state.yellow_team) if st.session_state.yellow_team in team_options else 0, 
                             key="yellow_team")
    col_yellow1, col_yellow2 = st.columns(2)
    with col_yellow1:
        if st.button("Thêm Cầu thủ Thẻ vàng", key="add_yellow"):
            if yellow_input.strip() and yellow_team:
                st.session_state.yellow_cards.append(f"{yellow_input.strip()} - {yellow_team}")
                st.session_state.temp_reset["yellow"] = True
                st.success("Đã thêm cầu thủ thẻ vàng!")
                st.rerun()
            else:
                st.warning("Vui lòng nhập tên cầu thủ và chọn đội.")
    with col_yellow2:
        if st.button("Xóa Danh sách Thẻ vàng", key="clear_yellow"):
            st.session_state.yellow_cards = []
            st.session_state.temp_reset["yellow"] = True
            st.success("Đã xóa danh sách thẻ vàng!")
            st.rerun()
    if st.session_state.yellow_cards:
        st.write("Danh sách thẻ vàng: " + ", ".join(st.session_state.yellow_cards))

    st.subheader("Cầu thủ Thẻ đỏ")
    red_input = st.text_input("Tên cầu thủ (ví dụ: Phạm Văn D)", value=st.session_state.red_input_value, key="red_input")
    red_team = st.selectbox("Chọn đội", team_options, 
                          index=team_options.index(st.session_state.red_team) if st.session_state.red_team in team_options else 0, 
                          key="red_team")
    col_red1, col_red2 = st.columns(2)
    with col_red1:
        if st.button("Thêm Cầu thủ Thẻ đỏ", key="add_red"):
            if red_input.strip() and red_team:
                st.session_state.red_cards.append(f"{red_input.strip()} - {red_team}")
                st.session_state.temp_reset["red"] = True
                st.success("Đã thêm cầu thủ thẻ đỏ!")
                st.rerun()
            else:
                st.warning("Vui lòng nhập tên cầu thủ và chọn đội.")
    with col_red2:
        if st.button("Xóa Danh sách Thẻ đỏ", key="clear_red"):
            st.session_state.red_cards = []
            st.session_state.temp_reset["red"] = True
            st.success("Đã xóa danh sách thẻ đỏ!")
            st.rerun()
    if st.session_state.red_cards:
        st.write("Danh sách thẻ đỏ: " + ", ".join(st.session_state.red_cards))

    is_edit = st.session_state.edit_index is not None
    with st.form(key=f"match_form_{st.session_state.current_match_index}"):
        st.subheader("Tỷ số")
        col_score1, col_score2 = st.columns(2)
        with col_score1:
            team1_score = st.number_input(f"Điểm {match['Đội 1']}", min_value=0, value=0 if not is_edit else st.session_state.results[st.session_state.edit_index]["Đội 1 Tỷ số"], step=1)
        with col_score2:
            team2_score = st.number_input(f"Điểm {match['Đội 2']}", min_value=0, value=0 if not is_edit else st.session_state.results[st.session_state.edit_index]["Đội 2 Tỷ số"], step=1)

        submit_button = st.form_submit_button("Lưu Kết quả" if not is_edit else "Cập nhật Kết quả")

        if submit_button:
            result = match.copy()
            result["Tỷ số"] = f"{team1_score}-{team2_score}"
            result["Đội 1 Tỷ số"] = team1_score
            result["Đội 2 Tỷ số"] = team2_score
            result["Cầu thủ ghi bàn"] = ", ".join(st.session_state.scorers)
            result["Cầu thủ thẻ vàng"] = ", ".join(st.session_state.yellow_cards)
            result["Cầu thủ thẻ đỏ"] = ", ".join(st.session_state.red_cards)

            if is_edit:
                st.session_state.results[st.session_state.edit_index] = result
                st.session_state.edit_index = None
                st.session_state.scorers = []
                st.session_state.yellow_cards = []
                st.session_state.red_cards = []
                st.session_state.temp_reset["scorer"] = True
                st.session_state.temp_reset["yellow"] = True
                st.session_state.temp_reset["red"] = True
                st.success("Đã cập nhật kết quả!")
                st.rerun()
            else:
                if any(r["Trận đấu"] == match["Trận đấu"] and r["Ngày"] == match["Ngày"] for r in st.session_state.results):
                    st.warning("Trận này đã được nhập. Vui lòng chỉnh sửa hoặc chọn trận khác.")
                else:
                    st.session_state.results.append(result)
                    st.session_state.scorers = []
                    st.session_state.yellow_cards = []
                    st.session_state.red_cards = []
                    st.session_state.temp_reset["scorer"] = True
                    st.session_state.temp_reset["yellow"] = True
                    st.session_state.temp_reset["red"] = True
                    st.success("Đã lưu kết quả!")
                    if st.session_state.current_match_index < len(matches) - 1:
                        st.session_state.current_match_index += 1
                    st.rerun()

# Tab 2: Kết quả Trận đấu
with tab2:
    st.header("Kết quả Các Trận đấu")
    if st.session_state.results:
        df_results = pd.DataFrame(st.session_state.results)
        st.dataframe(df_results[["Ngày", "Thời gian", "Bảng/Vòng", "Trận đấu", "Sân", "Tỷ số", "Cầu thủ ghi bàn", "Cầu thủ thẻ vàng", "Cầu thủ thẻ đỏ"]], height=300)

        st.subheader("Chỉnh sửa hoặc Xóa Kết quả")
        result_options = [f"{r['Ngày']} {r['Thời gian']} - {r['Bảng/Vòng']} - {r['Trận đấu']}" for r in st.session_state.results]
        selected_result = st.selectbox("Chọn kết quả để chỉnh sửa/xóa", result_options, key="result_select")
        if selected_result:
            result_index = result_options.index(selected_result)
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Chỉnh sửa", key="edit_result"):
                    st.session_state.edit_index = result_index
                    st.session_state.current_match_index = [i for i, m in enumerate(matches) if m["Trận đấu"] == st.session_state.results[result_index]["Trận đấu"] and m["Ngày"] == st.session_state.results[result_index]["Ngày"]][0]
                    st.session_state.scorers = st.session_state.results[result_index]["Cầu thủ ghi bàn"].split(", ") if st.session_state.results[result_index]["Cầu thủ ghi bàn"] else []
                    st.session_state.yellow_cards = st.session_state.results[result_index]["Cầu thủ thẻ vàng"].split(", ") if st.session_state.results[result_index]["Cầu thủ thẻ vàng"] else []
                    st.session_state.red_cards = st.session_state.results[result_index]["Cầu thủ thẻ đỏ"].split(", ") if st.session_state.results[result_index]["Cầu thủ thẻ đỏ"] else []
                    st.session_state.scorer_input_value = ""
                    st.session_state.yellow_input_value = ""
                    st.session_state.red_input_value = ""
                    st.session_state.scorer_team = None
                    st.session_state.yellow_team = None
                    st.session_state.red_team = None
                    st.session_state.temp_reset = {"scorer": False, "yellow": False, "red": False}
                    st.rerun()
            with col2:
                if st.button("Xóa", key="delete_result"):
                    st.session_state.results.pop(result_index)
                    st.session_state.edit_index = None
                    st.session_state.temp_reset = {"scorer": False, "yellow": False, "red": False}
                    st.success("Đã xóa kết quả!")
                    st.rerun()
    else:
        st.write("Chưa có kết quả nào được nhập.")

# Tab 3: Bảng Xếp hạng
with tab3:
    st.header("Bảng Xếp hạng")
    if st.session_state.results:
        rankings = calculate_rankings(st.session_state.results)
        df_rankings = pd.DataFrame(rankings)
        for group in groups.keys():
            st.subheader(group)
            st.dataframe(df_rankings[df_rankings["Bảng"] == group][["Đội", "Trận", "Thắng", "Hòa", "Thua", "Bàn thắng", "Bàn thua", "Hiệu số", "Điểm"]], height=200)
    else:
        st.write("Chưa có dữ liệu để hiển thị bảng xếp hạng.")

# Tab 4: Thống kê Cá nhân
with tab4:
    st.header("Thống kê Cá nhân")
    if st.session_state.results:
        goal_stats, yellow_stats, red_stats = calculate_player_stats(st.session_state.results)
        
        st.subheader("Cầu thủ Ghi bàn")
        if goal_stats:
            st.dataframe(pd.DataFrame(goal_stats), height=200)
        else:
            st.write("Chưa có cầu thủ ghi bàn.")

        st.subheader("Cầu thủ Nhận Thẻ vàng")
        if yellow_stats:
            st.dataframe(pd.DataFrame(yellow_stats), height=200)
        else:
            st.write("Chưa có cầu thủ nhận thẻ vàng.")

        st.subheader("Cầu thủ Nhận Thẻ đỏ")
        if red_stats:
            st.dataframe(pd.DataFrame(red_stats), height=200)
        else:
            st.write("Chưa có cầu thủ nhận thẻ đỏ.")
    else:
        st.write("Chưa có dữ liệu để hiển thị thống kê.")

# Quản lý dữ liệu
st.header("Quản lý Dữ liệu")
col_save, col_load = st.columns(2)

with col_save:
    if st.button("Lưu Dữ liệu lên Cloud", key="save_data_github"):
        if st.session_state.results:
            json_buffer = io.StringIO()
            json.dump(st.session_state.results, json_buffer, ensure_ascii=False, indent=2)
            file_content = json_buffer.getvalue().encode('utf-8')
            file_path = save_to_github("results.json", file_content)
            st.success(f"Đã lưu results.json lên GitHub (Path: {file_path})!")
        else:
            st.warning("Chưa có dữ liệu để lưu.")

with col_load:
    if st.button("Tải Dữ liệu từ Cloud", key="load_data_github"):
        file_content = load_from_github("results.json")
        if file_content:
            try:
                data = json.loads(file_content.decode('utf-8'))
                if isinstance(data, list) and all(isinstance(item, dict) for item in data):
                    st.session_state.results = data
                    st.success("Đã tải dữ liệu từ GitHub!")
                    st.rerun()
                else:
                    st.error("File JSON không đúng định dạng.")
            except json.JSONDecodeError:
                st.error("Không thể đọc file JSON.")
        else:
            st.error("Không tìm thấy file results.json trên GitHub.")

# Lưu/tải cục bộ
if st.button("Lưu Dữ liệu cục bộ", key="save_data_local"):
    if st.session_state.results:
        json_buffer = io.StringIO()
        json.dump(st.session_state.results, json_buffer, ensure_ascii=False, indent=2)
        st.markdown(get_binary_file_downloader_html(json_buffer.getvalue().encode('utf-8'), "results.json"), unsafe_allow_html=True)
        st.success("Đã tạo link tải file results.json!")
    else:
        st.warning("Chưa có dữ liệu để lưu.")

uploaded_file = st.file_uploader("Tải File Dữ liệu cục bộ (results.json)", type=["json"], key="upload_data")
if uploaded_file is not None:
    try:
        data = json.load(uploaded_file)
        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            st.session_state.results = data
            st.success("Đã tải dữ liệu thành công!")
            st.rerun()
        else:
            st.error("File JSON không đúng định dạng.")
    except json.JSONDecodeError:
        st.error("Không thể đọc file JSON.")

# Xuất file Excel/CSV
st.header("Tải Kết quả và Bảng Xếp hạng")
if st.session_state.results:
    df_results = pd.DataFrame(st.session_state.results)
    
    excel_buffer = io.BytesIO()
    df_results.to_excel(excel_buffer, index=False, engine='xlsxwriter')
    excel_buffer.seek(0)
    st.markdown(get_binary_file_downloader_html(excel_buffer.getvalue(), "football_match_results.xlsx"), unsafe_allow_html=True)

    csv_buffer = io.StringIO()
    df_results.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
    csv_content = csv_buffer.getvalue().encode('utf-8-sig')
    st.markdown(get_binary_file_downloader_html(csv_content, "football_match_results.csv"), unsafe_allow_html=True)

    rankings = calculate_rankings(st.session_state.results)
    df_rankings = pd.DataFrame(rankings)
    excel_buffer_rankings = io.BytesIO()
    df_rankings.to_excel(excel_buffer_rankings, index=False, engine='xlsxwriter')
    excel_buffer_rankings.seek(0)
    st.markdown(get_binary_file_downloader_html(excel_buffer_rankings.getvalue(), "football_rankings.xlsx"), unsafe_allow_html=True)

    csv_buffer_rankings = io.StringIO()
    df_rankings.to_csv(csv_buffer_rankings, index=False, encoding='utf-8-sig')
    csv_content_rankings = csv_buffer_rankings.getvalue().encode('utf-8-sig')
    st.markdown(get_binary_file_downloader_html(csv_content_rankings, "football_rankings.csv"), unsafe_allow_html=True)

    col_export1, col_export2 = st.columns(2)
    with col_export1:
        if st.button("Lưu Kết quả lên GitHub", key="save_results_github"):
            save_to_github("football_match_results.xlsx", excel_buffer.getvalue())
            save_to_github("football_match_results.csv", csv_content)
            st.success("Đã lưu kết quả lên GitHub!")
    with col_export2:
        if st.button("Lưu Bảng Xếp hạng lên GitHub", key="save_rankings_github"):
            save_to_github("football_rankings.xlsx", excel_buffer_rankings.getvalue())
            save_to_github("football_rankings.csv", csv_content_rankings)
            st.success("Đã lưu bảng xếp hạng lên GitHub!")
else:
    st.write("Chưa có dữ liệu để xuất.")
