# watchfaces

Coleção de watchfaces para o **Samsung Galaxy Watch6 Classic** (Wear OS), feitas em
**Watch Face Format (WFF)**: o formato declarativo (XML) do Google e da Samsung. Sem código
Kotlin/Java dentro do relógio: o Wear OS lê o XML e as imagens e desenha tudo sozinho, o que
ajuda bateria e desempenho.

> **Status:** projeto-base pronto e a primeira watchface (**Cronos**, cronógrafo clássico realista)
> gerada e validada em XML. **Ainda não foi compilada nem instalada em um relógio de verdade**
> (o ambiente onde foi criada não tem o Android SDK). Veja "Como compilar" e "Estado e limitações".

## Prévia

![Cronos: temas e modo ambiente](previews/cronos_folha.png)

> As prévias são **simulações em Python** feitas com os mesmos PNGs que vão no APK. Servem para
> conferir desenho, proporção e posição. O brilho, as animações e as complicações reais só
> aparecem no relógio ou no emulador.

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

| Pasta | Nome | Estilo | Estado |
|---|---|---|---|
| `faces/cronos` | **Cronos** | Clássico realista: cronógrafo, subdials, engrenagem aparente | Prova de conceito pronta (sem teste no relógio) |
| (planejado) | Retrô | Pip-Boy: CRT verde/âmbar, scanlines, Vault Boy | Roadmap |
| (planejado) | Lunar | Calendário em anel, sol/lua, muita informação | Roadmap |
| (planejado) | Minimalistas | Linha limpa e elegante | Roadmap |

### Cronos: o que tem

- **3 temas** (preto/vermelho, branco/bronze/azul, preto/dourado), com mostrador texturizado
  (fibra de carbono, sunburst, guilloché), bisel com escala, índices aplicados em metal com lume,
  subdials rebaixados e sombras.
- **2 estilos de ponteiro** (espada e bastão), com sombra suave, facetas de metal e lume.
- **6 cores de destaque** (ponteiro de segundos, textos e arcos das complicações).
- **Ponteiro de segundos**: contínuo suave (`Sweep` a 15 Hz) ou com salto mecânico (`Tick`).
- **3 complicações trocáveis** nos subdials (bateria, passos, notificações por padrão), além da data.
- **Engrenagem aparente** no alto do mostrador, girando com os segundos.
- **Presets (Flavors)**: um por tema, já com cor e complicações combinando.
- **Modo ambiente (AOD)**: só contornos finos em cinza, sem textura, sem segundos e sem
  complicações; a data fica apagada. Poucos pixels acesos = menos bateria e sem risco de burn-in.
- **Memória**: ~2 MB no modo interativo e ~1 MB no ambiente na configuração padrão (limites
  do Google: 100 MB e 10 MB).

## Estrutura de pastas

```
watchfaces/
├── README.md                  este arquivo
├── settings.gradle.kts        lista os módulos (um por watchface)
├── build.gradle.kts, gradle/  configuração do Gradle (plugin Android)
├── gradlew, gradlew.bat       Gradle wrapper (baixa o Gradle certo sozinho)
├── faces/
│   └── cronos/                um módulo Android = uma watchface
│       ├── build.gradle.kts
│       └── src/main/
│           ├── AndroidManifest.xml          versão do WFF, hasCode=false
│           └── res/
│               ├── raw/watchface.xml        GERADO: o mostrador em XML
│               ├── drawable-nodpi/*.png     GERADO: fundos, ponteiros, engrenagem, ícones
│               ├── xml/watch_face_info.xml  prévia e flags (editável, Flavors)
│               └── values, values-pt/       textos (inglês e português)
├── tools/                     geração reproduzível por script (Python)
│   ├── gerar.py               gera PNGs + XML + prévias:  python tools/gerar.py cronos
│   ├── validar.py             valida XML contra os XSDs oficiais e estima memória
│   ├── wf/desenho.py          primitivas (gradientes, metal, sombras, texto radial)
│   ├── faces/cronos_assets.py desenho do mostrador, ponteiros, engrenagem
│   ├── faces/cronos_xml.py    montagem do watchface.xml
│   ├── faces/cronos_previa.py renderização das prévias
│   └── fonts/                 Inter (licença OFL) usada só para gerar as imagens
├── previews/                  prévias em PNG (geradas)
├── third_party/wff-xsd/       esquemas XSD oficiais do WFF v2 (Apache 2.0)
└── docs/
    ├── INSTALAR.md            passo a passo para iniciantes (relógio, celular, ADB por Wi-Fi)
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
python tools/gerar.py cronos      # ~30 s: reescreve PNGs, watchface.xml e previews/
python tools/validar.py cronos    # confere o XML e a memória
```

Confira `previews/cronos_folha.png` **antes** de instalar no relógio.

## Como compilar e instalar

Resumo (o passo a passo completo, com o que fazer no relógio e no celular, está em
**[docs/INSTALAR.md](docs/INSTALAR.md)**):

1. Instale o **Android Studio** (versão atual) e um **JDK 17+**. O Android Studio já traz os dois.
2. Abra esta pasta no Android Studio e aguarde o *Gradle Sync*. Ele baixa o Gradle 9.2.1 e o SDK 34.
   Ou, pela linha de comando: `./gradlew :faces:cronos:assembleDebug`
   (precisa de `ANDROID_HOME` apontando para o SDK ou de um `local.properties` com `sdk.dir=...`).
3. O APK sai em `faces/cronos/build/outputs/apk/debug/cronos-debug.apk`.
4. No relógio, ative as **Opções do desenvolvedor** e a **Depuração por Wi-Fi**, pareie com
   `adb pair` e conecte com `adb connect`.
5. Instale: `adb install -r faces/cronos/build/outputs/apk/debug/cronos-debug.apk`
6. No relógio, **segure o dedo na tela do mostrador atual**, deslize até o **Cronos** e toque nele.
   Para trocar tema, ponteiros e complicações, toque em **Personalizar**.

## Estado e limitações (leia)

- **Não foi compilado nem testado em relógio real.** O XML foi validado contra os XSDs oficiais do
  Google e os recursos foram conferidos por script, mas o primeiro build pode revelar ajustes
  (versão do plugin do Android, nomes de menu, etc.). Se der erro, copie a mensagem e me mande.
- **Validador oficial do Google não foi rodado.** Antes de qualquer publicação, rode o
  *Memory Footprint Evaluator* e o *dwf-validator* do repositório
  [google/watchface](https://github.com/google/watchface).
- **Ponteiros e sombras:** a sombra do ponteiro gira junto com ele (limitação do formato: o
  deslocamento fica "assado" na imagem). O efeito é sutil; está documentado em `docs/WFF_NOTAS.md`.
- **Salto mecânico do segundos (`Tick`)** usa valores (`strength`, `duration`) que ainda precisam de
  ajuste fino no relógio.
- O **bisel giratório** do Watch6 Classic não é acessível pelo WFF.
- Para o ponteiro de segundos suave, o relógio redesenha a 15 Hz no modo ativo. Isso gasta mais
  bateria que o salto de 1 segundo; por isso existe a opção "mecânico".

## Roadmap

- [x] Projeto-base, scripts de geração e validação, documentação para iniciantes
- [x] **Cronos** (clássico realista): 3 temas, 2 estilos de ponteiro, 6 cores, complicações, AOD
- [ ] Primeiro build e teste no Galaxy Watch6 Classic; ajustes de posição, tamanhos e bateria
- [ ] Cronos: cronógrafo funcional (WFF não tem timer próprio: avaliar complicação de cronômetro)
- [ ] Cronos: mais mostradores (algarismos romanos em branco, estilo da referência "RC One" refinado)
- [ ] **Retrô (Pip-Boy):** tema CRT verde/âmbar, scanlines, Vault Boy animado, barras de bateria e passos
- [ ] **Lunar:** anel de meses/dias, dia da semana em subdial, sol/lua animado, segundos laranja
- [ ] **Minimalistas:** linha de mostradores limpos e elegantes
- [ ] Efeito de profundidade com sensor (`Gyro`) em detalhes do mostrador
- [ ] Meteorologia (fontes `WEATHER.*`, WFF v2) em complicações
- [ ] Automatizar `assembleDebug` e validação no GitHub Actions
- [ ] Publicação (bundle `.aab` assinado, ícones e capturas para a Play Store)

## Créditos e licenças

- Formato e esquemas: Google LLC / Samsung Electronics (Apache 2.0), ver `third_party/wff-xsd/`.
- Fonte Inter (SIL OFL 1.1), usada só na geração das imagens, ver `tools/fonts/`.
- Os mostradores são originais, inspirados em estilos clássicos; não usam marcas ou arte de terceiros.
