@echo off
chcp 65001 >nul
echo ============================================================
echo   Pushing SmartDownloader to GitHub (@i7ego)
echo ============================================================
echo.

git init
git add .
git commit -m "feat: initial release v2.0.0 with cutter, converter, and modern UI"
git branch -M main
git remote add origin https://github.com/i7ego/SmartDownloader.git 2>nul || git remote set-url origin https://github.com/i7ego/SmartDownloader.git

echo.
echo [*] Pushing to main branch on https://github.com/i7ego/SmartDownloader ...
git push -u origin main

echo.
echo [*] Pushing Release tag v2.0.0 (triggers automatic Windows, Linux & macOS builds)...
git tag -f v2.0.0 -m "Release v2.0.0"
git push origin v2.0.0 --force

echo.
echo ============================================================
echo   Done! Repository & Multi-Platform Release Published!
echo   https://github.com/i7ego/SmartDownloader
echo ============================================================
pause
