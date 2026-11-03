# Instalar uma watchface no Galaxy Watch6 Classic (para iniciantes)

Você vai: (1) preparar o computador, (2) preparar o relógio, (3) compilar, (4) instalar por Wi-Fi.
Tudo é feito **uma vez**; depois, atualizar a watchface é só compilar e rodar um comando.

> Os nomes dos menus abaixo seguem a documentação oficial do Wear OS. Na Samsung (One UI Watch) eles
> podem ser um pouco diferentes. Se algum nome não bater, procure um parecido.

## Atalho: baixar os APKs prontos (sem Android Studio)

O GitHub compila os APKs sozinho a cada alteração. Se você só quer instalar:
1. Abra o repositório no GitHub > aba **Actions** > clique na execução mais recente (com ✔ verde).
2. Role até **Artifacts** e baixe **watchfaces-apk** (precisa estar logado no GitHub). Descompacte o zip.
3. Pule para a seção **2. No relógio** e **4. Parear e conectar**; depois instale cada `.apk` com
   `adb install -r caminho/do/arquivo.apk`. Você só precisa do `adb` (pacote *platform-tools*), não do Android Studio inteiro.

## 1. No computador

1. Instale o **Android Studio** (https://developer.android.com/studio). Ele já inclui o JDK e o gerenciador do SDK.
2. Abra o Android Studio, vá em **More Actions > SDK Manager** e confirme que o **Android SDK Platform 34**
   está instalado. Em **SDK Tools**, deixe marcado **Android SDK Platform-Tools** (é onde fica o `adb`).
3. Coloque o `adb` no PATH, ou use o caminho completo. Local típico:
   - Windows: `C:\Users\SEU_USUARIO\AppData\Local\Android\Sdk\platform-tools`
   - macOS: `~/Library/Android/sdk/platform-tools`
   - Linux: `~/Android/Sdk/platform-tools`
4. Teste: `adb version`. O documento oficial pede **ADB 30.0.0 ou mais novo**.

## 2. No relógio

1. **Conecte o relógio ao Wi-Fi** da mesma rede do computador (Configurações > Conexões > Wi-Fi). Se o
   relógio só usa Bluetooth pelo celular, a depuração por Wi-Fi não funciona.
2. **Ative as opções do desenvolvedor.** Na Samsung costuma ser: **Configurações > Sobre o relógio >
   Informações do software** e toque várias vezes (cerca de 5 a 7) em **Versão do software** (ou
   *Número da versão*) até aparecer "Modo desenvolvedor ativado".
3. Volte para **Configurações > Opções do desenvolvedor** e ative:
   - **Depuração ADB**
   - **Depuração sem fio** (Wireless debugging). Se aparecer um aviso, toque em **Permitir** (ou
     *Sempre permitir nesta rede*).

## 3. No celular

Nada é obrigatório. O celular só precisa estar na mesma rede se você também quiser usar o app
Galaxy Wearable para ver o relógio. A instalação é feita direto do computador para o relógio.

## 4. Parear e conectar (por Wi-Fi)

Só na **primeira vez** você pareia. Nas outras, basta conectar.

**Parear (uma vez):**
1. No relógio: **Configurações > Opções do desenvolvedor > Depuração sem fio > Parear novo dispositivo**.
   Anote o **código de pareamento**, o **endereço IP** e a **porta** que aparecem.
2. No computador:
   ```bash
   adb pair ENDERECO_IP:PORTA_DO_PAREAMENTO
   ```
   Digite o código de 6 dígitos. Deve aparecer `Successfully paired`.

**Conectar (sempre que reiniciar a depuração ou trocar de rede):**
1. No relógio, na tela **Depuração sem fio** (não a de "Parear"), veja o **IP** e a **porta**. A porta
   é **diferente** da do pareamento.
2. No computador:
   ```bash
   adb connect ENDERECO_IP:PORTA_DE_CONEXAO
   adb devices
   ```
   O relógio deve aparecer na lista como `device`.

Se não funcionar: confirme a mesma rede Wi-Fi (redes de empresa com "isolamento" bloqueiam; tente o
roteador de casa ou um hotspot do celular), rode `adb kill-server` e `adb start-server`, e desligue e ligue a
**Depuração sem fio** no relógio.

## 5. Compilar

Na pasta do projeto:

```bash
./gradlew assembleDebug        # todas as watchfaces. Só uma: ./gradlew :faces:cronos:assembleDebug  (Windows: gradlew.bat ...)
```

Na primeira vez ele baixa o Gradle e dependências (alguns minutos). Se reclamar do SDK, crie o arquivo
`local.properties` na raiz com `sdk.dir=/caminho/do/seu/Android/Sdk` (sem aspas; no Windows use `\\`).

Alternativa: abra a pasta no Android Studio, aguarde o *Sync* e use **Build > Build APK(s)**.
O arquivo sai em `faces/cronos/build/outputs/apk/debug/cronos-debug.apk`.

## 6. Instalar e ativar

```bash
adb install -r faces/cronos/build/outputs/apk/debug/cronos-debug.apk
# as outras: crt, lunar, linha (mesmo caminho, trocando o nome)
```

No relógio: **segure o dedo no mostrador** atual, deslize até **Cronos** e toque para escolher.
Toque em **Personalizar** para trocar o tema, o estilo dos ponteiros, a cor de destaque, o
ponteiro de segundos e as complicações dos três subdials.

Dica: pelo Android Studio, a configuração de execução de watchface já instala **e ativa** o mostrador
automaticamente (é o jeito documentado pelo Google). Pelo `adb install`, a ativação é manual como acima.

## 7. Se algo falhar

| Sintoma | O que tentar |
|---|---|
| `adb devices` não lista o relógio | Refaça o **Conectar**; confira IP/porta (mudam ao religar a depuração) |
| `INSTALL_FAILED_...` | Desinstale a versão anterior: `adb uninstall br.com.thiagobritoo.watchfaces.cronos` e instale de novo |
| Gradle: "SDK location not found" | Crie `local.properties` com `sdk.dir=...` |
| Gradle: erro de versão do plugin | Atualize o Android Studio para a versão estável mais recente |
| O mostrador instala mas não aparece na lista | Reinicie o relógio; confira se a versão do Wear OS é 5 ou maior |
| Tela preta ou elemento faltando | Rode `python tools/validar.py cronos` e me mande a saída e uma foto |

Ver logs do relógio: `adb logcat` (filtre por `watchface`). Copie as linhas de erro para mim.
