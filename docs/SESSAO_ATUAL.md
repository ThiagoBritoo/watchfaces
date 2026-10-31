# Sessão atual

## Objetivo
Coleção de watchfaces em **Watch Face Format (v2)** para o Galaxy Watch6 Classic. Primeira entrega:
**Cronos** (clássico realista) como prova de conceito, antes das outras linhas (retrô, lunar, minimalistas).

## Decisões
- WFF **v2**, `minSdk 34`, Gradle com um módulo por watchface (`faces/<nome>`).
- Assets e XML **gerados por script** (`tools/`), versionados no repositório para compilar sem Python.
- Espaço de coordenadas 480x480. Imagens PNG em `drawable-nodpi`.
- Validação própria (`tools/validar.py`) baseada nos XSDs oficiais vendorizados; o validador oficial do
  Google **não foi rodado** (compilar código externo foi bloqueado neste ambiente).
- Sem Android SDK neste ambiente (`dl.google.com` bloqueado): **nada foi compilado em APK**.

## Feito
- Pesquisa da documentação oficial (versões, `AnalogClock`, `Sweep`/`Tick`, `Variant`, `ComplicationSlot`,
  `DefaultProviderPolicy`, configurações, `Flavors`, limites de memória, depuração por Wi-Fi).
- Projeto Gradle (AGP 9.0.0, Gradle 9.2.1, wrapper), manifesto, `watch_face_info.xml`, strings (en/pt).
- **Cronos**: 3 temas, 2 estilos de ponteiro, 6 cores de destaque, ponteiro de segundos suave/mecânico,
  3 complicações, engrenagem animada, Flavors, modo ambiente com contornos.
- `tools/gerar.py` (assets + XML + prévias) e `tools/validar.py` (estrutura, recursos, configs, expressões, memória).
- Prévias em `previews/`. Memória estimada: ~2 MB interativo e ~1 MB ambiente (padrão).
- README e `docs/INSTALAR.md` (ADB por Wi-Fi) e `docs/WFF_NOTAS.md`.

## Em andamento / dúvidas abertas
- **Primeiro build real**: compilar com Android Studio, instalar e conferir no relógio. Pontos de risco:
  versão do AGP/Android Studio, `Tick strength/duration`, posição do texto das complicações, `Transform angle`
  em `PartImage` (a engrenagem), `ListConfiguration` repetido (mesmo id usado em vários grupos da cena).
- Conferir se o `Preview` (450x450) é aceito como está.

## Próximos passos
1. Você compila e instala (ver `docs/INSTALAR.md`) e manda fotos/prints e mensagens de erro.
2. Ajustes finos de tamanho, posição e bateria.
3. Rodar o validador oficial do Google (play-validations/memory-footprint) em uma máquina com SDK.
4. Próxima watchface: Retrô (Pip-Boy), depois Lunar e Minimalistas.

## Comandos para verificar
```bash
pip install -r tools/requirements.txt
python tools/gerar.py cronos       # regenera PNGs, XML e prévias
python tools/validar.py cronos     # valida XML/recursos/memória
./gradlew :faces:cronos:assembleDebug   # precisa do Android SDK (no seu computador)
```

## Arquivos principais
`tools/faces/cronos_assets.py` (desenho), `tools/faces/cronos_xml.py` (XML), `tools/faces/cronos_previa.py`,
`faces/cronos/src/main/res/raw/watchface.xml` (gerado), `previews/cronos_folha.png`.
