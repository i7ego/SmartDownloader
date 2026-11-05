"""
أداة بناء الحزمة التنفيذية المستقلة (SmartDownloader.exe) باستخدام PyInstaller.
تقوم هذه الأداة بإنشاء نسخة بورتابل (Portable) تعمل على أي جهاز ويندوز دون الحاجة لتثبيت بايثون أو أي برامج أخرى.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
BUILD_DIR = BASE_DIR / "build"
BIN_DIR = BASE_DIR / "bin"
ASSETS_DIR = BASE_DIR / "assets"
ICON_PATH = ASSETS_DIR / "app_icon.ico"


def build():
    print("=" * 60)
    print("  بدء بناء برنامج محمل الوسائط الذكي (SmartDownloader) بصيغة EXE")
    print("=" * 60)

    # إغلاق أي عملية سابقة للبرنامج قبل إعادة البناء لمنع قفل الملفات
    if sys.platform == "win32":
        try:
            subprocess.run(["taskkill", "/f", "/im", "SmartDownloader.exe"], capture_output=True)
        except Exception:
            pass

    # 1. التأكد من وجود الأيقونة
    if not ICON_PATH.exists():
        print("[!] جاري إنشاء أيقونة التطبيق...")
        from ui.icons import create_app_logo_pil
        img = create_app_logo_pil(256)
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        img.save(ICON_PATH, format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        img.save(ASSETS_DIR / "app_icon.png", format="PNG")
        print("[+] تم إنشاء الأيقونة بنجاح.")

    # 2. إعداد أمر PyInstaller المتوافق مع جميع الأنظمة (Windows, Linux, macOS)
    path_sep = os.pathsep
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--name=SmartDownloader",
        "--windowed",  # بدون شاشة سوداء CMD
        f"--add-data={ASSETS_DIR}{path_sep}assets",
        "--collect-all=customtkinter",
        "--collect-all=yt_dlp",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
    ]

    if sys.platform == "win32":
        cmd.extend([
            f"--icon={ICON_PATH}",
            "--hidden-import=windnd",
        ])
    elif sys.platform == "darwin":
        cmd.extend([
            "--osx-bundle-identifier=com.i7ego.smartdownloader",
        ])

    cmd.append(str(BASE_DIR / "main.py"))

    print("[*] جاري تشغيل PyInstaller لبناء الملفات التنفيذية...")
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    if result.returncode != 0:
        print(f"[!] فشل بناء البرنامج برمز خروج: {result.returncode}")
        sys.exit(result.returncode)

    # 3. نسخ أدوات FFmpeg وملفات الأصول إلى مجلد التوزيع النهائي ليعمل على أي جهاز
    target_folder = DIST_DIR / "SmartDownloader"
    if target_folder.exists():
        # نسخ مجلد assets
        target_assets = target_folder / "assets"
        if not target_assets.exists():
            shutil.copytree(ASSETS_DIR, target_assets)

        # نسخ أدوات FFmpeg
        if BIN_DIR.exists():
            target_bin = target_folder / "bin"
            target_bin.mkdir(exist_ok=True)
            print("[*] جاري نسخ أدوات FFmpeg المدمجة إلى حزمة التوزيع...")
            for item in BIN_DIR.glob("*.*"):
                dest_file = target_bin / item.name
                if not dest_file.exists():
                    shutil.copy2(item, dest_file)
            print("[+] تم تضمين أدوات FFmpeg بنجاح.")

    print("\n" + "=" * 60)
    print("  تم اكتمال البناء بنجاح!")
    print(f"  المسار النهائي للبرنامج الجاهز للنقل: {target_folder}")
    print("=" * 60)


if __name__ == "__main__":
    build()
