# Millioner_lifestyle – Shorts üretim yöntemi

Bu belge, kanalın günlük YouTube Shorts üretiminin eksiksiz tarifidir. Üretimi bulut görevi (KOMUTA) yapar.
**Yükleme ayrıdır:** üretilen videolar ancak kullanıcı onayladıktan sonra YouTube'a yüklenir. Bulut görevi YouTube'a hiçbir şey yüklemez, hiçbir ayarı değiştirmez.

- Kanal: **Millioner_lifestyle** (Google hesabı: berke.arica23 – aynı hesapta İman Işığı kanalı da var)
- Studio: https://studio.youtube.com/channel/UCRiUNFDXh38P3qsO2DO9lfQ
- Dil: videolar **İngilizce**, hedef kitle **ABD**
- Repo: `spR1nt23/millioner-videos` (herkese açık; videolar `raw.githubusercontent.com` üzerinden yüklemeye verilir)

---

## 1. Kurulum (temiz Linux, bir kez)

```bash
git clone https://github.com/spR1nt23/millioner-videos && cd millioner-videos
python3 -m venv .venv && . .venv/bin/activate      # önerilir
bash tools/setup.sh
```

`tools/setup.sh` şunları yapar:
1. `ffmpeg` yoksa `apt-get install ffmpeg` (libx264 + aac gerekir).
2. `pip install -r tools/requirements.txt` → `kokoro-onnx 0.6.1` (onnxruntime, phonemizer, espeakng-loader ile; espeak-ng paketin içinde gelir, apt gerekmez), numpy, pillow, soundfile.
3. Kokoro v1.0 model dosyaları (~350 MB) → `tools/models/`
   `https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/{kokoro-v1.0.onnx,voices-v1.0.bin}`
4. Poppins fontları (OFL) → `tools/fonts/`
   `https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/{Poppins-Bold.ttf,Poppins-Medium.ttf}`
5. TTS duman testi ("TTS OK").

Venv kullanılmıyorsa ve sistem Python'u pip'i engelliyorsa: `PIP_FLAGS="--break-system-packages" bash tools/setup.sh`.
Model ve fontlar `.gitignore`'da; repoya girmez. Farklı yer için `MK_MODELS_DIR` / `MK_FONTS_DIR` ortam değişkenleri.

Python ≥ 3.10. Test edildi: Python 3.13, ffmpeg 6.1, temiz venv – kurulum ~15 sn (ağ hızına bağlı), bir video render ~30 sn.

---

## 2. Günlük plan

- Günde **2 Short**.
- Yayın saatleri (İstanbul): **20:00** ve **ertesi gün 01:00**.
  ABD Doğu (ET) kış saatinde İstanbul −8 saat → **12:00 ET** (öğle) ve **17:00 ET** (akşam). ABD yaz saatinde (Mart–Kasım başı) fark −7 saattir; İstanbul saatleri aynı kalır, ET karşılığı 13:00 ve 18:00 olur.
- Karışım: genelde **1 kişisel finans** + **1 girişimci/şirket hikâyesi**.
- Gün `D` için üretilen videolar: `D 20:00` ve `D+1 01:00` (İstanbul).

### Günlük adımlar (bulut görevi)
1. `git pull`.
2. Bölüm 4'teki listeye bakıp **kanalda olmayan** 2 konu seç.
3. Her bilgiyi bölüm 3'e göre doğrula (kaynak URL'lerini not al).
4. `tools/specs/spec_<ad>.json` yaz (bölüm 5–7).
5. Render: `python3 tools/mk.py tools/specs/spec_<ad>.json -o out` (bölüm 8).
6. Kare kontrolü (bölüm 9). Çıkış kodu 2 ise metni düzelt, yeniden render et.
7. Videoları `videos/YYYY-MM-DD/vidNEW7_<ad>.mp4` altına koy (YYYY-MM-DD = ilk yayın günü), yanına `videos/YYYY-MM-DD/meta.json` yaz (bölüm 10), spec dosyalarını commit et.
8. Bölüm 4'teki geçmiş konular listesine yeni konuları ekle.
9. Commit + push (main). **YouTube'a yükleme yapma.** Kullanıcıya özet: başlıklar, süreler, kaynaklar, planlanan saatler.

---

## 3. Konu seçimi ve bilgi doğrulama kuralları

**Konu türleri**
- *Kişisel finans (ABD):* bileşik faiz, ücretler, bütçe kuralları, kredi puanı, 401(k), kira, birikim alışkanlıkları… Somut bir sayı/hesap içermeli.
- *Girişimci hikâyeleri:* tek bir şaşırtıcı, doğrulanabilir olgu etrafında (yaş, ilk sermaye, ret sayısı, satış rakamı…).

**Doğrulama**
- Her olgu, rakam, tarih **en az bir güvenilir kaynaktan** (resmî site, şirketin kendi sitesi, büyük haber kuruluşu, devlet/araştırma kurumu, Wikipedia + birincil kaynak) **web araması ile** doğrulanır; bellekten yazılmaz.
- Örnek kaynaklar: myFICO (kredi puanı yüzdeleri), HUD / Kongre Araştırma Servisi CRS (kira yükü), IKEA.com, NYT/Bloomberg haberleri.
- Tartışmalı ya da efsane olan hikâyelerden kaçın (ör. "1.009 ret" KFC efsanesi, Netflix'in $40 gecikme cezası hikâyesi). Emin değilsen o ayrıntıyı çıkar.
- Yıllık değişen limitler (IRS katkı limitleri, faiz oranları) güncel kaynağa bakılmadan kullanılmaz.
- Finans hesapları **kodla** yapılır (örn. `python3 -c ...`), elle değil. Getiri varsayımı açıkça "hypothetical" diye belirtilir (genelde %7 yıllık).
- Yuvarlama: ekranda kısa gösterim (`$172K`, `$34.5K`), konuşmada yuvarlak sayı ("about one seventy two thousand").
- Finans videolarının açıklamasında **"Educational only, not financial advice."** zorunlu. Kişisel yatırım tavsiyesi verilmez ("buy X" yok).

**Tekrar önleme**
- Bölüm 4'teki listede olan konu tekrar yapılmaz (aynı kişi farklı açıdan bile olsa kaçın; Buffett ve Jobs zaten ikişer kez işlendi).
- Kanalın Studio'daki Shorts listesi tek doğru kaynaktır; şüphede kullanıcıdan liste istenir.

---

## 4. Geçmiş konular (kanalda olan – TEKRARLAMA)

Kanal başlıkları (en yeniden eskiye), 13 Kasım 2026 itibarıyla:

| # | Başlık | Tür | Yayın (İstanbul) |
|---|---|---|---|
| 0a | Over 100 Investors Said No to Canva (Melanie Perkins) | hikâye | 15 Kas 01:00 |
| 0b | Is a 72-Month Car Loan a Trap? (48 vs 72 ay faiz) | finans | 14 Kas 20:00 |
| 1 | He Gave Away His $3 Billion Company (Patagonia, Chouinard) | hikâye | 14 Kas 01:00 |
| 2 | Got a Raise? Do This Before You Spend It (zammın yarısını biriktir) | finans | 13 Kas 20:00 |
| 3 | He Started IKEA at 17 (Kamprad) | hikâye | 13 Kas 01:00 |
| 4 | How Much Rent Can You Really Afford? (%30 kuralı) | finans | 12 Kas 20:00 |
| 5 | 13 Employees, $1 Billion: The Instagram Deal | hikâye | 12 Kas 01:00 |
| 6 | What Really Builds Your Credit Score? (FICO %35/%30) | finans | 11 Kas 20:00 |
| 7 | 5,127 Prototypes: How James Dyson Never Quit | hikâye | 11 Kas 01:00 |
| 8 | Skipping Your 401(k) Match? That's Free Money | finans | 10 Kas 20:00 |
| 9 | How Cereal Saved Airbnb (Obama O's) | hikâye | 10 Kas 01:00 |
| 10 | A 1% Fee Can Cost You $187,000 | finans | 9 Kas 20:00 |
| 11 | The 4% Rule: How Much Do You Need to Retire? | finans | 8 Kas |
| 12 | How Fast Do Prices Double? Inflation Explained | finans | 8 Kas |
| 13 | Buffett's 1958 House: $31,500 Then, Millions Now | hikâye | 8 Kas |
| 14 | Steve Jobs Took a $1 Salary. Here's Why. | hikâye | 8 Kas |
| 15 | What Does a Credit Card Balance Really Cost? | finans | 7 Kas |
| 16 | Dollar Cost Averaging in 20 Seconds | finans | 7 Kas |
| 17 | How Much Emergency Cash Is Enough? | finans | 7 Kas |
| 18 | Nike Started With $500 Each | hikâye | 7 Kas |
| 19 | He Opened His First Walmart at 44 (Sam Walton) | hikâye | 7 Kas |
| 20 | Would You Take a Penny Doubled for 30 Days? | finans | 6 Kas |
| 21 | Your Cash Is Quietly Shrinking (enflasyon, 1990→bugün) | finans | 6 Kas |
| 22 | What $100 a Month Becomes in 30 Years | finans | 6 Kas |
| 23 | Budget in 10 Seconds: The 50/30/20 Rule | finans | 6 Kas |
| 24 | From $5,000 to a Billion: Sara Blakely's Story (Spanx) | hikâye | 6 Kas |
| 25 | Warren Buffett Bought His First Stock at 11 | hikâye | 5 Kas |
| 26 | Henry Ford Failed Twice Before the Model T | hikâye | 5 Kas |
| 27 | Rejected Again and Again: Jack Ma's Story | hikâye | 5 Kas |
| 28 | Does $5 a Day Really Add Up? | finans | 5 Kas |
| 29 | From Garbage Bags to $5.7 Billion: Mark Cuban | hikâye | 5 Kas |
| 30 | Elon Musk's First Company Was Not Tesla (Zip2) | hikâye | 4 Kas |
| 31 | From Poverty to Billionaire: Oprah Winfrey | hikâye | 4 Kas |
| 32 | Started at 52? Ray Kroc and McDonald's | hikâye | ≤4 Kas |
| 33 | Can Money Double Itself? The Rule of 72 | finans | ≤4 Kas |
| 34 | Walt Disney Went Bankrupt First | hikâye | ≤4 Kas |
| 35 | Even Harry Potter Was Rejected (J.K. Rowling) | hikâye | ≤4 Kas |
| 36 | Too Old to Start? Colonel Sanders Story (KFC) | hikâye | ≤4 Kas |
| 37 | Jeff Bezos: Amazon Started in a Rented Garage | hikâye | ≤4 Kas |
| 38 | Fired From His Own Company? Steve Jobs Story | hikâye | ≤4 Kas |
| 39 | Bill Gates: The College Dropout Who Built Microsoft | hikâye | ≤4 Kas |
| 40 | Warren Buffett: Still in the Same Omaha House | hikâye | ≤4 Kas |

Kullanılmış kişiler/şirketler (kısa liste): Buffett, Jobs/Apple, Bezos/Amazon, Gates/Microsoft, Musk/Zip2, Oprah, Jack Ma/Alibaba, Mark Cuban, Henry Ford, Walt Disney, J.K. Rowling, Colonel Sanders/KFC, Ray Kroc/McDonald's, Sara Blakely/Spanx, Nike/Phil Knight, Sam Walton/Walmart, Airbnb, Dyson, Instagram, IKEA/Kamprad, Patagonia/Chouinard, Canva/Melanie Perkins.
Kullanılmış finans fikirleri: bileşik faiz ($100/ay, $5/gün, penny doubled, Rule of 72), enflasyon (×2), 50/30/20, acil durum fonu, DCA, kredi kartı faizi, %4 kuralı, %1 ücret, 401(k) eşleşmesi, FICO, %30 kira, zammın yarısı, 72 ay araba kredisi.

**Yeni konu ekleyince bu tabloya satır ekle.**

---

## 5. Senaryo ve kanca kuralları

- Süre **19–23 sn** (`mk.py` dışına çıkarsa hata verir). 4 sahne: `hook → stat/bars → stat/bars → cta`.
- Her sahnede tek bir fikir; `say` metni 1–2 kısa cümle. Sahne süresi = ses süresi + 0,7 sn.
- **Kanca (hook):** ilk sahne 2–3 sn; sayı, soru ya da şaşırtıcı iddia. Başlık ≤ ~7 kelime.
  Örnekler: "He failed 5,126 times", "13 employees. $1 billion.", "Got a raise? Do this first.", "A tiny 1% fee can cost you $187K".
- Ekrandaki büyük rakam ile konuşmadaki rakam aynı olmalı.
- **CTA:** tek satır ders + "Follow for more money math" (finans) / "Follow for more money tips" / "Follow for more founder stories" (hikâye).
- Rakamlar konuşmada okunacak gibi yazılır ("nineteen forty three", "fifteen hundred"); TTS "$1,500" gibi biçimleri bazen yanlış okur.
- "Guaranteed", "you will get rich" gibi vaatler yok.

## 6. Ses

- Kokoro v1.0 (ONNX), ses **`am_michael`**, dil `en-us`, hız 1.0, 24 kHz.
- Her sahne ayrı TTS; sesler sahne başlangıçlarına yerleştirilip birleştirilir.
- Kokoro kelime zamanı vermez; altyazı zamanlaması kelime uzunluğuna göre orantılı dağıtılır.
- Müzik yok.

## 7. Görsel stil ve grafikler

- 1080×1920, 30 fps.
- Arka plan: koyu zemin üstünde bulanık renkli lekeler (mavi, mor, yeşil, turuncu, kırmızı), yavaşça kayar. Renk düzeni video adından türetilir (her video farklı, ama tekrar render'da aynı).
- Üstte sarı (#FFD228) ilerleme çubuğu.
- Font: Poppins Bold (başlık/rakam/altyazı), Poppins Medium (alt metin).
- Altyazı: y≈1450'de, 4 kelimelik gruplar, sahne sınırını aşmaz; okunan kelime **sarı**, geçmişler **beyaz**, gelecekler **gri**; siyah kontur.
- Sahne tipleri (spec alanları `tools/mk.py` başında ve `tools/specs/TEMPLATE.json`'da):
  - `hook`: büyük sarı başlık + alt satır.
  - `stat`: dev sarı rakam (`count` verilirse 0'dan sayar) + açıklama.
  - `bars`: çubuk grafik; `hl` = sarı vurgulanacak çubuk (asıl mesaj olan çubuk), diğerleri mavi. Çubuk sayısı 2–5; etiketler kısa ("On-time pay", "Debt owed").
  - `cta`: beyaz başlık + alt satır.
- Yazılar otomatik küçülür; sığmazsa `mk.py` "TEXT DOES NOT FIT" der.

## 8. Render

```bash
. .venv/bin/activate
python3 tools/mk.py tools/specs/spec_<ad>.json -o out
```
Çıktı: `out/vidNEW7_<ad>.mp4` (H.264 CRF 20 + AAC 160k, faststart), `out/stills_<ad>/still_<n>_<tip>.png` (her sahnenin %80'inden bir kare), `out/sheet_<ad>.png` (yan yana özet).
Çıkış kodu: 0 = tamam, 2 = kontrol hatası (süre veya sığmayan yazı).

## 9. Kare kontrolü (yüklemeden önce zorunlu)

`out/sheet_<ad>.png` dosyasına **bakılır**:
- Hiçbir yazı kenara taşmıyor / kesilmiyor, satırlar üst üste binmiyor.
- Rakamlar ve etiketler doğru, yazım hatası yok.
- Grafik doğru çubuğu vurguluyor; çubuk etiketleri okunuyor.
- Altyazı başka sahnenin kelimelerini göstermiyor.
- Süre 19–23 sn (`ffprobe -v error -show_entries format=duration -of csv=p=0 out/vidNEW7_<ad>.mp4`).
Sorun varsa metni kısalt / font sığdır, yeniden render et.

## 10. Başlık, açıklama, hashtag

- **Başlık** (İngilizce, ≤ ~60 karakter, merak uyandıran): "He Started IKEA at 17", "What Really Builds Your Credit Score?", "A 1% Fee Can Cost You $187,000".
- **Açıklama**: 1–2 cümlelik olgu özeti (rakamlar + yıl) → finans videosunda `Educational only, not financial advice.` → **3 hashtag**, sonda bir boşluk:
  1. konuya özel (`#ikea`, `#401k`, `#creditscore`, `#jamesdyson`)
  2. orta hacimli niş (`#personalfinance`, `#entrepreneur`, `#startup`, `#savingmoney`)
  3. `#shorts`
  Çok genel etiketlerden kaçın (`#money`, `#millionaire`). Hashtag yazımını kontrol et (eski hata: `#rulof72`).
- Hipotetik hesaplarda açıklamada "hypothetical" geçsin; plan/oran değişkense "plans vary".

`videos/YYYY-MM-DD/meta.json` (onay ve yükleme için):
```json
[
  {"file": "vidNEW7_raisehalf.mp4", "title": "...", "description": "... #savingmoney #personalfinance #shorts ",
   "schedule_istanbul": "2026-11-13 20:00", "sources": ["https://..."]},
  {"file": "...", "title": "...", "description": "...", "schedule_istanbul": "2026-11-14 01:00", "sources": ["..."]}
]
```

## 11. Studio yükleme (yalnızca kullanıcı onayından sonra, ayrı adım)

Yükleme yerleşik tarayıcıyla (Claude masaüstü uygulaması) yapılır:
1. **Doğru hesap/kanal:** tarayıcı çoğu zaman başka hesapta kalır (Studio 403 "izniniz yok" verir). `youtube.com/account` → `#avatar-btn` → "Hesap değiştir" (İngilizce arayüzde "Switch account") → **Millioner_lifestyle**. Pencere dar ise genişliği 1280 yap. Gizli panelde sayfa geç yüklenir; 5 sn bekleyip tekrar dene. Başka bir sohbet/kanal aynı anda yükleme yapıyorsa bekle.
2. `https://studio.youtube.com/channel/UCRiUNFDXh38P3qsO2DO9lfQ/videos/upload?d=ud`
3. Dosyayı GitHub'dan ver (dosya seçme penceresi gerekmez):
   ```js
   const url='https://raw.githubusercontent.com/spR1nt23/millioner-videos/main/videos/<TARIH>/<DOSYA>.mp4';
   const b=await (await fetch(url,{cache:'no-store'})).blob();
   const inp=document.querySelector('ytcp-uploads-file-picker input[type=file]');
   const dt=new DataTransfer(); dt.items.add(new File([b],'<DOSYA>.mp4',{type:'video/mp4'}));
   inp.files=dt.files; inp.dispatchEvent(new Event('change',{bubbles:true}));
   ```
   Videolar tek tek; yükleme bitmeden sayfadan ayrılma; Escape'e basma.
4. Başlık ve açıklama kutusuna tıkla → Ctrl+A → yaz (meta.json'dan).
5. Kitle: **"Hayır, çocuklara özel değil"** (`tp-yt-paper-radio-button[name=VIDEO_MADE_FOR_KIDS_NOT_MFK]`).
6. `#next-button` ×3 → Görünürlük → **Planlayın** (`#second-container-expand-button`).
7. **Tarih:** takvim kutusuna tıkla, günü takvimden seç.
   **Saat:** yazarak değişmez. `#time-of-day-container input` için focus+click → 1,5 sn bekle → listedeki `tp-yt-paper-item` ("20:00" / "01:00") tıkla → input değerini kontrol et. Saat dilimi İstanbul (GMT+3).
8. `#done-button` (Planla) → "Video planlandı … tarihinde" görülmeli.
9. Sonda Shorts listesinde hepsi **Planlandı**, açıklamalar dolu, tarih/saat doğru.
- Oynatma listesi kullanılmıyor. Ücretli tanıtım yok. Yapay zekâ ile değiştirilmiş içerik sorusu: varsayılan.
- Doğrulanmamış kanalda günlük yükleme sınırı düşüktür (Studio → Ayarlar → Kanal → Özellik uygunluğu ile telefon doğrulaması önerilir).
- Silme, kanal ayarı değiştirme, hemen herkese açık yayınlama gibi geri alınamaz işler **kullanıcıya sorulmadan yapılmaz.**

## 12. Notlar / durum

- 13 Kas 2026 itibarıyla 9–12 Kas videoları 0–2 izlenmede; YouTube dağıtım yapmıyor. Denenebilecekler: ilk 1 sn'de soru soran daha sert kancalar, 10–15 sn'lik daha kısa videolar, tekrar eden seri formatı ("Founder at 17" vb.). Değişiklik kullanıcıyla konuşularak yapılır.
- Eski çıktı adı kuralı `vidNEW7_<ad>.mp4` korunuyor.
