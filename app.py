import streamlit as st
import pandas as pd

# --------------------------------------------------------------------------
# 0. 설정값
# --------------------------------------------------------------------------
# 리스트 영역에 회색 배경을 줄 섹션 이름 (시트의 '구분' 값과 동일해야 함). 여러 개도 가능.
HIGHLIGHT_CATEGORIES = ["Key Support"]

SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1Fv6w0QM7xXMMo85q-uLq2INbDSodM9AshbalxVifhdI/export?format=csv&gid=0"
)

# --------------------------------------------------------------------------
# 1. 디자인 설정
# --------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="10x AI _ Smart Marketing Hub")

st.markdown("""
<style>
    body { font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif; color: #333; }

    .main-title {
        font-size: 28px; font-weight: 800; margin-bottom: 30px;
        color: #2c3e50; display: flex; align-items: center; gap: 10px;
    }

    /* 섹션 전체 */
    .section-wrap { margin-top: 50px; margin-bottom: 40px; }

    /* 섹션 제목 (연한 푸른색 하이라이트) */
    .section-header {
        font-size: 18px; font-weight: 700; color: #1e40af;
        margin-bottom: 0; padding: 10px 14px;
        background-color: #e0ecff;
        border-radius: 8px 8px 0 0;
        display: flex; align-items: center; gap: 8px;
    }

    .divider-top { border-top: 2px solid #1e40af; margin-bottom: 0; }

    /* 리스트 전체 영역 (강조 섹션은 연한 회색 배경) */
    .list-box.highlight {
        background-color: #f1f3f5;
        border-radius: 0 0 8px 8px;
        padding-bottom: 6px;
    }
    .list-box.highlight .list-header { background-color: #e5e7eb; }
    .list-box.highlight .list-row { border-bottom: 1px solid #dee2e6; }
    .list-box.highlight .list-row:hover { background-color: #f8f9fa; }

    /* 컬럼 제목줄 */
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
@st.cache_data(ttl=60)  # 60초마다 시트를 새로 읽어옴 (시트 수정 시 자동 반영)
def get_data():
    backup_data = [
        {"구분": "Study", "내용": "샘플 데이터", "기능": "엑셀 연결 필요", "활용도": 5, "링크": "#"}
    ]

    try:
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

        if '내용' in df.columns:
            trash_words = ['상세분류', '구분', '내용', '기능', '활용도']
            df = df[~df['내용'].isin(trash_words)]
            df = df[df['내용'] != ""]

        if '구분' in df.columns:
            df['구분'] = df['구분'].replace("", pd.NA).ffill()

        return df, None

    except Exception as e:
        return pd.DataFrame(backup_data), f"⚠️ 에러 발생: {e}"


# --------------------------------------------------------------------------
# 3. 화면 그리기
# --------------------------------------------------------------------------
st.markdown('<div class="main-title">🚀 10x AI _ Smart Marketing Hub</div>', unsafe_allow_html=True)

df, alert_msg = get_data()

if alert_msg:
    st.markdown(f'<div class="alert-box">{alert_msg}</div>', unsafe_allow_html=True)

if not df.empty and '구분' in df.columns:
    for category in df['구분'].unique():
        if not category or pd.isna(category):
            continue

        # 섹션 하나를 HTML 한 덩어리로 출력해야 리스트 전체에 배경색이 적용됩니다.
        # (들여쓰기/빈 줄이 있으면 마크다운이 코드블록으로 오인하므로 이어 붙임)
        rows_html = [
            '<div class="list-header">'
            '<div class="content-area" style="padding-left: 5px;">내용</div>'
            '<div class="star-rating">활용도</div>'
            '<div class="link-area">링크</div>'
            '</div>'
        ]

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

            rows_html.append(
                '<div class="list-row">'
                '<div class="content-area">'
                f'<span class="content-title">{title}</span>'
                f'<span class="content-desc">{desc}</span>'
                '</div>'
                f'<div class="star-rating" style="color:#f59e0b;">{stars}</div>'
                f'<div class="link-area"><a href="{link}" target="_blank" class="link-btn">Link 🔗</a></div>'
                '</div>'
            )

        box_class = "list-box highlight" if category in HIGHLIGHT_CATEGORIES else "list-box"
        st.markdown(
            '<div class="section-wrap">'
            f'<div class="section-header"><span class="folder-icon">📂</span> {category}</div>'
            '<div class="divider-top"></div>'
            f'<div class="{box_class}">{"".join(rows_html)}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
