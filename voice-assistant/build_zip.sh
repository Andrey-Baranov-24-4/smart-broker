#!/usr/bin/env bash
# Собирает scenario.zip для загрузки в SmartApp Studio → Code for SmartApp
# Запускать из папки voice-assistant/

set -e

OUTPUT="scenario.zip"

rm -f "$OUTPUT"

zip -r "$OUTPUT" \
    chatbot.yaml \
    caila_import.json \
    src/ \
    test/

echo "Готово: $(pwd)/$OUTPUT"
echo "Загрузите этот файл в SmartApp Studio (Code for SmartApp)."
