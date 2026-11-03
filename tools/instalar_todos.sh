#!/usr/bin/env bash
# Instala no relógio TODOS os .apk de uma pasta (por exemplo, a pasta descompactada do artefato "watchfaces-apk" do GitHub Actions).
# Uso:  tools/instalar_todos.sh /caminho/da/pasta [IP:PORTA]
# Antes: pareie e conecte o relógio por Wi-Fi (veja docs/INSTALAR.md). Se informar IP:PORTA, o script usa "adb -s IP:PORTA".
set -u
PASTA="${1:-.}"
ALVO=()
[ -n "${2:-}" ] && ALVO=(-s "$2")
ok=0; falha=0
while IFS= read -r apk; do
  if adb "${ALVO[@]}" install -r "$apk" > /tmp/adb_saida.txt 2>&1 && grep -q Success /tmp/adb_saida.txt; then
    echo "OK     $(basename "$apk")"; ok=$((ok+1))
  else
    echo "FALHOU $(basename "$apk"): $(tail -1 /tmp/adb_saida.txt)"; falha=$((falha+1))
  fi
done < <(find "$PASTA" -name '*.apk' | sort)
echo "Instalados: $ok | falhas: $falha"
