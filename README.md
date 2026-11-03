# watchfaces

Coleção de watchfaces para o **Samsung Galaxy Watch6 Classic** (Wear OS), feitas em
**Watch Face Format (WFF)**: o formato declarativo (XML) do Google e da Samsung. Sem código
Kotlin/Java dentro do relógio: o Wear OS lê o XML e as imagens e desenha tudo sozinho, o que
ajuda bateria e desempenho.

> **Status:** 6 watchfaces prontas (Cronos, Aviador, Terminal CRT, Sol e Lua, Linha, Painel). O GitHub Actions **compila os APKs de
> verdade** a cada push (aba *Actions*, seção *Artifacts*). **Ainda não foram testadas em um relógio real**:
> falta você instalar e conferir. Veja "Como instalar" e "Estado e limitações".

## Prévias

| Cronos (clássico realista) | Aviador (piloto) |
|---|---|
| ![Cronos](previews/cronos_folha.png) | ![Aviador](previews/aviador_folha.png) |

| Terminal CRT (retrô) |
|---|
| ![Terminal CRT](previews/crt_folha.png) |

| Sol e Lua (calendário em anel) | Linha (minimalista) |
|---|---|
| ![Sol e Lua](previews/lunar_folha.png) | ![Linha](previews/linha_folha.png) |

| Painel (digital esportiva com clima) |
|---|
| ![Painel](previews/painel_folha.png) |

> As prévias são **simulações em Python** feitas com os mesmos PNGs que vão no APK. Servem para
> conferir desenho, proporção e posição. O brilho, as animações, a fonte do sistema e as complicações reais
> só aparecem no relógio ou no emulador.

## Relógio-alvo

| Item | Valor |
|---|---|
| Modelo | Samsung Galaxy Watch6 Classic (43 mm ou 47 mm) |
| Tela | AMOLED redonda, 1,5" (47 mm: 480x480; 43 mm: 432x432) |
| Sistema | Wear OS 5 (One UI Watch) ou mais novo |
| Formato | Watch Face Format **versão 2** (`minSdk 34`) |
| Bisel | O bisel giratório físico **não** é lido pelo WFF; a interação fica na tela e nos botões |

O XML usa um espaço de coordenadas fixo de **480x480**; o sistema reescala para 432x432 no modelo de 43 mm.
Por que a versão 2 e não a 1? A v2 traz os *Flavors* (presets de tema/complicações) e o Wear OS 5,
que o Watch6 Classic já recebeu. A v1 rodaria no Wear OS 4, mas sem os presets.

## Watchfaces

| Pasta | Nome | Estilo | Personalização |
|---|---|---|---|
| `faces/cronos` | **Cronos** | Clássico realista: 2 mostradores com agulha, engrenagens aparentes engrenadas, 4 campos de texto | 5 temas (preto/vermelho, branco/bronze/azul, preto/dourado, branco/dourado com romanos, grafite/ciano neon), 2 estilos de ponteiro, 7 cores, segundos suave/mecânico, 6 complicações, presets |
| `faces/aviador` | **Aviador** | Clássico realista: relógio de piloto, algarismos com lume, triângulo no 12h, janela de data, serrilhado do aro | 3 mostradores (preto fosco, oliva militar, azul sunburst), 2 estilos de ponteiro, 5 cores, segundos suave/mecânico, 1 complicação |
| `faces/crt` | **Terminal CRT** | Retrô: tela de fósforo, scanlines, mascote robô original animado, hora grande em fonte pixel | 4 cores de fósforo (verde, âmbar, ciano, branco), 2 complicações |
| `faces/lunar` | **Sol e Lua** | Super informativo: anel de meses e dias, subdial do dia da semana, janela com sol/lua que anda no céu e fase da lua real | 2 mostradores (claro/escuro), 5 cores de destaque, 2 complicações |
| `faces/linha` | **Linha** | Minimalista: hora fina grande ou ponteiros finos, anéis de passos/bateria, cápsulas | 4 temas de paleta, 5 destaques, estilo digital/analógico, anéis opcionais, 3 complicações |
| `faces/painel` | **Painel** | Digital esportiva: hora grande, data, clima (ícone, temperatura, máx/mín), 3 mostradores circulares, anel dos segundos | 4 temas, 5 destaques, anel dos segundos opcional, 3 complicações |

Detalhes e como cada referência de estilo vira Watch Face Format: **[docs/REFERENCIAS.md](docs/REFERENCIAS.md)**.

Em todas: **modo ambiente (AOD)** só com contornos/traços finos (poucos pixels acesos), sem textura, sem segundos,
sem complicações; memória estimada de 1 a 3 MB no modo normal e abaixo de 2 MB no ambiente (limites do Google: 100 MB e 10 MB).

## Estrutura de pastas

```
watchfaces/
├── README.md                  este arquivo
├── settings.gradle.kts        lista os módulos (um por watchface)
├── build.gradle.kts, gradle/  configuração do Gradle (plugin Android)
├── gradlew, gradlew.bat       Gradle wrapper (baixa o Gradle certo sozinho)
├── .github/workflows/build.yml   CI: valida o XML, compila os APKs e roda os validadores do Google
├── faces/
│   ├── cronos/ aviador/ crt/ lunar/ linha/ painel/   um módulo Android = uma watchface
│   └── <nome>/src/main/
│       ├── AndroidManifest.xml          versão do WFF, hasCode=false
│       └── res/
│           ├── raw/watchface.xml        GERADO: o mostrador em XML
│           ├── drawable-nodpi/*.png     GERADO: fundos, ponteiros, fontes pixel, ícones
│           ├── xml/watch_face_info.xml  prévia e flags (editável)
│           └── values, values-pt/       textos (inglês e português)
├── tools/                     geração reproduzível por script (Python)
│   ├── gerar.py               gera PNGs + XML + prévias:  python tools/gerar.py <cronos|aviador|crt|lunar|linha|painel>
│   ├── validar.py             valida XML contra os XSDs oficiais e estima memória
│   ├── wf/desenho.py          primitivas (gradientes, metal, sombras, texto em arco)
│   ├── wf/modulo.py           cria o módulo Android (manifesto, Gradle, strings) de uma watchface
│   ├── faces/cronos*.py       Cronos (assets, xml, prévia);  faces/aviador.py, crt.py, lunar.py, linha.py, painel.py
│   └── fonts/                 Inter e Liberation Serif (licença OFL), só para gerar as imagens
├── previews/                  prévias em PNG (geradas)
├── third_party/wff-xsd/       esquemas XSD oficiais do WFF v2 (Apache 2.0)
└── docs/
    ├── INSTALAR.md            passo a passo para iniciantes (relógio, celular, ADB por Wi-Fi)
    ├── REFERENCIAS.md         análise dos prints de referência e como cada estilo vira WFF
    ├── TESTE_NO_RELOGIO.md    roteiro de conferência no relógio, item por item
    ├── WFF_NOTAS.md           o que foi confirmado na documentação oficial, limites e armadilhas
    └── SESSAO_ATUAL.md        estado do trabalho e próximos passos
```

Os PNGs e o `watchface.xml` são **gerados**, mas ficam versionados para você poder compilar sem rodar
Python. Para mudar o desenho, edite os scripts em `tools/` e gere de novo.

## Como gerar os assets e as prévias

Precisa de Python 3.10+.

```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r tools/requirements.txt
python tools/gerar.py cronos      # ~30 s: reescreve PNGs, watchface.xml e previews/  (também: crt, lunar, linha)
python tools/validar.py cronos    # confere o XML e a memória
```

Confira `previews/<nome>_folha.png` **antes** de instalar no relógio.

## Como instalar

Passo a passo completo, para iniciantes (o que fazer no relógio e no celular): **[docs/INSTALAR.md](docs/INSTALAR.md)**.

**Caminho mais fácil (sem instalar o Android Studio):** o GitHub compila os APKs sozinho.
1. No GitHub, abra a aba **Actions**, clique na execução mais recente (verde) e baixe **watchfaces-apk** em *Artifacts*.
2. Descompacte. Há um `.apk` por watchface (`cronos-debug.apk`, `crt-debug.apk`, `lunar-debug.apk`, `linha-debug.apk`, `painel-debug.apk`, `aviador-debug.apk`).
3. No relógio, ative as **Opções do desenvolvedor** e a **Depuração sem fio**; pareie e conecte com `adb pair` / `adb connect`.
4. `adb install -r cronos-debug.apk` (repita para as outras).
5. No relógio, **segure o dedo no mostrador atual**, deslize até a watchface e toque nela. **Personalizar** troca tema, cores e complicações.

**Compilando você mesmo:** instale o Android Studio, abra esta pasta e rode `./gradlew assembleDebug`
(precisa do SDK 34; crie `local.properties` com `sdk.dir=...` se pedir). Os APKs saem em `faces/<nome>/build/outputs/apk/debug/`.

## Estado e limitações (leia)

- **Compilam no CI, mas não foram testadas em relógio real.** O build dos 4 APKs passa no GitHub Actions
  (isso confirma a estrutura Android e os recursos), porém só o relógio mostra se o desenho, as animações e as
  complicações se comportam como no preview. Se algo falhar, me mande o print e a mensagem de erro.
- **Validadores oficiais do Google** (formato e memória) rodam no CI em modo informativo; veja o resultado na
  aba *Actions* (job `validador-oficial`) e em `docs/SESSAO_ATUAL.md`.
- **Pontos de risco conhecidos** (só o relógio confirma): `BitmapFont` com `tintColor` (Terminal CRT), `Transform`
  de ângulo em complicações `RANGED_VALUE` (agulhas da Cronos), `Tick` do segundo mecânico, fonte do sistema
  (`SYNC_TO_DEVICE`) no tamanho 132 da Linha e mapeamento das fases da lua `MOON_PHASE_TYPE` 0..7 (assumido:
  0 nova, 2 quarto crescente, 4 cheia, 6 quarto minguante).
- **Sombra do ponteiro** gira junto com ele (limitação do formato): deslocamento pequeno para não aparecer.
- O **bisel giratório** do Watch6 Classic não é acessível pelo WFF; não há cronógrafo funcional (sem timer no WFF).
- Segundos suaves (15 Hz) gastam mais bateria que o salto de 1 s; por isso existe a opção "mecânico" na Cronos.
- **Terminal CRT:** inspirada em terminais retrô, com arte original; não usa Pip-Boy/Vault Boy/Fallout (marcas da Bethesda).

## Roadmap

- [x] Projeto-base, scripts de geração e validação, documentação para iniciantes
- [x] **Cronos** (clássico realista), **Terminal CRT** (retrô), **Sol e Lua** (informativo), **Linha** (minimalista)
- [x] CI no GitHub Actions: valida XML, compila APKs, roda validadores oficiais
- [ ] **Teste no Galaxy Watch6 Classic** e ajustes de posição, tamanhos e bateria (depende de você)
- [ ] Cronos: cronógrafo funcional (WFF não tem timer próprio: avaliar complicação de cronômetro)
- [ ] Terminal CRT: mais mascotes/animações, barra de passos, Pip-Boy-like fiel só para uso pessoal (não publicável)
- [ ] Sol e Lua: segundo anel de fuso horário, nascer/pôr do sol reais no arco do céu
- [ ] Mais minimalistas (ex.: uma só complicação grande, hora em palavras)
- [ ] Efeito de profundidade com sensor (`Gyro`) em detalhes do mostrador
- [ ] Meteorologia (fontes `WEATHER.*`, WFF v2) em complicações
- [ ] Publicação (bundle `.aab` assinado, ícones e capturas para a Play Store)

## Créditos e licenças

- Formato e esquemas: Google LLC / Samsung Electronics (Apache 2.0), ver `third_party/wff-xsd/`.
- Fontes Inter, JetBrains Mono e Liberation Serif (SIL OFL), usadas só na geração das imagens, ver `tools/fonts/`.
- Os mostradores são originais, inspirados em estilos clássicos; não usam marcas ou arte de terceiros.
