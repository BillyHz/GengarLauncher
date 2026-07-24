# Solución al flag de Windows Defender

## 🔍 Por qué pasa

Los binarios de **PyInstaller** son flaggeados masivamente por Windows
Defender y otros antivirus. Es un problema conocido y reportado, no es
específico de HexLauncher.

Las razones técnicas:

1. **El bootloader de PyInstaller es compartido** entre todos los
   binarios que genera. Los autores de malware lo usan mucho.
2. **El `.exe` desempaqueta archivos en `%TEMP%` al ejecutarse** — patrón
   muy sospechoso para heurísticas.
3. **El binario no está firmado digitalmente** — Windows SmartScreen
   muestra "Aplicación desconocida del publicador" y muchos antivirus
   lo bloquean preventivamente.
4. **Sin metadata de publisher/producto/version** completa.

No es que tu código sea malware. Es que **cualquier `.exe` PyInstaller
sin firmar tiene la misma firma** que malware real que también usa
PyInstaller.

## ✅ Lo que podés hacer (gratis, inmediato)

### 1. Reportar como falso positivo a Microsoft

Microsoft revisa submissions y suele whitelistear binarios legítimos en
1-3 días hábiles.

**Pasos:**
1. Andá a https://www.microsoft.com/en-us/wdsi/filesubmission
2. Elegí "I believe this file should not be detected as malware"
3. Subí `dist/HexLauncher.exe`
4. Llená el form:
   - **Software name:** HexLauncher
   - **Company name:** (tu nombre o el del proyecto)
   - **Description:** "Open-source Minecraft launcher. Source: github.com/BillyHz/HexLauncher"
5. Esperá el email de Microsoft con el resultado

### 2. Distribuir vía GitHub Releases

Los binarios subidos a GitHub Releases pasan por el scanner de GitHub y
suelen tener mejor reputación que un `.exe` descargado de un sitio random.

**Pasos:**
1. Andá a tu repo → Releases → "Create new release"
2. Tag: `v0.7.0`
3. Adjuntá `dist/HexLauncher.exe` (lo sube como asset)
4. Publicá

### 3. Instrucciones para usuarios finales

Pegá esto en tu README para que los usuarios agreguen una exclusión:

```powershell
# PowerShell (ejecutar como Administrador)
Add-MpPreference -ExclusionPath "C:\ruta\donde\estan\HexLauncher.exe"
```

O desde la GUI:
1. **Seguridad de Windows** → **Protección contra virus y amenazas**
2. → **Administrar la configuración** (en "Configuración de protección")
3. → **Exclusiones** → **Agregar o quitar exclusiones**
4. → **Agregar una exclusión** → **Carpeta**
5. Seleccioná la carpeta donde está `HexLauncher.exe`

## 🛡️ Solución de medio plazo (gratis con esfuerzo)

### 4. Auto-firmar con certificado propio

Podés crear un certificado code-signing gratis y firmar el `.exe`. **No
elimina el warning de SmartScreen completamente**, pero reduce falsos
positivos en algunos antivirus.

```powershell
# Crear certificado self-signed
$cert = New-SelfSignedCertificate `
    -Subject "CN=HexLauncher, O=Open Source, C=US" `
    -Type CodeSigningCert `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -NotAfter (Get-Date).AddYears(5)

# Exportar a .pfx
$password = ConvertTo-SecureString -String "tu_password" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "HexLauncher.pfx" -Password $password

# Firmar el .exe
Set-AuthenticodeSignature -FilePath "dist\HexLauncher.exe" `
    -Certificate $cert -TimestampServer "http://timestamp.digicert.com"
```

**Limitación:** Windows SmartScreen sigue mostrando warning hasta que el
certificado acumule reputación (puede tomar semanas o nunca, ya que no
es de una CA reconocida).

## 💰 Solución definitiva (con costo)

### 5. Certificado de code signing de una CA reconocida

| CA | Precio/año | SmartScreen |
|---|---|---|
| Certum (Open Source) | Gratis (solo para OSS) | ✅ Resuelto |
| SignPath.io | Gratis (OSS) | ✅ Resuelto |
| SSL.com | ~$70 | ✅ Resuelto |
| DigiCert | ~$300 | ✅ Resuelto |
| Sectigo | ~$180 | ✅ Resuelto |
| **EV Code Signing** | **$300-500** | ✅✅ **Sin warning desde día 1** |

**EV (Extended Validation) es el único que bypasea SmartScreen
inmediatamente** sin tener que acumular reputación.

**Para OSS gratis:**
- **Certum Open Source Code Signing** (https://shop.certum.eu) —专为 open source, gratis para proyectos aprobados
- **SignPath.io** — gratis para OSS, más moderno

## 🔄 Solución alternativa: cambiar de packager

### 6. Nuitka en vez de PyInstaller

**Nuitka** compila Python a C y luego a binario nativo. Los antivirus
lo flaggean mucho menos porque:
- El binario es nativo, no usa un bootloader compartido
- El patrón de desempaquetar `%TEMP%` desaparece
- Es compilado, no interpretado

```bash
pip install nuitka
nuitka --standalone --onefile --windows-disable-console `
       --windows-icon-from-ico=Hex.ico `
       --output-filename=HexLauncher.exe `
       main.py
```

**Resultado:** binario nativo, mucho más legítimo, **tasa de detección
reportada ~3-5% vs ~70% de PyInstaller**.

## 🎯 Mi recomendación

Por **corto plazo** (hoy):
1. ✅ Subí a GitHub Releases
2. ✅ Reportá a Microsoft
3. ✅ Agregá instrucciones de exclusión en el README

Por **mediano plazo** (esta semana):
4. 🔄 Probá Nuitka — es el cambio más impactante con esfuerzo moderado

Por **largo plazo** (cuando tengas usuarios activos):
5. 💰 Certum Open Source cert (gratis) o SignPath.io para tu proyecto

Si querés, te puedo **migrar a Nuitka** y comparar resultados. Es un
cambio de ~1 hora de trabajo.
