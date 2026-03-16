import json
from urllib.parse import urlparse

import streamlit as st


st.set_page_config(
    page_title="스포츠 종목 관리 앱",
    page_icon="⚾",
    layout="wide",
)

# -----------------------------
# 스타일
# -----------------------------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .sub-text {
        color: #94a3b8;
        margin-bottom: 1rem;
    }
    .card-title {
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .card-meta {
        color: #94a3b8;
        font-size: 0.92rem;
        margin-bottom: 0.4rem;
    }
    .tag {
        display: inline-block;
        background: #1e293b;
        color: #e2e8f0;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        font-size: 0.82rem;
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

SPORT_EMOJI = {
    "축구": "⚽",
    "농구": "🏀",
    "야구": "⚾",
    "배구": "🏐",
    "테니스": "🎾",
    "e스포츠": "🎮",
    "격투기": "🥊",
    "기타": "🏅",
}

DEFAULT_IMAGE = "https://via.placeholder.com/800x500?text=No+Image"

INITIAL_SPORTS = [
    {
        "id": 1,
        "name": "KBO 리그",
        "category": "야구",
        "league": "KBO",
        "country": "대한민국",
        "image_url": "https://images.unsplash.com/photo-1508344928928-7165b67de128?q=80&w=1200&auto=format&fit=crop",
        "description": "대한민국 프로야구 리그로, 여러 구단이 정규시즌과 포스트시즌을 진행합니다.",
        "favorite": True,
    },
    {
        "id": 2,
        "name": "메이저리그",
        "category": "야구",
        "league": "MLB",
        "country": "미국",
        "image_url": "https://images.unsplash.com/photo-1471295253337-3ceaaedca402?q=80&w=1200&auto=format&fit=crop",
        "description": "미국과 캐나다를 기반으로 운영되는 대표적인 프로야구 리그입니다.",
        "favorite": False,
    },
    {
        "id": 3,
        "name": "프리미어리그",
        "category": "축구",
        "league": "EPL",
        "country": "잉글랜드",
        "image_url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?q=80&w=1200&auto=format&fit=crop",
        "description": "잉글랜드의 최상위 프로축구 리그입니다.",
        "favorite": True,
    },
    {
        "id": 4,
        "name": "NBA",
        "category": "농구",
        "league": "NBA",
        "country": "미국",
        "image_url": "https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=1200&auto=format&fit=crop",
        "description": "미국 프로농구 리그로 세계적으로 가장 높은 인지도를 가지고 있습니다.",
        "favorite": False,
    },
]


def is_valid_url(url: str) -> bool:
    if not url:
        return True
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and bool(result.netloc)
    except Exception:
        return False


def normalize_text(text: str) -> str:
    return " ".join(text.strip().split()).lower()


def next_id() -> int:
    if not st.session_state.sports:
        return 1
    return max(item["id"] for item in st.session_state.sports) + 1


def reset_data() -> None:
    st.session_state.sports = [item.copy() for item in INITIAL_SPORTS]
    st.session_state.editing_id = None


def find_item_by_id(item_id: int):
    for item in st.session_state.sports:
        if item["id"] == item_id:
            return item
    return None


def delete_item(item_id: int) -> None:
    st.session_state.sports = [item for item in st.session_state.sports if item["id"] != item_id]
    if st.session_state.editing_id == item_id:
        st.session_state.editing_id = None


def toggle_favorite(item_id: int) -> None:
    for item in st.session_state.sports:
        if item["id"] == item_id:
            item["favorite"] = not item["favorite"]
            break


if "sports" not in st.session_state:
    st.session_state.sports = [item.copy() for item in INITIAL_SPORTS]

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None


# -----------------------------
# 헤더
# -----------------------------
st.markdown('<div class="main-title">⚾ 스포츠 종목 관리 앱</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">야구 포함 다양한 스포츠 종목을 조회, 검색, 필터, 추가, 수정, 삭제할 수 있는 Streamlit 앱</div>',
    unsafe_allow_html=True,
)
st.divider()

# -----------------------------
# 사이드바 필터
# -----------------------------
with st.sidebar:
    st.header("🔎 검색 / 필터")

    keyword = st.text_input("종목명 검색", placeholder="예: 야구, KBO, NBA")
    category_options = ["전체"] + sorted({item["category"] for item in st.session_state.sports})
    selected_category = st.selectbox("종목 분류", category_options)

    country_keyword = st.text_input("국가 검색", placeholder="예: 대한민국, 미국")
    favorite_only = st.toggle("즐겨찾기만 보기", value=False)

    sort_option = st.selectbox(
        "정렬 방식",
        ["이름 오름차순", "이름 내림차순", "카테고리순", "즐겨찾기 우선"],
    )

    st.divider()
    st.header("🗂 데이터 관리")

    if st.button("초기 데이터로 리셋", use_container_width=True):
        reset_data()
        st.success("데이터를 초기 상태로 되돌렸어.")
        st.rerun()

    st.download_button(
        "현재 데이터 JSON 다운로드",
        data=json.dumps(st.session_state.sports, ensure_ascii=False, indent=2),
        file_name="sports_data.json",
        mime="application/json",
        use_container_width=True,
    )

# -----------------------------
# 상단 메트릭
# -----------------------------
total_count = len(st.session_state.sports)
favorite_count = sum(1 for item in st.session_state.sports if item["favorite"])
category_count = len(set(item["category"] for item in st.session_state.sports))

m1, m2, m3 = st.columns(3)
m1.metric("전체 종목 수", total_count)
m2.metric("즐겨찾기 수", favorite_count)
m3.metric("카테고리 수", category_count)

# -----------------------------
# 데이터 필터링
# -----------------------------
filtered_sports = []
for item in st.session_state.sports:
    match_keyword = keyword.lower() in item["name"].lower() if keyword else True
    match_category = selected_category == "전체" or item["category"] == selected_category
    match_country = country_keyword.lower() in item["country"].lower() if country_keyword else True
    match_favorite = item["favorite"] if favorite_only else True

    if match_keyword and match_category and match_country and match_favorite:
        filtered_sports.append(item)

if sort_option == "이름 오름차순":
    filtered_sports = sorted(filtered_sports, key=lambda x: x["name"])
elif sort_option == "이름 내림차순":
    filtered_sports = sorted(filtered_sports, key=lambda x: x["name"], reverse=True)
elif sort_option == "카테고리순":
    filtered_sports = sorted(filtered_sports, key=lambda x: (x["category"], x["name"]))
elif sort_option == "즐겨찾기 우선":
    filtered_sports = sorted(filtered_sports, key=lambda x: (not x["favorite"], x["name"]))

# -----------------------------
# 탭
# -----------------------------
tab1, tab2, tab3 = st.tabs(["📋 종목 목록", "➕ 종목 추가 / 수정", "🧾 데이터 보기"])

# -----------------------------
# 탭 1: 목록
# -----------------------------
with tab1:
    st.subheader("종목 목록")

    if not filtered_sports:
        st.info("조건에 맞는 종목이 없어.")
    else:
        for i in range(0, len(filtered_sports), 3):
            cols = st.columns(3)
            row_items = filtered_sports[i : i + 3]

            for col, item in zip(cols, row_items):
                with col:
                    with st.container(border=True):
                        emoji = SPORT_EMOJI.get(item["category"], "🏅")
                        favorite_icon = "⭐" if item["favorite"] else "☆"

                        st.image(item["image_url"] or DEFAULT_IMAGE, use_container_width=True)
                        st.markdown(
                            f'<div class="card-title">{emoji} {item["name"]} {favorite_icon}</div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f'<div class="card-meta">{item["league"]} · {item["country"]}</div>',
                            unsafe_allow_html=True,
                        )

                        st.markdown(
                            f'<span class="tag">{item["category"]}</span><span class="tag">{item["league"]}</span>',
                            unsafe_allow_html=True,
                        )

                        st.write(item["description"])

                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if st.button(
                                "즐겨찾기",
                                key=f"fav_{item['id']}",
                                use_container_width=True,
                            ):
                                toggle_favorite(item["id"])
                                st.rerun()

                        with c2:
                            if st.button(
                                "수정",
                                key=f"edit_{item['id']}",
                                use_container_width=True,
                            ):
                                st.session_state.editing_id = item["id"]
                                st.rerun()

                        with c3:
                            if st.button(
                                "삭제",
                                key=f"delete_{item['id']}",
                                use_container_width=True,
                            ):
                                delete_item(item["id"])
                                st.success("삭제 완료")
                                st.rerun()

# -----------------------------
# 탭 2: 추가/수정
# -----------------------------
with tab2:
    editing_item = find_item_by_id(st.session_state.editing_id) if st.session_state.editing_id else None

    if editing_item:
        st.subheader(f"종목 수정 - {editing_item['name']}")
        default_name = editing_item["name"]
        default_category = editing_item["category"]
        default_league = editing_item["league"]
        default_country = editing_item["country"]
        default_image_url = editing_item["image_url"]
        default_description = editing_item["description"]
        default_favorite = editing_item["favorite"]
    else:
        st.subheader("새 종목 추가")
        default_name = ""
        default_category = "야구"
        default_league = ""
        default_country = ""
        default_image_url = ""
        default_description = ""
        default_favorite = False

    with st.form("sport_form", clear_on_submit=False):
        name = st.text_input("종목명", value=default_name, placeholder="예: KBO 리그")
        category = st.selectbox(
            "종목 분류",
            options=list(SPORT_EMOJI.keys()),
            index=list(SPORT_EMOJI.keys()).index(default_category) if default_category in SPORT_EMOJI else 0,
        )
        league = st.text_input("리그명", value=default_league, placeholder="예: KBO, MLB, EPL")
        country = st.text_input("국가", value=default_country, placeholder="예: 대한민국")
        image_url = st.text_input("이미지 URL", value=default_image_url, placeholder="https://...")
        description = st.text_area(
            "설명",
            value=default_description,
            placeholder="해당 종목 또는 리그에 대한 설명을 입력해줘.",
            height=120,
        )
        favorite = st.checkbox("즐겨찾기 등록", value=default_favorite)

        submitted = st.form_submit_button("저장하기", use_container_width=True)

        if submitted:
            clean_name = name.strip()
            clean_league = league.strip()
            clean_country = country.strip()
            clean_description = description.strip()
            final_image = image_url.strip() if image_url.strip() else DEFAULT_IMAGE

            if not clean_name:
                st.error("종목명을 입력해줘.")
            elif not clean_league:
                st.error("리그명을 입력해줘.")
            elif not clean_country:
                st.error("국가를 입력해줘.")
            elif not clean_description:
                st.error("설명을 입력해줘.")
            elif not is_valid_url(final_image):
                st.error("이미지 URL 형식이 올바르지 않아.")
            else:
                duplicate = any(
                    normalize_text(item["name"]) == normalize_text(clean_name)
                    and item["id"] != (editing_item["id"] if editing_item else -1)
                    for item in st.session_state.sports
                )

                if duplicate:
                    st.warning("같은 이름의 종목이 이미 있어.")
                else:
                    if editing_item:
                        editing_item["name"] = clean_name
                        editing_item["category"] = category
                        editing_item["league"] = clean_league
                        editing_item["country"] = clean_country
                        editing_item["image_url"] = final_image
                        editing_item["description"] = clean_description
                        editing_item["favorite"] = favorite
                        st.session_state.editing_id = None
                        st.success("종목 수정 완료")
                    else:
                        st.session_state.sports.append(
                            {
                                "id": next_id(),
                                "name": clean_name,
                                "category": category,
                                "league": clean_league,
                                "country": clean_country,
                                "image_url": final_image,
                                "description": clean_description,
                                "favorite": favorite,
                            }
                        )
                        st.success("종목 추가 완료")

                    st.rerun()

    if editing_item:
        if st.button("수정 취소", use_container_width=True):
            st.session_state.editing_id = None
            st.rerun()

# -----------------------------
# 탭 3: 데이터 보기
# -----------------------------
with tab3:
    st.subheader("현재 데이터")
    st.code(json.dumps(st.session_state.sports, ensure_ascii=False, indent=2), language="json")

    st.download_button(
        "JSON 다운로드",
        data=json.dumps(st.session_state.sports, ensure_ascii=False, indent=2),
        file_name="sports_data.json",
        mime="application/json",
        use_container_width=False,
    )
