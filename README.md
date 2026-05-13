# Code Review Agent

Çok dilli kod dosyalarını gerçek statik analiz araçlarıyla inceleyen ve Claude API'nin **tool use** özelliği aracılığıyla pedagojik geri bildirim sunan AI agent uygulaması.

---

## Özellikler

- Kod dosyası yükleme veya kodu doğrudan yapıştırma
- **Çok dilli destek** — Python, JavaScript, TypeScript, Java, C++, Go, Ruby
- **pylint** ve **flake8** ile otomatik statik analiz
- **AST** tabanlı karmaşıklık ölçümü:
  - Fonksiyon uzunluğu
  - İç içe geçme derinliği
- Oturumlar arası kalıcı kullanıcı profili
- Tekrar eden hatalara odaklanan geri bildirim yapısı
- Streamlit tabanlı web arayüzü
- Native Anthropic SDK tool use döngüsü
- Wrapper kütüphane kullanmadan doğrudan SDK entegrasyonu

---

## Desteklenen Diller

| Dil | Uzantı |
|---|---|
| Python | `.py` |
| JavaScript | `.js` |
| TypeScript | `.ts` |
| Java | `.java` |
| C++ | `.cpp`, `.cc`, `.h` |
| Go | `.go` |
| Ruby | `.rb` |

---

## Kurulum

### 1. Projeyi indir

ZIP dosyasını çıkart ve proje klasörüne gir:

```bash
cd code-review-agent
```

### 2. Sanal ortam oluştur ve etkinleştir

Bu adım opsiyoneldir fakat önerilir.

```bash
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
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

Ardından `.env` dosyasını aç ve API anahtarlarını gir:

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENROUTER_API_KEY=sk-or-...
```

> `OPENROUTER_API_KEY` yalnızca OpenRouter modelleri kullanılacaksa gereklidir.

---

## Çalıştırma

Uygulamayı başlatmak için:

```bash
streamlit run app.py
```

Tarayıcıda aşağıdaki adres otomatik olarak açılır:

```text
http://localhost:8501
```

---

## Proje Yapısı

```text
code-review-agent/
├── app.py                    # Streamlit UI giriş noktası
├── requirements.txt
├── .env.example
├── agent/
│   ├── __init__.py
│   ├── core.py               # Agentic loop — Anthropic SDK + tool execution
│   ├── openrouter_core.py    # OpenRouter entegrasyonu — Bridge Pattern
│   ├── tools.py              # Tool şemaları ve Python implementasyonları
│   ├── prompts.py            # System prompt metinleri
│   └── memory.py             # Session history yönetimi
├── data/
│   └── user_profile.json     # Oturumlar arası kalıcı kullanıcı profili
└── tests/
    ├── sample_code/          # Test kod dosyaları: py, js, ts, java, cpp, go, rb
    ├── test_core.py
    └── test_tools.py
```

---

## Desteklenen Modeller

| Model | Sağlayıcı |
|---|---|
| Claude Sonnet 4.6 | Anthropic |
| Claude Sonnet 4.5 | Anthropic |
| Claude Haiku 4.5 | Anthropic |
| NVIDIA Nemotron Super (Free) | OpenRouter |
| GPT-OSS 120B (Free) | OpenRouter |
| Gemma 4 31B (Free) | OpenRouter |
| Llama 3.3 70B (Free) | OpenRouter |
| OpenRouter Free (Auto) | OpenRouter |

---

## Kullanılan Teknolojiler

| Teknoloji | Sürüm | Amaç |
|---|---:|---|
| Python | 3.11+ | Dil |
| Anthropic SDK | ≥ 0.40 | Claude API + tool use |
| Streamlit | ≥ 1.40 | Web arayüzü |
| pylint | ≥ 3.2 | Statik analiz |
| flake8 | ≥ 7.1 | Stil ve hata denetimi |
| python-dotenv | ≥ 1.0 | API key yönetimi |
| openai | ≥ 1.0 | OpenRouter entegrasyonu |
| pytest | ≥ 8.0 | Test altyapısı |

---

## Agent Mimarisi

```text
Kullanıcı girdisi
      │
      ▼
agent/core.py ──► Claude API (claude-sonnet-4-6)
      │                      │
      │          ┌───────────┘
      │          │ stop_reason == "tool_use"
      │          ▼
      │     Tool dispatch
      │     ├── read_python_file      — dosyayı okur
      │     ├── run_static_analysis   — pylint + flake8 çalıştırır (Python)
      │     ├── analyze_complexity    — AST ile karmaşıklık hesaplar
      │     ├── get_user_profile      — geçmiş hata istatistiklerini okur
      │     └── update_user_profile   — tekrar eden hata sayacını günceller
      │          │
      │          └──► Sonuç Claude'a geri beslenir
      │
      └──► stop_reason == "end_turn" → Markdown inceleme raporu
```

---

## Çalışma Mantığı

`core.py` içindeki döngü, Claude `end_turn` dönene veya maksimum iterasyon sayısına ulaşana kadar devam eder.

Varsayılan maksimum iterasyon sayısı:

```python
_MAX_ITERATIONS = 20
```

Döngü akışı şu şekildedir:

1. Kullanıcı kodu veya dosyası alınır.
2. Claude API'ye istek gönderilir.
3. Claude bir tool çağrısı isterse `stop_reason == "tool_use"` döner.
4. İlgili tool Python tarafında çalıştırılır.
5. Tool sonucu tekrar Claude'a gönderilir.
6. Claude nihai yanıtı ürettiğinde `stop_reason == "end_turn"` döner.
7. Kullanıcıya Markdown formatında kod inceleme raporu sunulur.

System prompt caching kullanılır. Böylece her iterasyonda tekrar eden sistem prompt token maliyeti önemli ölçüde azaltılır.

---

## Tool Listesi

| Tool | Açıklama |
|---|---|
| `read_python_file` | Python dosyasını okur |
| `run_static_analysis` | Python kodu için `pylint` ve `flake8` çalıştırır |
| `analyze_complexity` | AST üzerinden karmaşıklık ölçümü yapar |
| `get_user_profile` | Kullanıcının geçmiş hata istatistiklerini okur |
| `update_user_profile` | Tekrar eden hata sayaçlarını günceller |

---

## OpenRouter Entegrasyonu

OpenRouter modelleri için `openrouter_core.py`, aynı agentic döngüyü OpenAI uyumlu API üzerinden yürütür.

Anthropic formatındaki tool şemaları, `_to_openai_tool` fonksiyonu ile OpenAI tool formatına dönüştürülür.

Bu yapı, Anthropic ve OpenRouter entegrasyonlarının aynı mantıksal agent mimarisini kullanmasını sağlar.

Bu yaklaşım projede **Bridge Pattern** olarak uygulanmıştır.

---

## Örnek Kullanım Akışı

1. Kullanıcı bir kod dosyası yükler veya kodu doğrudan yapıştırır.
2. Sistem dosya türünü ve dili algılar.
3. Python dosyaları için:
   - `pylint` çalıştırılır.
   - `flake8` çalıştırılır.
   - AST tabanlı karmaşıklık analizi yapılır.
4. Kullanıcı profili okunur.
5. Claude, statik analiz sonuçlarını ve kullanıcı geçmişini birlikte değerlendirir.
6. Kod inceleme raporu Markdown formatında oluşturulur.
7. Tekrar eden hata türleri kullanıcı profiline kaydedilir.

---

## Testler

Testleri çalıştırmak için:

```bash
pytest
```

Belirli bir test dosyasını çalıştırmak için:

```bash
pytest tests/test_tools.py
```

---

## Notlar

- `pylint` ve `flake8` analizleri yalnızca Python dosyaları için otomatik olarak çalıştırılır.
- Diğer diller için agent, kod yapısını LLM tabanlı olarak değerlendirir.
- Kullanıcı profili `data/user_profile.json` dosyasında saklanır.
- OpenRouter entegrasyonu opsiyoneldir.
- Anthropic SDK ana entegrasyon katmanıdır.

---

## Lisans

Bu proje eğitim ve geliştirme amaçlı hazırlanmıştır.
