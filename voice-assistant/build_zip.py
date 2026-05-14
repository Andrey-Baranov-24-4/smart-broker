"""Собирает scenario.zip для загрузки в SmartApp Studio.
Запускать из папки voice-assistant/:  python build_zip.py
"""
import os
import zipfile

OUTPUT = "scenario.zip"

with zipfile.ZipFile(OUTPUT, "w", zipfile.ZIP_DEFLATED) as zf:
    for item in ("chatbot.yaml", "caila_import.json"):
        zf.write(item)
    for folder in ("src", "test"):
        for root, _, files in os.walk(folder):
            for fname in files:
                zf.write(os.path.join(root, fname))

print(f"Создан {OUTPUT} — загрузите в SmartApp Studio (Code for SmartApp).")
