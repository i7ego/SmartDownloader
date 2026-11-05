[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Pushing SmartDownloader to GitHub - @i7ego" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

git init
git add .
git commit -m "feat: initial release v2.0.0 with cross-platform support" 2>$null
git branch -M main

$remoteUrl = "https://github.com/i7ego/SmartDownloader.git"
git remote remove origin 2>$null
git remote add origin $remoteUrl

Write-Host "[*] Pushing to GitHub repository: $remoteUrl ..." -ForegroundColor Yellow
git push -u origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "  [!] تنبيه: فشل الرفع لأن المستودع غير موجود بعد على حسابك!" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "  يرجى عمل الآتي الآن:" -ForegroundColor White
    Write-Host "  1. افتح الرابط: https://github.com/new" -ForegroundColor Green
    Write-Host "  2. اكتب في اسم المستودع: SmartDownloader" -ForegroundColor Green
    Write-Host "  3. اضغط الزر الأخضر: Create repository" -ForegroundColor Green
    Write-Host "  4. بعد إنشاء المستودع على الموقع، أعد تشغيل هذا الملف فقط!" -ForegroundColor Yellow
    Write-Host "============================================================" -ForegroundColor Red
    Read-Host "اضغط Enter للإغلاق..."
    exit 1
}

Write-Host ""
Write-Host "[*] Pushing Release tag v2.0.0 (triggers automatic builds in Cloud)..." -ForegroundColor Yellow
git tag -f v2.0.0 -m "Release v2.0.0"
git push origin v2.0.0 --force

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  [+] تم رفع المشروع والإصدار بنجاح!" -ForegroundColor Green
Write-Host "  رابط المستودع: https://github.com/i7ego/SmartDownloader" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Green
Read-Host "اضغط Enter للإغلاق..."
