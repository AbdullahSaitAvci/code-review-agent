import streamlit as st

from agent.core import review_code
from agent.memory import add_assistant_message, new_session

st.set_page_config(
    page_title="Code Review Agent",
    page_icon="🔍",
    layout="wide",
)

# ── Session state defaults ──────────────────────────────────────────────────
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "messages" not in st.session_state:
    st.session_state.messages = new_session()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Code Review Agent")
    st.caption(
        "Python dosyalarını pylint, flake8 ve AST analiziyle inceleyen "
        "ve Claude API aracılığıyla pedagojik geri bildirim sunan AI agent."
    )
    st.divider()

    uploaded_file = st.file_uploader(
        ".py dosyası yükle",
        type=["py"],
        help="Bir Python dosyası seçin; içeriği otomatik olarak yüklenir.",
    )

    default_code = ""
    if uploaded_file is not None:
        default_code = uploaded_file.read().decode("utf-8", errors="replace")

    code_input = st.text_area(
        "Ya da kodu buraya yapıştır",
        value=default_code,
        height=350,
        placeholder="# Python kodunu buraya yapıştırın...",
    )

    st.divider()
    run_button = st.button("İncele", type="primary", use_container_width=True)

# ── Main panel ───────────────────────────────────────────────────────────────
st.header("İnceleme Sonucu")

if run_button:
    code = code_input.strip()
    if not code:
        st.warning("Lütfen kod girin.")
    else:
        with st.spinner("Agent araçları çalıştırıyor..."):
            result = review_code(code)
        st.session_state.last_result = result
        if result.get("success"):
            add_assistant_message(st.session_state.messages, result["review"])

result = st.session_state.last_result

if result is None:
    st.info("Henüz bir inceleme yapılmadı. Sol panelden kod girin ve **İncele** butonuna basın.")
elif result.get("success"):
    st.markdown(result["review"])

    tools_used = result.get("tools_used", [])
    if tools_used:
        st.divider()
        with st.expander("Kullanılan araçlar", expanded=False):
            for i, tool in enumerate(tools_used, 1):
                st.write(f"{i}. `{tool}`")
else:
    st.error(f"Hata: {result.get('error', 'Bilinmeyen hata.')}")
    tools_used = result.get("tools_used", [])
    if tools_used:
        with st.expander("Hata öncesi kullanılan araçlar", expanded=False):
            for i, tool in enumerate(tools_used, 1):
                st.write(f"{i}. `{tool}`")
