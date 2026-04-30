# Code Review Agent — Proje Bağlamı

## Amaç
Python kod dosyalarını gerçek araçlarla (pylint, flake8, ast) analiz edip
Claude API'nin tool use özelliğiyle kullanıcıya bağlamlı, pedagojik kod incelemesi
sunan bir AI agent uygulaması.

## Mimari
- app.py → Streamlit UI giriş noktası
- agent/core.py → Agentic loop (Claude API çağrısı + tool execution döngüsü)
- agent/tools.py → Tool şemaları + Python implementasyonları
- agent/prompts.py → System prompt metinleri (sabit string'ler)
- agent/memory.py → Session history (st.session_state) + persistent user profile
- data/user_profile.json → Oturumlar arası kalıcı bellek

## Kurallar
- Tool use native Anthropic SDK ile yapılır, wrapper kütüphane kullanılmaz.
- Her tool hem bir JSON şeması (API'ye gönderilecek) hem bir Python fonksiyonu olarak tanımlanır.
- subprocess ile çalıştırılan araçlar (pylint, flake8) timeout=15s ile korunur.
- API key yalnızca .env'den python-dotenv ile okunur, kod içine yazılmaz.
- Tüm kullanıcı girdileri agent/core.py'ye girmeden önce temizlenir (boş mu, geçerli Python mu).
- Streamlit session_state dışında global değişken kullanılmaz.

## Tool listesi
1. read_python_file(file_path) — dosya okuma
2. run_static_analysis(code) — pylint + flake8, JSON çıktı
3. analyze_complexity(code) — ast ile fonksiyon uzunluğu + iç içe geçme derinliği
4. get_user_profile() — data/user_profile.json oku
5. update_user_profile(issue_key) — recurring_issues sayacını artır

## Stil
- Python 3.11+
- Type hint'ler kullan (def foo(x: str) -> dict:)
- Her fonksiyonun docstring'i olsun (tek satır yeterli)
- Türkçe commit mesajı yazma, İngilizce yaz