# Migración HexLauncher

Esta carpeta contiene todo lo relacionado con la migración futura del launcher
a un stack más moderno (actualmente recomendado: **Tauri**).

## 📄 Contenido

- [`MIGRATION.md`](./MIGRATION.md) — Plan completo de migración a Tauri:
  comparativa con stack actual, requisitos, timeline, fases de trabajo.

## 🚧 Estado actual

**No se está ejecutando la migración.** El launcher sigue corriendo en
CustomTkinter + PyInstaller (ver [`BUILD.md`](../BUILD.md) en la raíz).

## 📦 Si decidís migrar

1. Copiá esta carpeta a un proyecto nuevo (ej. `hexlauncher-tauri/`)
2. Seguí el plan de `MIGRATION.md`
3. El proyecto original seguirá funcionando en `../`
