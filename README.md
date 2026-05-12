# Code Review Agent

Çok dilli kod dosyalarını gerçek statik analiz araçlarıyla inceleyen ve Claude API'nin **tool use** özelliği aracılığıyla pedagojik geri bildirim sunan AI agent uygulaması.

## Özellikler

- Kod dosyası yükleme veya kodu doğrudan yapıştırma
- **Çok dilli destek** — Python, JavaScript, TypeScript, Java, C++, Go, Ruby
- **pylint** ve **flake8** ile otomatik statik analiz
- **AST** tabanlı karmaşıklık ölçümü (fonksiyon uzunluğu, iç içe geçme derinliği)
- Oturumlar arası kalıcı kullanıcı profili — tekrar eden hatalara odaklanır
- Streamlit tabanlı sade web arayüzü
- Native Anthropic SDK tool use döngüsü (wrapper kütüphane yok)

## Desteklenen Diller

| Dil | Uzantı |
|-----|--------|
| Python | `.py` |
| JavaScript | `.js` |
| TypeScript | `.ts` |
| Java | `.java` |
| C++ | `.cpp`, `.cc`, `.h` |
| Go | `.go` |
| Ruby | `.rb` |

## Kurulum

### 1. Depoyu klonla

```bash
git clone <repo-url>
cd code-review-agent
```

### 2. Sanal ortam oluştur ve etkinleştir

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Bağımlılıkları yükle

```bash
pip install -r requirements.txt
```

### 4. `.env` dosyasını oluştur

```bash
cp .env.example .env
```

`.env` dosyasını aç ve API anahtarlarını gir:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
```

`OPENROUTER_API_KEY` yalnızca OpenRouter modelleri kullanılacaksa gereklidir.

## Çalıştırma

```bash
streamlit run app.py
```

Tarayıcıda `http://localhost:8501` adresi otomatik açılır.

## Proje Yapısı

```
code-review-agent/
├── app.py                  # Streamlit UI giriş noktası
├── requirements.txt
├── .env.example
├── agent/
│   ├── __init__.py
│   ├── core.py             # Agentic loop — Claude API çağrısı + tool execution
│   ├── tools.py            # Tool şemaları ve Python implementasyonları
│   ├── prompts.py          # System prompt metinleri
│   └── memory.py           # Session history yönetimi
├── data/
│   └── user_profile.json   # Oturumlar arası kalıcı kullanıcı profili
└── tests/
```

## Desteklenen Modeller

| Model | Sağlayıcı |
|-------|-----------|
| Claude Sonnet 4.6 | Anthropic |
| Claude Sonnet 4.5 | Anthropic |
| Claude Haiku 4.5 | Anthropic |
| NVIDIA Nemotron Super (Free) | OpenRouter |
| GPT-OSS 120B (Free) | OpenRouter |
| Gemma 4 31B (Free) | OpenRouter |
| Llama 3.3 70B (Free) | OpenRouter |
| OpenRouter Free (Auto) | OpenRouter |

## Kullanılan Teknolojiler

| Teknoloji | Sürüm | Amaç |
|-----------|-------|------|
| Python | 3.11+ | Dil |
| [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) | ≥ 0.40 | Claude API + tool use |
| Streamlit | ≥ 1.40 | Web arayüzü |
| pylint | ≥ 3.2 | Statik analiz |
| flake8 | ≥ 7.1 | Stil ve hata denetimi |
| python-dotenv | ≥ 1.0 | API key yönetimi |
| pytest | ≥ 8.0 | Test altyapısı |

## Agent Mimarisi

```
Kullanıcı girdisi
      │
      ▼
 agent/core.py  ──►  Claude API (claude-sonnet-4-6)
      │                      │
      │          ┌───────────┘  stop_reason == "tool_use"
      │          │
      │          ▼
      │     Tool dispatch
      │     ├── read_python_file      — dosyayı okur
      │     ├── run_static_analysis   — pylint + flake8 çalıştırır
      │     ├── analyze_complexity    — AST ile karmaşıklık hesaplar
      │     ├── get_user_profile      — geçmiş hata istatistiklerini okur
      │     └── update_user_profile   — tekrar eden hata sayacını günceller
      │          │
      │          └──► Sonuç Claude'a geri beslenir
      │
      └──► stop_reason == "end_turn"  →  Markdown inceleme raporu
```

`core.py` içindeki döngü, Claude `end_turn` dönene veya maksimum iterasyon sayısına (`_MAX_ITERATIONS = 20`) ulaşana kadar tool çağrısı → sonuç → yeni istek döngüsünü sürdürür. System prompt prompt caching ile korunur; her iterasyonda önbelleğe alınan token maliyeti sıfıra yakındır.
