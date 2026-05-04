import importlib

import streamlit as st

from agent.memory import add_assistant_message, new_session

_MODEL_CONFIGS: dict[str, dict] = {
    "Claude (Sonnet 4.6)":            {"module": "agent.core",            "model": "claude-sonnet-4-6"},
    "Claude Sonnet 4.5":              {"module": "agent.core",            "model": "claude-sonnet-4-5-20250514"},
    "Claude Haiku 4.5":               {"module": "agent.core",            "model": "claude-haiku-4-5-20251001"},
    "NVIDIA Nemotron Super (Free)":   {"module": "agent.openrouter_core", "model": "nvidia/nemotron-3-super-120b-a12b:free"},
    "GPT-OSS 120B (Free)":            {"module": "agent.openrouter_core", "model": "openai/gpt-oss-120b:free"},
    "NVIDIA Nemotron Nano 30B (Free)":{"module": "agent.openrouter_core", "model": "nvidia/nemotron-3-nano-30b-a3b:free"},
    "Gemma 4 31B (Free)":             {"module": "agent.openrouter_core", "model": "google/gemma-4-31b-it:free"},
    "Llama 3.3 70B (Free)":           {"module": "agent.openrouter_core", "model": "meta-llama/llama-3.3-70b-instruct:free"},
    "OpenRouter Free (Auto)":         {"module": "agent.openrouter_core", "model": "openrouter/free"},
    "Groq (Llama 3.3 70B)":           {"module": "agent.groq_core"},
}

_PROVIDER_META: dict[str, dict] = {
    "agent.core":            {"label": "Anthropic",   "bg": "#1a56db", "fg": "#ffffff"},
    "agent.groq_core":       {"label": "Groq",        "bg": "#f97316", "fg": "#ffffff"},
    "agent.openrouter_core": {"label": "OpenRouter",  "bg": "#16a34a", "fg": "#ffffff"},
}


def _provider_badge(module: str) -> str:
    """Return an HTML badge string for the given module's provider."""
    meta = _PROVIDER_META.get(module, {"label": module, "bg": "#6b7280", "fg": "#ffffff"})
    return (
        f'<span style="background:{meta["bg"]};color:{meta["fg"]};'
        f'padding:2px 10px;border-radius:12px;font-size:0.75rem;'
        f'font-weight:600;letter-spacing:0.03em;">'
        f'{meta["label"]}</span>'
    )


st.set_page_config(
    page_title="Code Review Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { min-width: 320px; max-width: 320px; }
    [data-testid="stSidebar"] .stSelectbox { width: 100% !important; }

    /* Main panel card */
    .main .block-container {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 2rem 2.5rem 2.5rem;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
        margin-top: 0.75rem;
    }

    /* Review içindeki başlıkları küçült */
    .main .block-container h1 { font-size: 1.2rem !important; }
    .main .block-container h2 { font-size: 1.05rem !important; }
    .main .block-container h3 { font-size: 0.95rem !important; }

    /* Tool chips — dark theme */
    .tool-chip {
        display: inline-block;
        background: #1e293b;
        color: #94a3b8;
        border: 1px solid #334155;
        border-radius: 999px;
        padding: 2px 12px;
        font-size: 0.8rem;
        font-family: monospace;
        font-weight: 500;
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Session state defaults ──────────────────────────────────────────────────
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "messages" not in st.session_state:
    st.session_state.messages = new_session()
if "last_model" not in st.session_state:
    st.session_state.last_model = None

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Code Review Agent")
    st.caption(
        "Python dosyalarını pylint, flake8 ve AST analiziyle inceleyen "
        "ve Claude API aracılığıyla pedagojik geri bildirim sunan AI agent."
    )
    st.divider()

    selected_model = st.selectbox(
        "Model Seç",
        options=list(_MODEL_CONFIGS.keys()),
        index=0,
    )

    # Provider badge
    cfg_preview = _MODEL_CONFIGS[selected_model]
    st.markdown(
        f'Sağlayıcı:&nbsp;&nbsp;{_provider_badge(cfg_preview["module"])}',
        unsafe_allow_html=True,
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
st.header("🔍 İnceleme Sonucu", anchor=False)
st.caption("AI destekli statik analiz ve pedagojik geri bildirim")
st.markdown(
    '<hr style="border:none;border-top:2px solid #1a56db;margin:0.1rem 0 1.25rem;">',
    unsafe_allow_html=True,
)

if run_button:
    code = code_input.strip()
    if not code:
        st.warning("Lütfen kod girin.")
    else:
        cfg = _MODEL_CONFIGS[selected_model]
        review_code = importlib.import_module(cfg["module"]).review_code
        kwargs = {"model": cfg["model"]} if "model" in cfg else {}
        with st.spinner("Agent araçları çalıştırıyor..."):
            result = review_code(code, **kwargs)
        st.session_state.last_result = result
        st.session_state.last_model = selected_model
        if result.get("success"):
            add_assistant_message(st.session_state.messages, result["review"])

result = st.session_state.last_result
last_model = st.session_state.last_model

if result is None:
    st.info("Henüz bir inceleme yapılmadı. Sol panelden kod girin ve **İncele** butonuna basın.")
elif result.get("success"):
    # ── Metrics row ─────────────────────────────────────────────────────────
    tools_used = result.get("tools_used", [])
    mcol1, mcol2, mcol3 = st.columns(3)
    with mcol1:
        st.caption("Kullanılan Araç")
        st.write(f"**{len(tools_used)}**")
    with mcol2:
        st.caption("Model")
        st.write(f"**{last_model or selected_model}**")
    with mcol3:
        if last_model:
            mod = _MODEL_CONFIGS[last_model]["module"]
            provider_label = _PROVIDER_META.get(mod, {}).get("label", "—")
            st.caption("Sağlayıcı")
            st.write(f"**{provider_label}**")

    st.divider()
    st.markdown(result["review"])

    # ── Tool chips ───────────────────────────────────────────────────────────
    if tools_used:
        st.divider()
        st.caption("Kullanılan araçlar")
        chips = " ".join(f'<span class="tool-chip">🔧 {t}</span>' for t in tools_used)
        st.markdown(chips, unsafe_allow_html=True)
else:
    st.error(f"Hata: {result.get('error', 'Bilinmeyen hata.')}")
    tools_used = result.get("tools_used", [])
    if tools_used:
        st.caption("Hata öncesi kullanılan araçlar")
        chips = " ".join(f'<span class="tool-chip">🔧 {t}</span>' for t in tools_used)
        st.markdown(chips, unsafe_allow_html=True)
