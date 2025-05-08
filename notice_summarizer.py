import streamlit as st
import re
from PIL import Image
import openai

# ✅ Streamlit Cloud의 Secrets에서 API 키 불러오기
openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_section(text, heading):
    for line in text.splitlines():
        if line.startswith(heading):
            return line.replace(heading, "").strip()
    return "❌ 명시되지 않음"

def extract_links(text):
    url_pattern = r"https?://[^\s]+"
    urls = re.findall(url_pattern, text)
    return urls if urls else ["❌ 명시되지 않음"]

def summarize_notice(text):
    system_prompt = """
다음 공지 내용을 요약하고, 공지 안에 포함된 중요한 정보를 항목별로 정리해줘.

다음 항목을 포함하되, 공지에 없으면 '❌ 명시되지 않음'이라고 표시해줘:
- 날짜/시간
- 장소
- 제출 방법 또는 대상
- 링크(URL)
- 기타 주의 사항

출력 형식은 다음처럼 통일해줘:

📌 요약:  
🗓 날짜:  
📍 장소:  
📝 제출:  
📎 링크:  
⚠ 주의:

간결하고 포스터처럼 보기 좋게 정리해줘.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": text}
        ],
        temperature=0.2
    )

    reply = response["choices"][0]["message"]["content"]

    return {
        "요약": extract_section(reply, "📌 요약:"),
        "날짜": extract_section(reply, "🗓 날짜:"),
        "장소": extract_section(reply, "📍 장소:"),
        "제출": extract_section(reply, "📝 제출:"),
        "링크": extract_links(text),
        "주의": extract_section(reply, "⚠ 주의:")
    }

st.title("📢 카카오톡 공지 요약기")
st.markdown("텍스트 공지와 이미지를 입력하면 GPT가 항목별로 요약해줍니다.")

text_input = st.text_area("📄 공지 텍스트를 입력하세요", height=200)

uploaded_image = st.file_uploader("🖼 공지 이미지 업로드 (선택)", type=["png", "jpg", "jpeg"])
if uploaded_image:
    image = Image.open(uploaded_image)
    st.image(image, caption="첨부된 이미지", use_column_width=True)

if st.button("🤖 요약하기"):
    if text_input.strip() == "":
        st.warning("공지 텍스트를 입력해주세요.")
    else:
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
