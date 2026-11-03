# Referências de estilo e como cada uma vira Watch Face Format

Análise dos prints enviados. As referências são **inspiração**: o objetivo é levar cada ideia mais longe,
com arte própria. Não copiamos marcas, logotipos nem arte de terceiros.

## 1. Clássico realista (prioridade): "RC One", "Frost", "Noir" e a branca com romanos

| O que se vê | Como fazer em WFF | Estado na Cronos |
|---|---|---|
| Mostradores analógicos com escala e agulha (bateria, passos, etc.) | Escala em PNG; agulha = `PartImage` com `Transform target="angle"` dentro de `Complication type="RANGED_VALUE"` | Feito (2 mostradores) |
| Engrenagens aparentes no centro, atrás dos ponteiros | PNGs de engrenagem girando por `Transform angle` com `[SECOND]` | Feito (3 engrenagens engrenadas) |
| Campos de texto nos cantos (`LON 9:08`, `STEPS 5500`) | `ComplicationSlot` com `BoundingBox` e `SHORT_TEXT` (título + valor) | Feito (4 campos) |
| Marcador em cunha no 12h | PNG com facetas | Feito |
| Bisel com escala e números | PNG | Feito |
| Índices aplicados em metal com lume | PNG com bisel, sombra e inlay | Feito |
| Ponteiros largos facetados com lume e sombra | PNG + sombra em `HourHand`/`MinuteHand` extras | Feito (espada e bastão) |
| Variação de cor (bronze → azul, vermelho, dourado) | `ListConfiguration` de tema + `ColorConfiguration` de destaque + `Flavors` | Feito (3 temas, 6 cores) |
| Data em janela (RC One: `MON 21`) | `PartText` com `[DAY_OF_WEEK_S]`/`[DAY_Z]` | Feito (texto; janela fica para depois) |
| Algarismos romanos (branca com dourado) | PNG de mostrador | Pendente (tema extra) |
| Mostradores com brilho neon/ciano (a escura com ciano) | Cor de destaque + camada de brilho | Pendente (tema extra) |
| Mostrador colorido em formato "bolha" (Noir/Frost com gradiente de cobre) | PNGs com mais gradiente | Parcial |

## 2. Retrô: Pip-Boy

Tela CRT verde ou âmbar: hora grande em duas linhas (`10` / `08`), segundos pequenos, dia da semana em
caixa invertida, passos, horário do pôr do sol, barra de bateria `PWR 89/100`, mascote animado, carcaça
com botões laranja.

| Elemento | WFF |
|---|---|
| Hora grande em duas linhas, estilo pixel | `DigitalClock` + `TimeText` com fonte própria **ou** `BitmapFonts` (a fonte bitmap pesa na memória do ambiente) |
| Barra de bateria e passos | `PartDraw` com `Rectangle` e `Transform` por `[BATTERY_PERCENT]`/`[STEP_PERCENT]`; textos com `[STEP_COUNT]` |
| Scanlines e brilho CRT | PNG semi-transparente por cima; leve variação por `Gyro` (a confirmar) |
| Mascote animado | `PartAnimatedImage` ou troca de quadros por `[SECOND]`; frames pequenos para caber na memória |
| Verde/âmbar | `ListConfiguration` com dois fundos ou `ColorConfiguration` + `tintColor` |
| Ambiente | Texto verde fino em fundo preto, sem scanlines |

**Observação de direitos:** Pip-Boy, Vault Boy e a identidade "Fallout" são marcas da Bethesda. Para uso
pessoal no seu relógio não há problema técnico, mas **não é publicável** na Play Store. Faremos um mascote
**original** no mesmo espírito (desenho retrô de revista dos anos 1950) para poder publicar depois.

## 3. Super informativo / lunar

Anel de calendário (meses e dias) que gira, dia da semana em subdial, sol/lua animado em uma janela e
ponteiro de segundos laranja.

| Elemento | WFF |
|---|---|
| Anel de dias/meses com o dia atual destacado | PNG do anel girado por `Transform angle` com `[DAY_OF_YEAR]` ou `[MONTH_0_11]`/`[DAY]` |
| Dia da semana em subdial | Disco com 7 nomes girado por `[DAY_OF_WEEK]` |
| Sol/lua animado | `PartImage` movendo em arco por `[HOUR_0_23_MINUTE]`; fase da lua com `[MOON_PHASE_TYPE]` |
| Segundos laranja | `SecondHand` com `tintColor` |

Legibilidade: muita informação em 480 px exige hierarquia (anel externo pequeno e discreto, só a data de
hoje em destaque).

## 4. Minimalistas

Referência de limpeza: a branca com `COMPL. 01/02/03`, anel de escala, hora grande e três complicações
em cápsula. Em WFF: `DigitalClock` grande, `ComplicationSlot` com `BoundingRoundBox`, `Arc` para progresso.

## Próximas decisões (para você)

- Ordem das próximas faces: Retrô, Lunar, Minimalista? (hoje assumimos esta).
- Cronos: quer um tema extra com **algarismos romanos** (branco/dourado) e outro **ciano neon**?


## Implementado até agora (3 nov 2026)

| Referência | Face | Notas |
|---|---|---|
| Clássico realista (RC One, Frost, Noir, romanos) | **Cronos** | 5 temas (inclui Romanos e Neon), 2 ponteiros, 7 cores, engrenagens engrenadas |
| Pip-Boy (retrô) | **Terminal CRT** | Arte original: robô retrô animado, fonte pixel, 4 cores de fósforo; sem marcas de terceiros |
| Super informativo / lunar | **Sol e Lua** | Anel de meses/dias, semana, sol/lua em arco, fase da lua, 2 temas |
| Minimalistas (branca com COMPL.) | **Linha** (elegante) e **Painel** (esportiva com clima) | Linha digital/analógica; Painel com 3 mostradores e anel de segundos |

Diferenças deliberadas em relação às referências: nada de logotipos, nomes ou marcas; mascote original; textos em português.
