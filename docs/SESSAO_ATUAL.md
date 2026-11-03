# Sessão atual

## Objetivo
Coleção de watchfaces em **Watch Face Format (v2)** para o Galaxy Watch6 Classic, com acabamento, animação,
personalização, AOD econômico e bateria respeitada.

## Estado (3 nov 2026)
5 watchfaces prontas, geradas por script, validadas por script próprio **e pelo validador oficial do Google no CI**,
e compiladas em APK pelo GitHub Actions. **Nenhuma foi testada em relógio real ainda.**

| Face | Estilo | Pontos principais |
|---|---|---|
| `cronos` | Clássico realista | 5 temas, 2 ponteiros, 7 cores, 6 complicações, engrenagens engrenadas, AOD |
| `crt` | Retrô (terminal de fósforo) | Fonte pixel (BitmapFont), 4 cores por `tintColor`, mascote animado original |
| `lunar` | Super informativo | Anel de meses/dias, subdial da semana, sol/lua em arco, fase da lua |
| `linha` | Minimalista | Digital fino ou analógico, anéis de progresso, cápsulas, 4 paletas |
| `painel` | Digital esportiva | Clima (BitmapFont de ícones), hora grande, 3 mostradores com complicação, anel de segundos |

## Decisões
- WFF **v2**, `minSdk 34`, um módulo Gradle por watchface (`faces/<nome>`), criado por `tools/wf/modulo.py`.
- Assets e XML **gerados por script** (`tools/`), versionados para compilar sem Python.
- CI (`.github/workflows/build.yml`): valida XML (script próprio), compila `assembleDebug`, publica os APKs como
  artefato e roda os validadores oficiais (`wff-validator` e `memory-footprint`).
- Paleta por `ColorConfiguration` (`[CONFIGURATION.id.N]`) quando o tema é só cor (Linha); `ListConfiguration` quando
  muda a arte (Cronos, Sol e Lua).
- Terminal CRT usa arte original (sem Pip-Boy/Vault Boy/Fallout) para ser publicável.

## Achados importantes desta sessão
- O validador oficial exigiu `name` em **todo `<Group>`** (WFF v2). `tools/wf/modulo.py:nomear_grupos` agora nomeia
  automaticamente e `tools/validar.py` passou a checar atributos obrigatórios.
- O runner do GitHub já traz o Android SDK; a action `setup-android` falhou e foi removida.
- Fontes de dados usadas: `SECOND`, `HOUR_0_23_MINUTE`, `MONTH_0_11`, `DAY`, `DAY_OF_WEEK`, `MOON_PHASE_TYPE`,
  `BATTERY_PERCENT`, `STEP_PERCENT`, `STEP_COUNT`, `COMPLICATION.*` (conferidas na tabela oficial).
- Operadores `%`, `?:`, `&&`, `||`, `clamp`, `round` confirmados na referência de expressões.

## Riscos que só o relógio confirma
1. `BitmapFont` com `tintColor` no Terminal CRT (se o tom não pegar, o texto fica branco).
2. `Transform target="angle"` em `PartImage` dentro de `Complication type="RANGED_VALUE"` (agulhas da Cronos).
3. `Tick strength/duration` (segundos mecânico da Cronos) e `Sweep frequency=15`.
4. Mapeamento de `MOON_PHASE_TYPE` 0..7 (assumido: 0 nova, 2 quarto crescente, 4 cheia, 6 quarto minguante).
5. Fonte `SYNC_TO_DEVICE` em tamanho 132 na Linha (a fonte real do relógio pode ser mais larga que a Inter da prévia).
6. Posição e legibilidade das complicações (a prévia usa textos fixos).
7. Clima (Painel): depende de o usuário permitir dados de clima; o mapeamento código -> ícone vem do exemplo oficial.

## Próximos passos
1. Você instala (ver `docs/INSTALAR.md`, atalho com APKs prontos do GitHub Actions) e manda prints/erros.
2. Ajustes finos a partir do que aparecer no relógio.
3. Novas faces/temas (ver Roadmap no README).

## Comandos para verificar
```bash
pip install -r tools/requirements.txt
python tools/gerar.py <cronos|crt|lunar|linha|painel>   # regenera PNGs, XML e prévias
python tools/validar.py <nome>                   # valida XML/recursos/memória
./gradlew assembleDebug                          # precisa do Android SDK (o CI faz isso)
```

## Arquivos principais
`tools/faces/*.py` (um módulo por watchface), `tools/wf/desenho.py` (primitivas), `tools/wf/modulo.py` (módulo Android),
`tools/validar.py`, `.github/workflows/build.yml`, `previews/*_folha.png`, `docs/REFERENCIAS.md`, `docs/WFF_NOTAS.md`.
