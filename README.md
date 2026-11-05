<div align="center">

# ⚡ Smart Media Downloader, Cutter & Converter
### محمّل الوسائط الذكي، أداة تقطيع الفيديوهات والموسيقى، ومحوّل الصيغ الاحترافي

<br>

<img src="assets/app_icon.png" width="130" height="130" alt="SmartDownloader Icon" style="border-radius: 26px; box-shadow: 0 10px 25px rgba(108,92,231,0.3);">

<br>
<br>

**The ultimate all-in-one desktop media suite for Windows: High-speed 4K/8K Video & Playlist Downloader, Precision Lossless Video & Audio Cutter, and Universal Video Converter.**

*أقوى برنامج سطح مكتب متكامل لنظام ويندوز: تحميل الفيديوهات وقوائم التشغيل بأعلى دقة 4K/8K، تقطيع الفيديو والصوت فائق السرعة بدون فقدان جودة، وتحويل وضغط الفيديوهات بجميع الصيغ العالمية.*

<br>

<!-- Direct Download CTA Badges -->
<p align="center">
  <a href="https://github.com/i7ego/SmartDownloader/releases/latest">
    <img src="https://img.shields.io/badge/⬇️_Direct_Download-Portable_EXE_(64--bit)-6C5CE7?style=for-the-badge&logo=windows&logoColor=white" height="40" alt="Download Standalone EXE">
  </a>
  <a href="https://github.com/i7ego/SmartDownloader/archive/refs/heads/main.zip">
    <img src="https://img.shields.io/badge/📦_Download_ZIP-Source_Code-00CEC9?style=for-the-badge&logo=github&logoColor=white" height="40" alt="Download ZIP">
  </a>
</p>

<!-- Metadata Shields Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Release-v2.0.0-6C5CE7?style=flat-square" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.14%20%7C%203.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-blueviolet?style=flat-square" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-0078D6?style=flat-square" alt="Multi-Platform Support">
  <img src="https://img.shields.io/badge/Engine-yt--dlp%20%26%20FFmpeg-E50914?style=flat-square&logo=ffmpeg&logoColor=white" alt="Engine">
  <img src="https://img.shields.io/badge/Build-Portable_Standalone-success?style=flat-square" alt="Standalone">
  <img src="https://img.shields.io/badge/Tests-13%20Passed%20(100%25)-brightgreen?style=flat-square" alt="Test Suite">
  <img src="https://img.shields.io/badge/License-MIT-orange?style=flat-square" alt="License">
</p>

<br>

<!-- Multi-Language Bar -->
**🌐 Languages / اللغات:**  
[English](#-english) • [العربية](#-العربية) • [Español](#-español) • [Français](#-français)

---

</div>

<br>

<a name="-english"></a>
## 🇬🇧 English

### 🌟 Features Overview

#### 1. 📥 High-Speed Media & Playlist Downloader
- **Ultra HD Resolutions:** Download videos in **1080p, 1440p (2K), 2160p (4K), and 4320p (8K)** at 60fps with automatic audio-video stream merging.
- **Audio Extraction:** Convert media directly to high-bitrate **MP3 (320kbps), M4A, WAV, or FLAC**.
- **Interactive Playlist Manager:** Search, inspect, batch-select, invert, and download full playlists with multi-threaded concurrent transfers.
- **Full Transfer Controls:** Real-time speed metrics, percentage progress, ETA calculation, pause, resume, and cancel.
- **Instant URL Detection:** Automatic paste & analyze upon typing `Ctrl+V` or dragging and dropping URLs.

#### 2. ✂️ Media Cutter (Video & Audio)
- **Fast Lossless Video Cut (`-c copy`):** Cut videos in milliseconds without re-encoding, preserving 100% of original visual and audio quality.
- **Accurate Re-encode Cut:** Frame-accurate cuts with custom output containers (`MP4`, `MKV`, `WebM`).
- **High-Res GIF Maker:** Export any trimmed video scene as an optimized animated GIF using two-pass palette filters.
- **Audio Trimming & Fade:** Audio segment trimming with smooth **Fade In** and **Fade Out** duration sliders.
- **Interactive Seek Bar & Marker Buttons:** Live playback preview with interactive seek bar and instant **`[ Set Start`** & **`Set End ]`** marker buttons while listening or watching.

#### 3. 🔄 Universal Video & Media Converter
- **Multi-Format Transcoding:** Convert between `MP4`, `MKV`, `WebM`, `AVI`, `MOV`, `GIF`, and `MP3`.
- **Resolution Resizing:** Resize videos to `Original`, `1080p (FHD)`, `720p (HD)`, or `480p (SD)`.
- **Smart Compression Presets:**
  - `High Quality`: Minimal compression for archival.
  - `Balanced`: Optimal ratio between small size and crystal-clear clarity.
  - `Small Size (Compressed)`: Highly compressed for quick WhatsApp, Discord, and email sharing.
- **Live Progress & Cancellation:** Dedicated progress bar with live percentage and instant cancel support.

#### 4. 🎨 State-of-the-Art Flat UI & Bilingual Support
- **Modern Theme System:** Dark Mode (`#0F1117`) and Light Mode (`#F5F7FB`) with Purple (`#6C5CE7`) and Turquoise (`#00CEC9`) accents.
- **Default English LTR & Full Arabic RTL:** Dynamic layout mirroring with built-in modern Arabic typography (**Cairo** and **Tajawal**).
- **System Tray & Windows Integration:** Independent Windows Taskbar grouping with custom application logo and background minimize tray.

#### 5. 📦 Cross-Platform & Standalone
- **Windows:** Pre-compiled standalone portable `.exe` running without Python or dependencies.
- **Linux & macOS:** Runs smoothly via Python 3 with native Dark/Light UI, system tray, and FFmpeg integration.

---

<a name="-quick-start"></a>
### 🚀 How to Run

#### Option 1: Portable Standalone Executable (Windows)
1. Download or navigate to:
   ```
   dist\SmartDownloader\SmartDownloader.exe
   ```
2. Double-click **`SmartDownloader.exe`**.
3. *No installation, no terminal window, no dependencies required!*

#### Option 2: Running from Source (Windows, Linux, macOS)
```bash
# 1. Clone repository
git clone https://github.com/i7ego/SmartDownloader.git
cd SmartDownloader

# 2. Linux / macOS: install prerequisites (if not already installed)
# Ubuntu / Debian : sudo apt install ffmpeg python3-tk
# Fedora          : sudo dnf install ffmpeg python3-tkinter
# Arch Linux      : sudo pacman -S ffmpeg tk
# macOS (Homebrew): brew install ffmpeg python-tk

# 3. One-click Launcher
# On Linux / macOS:
chmod +x run.sh && ./run.sh

# On Windows:
run.bat
# or via python directly:
python main.py
```

#### Option 3: Compiling Your Own Standalone Binary
- **Windows:** Double-click `build.bat` or run `python build_exe.py`
- **Linux / macOS:** Run `chmod +x build.sh && ./build.sh`

---

<a name="-العربية"></a>
## 🇸🇦 العربية

### 🌟 نظرة شاملة على المميزات

#### 1. 📥 محمّل الفيديوهات وقوائم التشغيل فائق السرعة
- **تحميل أعلى الدقات:** دعم كامل لدقات **1080p و 2K و 4K و 8K** بمعدل 60 إطاراً في الثانية مع دمج مسارات الصوت والفيديو تلقائياً عبر محرك FFmpeg المدمج.
- **استخراج وتحويل الصوتيات:** تحميل الصوت المباشر بأعلى نقاء وجودة بصيغ **MP3 (320kbps) و M4A و WAV و FLAC**.
- **مدير قوائم التشغيل التفاعلي:** فحص والبحث داخل قوائم التشغيل، اختيار الكل، عكس التحديد، وتحميل القوائم المتعددة بالتوازي وبسرعة قصوى.
- **تحكم كامل بالتحميلات:** مؤشر سرعة لحظي، نسبة مئوية دقيقة، الوقت المتبقي (ETA)، مع إمكانية الإيقاف المؤقت، الاستئناف، والإلغاء.
- **لصق وتحليل تلقائي:** تحليل الرابط فورياً بمجرد نسخه ولصقه عبر `Ctrl+V` أو سحبه وإفلاته داخل البرنامج.

#### 2. ✂️ تقطيع الوسائط (فيديو وصوت)
- **قص سريع بدون فقد جودة (Lossless Fast Cut):** قص مقاطع الفيديو في أجزاء من الثانية دون إعادة ترميز (`-c copy`) مع الحفاظ بنسبة 100% على الجودة الأصلية.
- **قص دقيق على مستوى الإطار:** قص الفيديو وإعادة ترميزه بدقة متناهية بالصيغة المرغوبة (`MP4`, `MKV`, `WebM`).
- **صانع الصور المتحركة (GIF):** تحويل أي لقطة من الفيديو إلى صورة متحركة `GIF` عالية الدقة.
- **تقطيع الصوت وتأثيرات التلاشي:** التحكم في بداية ونهاية الأغاني والمقاطع الصوتية مع مؤثرات التلاشي التدريجي (**Fade In / Fade Out**).
- **مشغل مباشر وأزرار التحديد الحية:** استعراض الفيديو والصوت عبر شريط تمرير تفاعلي (Seek Bar) وأزرار تحديد البداية والنهاية أثناء الاستماع والمشاهدة:
  - **`[ تعيين كبداية`**
  - **`تعيين كنهاية ]`**

#### 3. 🔄 محوّل الفيديوهات والوسائط الشامل
- **التحويل بين جميع الصيغ العالمية:** `MP4`، `MKV`، `WebM`، `AVI`، `MOV`، `GIF`، واستخراج الصوت `MP3`.
- **تغيير وتصغير الدقة:** إمكانية التحويل لدقات `Original (نفس الدقة)`، `1080p`، `720p`، `480p`.
- **أنماط الضغط الذكي:**
  - `أعلى جودة (High Quality)`: ضغط خفيف للحفاظ على الدقة الأصلية.
  - `متوازن (Balanced)`: التوازن المثالي بين وضوح الصورة وحجم الملف.
  - `مضغوط لحجم أصغر (Small Size)`: مثالي لتقليل الحجم للمشاركة السريعة عبر الواتساب ووسائل التواصل.
- **متابعة حية للتقدم مع إمكانية الإلغاء.**

#### 4. 🎨 واجهة مستخدم مسطحة وعصرية (Bilingual UI)
- **ثيم داكن وفاتح فخم:** تصميم أنيق مبني على أحدث معايير الواجهات، بألوان بنفسجية وتركوازية متناسقة.
- **دعم كامل للغتين:** واجهة تفتح بالإنجليزية افتراضياً وتتحول للعربية بضغطة زر مع انعكاس كامل للتخطيط (RTL / LTR) وخطوط عربية مدمجة (**Cairo** و **Tajawal**).
- **أيقونة مخصصة في شريط المهام (Taskbar) وصينية النظام (System Tray).**

#### 5. 📦 دعم متعدد المنصات (Windows, Linux, macOS)
- **ويندوز (Windows):** نسخة تنفيذية محمولة ومستقلة 100% تعمل دون الحاجة لتثبيت بايثون أو أي برامج إضافية.
- **لينكس وماك (Linux & macOS):** تشغيل سلس عبر سكربت `run.sh` أو أمر بايثون، مع توافق كامل لمحركات FFmpeg وواجهة CustomTkinter الحديثة.

---

<a name="-español"></a>
## 🇪🇸 Español

### 🌟 Características Principales
- **Descargador de Medios y Listas de Reproducción en 4K/8K:** Descarga videos en 1080p, 2K, 4K y 8K a 60 fps con combinación automática de audio y video mediante FFmpeg integrado. Extracción directa de audio a MP3 (320kbps), M4A, WAV y FLAC.
- **Cortador de Medios (Video y Audio):** Corte ultrarrápido sin pérdida de calidad (`-c copy`) en milisegundos, corte cuadro por cuadro con recodificación, creación de GIFs animados y efectos de Fade In/Out para audio con barra de desplazamiento interactiva y botones de marcado en tiempo real.
- **Convertidor Universal de Video:** Conversión entre MP4, MKV, WebM, AVI, MOV, GIF y MP3 con escalado de resolución (1080p, 720p, 480p) y perfiles de compresión para compartir fácilmente.
- **100% Portátil y Autónomo:** Ejecutable independiente para Windows sin necesidad de instalar Python ni dependencias externas.

---

<a name="-français"></a>
## 🇫🇷 Français

### 🌟 Caractéristiques Principales
- **Téléchargeur Multimédia & Playlists 4K/8K:** Téléchargement haute vitesse jusqu'à 8K 60fps avec fusion audio/vidéo automatique via FFmpeg. Extraction audio MP3 (320kbps), M4A, WAV, FLAC.
- **Découpeur Multimédia (Vidéo & Audio):** Découpe ultra-rapide sans perte (`-c copy`) en quelques millisecondes, découpe précise à l'image près, conversion GIF animée haute résolution et effets de fondu (Fade In / Out).
- **Convertisseur Vidéo Universel:** Conversion multi-formats (MP4, MKV, WebM, AVI, MOV, GIF, MP3), redimensionnement de résolution et modes de compression optimisés pour le partage.
- **Application Portable et Autonome:** Fonctionne directement sur Windows sans nécessiter l'installation de Python ou d'outils tiers.

---

## 🔒 Security & Code Protection Guidelines / دليل حماية الكود المصدري

If you plan to publish this software while protecting your proprietary code:

1. **Distribute the Standalone Compiled EXE Only:**
   - The compiled package inside `dist/SmartDownloader/` bundles the encrypted bytecode and binaries without shipping your raw `.py` source files.
2. **Bytecode Obfuscation (PyArmor):**
   - You can encrypt core Python modules with [PyArmor](https://github.com/dashingsoft/pyarmor) before compiling, preventing decompilation:
     ```bash
     pip install pyarmor
     pyarmor gen --pack dist/SmartDownloader/SmartDownloader.exe main.py
     ```
3. **C-Compilation (Nuitka / Cython):**
   - Transpile Python into C native extension binaries (`.pyd`), making reverse engineering impossible.
4. **GitHub Repository Privacy:**
   - Keep your GitHub repository **Private** to protect your source code, and share only the compiled portable `.zip` through **GitHub Releases** for public download.

---

## 🧪 Automated Testing / الاختبارات الآلية

All unit, integration, and UI workflow tests run cleanly via pytest:

```bash
python -m pytest -v
```

```
tests/test_converter.py::test_convert_video_to_mp4_resolution PASSED     [  7%]
tests/test_converter.py::test_convert_video_to_audio_mp3 PASSED          [ 15%]
tests/test_converter.py::test_convert_video_to_gif PASSED                [ 23%]
tests/test_cutter.py::test_get_media_duration PASSED                     [ 30%]
tests/test_cutter.py::test_cut_audio_simple PASSED                       [ 38%]
tests/test_cutter.py::test_cut_audio_with_fade PASSED                    [ 46%]
tests/test_cutter.py::test_preview_player_lifecycle PASSED               [ 53%]
tests/test_cutter.py::test_media_type_detection PASSED                   [ 61%]
tests/test_cutter.py::test_cut_video_and_gif PASSED                      [ 69%]
tests/test_ui_and_core.py::test_theme_constants_exact_match PASSED       [ 76%]
tests/test_ui_and_core.py::test_no_hardcoded_hex_colors_outside_theme PASSED [ 84%]
tests/test_ui_and_core.py::test_storage_and_downloader_core PASSED       [ 92%]
tests/test_ui_and_core.py::test_full_gui_workflow PASSED                 [100%]
============================= 13 passed in 7.86s ==============================
```

---

## 📁 Repository Structure / هيكلية المستودع

```
SmartDownloader/
├── assets/                  # Icons, graphics, and embedded Arabic fonts (Cairo, Tajawal)
├── bin/                     # Standalone FFmpeg, FFplay, and FFprobe binaries
├── core/                    # Application logic
│   ├── converter.py         # Multi-format video converter & resolution compressor
│   ├── cutter.py            # Precision video & audio cutter, GIF maker & preview player
│   ├── downloader.py        # yt-dlp downloader engine & playlist queue manager
│   └── storage.py           # Settings and history persistence
├── ui/                      # CustomTkinter interface
│   ├── theme.py             # Design tokens, color palette & typography
│   ├── i18n.py              # English (LTR) & Arabic (RTL) localization
│   ├── icons.py             # Vector Lucide/Phosphor dynamic icon generator
│   ├── app.py               # Main window layout, sidebar & system tray
│   ├── components/          # Reusable buttons, chips, cards, dialogs & toasts
│   └── pages/               # Application tabs (New, Active, Cutter, Converter, History, Settings)
├── tests/                   # Automated pytest unit & integration test suite
├── github_upload/           # Clean, pre-packaged directory ready to push to GitHub
├── dist/SmartDownloader/    # Built standalone portable distribution (SmartDownloader.exe)
├── main.py                  # Entry point
├── build_exe.py             # Automated PyInstaller packaging pipeline
├── build.bat                # One-click Windows build script
├── run.bat                  # One-click Windows silent launcher
└── requirements.txt         # Dependencies
```

---

## 👤 Developer & Contact / المطور والتواصل

<div align="center">

**Developed with care by:**  
### **Ahmed Hagag**

📫 **Email / البريد الإلكتروني:** [ahmed.m.hagag22@gmail.com](mailto:ahmed.m.hagag22@gmail.com)  
⚖️ **Copyright:** © 2026 Ahmed Hagag. All rights reserved.

<br>

[![GitHub](https://img.shields.io/badge/GitHub-i7ego-181717?style=for-the-badge&logo=github)](https://github.com/i7ego)
[![Email](https://img.shields.io/badge/Contact-ahmed.m.hagag22%40gmail.com-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:ahmed.m.hagag22@gmail.com)

</div>

---

## 📄 License

This software is released under the [MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
