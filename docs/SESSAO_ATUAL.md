# Sessão atual

## Objetivo
Coleção de watchfaces em **Watch Face Format (v2)** para o Galaxy Watch6 Classic, com acabamento, animação,
personalização, AOD econômico e bateria respeitada.

## Estado (3 nov 2026)
43 watchfaces prontas, geradas por script, validadas por script próprio **e pelo validador oficial do Google no CI**,
e compiladas em APK pelo GitHub Actions (todas passam no `wff-validator` v2 e no `memory-footprint` do Google). **Nenhuma foi testada em relógio real ainda.**

| Face | Estilo | Pontos principais |
|---|---|---|
| `cronos` | Clássico realista | 5 temas, 2 ponteiros, 7 cores, 6 complicações, engrenagens engrenadas, AOD |
| `aviador` | Clássico realista (piloto) | 3 mostradores, algarismos com lume, janela de data, reaproveita ponteiros da Cronos |
| `crt` | Retrô (terminal de fósforo) | Fonte pixel (BitmapFont), 4 cores por `tintColor`, mascote animado original |
| `lunar` | Super informativo | Anel de meses/dias, subdial da semana, sol/lua em arco, fase da lua |
| `linha` | Minimalista | Digital fino ou analógico, anéis de progresso, cápsulas, 4 paletas |
| `pura` | Minimalista extremo | Analógica só de traços, ponteiros dauphine, 4 paletas, 5 destaques |
| `regua` | Abstrata | Escalas giratórias sob cápsula, hora gigante |
| `fragmento` | Abstrata | Dois mostradores gigantes recortados, linha inclinada |
| `deslizante` | Abstrata/digital | Réguas de números que deslizam (Transform x/alpha/scale) |
| `matriz` | Retrô-futurista | Fonte de pontos LED 5x7 original, 4 segmentos de anel, 10 cores |
| `montanha` | Arte de linha | Paisagem, sol girando, régua de minutos, TextCircular |
| `mare` | Abstrata | Nível de água sobe no dia (SECONDS_IN_DAY), ondas com SECOND_MILLISECOND |
| `aneis` | Abstrata | 4 anéis concêntricos com cabeças luminosas |
| `pendulo` | Abstrata | Pêndulo (Group angle=cos(SECOND·π)), hora contra-rotacionada dentro do peso |
| `eclipse` | Abstrata | Lua (PartImage x por minuto) cruza o Sol; corona procedural |
| `ceu` | Céu real | Faixa de gradiente 24h deslizando (SECONDS_IN_DAY), sol/lua em Group com pivô na base |
| `gigante` | Tipografia | Números BLACK enormes + anel de segundos |
| `binario` | Abstrata | BCD com Transform alpha por bit (floor/%) |
| `vinil` | Objeto | Disco rotativo a cada segundo, braço fixo |
| `bussola` | Instrumento | Mostrador + ponteiros em duas peças (cauda + ponta tingida) |
| `constelacao` | Abstrata | Anéis de estrelas e Group rotativo com linha até o centro |
| `barras` | Minimalista | 4 barras com Transform width |
| `odometro` | Mecânico | Colunas de dígitos com rolagem nos últimos 10 s e vai-um |
| `radar` | Retrô-instrumento | Varredura (conic alpha) girando por minuto, alvos de hora/minuto |
| `mondrian` | Arte | Rect com Transform x/y/width/height ligados a MINUTE/HOUR_0_11_MINUTE |
| `ampulheta` | Objeto | Areia = máscara tingida + retângulos pretos de altura animada |
| `vintequatro` | Instrumento | Ponteiro de 24 h (uma volta/dia) + subdial de minutos |
| `aurora` | Abstrata | 3 bolhas radiais com Transform x/y (sin/cos de SECONDS_IN_DAY) |
| `moire` | Abstrata | 2 PNGs de anéis; o segundo orbita com os minutos |
| `engrenagens` | Mecânico | 3 engrenagens engrenadas com fases calculadas; hora no cubo |
| `osciloscopio` | Retrô-instrumento | Onda PNG 960 px deslizando por segundo |
| `topo` | Mapa | Curvas de nível por ruído + pinos em Group rotativo |
| `calendario` | Prático | 42 células com Transform alpha (primeiro dia do mês por expressão) + marcador de hoje |
| `lua` | Céu | 8 PNGs de fase com alpha por MOON_PHASE_TYPE (mapeamento assumido) |
| `lcd` | Retrô | 7 segmentos (BitmapFont gerada), 3 telas |
| `flip` | Retrô | Cartões com dobradiça, 5 paletas |
| `ondas` | Abstrata | 4 elipses com Transform x/y/width/height + alpha por SECOND_MILLISECOND |
| `duo` | Gráfica | Dois blocos de cor + números BLACK |
| `solpedra` | Instrumento | Relógio de sol com sombra rotativa (pivô no gnômon) |
| `espectro` | Abstrata | Faixa HSV 2400 px deslizando por SECONDS_IN_DAY |
| `pontilhado` | Abstrata | 60 pontos com alpha por distância do ponteiro de segundos |
| `palavras` | Texto | Hora por extenso (alpha por [HOUR_1_12] e floor([MINUTE]/5)) |
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

## Riscos novos (faces abstratas) que só o relógio confirma
- `Transform` de `x`, `alpha`, `scaleX/scaleY` em `PartText` (Deslizante) e `numberFormat("00", ...)` em `Parameter`.
- `SECOND_MILLISECOND` (Maré): ondas suaves, mas redesenha em alta frequência no modo ativo (mais bateria; só com a tela ligada).
- `TextCircular` (Montanha): raio efetivo do texto curvo e direção; `Group angle` dentro de complicação (textos laterais).
- `Arc` com `endAngle` por expressão partindo de `startAngle=0` (Anéis, Matriz): 0 = 12h confirmado pelo exemplo oficial.
- Imagens maiores que a tela (Fragmento: 700x700 e 540x540; Maré: 960x120) e `Group` de 480x480 girando (Anéis).

## Riscos das 10 faces mais novas
- `Group` com `pivotY="0"` ou `"1"` (Pêndulo, Céu do Dia) e `Group` contra-rotacionado; `Transform` de `alpha` com ternário e `abs`/`floor`/`%`.
- `numberFormat("0", expr)` e `BLACK` (peso da fonte do sistema) em Gigante/Odômetro; largura dos dígitos pode diferir da prévia.
- Odômetro/Binário dependem de `[HOUR_0_23]` (24 h sempre; não respeita 12 h).
- `[SECOND]` atualiza 1 vez por segundo: pêndulo, disco e rolagem andam em passos (efeito de tic-tac, de propósito).

## Próximos passos
1. Você instala (ver `docs/INSTALAR.md`, atalho com APKs prontos do GitHub Actions) e manda prints/erros.
2. Ajustes finos a partir do que aparecer no relógio.
3. Novas faces/temas (ver Roadmap no README).

## Comandos para verificar
```bash
pip install -r tools/requirements.txt
python tools/gerar.py <nome em faces/>   # regenera PNGs, XML e prévias
python tools/validar.py <nome>                   # valida XML/recursos/memória
./gradlew assembleDebug                          # precisa do Android SDK (o CI faz isso)
```

## Arquivos principais
`tools/faces/*.py` (um módulo por watchface), `tools/wf/desenho.py` (primitivas), `tools/wf/modulo.py` (módulo Android),
`tools/validar.py`, `.github/workflows/build.yml`, `previews/*_folha.png`, `docs/REFERENCIAS.md`, `docs/WFF_NOTAS.md`.
