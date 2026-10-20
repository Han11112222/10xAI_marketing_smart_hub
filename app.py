import streamlit as st
import pandas as pd

# --------------------------------------------------------------------------
# 1. 디자인 설정
# --------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="10x AI_ Marketing Smart Hub")

st.markdown("""
<style>
    body { font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; color: #333; }

    .main-title {
        font-size: 28px; font-weight: 800; margin-bottom: 30px;
        color: #2c3e50; display: flex; align-items: center; gap: 10px;
    }

    .section-header {
        font-size: 18px; font-weight: 700; color: #1e40af;
        margin-top: 50px; margin-bottom: 10px;
        display: flex; align-items: center; gap: 8px;
    }

    .divider-top { border-top: 2px solid #1e40af; margin-bottom: 0; }

    /* 컬럼 제목줄 스타일 (회색 배경) */
    .list-header {
        display: flex; justify-content: space-between; align-items: center;
        padding: 10px 10px;
        background-color: #f8f9fa;
        border-bottom: 2px solid #e9ecef;
        font-weight: 700; color: #555; font-size: 14px;
    }

    /* 리스트 데이터 줄 */
    .list-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 15px 10px; border-bottom: 1px solid #e5e7eb;
    }
    .list-row:hover { background-color: #fdfdfd; }

    /* 각 영역 비율 (헤더와 내용의 줄이 맞아야 함) */
    .content-area { flex: 3; font-size: 15px; }
    .content-title { font-weight: 700; margin-right: 5px; }
    .content-desc { color: #555; font-size: 14px; }

    .star-rating { flex: 0.5; text-align: center; font-size: 14px; letter-spacing: 2px; color: #333; }

    .link-area { flex: 0.5; text-align: center; }

    .link-btn {
        display: inline-block; padding: 6px 20px;
        border: 1px solid #d1d5db; border-radius: 6px;
        background-color: white; text-decoration: none; color: #555;
        font-size: 13px; transition: background-color 0.2s;
    }
    .link-btn:hover { background-color: #f3f4f6; }

    .folder-icon { color: #fbbf24; }
    .alert-box { padding: 10px; background-color: #fff3cd; color: #856404; border: 1px solid #ffeeba; border-radius: 5px; margin-bottom: 20px; font-size: 14px;}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# 2. 데이터 로드 및 청소
# --------------------------------------------------------------------------
SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1Fv6w0QM7xXMMo85q-uLq2INbDSodM9AshbalxVifhdI/export?format=csv&gid=0"
)


@st.cache_data(ttl=60)  # 60초마다 시트를 새로 읽어옴 (시트 수정 시 자동 반영)
def get_data():
    backup_data = [
        {"구분": "Study", "내용": "샘플 데이터", "기능": "엑셀 연결 필요", "활용도": 5, "링크": "#"}
    ]

    try:
        # 헤더 위치를 찾기 위해 먼저 header=None 으로 읽습니다.
        raw = pd.read_csv(SHEET_URL, header=None)

        header_idx = -1
        for i, row in raw.iterrows():
            row_str = " ".join([str(val) for val in row])
            if "구분" in row_str and "내용" in row_str:
                header_idx = i
                break

        if header_idx == -1:
            return pd.DataFrame(backup_data), "⚠️ 스프레드시트 형식이 맞지 않습니다. ('구분', '내용' 헤더 없음)"

        df = pd.read_csv(SHEET_URL, header=header_idx)
        df = df.fillna("")
        df.columns = [c.strip() if isinstance(c, str) else c for c in df.columns]

        # 불필요한 헤더 행 제거
        if '내용' in df.columns:
            trash_words = ['상세분류', '구분', '내용', '기능', '활용도']
            df = df[~df['내용'].isin(trash_words)]
            df = df[df['내용'] != ""]

        # 병합 셀로 비어있는 '구분'은 위 값으로 채우기
        if '구분' in df.columns:
            df['구분'] = df['구분'].replace("", pd.NA).ffill()

        return df, None

    except Exception as e:
        return pd.DataFrame(backup_data), f"⚠️ 에러 발생: {e}"


# --------------------------------------------------------------------------
# 3. 화면 그리기
# --------------------------------------------------------------------------
st.markdown('<div class="main-title">🚀 10x AI_마케팅 스마트 허브</div>', unsafe_allow_html=True)

df, alert_msg = get_data()

if alert_msg:
    st.markdown(f'<div class="alert-box">{alert_msg}</div>', unsafe_allow_html=True)

if not df.empty:
    if '구분' in df.columns:
        categories = df['구분'].unique()
        for category in categories:
            if not category or pd.isna(category):
                continue

            # 1. 섹션 헤더
            st.markdown(f"""
                <div class="section-header"><span class="folder-icon">📂</span> {category}</div>
                <div class="divider-top"></div>
            """, unsafe_allow_html=True)

            # 2. 컬럼 헤더 (내용 | 활용도 | 링크)
            st.markdown("""
            <div class="list-header">
                <div class="content-area" style="padding-left: 5px;">내용</div>
                <div class="star-rating">활용도</div>
                <div class="link-area">링크</div>
            </div>
            """, unsafe_allow_html=True)

            # 3. 데이터 리스트 출력
            section_data = df[df['구분'] == category]
            for _, row in section_data.iterrows():
                title = row.get('내용', row.get('Title', ''))
                if not title or title in ['상세분류', '구분']:
                    continue

                desc = row.get('기능', row.get('설명', ''))
                stars_val = row.get('활용도', row.get('별점', 0))
                link = row.get('링크', row.get('Link', '#'))
                if not link:
                    link = "#"

                try:
                    if isinstance(stars_val, str) and "★" in stars_val:
                        stars = stars_val
                    else:
                        stars = "★" * int(float(stars_val)) if stars_val else "☆☆☆☆☆"
                except Exception:
                    stars = "☆☆☆☆☆"

                st.markdown(f"""
                <div class="list-row">
                    <div class="content-area">
                        <span class="content-title">{title}</span>
                        <span class="content-desc">{desc}</span>
                    </div>
                    <div class="star-rating" style="color:#f59e0b;">{stars}</div>
                    <div class="link-area"><a href="{link}" target="_blank" class="link-btn">Link 🔗</a></div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom: 40px;'></div>", unsafe_allow_html=True)
