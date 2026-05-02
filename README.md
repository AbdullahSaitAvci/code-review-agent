# Code Review Agent

Python dosyalarını gerçek statik analiz araçlarıyla inceleyen ve Claude API'nin **tool use** özelliği aracılığıyla pedagojik geri bildirim sunan AI agent uygulaması.

## Özellikler

- `.py` dosyası yükleme veya kodu doğrudan yapıştırma
- **pylint** ve **flake8** ile otomatik statik analiz
- **AST** tabanlı karmaşıklık ölçümü (fonksiyon uzunluğu, iç içe geçme derinliği)
- Oturumlar arası kalıcı kullanıcı profili — tekrar eden hatalara odaklanır
- Streamlit tabanlı sade web arayüzü
- Native Anthropic SDK tool use döngüsü (wrapper kütüphane yok)

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

`.env` dosyasını aç ve API anahtarını gir:

```
ANTHROPIC_API_KEY=sk-ant-...
```

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
