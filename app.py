import importlib

import streamlit as st

from agent.memory import add_assistant_message, new_session

_MODEL_CONFIGS: dict[str, dict] = {
    "Claude Sonnet 4.6":                {"module": "agent.core",            "model": "claude-sonnet-4-6",                       "free": False},
    "Claude Sonnet 4.5":                {"module": "agent.core",            "model": "claude-sonnet-4-5-20250514",              "free": False},
    "Claude Haiku 4.5":                 {"module": "agent.core",            "model": "claude-haiku-4-5-20251001",               "free": False},
    "NVIDIA Nemotron Super (Free)":     {"module": "agent.openrouter_core", "model": "nvidia/nemotron-3-super-120b-a12b:free",  "free": True},
    "GPT-OSS 120B (Free)":              {"module": "agent.openrouter_core", "model": "openai/gpt-oss-120b:free",               "free": True},
    "Gemma 4 31B (Free)":               {"module": "agent.openrouter_core", "model": "google/gemma-4-31b-it:free",             "free": True},
    "Llama 3.3 70B (Free)":             {"module": "agent.openrouter_core", "model": "meta-llama/llama-3.3-70b-instruct:free", "free": True},
    "OpenRouter Free (Auto)":           {"module": "agent.openrouter_core", "model": "openrouter/free",                        "free": True},
}

_PROVIDER_META: dict[str, dict] = {
    "agent.core":            {"label": "Anthropic",  "bg": "#1a56db", "fg": "#ffffff"},
    "agent.groq_core":       {"label": "Groq",       "bg": "#f97316", "fg": "#ffffff"},
    "agent.openrouter_core": {"label": "OpenRouter", "bg": "#16a34a", "fg": "#ffffff"},
}

_MODEL_LIST = list(_MODEL_CONFIGS.keys())


def _quality_score_html(tools_used: list[str]) -> str:
    """Return HTML for the Kod Kalite Skoru widget."""
    count = sum(1 for t in tools_used if t == "update_user_profile")
    score = max(0, round(10 - count * 1.5))
    if score >= 7:
        color, bg = "#16a34a", "#052e16"
    elif score >= 4:
        color, bg = "#ca8a04", "#1c1a08"
    else:
        color, bg = "#dc2626", "#1c0606"
    return (
        f'<div style="display:inline-flex;align-items:center;gap:14px;'
        f'background:{bg};border:1.5px solid {color};border-radius:10px;padding:12px 20px;">'
        f'<span style="color:#94a3b8;font-size:0.75rem;font-weight:700;'
        f'letter-spacing:0.06em;text-transform:uppercase;">Kod Kalite Skoru</span>'
        f'<span style="color:{color};font-size:1.8rem;font-weight:800;line-height:1;">{score}'
        f'<span style="font-size:0.95rem;font-weight:500;color:#64748b;">/10</span></span>'
        f'</div>'
    )


st.set_page_config(
    page_title="Code Review Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ────────────────────────────────────────────────────
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "messages" not in st.session_state:
    st.session_state.messages = new_session()
if "last_model" not in st.session_state:
    st.session_state.last_model = None
if "selected_model" not in st.session_state:
    st.session_state.selected_model = _MODEL_LIST[0]

if st.session_state.selected_model not in _MODEL_CONFIGS:
    st.session_state.selected_model = _MODEL_LIST[0]

selected_model = st.session_state.selected_model
cfg_active = _MODEL_CONFIGS[selected_model]
prov_active = _PROVIDER_META.get(cfg_active["module"], {"label": "?", "bg": "#6b7280", "fg": "#fff"})

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { min-width: 320px; max-width: 320px; }

    .main .block-container {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem 2.5rem 2.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        margin-top: 0.75rem;
    }
    .main .block-container h1 { font-size: 1.2rem !important; }
    .main .block-container h2 { font-size: 1.05rem !important; }
    .main .block-container h3 { font-size: 0.95rem !important; }

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

    section[data-testid="stSidebar"] > div:first-child { padding-top: 0; }
    button[data-testid="baseButton-headerNoPadding"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    </style>
    """,
    unsafe_allow_html=True,
)

# ── Gradient header ───────────────────────────────────────────────────────────
_prov_badge = (
    f'<span style="background:{prov_active["bg"]};color:{prov_active["fg"]};'
    f'padding:3px 12px;border-radius:999px;font-size:0.76rem;font-weight:700;">'
    f'{prov_active["label"]}</span>'
)
_free_badge = (
    '<span style="background:#16a34a;color:#fff;padding:3px 10px;border-radius:999px;'
    'font-size:0.73rem;font-weight:700;">Ücretsiz</span>'
    if cfg_active.get("free") else
    '<span style="background:#e85d04;color:#fff;padding:3px 10px;border-radius:999px;'
    'font-size:0.73rem;font-weight:700;">Ücretli</span>'
)

st.markdown(
    f"""
    <div style="
        background: linear-gradient(90deg, #185fa5 0%, #533ab7 100%);
        border-radius: 12px;
        padding: 20px 28px;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 20px rgba(83,58,183,0.28);
    ">
        <div>
            <div style="font-size:1.45rem;font-weight:800;color:#ffffff;
                        letter-spacing:-0.02em;line-height:1.1;">
                🔍 Code Review Agent
            </div>
            <div style="color:#c7d2fe;font-size:0.8rem;margin-top:5px;">
                AI destekli çok dilli kod analizi · Python · JavaScript · Java · ve daha fazlası
            </div>
        </div>
        <div style="display:flex;flex-wrap:wrap;gap:7px;align-items:center;justify-content:flex-end;">
            {_prov_badge}
            {_free_badge}
            <span style="color:#c7d2fe;font-size:0.75rem;max-width:180px;
                         text-align:right;line-height:1.2;">{selected_model}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.selectbox(
        "Model Seç",
        options=list(_MODEL_CONFIGS.keys()),
        index=_MODEL_LIST.index(selected_model),
        key="selected_model",
    )
    free_text = "Ücretsiz" if cfg_active.get("free") else "Ücretli"
    free_bg = "#16a34a" if cfg_active.get("free") else "#e85d04"
    st.markdown(
        f'<span style="background:{prov_active["bg"]};color:{prov_active["fg"]};'
        f'padding:2px 10px;border-radius:999px;font-size:0.72rem;font-weight:700;">'
        f'{prov_active["label"]}</span>'
        f'&nbsp;&nbsp;'
        f'<span style="background:{free_bg};color:#fff;'
        f'padding:2px 10px;border-radius:999px;font-size:0.72rem;font-weight:700;">'
        f'{free_text}</span>',
        unsafe_allow_html=True,
    )

    st.divider()

    _LANG_MAP = {
        "py": "python", "js": "javascript", "ts": "typescript",
        "java": "java", "cpp": "cpp", "c": "c", "cs": "csharp",
        "go": "go", "rb": "ruby",
    }
    uploaded_file = st.file_uploader(
        "Kod dosyası yükle",
        type=["py", "js", "ts", "java", "cpp", "c", "cs", "go", "rb"],
        help="Bir kod dosyası seçin; içeriği otomatik olarak yüklenir.",
    )
    default_code = ""
    upload_language = "python"
    if uploaded_file is not None:
        ext = uploaded_file.name.rsplit(".", 1)[-1].lower()
        upload_language = _LANG_MAP.get(ext, "python")
        default_code = uploaded_file.read().decode("utf-8", errors="replace")

    code_input = st.text_area(
        "Ya da kodu buraya yapıştır",
        value=default_code,
        height=350,
        placeholder="# Kodunuzu buraya yapıştırın (Python, JavaScript, Java, C++ ...)",
    )

    st.divider()
    run_button = st.button("İncele", type="primary", use_container_width=True)

# ── Review logic ──────────────────────────────────────────────────────────────
if run_button:
    code = code_input.strip()
    if not code:
        st.warning("Lütfen kod girin.")
    else:
        cfg = _MODEL_CONFIGS[selected_model]
        review_code = importlib.import_module(cfg["module"]).review_code
        kwargs: dict = {"language": upload_language}
        if "model" in cfg:
            kwargs["model"] = cfg["model"]
        with st.spinner("Agent araçları çalıştırıyor..."):
            result = review_code(code, **kwargs)
        st.session_state.last_result = result
        st.session_state.last_model = selected_model
        if result.get("success"):
            add_assistant_message(st.session_state.messages, result["review"])

result = st.session_state.last_result

if result is None:
    st.info("Henüz bir inceleme yapılmadı. Sol panelden kod girin ve **İncele** butonuna basın.")
elif result.get("success"):
    tools_used = result.get("tools_used", [])

    # ── Kod Kalite Skoru ─────────────────────────────────────────────────────
    st.markdown(_quality_score_html(tools_used), unsafe_allow_html=True)

    st.divider()
    st.markdown(result["review"])

    # ── Tool chips ───────────────────────────────────────────────────────────
    if tools_used:
        st.divider()
        st.caption("Kullanılan araçlar")
        chips = " ".join(f'<span class="tool-chip">🔧 {t}</span>' for t in tools_used)
        st.markdown(chips, unsafe_allow_html=True)
else:
    error_msg = result.get("error", "Bilinmeyen hata.")
    if "429" in str(error_msg) or "rate" in str(error_msg).lower():
        st.warning("⏳ Bu model şu an meşgul veya günlük limit doldu. Lütfen başka bir model deneyin veya yarın tekrar deneyin.")
    else:
        st.error(f"Hata: {error_msg}")
    tools_used = result.get("tools_used", [])
    if tools_used:
        st.caption("Hata öncesi kullanılan araçlar")
        chips = " ".join(f'<span class="tool-chip">🔧 {t}</span>' for t in tools_used)
        st.markdown(chips, unsafe_allow_html=True)
