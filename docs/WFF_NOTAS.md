# Notas do Watch Face Format (WFF)

Tudo abaixo foi **conferido** na documentação oficial (developer.android.com/reference/wear-os/wff,
developer.android.com/training/wearables/wff), nos XSDs oficiais (google/watchface) e nos exemplos do
repositório android/wear-os-samples (`WatchFaceFormat/`). O que não deu para confirmar está marcado **(não confirmado)**.

## Versões

| WFF | Wear OS mínimo | API |
|---|---|---|
| 1 | 4 | 33 |
| 2 | 5 | 34 |
| 3 | 5.1 | 35 |
| 4 | 6 | 36 |

Este projeto usa a **v2**: Flavors e `minSdk 34`. Cada recurso novo é marcado com a versão na referência.
Desde jan/2026 o WFF é obrigatório para instalar watchfaces em qualquer Wear OS.

## Estrutura de um módulo

- `AndroidManifest.xml`: `android:hasCode="false"` (obrigatório: sem código), `<uses-feature android:name="android.hardware.type.watch"/>`
  e `<property android:name="com.google.wear.watchface.format.version" android:value="2"/>`.
- `res/raw/watchface.xml`: raiz `<WatchFace width height clipShape>`; filhos: `Metadata`, `UserConfigurations`, `Scene`.
  `width/height` definem um **espaço de coordenadas**, não pixels reais: o sistema escala.
- `res/xml/watch_face_info.xml`: `Preview` (obrigatório), `Editable`, `MultipleInstancesAllowed`, `FlavorsSupported`.
- Imagens em `res/drawable*/`; referenciadas por nome (`resource="fundo_rc"`).

## Elementos usados na Cronos

| Elemento | Uso | Observação |
|---|---|---|
| `Scene` | Ordem do XML = ordem de desenho (de baixo para cima) | Ponteiros e complicações no fim reduz memória no ambiente |
| `Group`, `PartImage`, `PartText`, `PartDraw` | Camadas | `Group` aceita `Variant`, `ListConfiguration` |
| `AnalogClock` + `HourHand`/`MinuteHand`/`SecondHand` | Ponteiros | No máximo 2 de cada tipo por `AnalogClock` (usamos sombra + ponteiro) |
| `Sweep frequency` (2, 5, 10, 15) / `Tick strength duration` | Movimento do ponteiro de segundos | `Variant` vem **antes** de `Sweep`/`Tick` no XML |
| `Variant mode="AMBIENT" target="alpha"` | Esconder/mostrar no modo ambiente | Único `mode` válido hoje é `AMBIENT` |
| `ListConfiguration` / `ColorConfiguration` | Opções do usuário | Na cena, `ListConfiguration > ListOption > (um filho)` seleciona conteúdo; use `Group` para vários |
| `[CONFIGURATION.id]` | Cor de uma `ColorOption` com uma cor | Com várias cores: `[CONFIGURATION.id.N]` |
| `Flavors` / `Flavor` / `Configuration` | Presets (v2) | Podem ajustar `DefaultProviderPolicy` por slot |
| `ComplicationSlot` + `BoundingOval` + `Complication` | Complicações | Máx. 8 slots; um `Complication` por tipo (EMPTY dispensa) |
| `DefaultProviderPolicy` | Provedor padrão do slot | Usa `defaultSystemProvider` e `defaultSystemProviderType` |
| `Transform target="angle" value="[SECOND] * 6"` | Animação por expressão | Atualiza a cada segundo |
| `Condition` / `Expressions` / `Compare` / `Default` | Layout condicional | Cada `Compare` aceita **um** filho |

Fontes de dados usadas: `SECOND`, `DAY_OF_WEEK_S`, `DAY_Z`, `COMPLICATION.TEXT`, `COMPLICATION.TITLE`,
`COMPLICATION.RANGED_VALUE_*`, `COMPLICATION.MONOCHROMATIC_IMAGE`, `COMPLICATION.SMALL_IMAGE`.

## Limites e boas práticas de memória

- **Ambiente: 10 MB. Interativo: 100 MB.** Só contam bitmaps, fontes e camadas do XML.
- Cada imagem é medida pelo tamanho descomprimido (RGBA8888 = 4 x largura x altura). Um PNG quase em
  branco de 450x450 pesa poucos KB em disco mas ~750 KB na memória.
- O sistema assume **até 3 camadas em tela cheia no ambiente**, 2 estáticas: fundo, partes móveis, resto.
- Recorte imagens ao tamanho usado, reaproveite o mesmo recurso, prefira `Arc` a muitas imagens para
  barras de progresso.
- Fontes bitmap grandes costumam ser o maior consumo no ambiente.

## Modo ambiente (AOD)

- A tela AMOLED apaga pixels pretos: **menos pixels acesos = menos bateria**. Evite áreas grandes
  acesas, texturas e cores claras no ambiente.
- Estratégia da Cronos: o mostrador interativo some (`alpha` 0) e entra um PNG só de contornos cinza;
  ponteiros viram contornos; sem segundos e sem complicações; data a ~50 % de opacidade.
- O sistema pode deslocar levemente a imagem para evitar burn-in **(não confirmado nos documentos lidos)**.

## Limitações e decisões

- **Sombra do ponteiro:** o WFF gira a imagem inteira em volta do pivô; o deslocamento da sombra "assado"
  no PNG gira junto. Mantivemos o deslocamento pequeno (3 a 5 px) para o erro ser imperceptível.
- **Cronógrafo funcional:** o WFF não tem elemento de cronômetro/timer próprio **(não confirmado nos
  documentos lidos)**. Os mostradores são complicações (bateria, passos, etc.).
- **Bisel giratório da Samsung** não tem fonte de dados no WFF.
- **Sweep 15 Hz** gasta mais bateria que 1 Hz; por isso existe a opção `Tick`.
- Validadores oficiais (Memory Footprint Evaluator, dwf-validator) ficam em github.com/google/watchface;
  `tools/validar.py` é uma checagem própria e **não os substitui**.

## Como o projeto valida o XML

`tools/validar.py` carrega os XSDs v2 (`third_party/wff-xsd/2`) como tabela de dados: elementos permitidos,
atributos permitidos e hierarquia. Os XSDs usam `xs:all` com `maxOccurs>1` (XSD 1.1), que o `lxml`
não valida diretamente, por isso a checagem é feita por regras extraídas deles, não por validação XSD completa.


## Achados do validador oficial e do CI (3 nov 2026)

- **Todo `<Group>` precisa de `name`** (WFF v2). Sem isso o `wff-validator` e o `memory-footprint` do Google rejeitam o XML
  ("Attribute 'name' must appear on element 'Group'"). O gerador nomeia sozinho (`tools/wf/modulo.py:nomear_grupos`).
- O jar do `wff-validator` **sai com código 0 mesmo quando reprova**; por isso o CI procura o texto "NOT valid".
- Dentro de `DigitalClock` a ordem é `Localization`, `Variant`, `TimeText` (Variant antes de TimeText).
- Dentro de `SecondHand`, `Variant` vem antes de `Sweep`/`Tick`.
- **Paleta de cores**: um `ColorOption` aceita várias cores em `colors="#a #b #c #d"` e se lê com `[CONFIGURATION.id.0..3]`.
  Foi o jeito usado em Linha e Painel para temas (fundo, texto, secundário, cápsula) sem duplicar o XML.
- **BitmapFont** (fonte feita de PNGs): cada `Character name="X" resource="png" width height`; usada em `Text`/`TimeText`
  com `<BitmapFont family="nome" size="altura" />`. Os caracteres precisam existir no conjunto (letras minúsculas/acentuadas
  foram mapeadas para as mesmas imagens). Serviu para a fonte pixel do Terminal CRT e para os ícones do clima.
- **Expressões** confirmadas na referência: `%`, `?:`, `&&`, `||`, `==`, `clamp`, `round`, `floor`, `fract`, `sin/cos`, `numberFormat`,
  `icuText`. Em atributos XML use `&gt;`, `&lt;`, `&amp;`.
- **Clima** (v2): `WEATHER.IS_AVAILABLE`, `IS_DAY`, `CONDITION` (0..15), `TEMPERATURE`, `DAY_TEMPERATURE_HIGH/LOW`.
  A relação código -> ícone vem do exemplo oficial "Weather" do Google.
- **Fase da lua**: `MOON_PHASE_TYPE` 0..7 e `MOON_PHASE_POSITION` 0..28 existem; o significado exato de cada código 0..7
  **não foi confirmado** (assumido: 0 nova, 2 quarto crescente, 4 cheia, 6 quarto minguante).
- O runner `ubuntu-latest` do GitHub já tem Android SDK; `android-actions/setup-android` falhou (pacote `tools` ausente).
