import streamlit as st
import openai
import re
from PIL import Image
import os

# API 키 설정
openai.api_key = os.getenv("OPENAI_API_KEY")

# GPT 요약 함수 (신규 버전 대응)
def summarize_notice(text):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "공지 내용을 요약해줘. 날짜, 장소, 제출, 링크, 주의사항이 있으면 항목별로 구분해줘. 각 항목이 없으면 '❌ 명시되지 않음'이라고 적어줘."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )
    summary = response.choices[0].message.content
    return {
        "요약": summary,
        "날짜": extract_field(summary, "날짜"),
        "장소": extract_field(summary, "장소"),
        "제출": extract_field(summary, "제출"),
        "링크": extract_links(text),
        "주의": extract_field(summary, "주의")
    }

# 항목 추출 함수
def extract_field(text, label):
    pattern = rf"{label}[:：]?\s*(.+)"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "❌ 명시되지 않음"

# 링크 추출 함수
def extract_links(text):
    url_pattern = r"https?://[^\s]+"
    urls = re.findall(url_pattern, text)
    return urls if urls else ["❌ 명시되지 않음"]

# Streamlit UI
st.title("📢 카카오톡 공지 요약기")
st.markdown("공지 텍스트를 입력하면 GPT가 항목별로 요약해줍니다.")

text_input = st.text_area("📄 공지 텍스트 입력", height=200)

uploaded_image = st.file_uploader("🖼 공지 이미지 업로드 (선택)", type=["png", "jpg", "jpeg"])
if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="첨부된 이미지", use_column_width=True)

if st.button("🤖 요약하기"):
    if text_input.strip() == "":
        st.warning("공지 텍스트를 입력해주세요.")
    else:
        try:
            result = summarize_notice(text_input)
            st.markdown("### ✅ 요약 결과")
            st.markdown(f"**📌 요약:** {result['요약']}")
            st.markdown(f"**🗓 날짜:** {result['날짜']}")
            st.markdown(f"**📍 장소:** {result['장소']}")
            st.markdown(f"**📝 제출:** {result['제출']}")
            if result["링크"] and result["링크"][0] != "❌ 명시되지 않음":
                for url in result["링크"]:
                    st.markdown(f"[📎 링크 바로가기]({url})")
            else:
                st.markdown("📎 링크: ❌ 명시되지 않음")
            st.markdown(f"**⚠ 주의:** {result['주의']}")
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
