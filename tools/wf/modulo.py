"""Cria/atualiza o módulo Android de uma watchface (manifesto, Gradle, strings, info) e utilidades de XML."""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

PACOTE_BASE = "br.com.thiagobritoo.watchfaces"


def hexcor(c) -> str:
    return "#%02x%02x%02x" % tuple(int(v) for v in c)


def caixa(w: int, h: int, x: int = 0, y: int = 0, extra: str = "") -> str:
    return f'x="{x}" y="{y}" width="{w}" height="{h}"{extra}'


def texto(x, y, w, h, tam, cor, fmt: str, params: list[str], peso="NORMAL", align="CENTER", tint: str = "") -> str:
    ps = "".join(f'<Parameter expression="{p}" />' for p in params)
    t = f' tintColor="{tint}"' if tint else ""
    return (f'<PartText x="{x}" y="{y}" width="{w}" height="{h}"{t}><Text align="{align}" ellipsis="TRUE">'
            f'<Font family="SYNC_TO_DEVICE" size="{tam}" weight="{peso}" color="{cor}">'
            f'<Template><![CDATA[{fmt}]]>{ps}</Template></Font></Text></PartText>')


def _strings(d: dict[str, str]) -> str:
    linhas = "\n".join(f'    <string name="{k}">{escape(v).replace(chr(39), chr(92) + chr(39))}</string>' for k, v in d.items())
    return f'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n{linhas}\n</resources>\n'


def criar_modulo(raiz: Path, nome: str, strings_en: dict[str, str], strings_pt: dict[str, str],
                 wff: int = 2, minsdk: int = 34, versao: str = "0.1.0", flavors: bool = True) -> Path:
    """Gera os arquivos fixos do módulo `faces/<nome>` e registra no settings.gradle.kts."""
    mod = raiz / "faces" / nome
    res = mod / "src" / "main" / "res"
    for p in (res / "raw", res / "xml", res / "values", res / "values-pt", res / "drawable-nodpi"):
        p.mkdir(parents=True, exist_ok=True)
    (mod / "build.gradle.kts").write_text(f'''plugins {{
    alias(libs.plugins.android.application)
}}

android {{
    // Watch Face Format é só recursos (XML + imagens): sem código Kotlin/Java.
    enableKotlin = false
    namespace = "{PACOTE_BASE}.{nome}"
    compileSdk = 34

    defaultConfig {{
        applicationId = "{PACOTE_BASE}.{nome}"
        minSdk = {minsdk}
        targetSdk = 34
        versionCode = 1
        versionName = "{versao}"
    }}

    buildTypes {{
        debug {{
            isMinifyEnabled = false
        }}
        release {{
            isMinifyEnabled = false
            isShrinkResources = false
            signingConfig = signingConfigs.getByName("debug")
        }}
    }}
}}
''', encoding="utf-8")
    (mod / "src" / "main" / "AndroidManifest.xml").write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-feature android:name="android.hardware.type.watch" />

    <!-- hasCode="false" é obrigatório no Watch Face Format. -->
    <application
        android:label="@string/watch_face_name"
        android:hasCode="false">

        <meta-data
            android:name="com.google.android.wearable.standalone"
            android:value="true" />

        <property
            android:name="com.google.wear.watchface.format.version"
            android:value="{wff}" />
    </application>
</manifest>
''', encoding="utf-8")
    fl = '    <FlavorsSupported value="true" />\n' if flavors else ""
    (res / "xml" / "watch_face_info.xml").write_text(f'''<?xml version="1.0" encoding="utf-8"?>
<WatchFaceInfo>
    <Preview value="@drawable/preview" />
    <Editable value="true" />
    <MultipleInstancesAllowed value="true" />
{fl}</WatchFaceInfo>
''', encoding="utf-8")
    (res / "values" / "strings.xml").write_text(_strings(strings_en), encoding="utf-8")
    (res / "values-pt" / "strings.xml").write_text(_strings(strings_pt), encoding="utf-8")
    cfg = raiz / "settings.gradle.kts"
    linha = f'include(":faces:{nome}")'
    s = cfg.read_text(encoding="utf-8")
    if linha not in s:
        cfg.write_text(s.rstrip("\n") + "\n" + linha + "\n", encoding="utf-8")
    return res
