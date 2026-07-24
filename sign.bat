@echo off
REM Create a self-signed code-signing certificate and sign HexLauncher.exe.
REM
REM This DOES NOT bypass Windows SmartScreen completely, but it reduces
REM false positives in many antivirus products. For full protection,
REM get a real certificate from Certum (free for OSS) or a commercial CA.
REM
REM Usage:
REM     1. Run this script as Administrator
REM     2. The .exe will be signed in-place

setlocal

set CERT_SUBJECT=CN=HexLauncher, O=Open Source
set CERT_PASSWORD=HexLauncherCert
set PFX_FILE=HexLauncher.pfx
set EXE_FILE=dist\HexLauncher.exe
set TIMESTAMP_SERVER=http://timestamp.digicert.com

echo Creating self-signed code-signing certificate...
powershell -NoProfile -Command ^
    "$cert = New-SelfSignedCertificate -Subject '%CERT_SUBJECT%' -Type CodeSigningCert -CertStoreLocation 'Cert:\CurrentUser\My' -NotAfter (Get-Date).AddYears(5); ^
     $password = ConvertTo-SecureString -String '%CERT_PASSWORD%' -Force -AsPlainText; ^
     Export-PfxCertificate -Cert $cert -FilePath '%PFX_FILE%' -Password $password; ^
     Write-Host 'Certificate created: %PFX_FILE%'"

if not exist "%EXE_FILE%" (
    echo ERROR: %EXE_FILE% not found. Run build.py first.
    exit /b 1
)

echo Signing %EXE_FILE%...
powershell -NoProfile -Command ^
    "$password = ConvertTo-SecureString -String '%CERT_PASSWORD%' -Force -AsPlainText; ^
     $cert = Import-PfxCertificate -FilePath '%PFX_FILE%' -CertStoreLocation 'Cert:\CurrentUser\My' -Password $password; ^
     Set-AuthenticodeSignature -FilePath '%EXE_FILE%' -Certificate $cert -TimestampServer '%TIMESTAMP_SERVER%'"

if %errorlevel% neq 0 (
    echo Signing failed.
    exit /b 1
)

echo.
echo Done. %EXE_FILE% is now self-signed.
echo.
echo NOTE: This is a SELF-SIGNED cert. Windows SmartScreen will still warn.
echo For full protection, get a real cert:
echo   - Certum (free for OSS): https://shop.certum.eu/open-source-code-signing-certificate.html
echo   - SignPath.io (free for OSS): https://signpath.io
endlocal
