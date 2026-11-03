"""Gera res/raw/watchface.xml da watchface Cronos (Watch Face Format v2).

Cada elemento/atributo usado aqui foi conferido na documentação oficial
(developer.android.com/reference/wear-os/wff) e nos XSDs do repositório google/watchface.
"""
from __future__ import annotations

from xml.sax.saxutils import quoteattr

from .cronos_assets import C, ENGRENAGENS, GAUGES, R_GAUGE, TEMAS, TEXTO_H, TEXTO_W, TEXTOS, W, fase_engrenagens

ACENTOS = ["#e0262b", "#2e70b5", "#d4af5f", "#ff7a1a", "#2fa365", "#8a5fd0", "#19d3f0"]
ESTILOS = ["espada", "bastao"]
# medidas dos ponteiros (px no espaço 480): comprimento, cauda, largura por estilo
MEDIDAS = {
    "hora": {"espada": (118, 26, 30), "bastao": (118, 26, 22)},
    "min": {"espada": (178, 30, 22), "bastao": (178, 30, 16)},
}
SEG = (208, 52)
PAD_SOMBRA = 10


def q(v) -> str:
    return quoteattr(str(v))


def _caixa(extra: str = "") -> str:
    return f'x="0" y="0" width="{W}" height="{W}"{extra}'


class Medidas:
    """Dimensões reais dos PNGs gerados (preenchidas por `gerar`)."""

    def __init__(self) -> None:
        self.dim: dict[str, tuple[int, int, float]] = {}  # nome -> (w, h, pivo_y)

    def mao(self, nome: str, w: int, h: int, pivo_y: float) -> None:
        self.dim[nome] = (w, h, pivo_y)

    def tag(self, tipo: str, nome: str, extra: str = "") -> str:
        w, h, py = self.dim[nome]
        return (f'<{tipo} resource="{nome}" x="{C - w // 2}" y="{round(C - py)}" width="{w}" height="{h}" '
                f'pivotX="0.5" pivotY="{py / h:.6f}"{extra}')


def _bloco_mao(m: Medidas, tipo: str, nome: str, extra: str = "", filhos: str = "") -> str:
    t = m.tag(tipo, nome, extra)
    return f"{t}>{filhos}</{tipo}>" if filhos else f"{t} />"


def _relogio_interativo(m: Medidas, estilo: str, tema: str) -> str:
    return f"""<AnalogClock {_caixa()}>
              <Variant mode="AMBIENT" target="alpha" value="0" />
              {_bloco_mao(m, 'HourHand', f'hora_sombra_{estilo}')}
              {_bloco_mao(m, 'MinuteHand', f'min_sombra_{estilo}')}
              {_bloco_mao(m, 'HourHand', f'hora_{estilo}_{tema}')}
              {_bloco_mao(m, 'MinuteHand', f'min_{estilo}_{tema}')}
            </AnalogClock>"""


def _relogio_ambiente(m: Medidas, estilo: str) -> str:
    return f"""<AnalogClock {_caixa(' alpha="0"')}>
              <Variant mode="AMBIENT" target="alpha" value="255" />
              {_bloco_mao(m, 'HourHand', f'hora_contorno_{estilo}')}
              {_bloco_mao(m, 'MinuteHand', f'min_contorno_{estilo}')}
            </AnalogClock>"""


def _segundos(m: Medidas, modo: str) -> str:
    mov = '<Sweep frequency="15" />' if modo == "suave" else '<Tick strength="0.4" duration="0.25" />'
    return f"""<AnalogClock {_caixa()}>
              <Variant mode="AMBIENT" target="alpha" value="0" />
              {_bloco_mao(m, 'SecondHand', 'seg_sombra', filhos=mov)}
              {_bloco_mao(m, 'SecondHand', 'seg', ' tintColor="[CONFIGURATION.acento]"', filhos=mov)}
            </AnalogClock>"""


def _tpl(x, y, w, h, tam, cor, fmt: str, params: list[str], peso="NORMAL") -> str:
    ps = "".join(f'<Parameter expression="{p}" />' for p in params)
    return f"""<PartText x="{x}" y="{y}" width="{w}" height="{h}">
                <Text ellipsis="TRUE">
                  <Font family="SYNC_TO_DEVICE" size="{tam}" weight="{peso}" color="{cor}">
                    <Template><![CDATA[{fmt}]]>{ps}</Template>
                  </Font>
                </Text>
              </PartText>"""


def _por_tema(w: int, h: int, fabrica) -> str:
    """Repete um bloco por tema (a cor do texto muda com o mostrador claro/escuro)."""
    ops = "".join(f'<ListOption id="{t}"><Group x="0" y="0" width="{w}" height="{h}">{fabrica(th)}</Group></ListOption>'
                  for t, th in TEMAS.items())
    return f'<Group x="0" y="0" width="{w}" height="{h}"><ListConfiguration id="tema">{ops}</ListConfiguration></Group>'


def _hex(c) -> str:
    return "#%02x%02x%02x" % tuple(c)


def _slot_gauge(nome: str, slot_id: int, cx: int, cy: int, padrao: tuple[str, str], m: Medidas) -> str:
    S = 2 * R_GAUGE
    cor = "[CONFIGURATION.acento]"
    norm = ("(clamp([COMPLICATION.RANGED_VALUE_VALUE], [COMPLICATION.RANGED_VALUE_MIN], "
            "[COMPLICATION.RANGED_VALUE_MAX]) - [COMPLICATION.RANGED_VALUE_MIN]) / "
            "([COMPLICATION.RANGED_VALUE_MAX] - [COMPLICATION.RANGED_VALUE_MIN])")
    w, h, py = m.dim["agulha"]
    centro = _por_tema(S, S, lambda th: _tpl(S // 2 - 34, S // 2 - 17, 68, 34, 26, _hex(th.num_cuba), "%s", ["[COMPLICATION.TEXT]"], "SEMI_BOLD"))
    return f"""<ComplicationSlot name="{nome}" slotId="{slot_id}" x="{cx - S // 2}" y="{cy - S // 2}" width="{S}" height="{S}"
        displayName="slot_{nome}" supportedTypes="RANGED_VALUE SHORT_TEXT MONOCHROMATIC_IMAGE SMALL_IMAGE EMPTY" isCustomizable="TRUE">
      <BoundingOval x="0" y="0" width="{S}" height="{S}" />
      <DefaultProviderPolicy defaultSystemProvider="{padrao[0]}" defaultSystemProviderType="{padrao[1]}" />
      <Variant mode="AMBIENT" target="alpha" value="0" />
      <Complication type="RANGED_VALUE">
        <PartImage x="{S // 2 - w // 2}" y="{round(S // 2 - py)}" width="{w}" height="{h}" pivotX="0.5" pivotY="{py / h:.6f}" tintColor="{cor}">
          <Image resource="agulha" />
          <Transform target="angle" value="-135 + ({norm}) * 270" />
        </PartImage>
      </Complication>
      <Complication type="SHORT_TEXT">
        {centro}
      </Complication>
      <Complication type="MONOCHROMATIC_IMAGE">
        <PartImage x="{S // 2 - 24}" y="{S // 2 - 24}" width="48" height="48" tintColor="{cor}">
          <Image resource="[COMPLICATION.MONOCHROMATIC_IMAGE]" />
        </PartImage>
      </Complication>
      <Complication type="SMALL_IMAGE">
        <PartImage x="{S // 2 - 24}" y="{S // 2 - 24}" width="48" height="48">
          <Image resource="[COMPLICATION.SMALL_IMAGE]" />
        </PartImage>
      </Complication>
    </ComplicationSlot>"""


def _slot_texto(nome: str, slot_id: int, cx: int, cy: int, padrao: tuple[str, str]) -> str:
    W_, H_ = TEXTO_W, TEXTO_H
    cor = "[CONFIGURATION.acento]"

    def dois(th) -> str:
        return (_tpl(0, 1, W_, 16, 13, cor, "%s", ["[COMPLICATION.TITLE]"], "MEDIUM")
                + _tpl(0, 15, W_, 28, 24, _hex(th.texto), "%s", ["[COMPLICATION.TEXT]"], "SEMI_BOLD"))

    def um(th) -> str:
        return _tpl(0, 7, W_, 30, 25, _hex(th.texto), "%s", ["[COMPLICATION.TEXT]"], "SEMI_BOLD")

    return f"""<ComplicationSlot name="{nome}" slotId="{slot_id}" x="{cx - W_ // 2}" y="{cy - H_ // 2}" width="{W_}" height="{H_}"
        displayName="slot_{nome}" supportedTypes="SHORT_TEXT RANGED_VALUE EMPTY" isCustomizable="TRUE">
      <BoundingBox x="0" y="0" width="{W_}" height="{H_}" />
      <DefaultProviderPolicy defaultSystemProvider="{padrao[0]}" defaultSystemProviderType="{padrao[1]}" />
      <Variant mode="AMBIENT" target="alpha" value="0" />
      <Complication type="SHORT_TEXT">
        <Condition>
          <Expressions>
            <Expression name="comTitulo"><![CDATA[[COMPLICATION.TITLE] != null]]></Expression>
          </Expressions>
          <Compare expression="comTitulo">
            {_por_tema(W_, H_, dois)}
          </Compare>
          <Default>
            {_por_tema(W_, H_, um)}
          </Default>
        </Condition>
      </Complication>
      <Complication type="RANGED_VALUE">
        {_por_tema(W_, H_, um)}
      </Complication>
    </ComplicationSlot>"""


def gerar_xml(m: Medidas) -> str:
    L: list[str] = []
    a = L.append
    a('<?xml version="1.0" encoding="utf-8"?>')
    a("<!-- GERADO por tools/gerar.py cronos. Não edite à mão: mude tools/faces/cronos_xml.py e gere de novo. -->")
    a(f'<WatchFace width="{W}" height="{W}" clipShape="CIRCLE">')
    a('  <Metadata key="CLOCK_TYPE" value="ANALOG" />')
    a('  <Metadata key="PREVIEW_TIME" value="10:08:32" />')
    # ---- configurações do usuário
    a("  <UserConfigurations>")
    a('    <ListConfiguration id="tema" displayName="tema_label" icon="icone_tema_rc" defaultValue="rc">')
    for t in TEMAS:
        a(f'      <ListOption id="{t}" displayName="tema_{t}" icon="icone_tema_{t}" />')
    a("    </ListConfiguration>")
    a('    <ListConfiguration id="estilo" displayName="estilo_label" icon="icone_estilo_espada" defaultValue="espada">')
    for e in ESTILOS:
        a(f'      <ListOption id="{e}" displayName="estilo_{e}" icon="icone_estilo_{e}" />')
    a("    </ListConfiguration>")
    a('    <ColorConfiguration id="acento" displayName="acento_label" defaultValue="0">')
    for i, c in enumerate(ACENTOS):
        a(f'      <ColorOption id="{i}" displayName="acento_{i}" colors="{c}" />')
    a("    </ColorConfiguration>")
    a('    <ListConfiguration id="segundos" displayName="segundos_label" defaultValue="suave">')
    a('      <ListOption id="suave" displayName="segundos_suave" />')
    a('      <ListOption id="mecanico" displayName="segundos_mecanico" />')
    a("    </ListConfiguration>")
    a('    <Flavors defaultValue="rc">')
    # slots: 0/1 = mostradores analógicos (esq/dir), 2..5 = campos de texto (te, td, be, bd)
    g = [("WATCH_BATTERY", "RANGED_VALUE"), ("STEP_COUNT", "RANGED_VALUE")]
    presets = [("rc", "rc", "espada", 0, g + [("WORLD_CLOCK", "SHORT_TEXT"), ("STEP_COUNT", "SHORT_TEXT"), ("SUNRISE_SUNSET", "SHORT_TEXT"), ("UNREAD_NOTIFICATION_COUNT", "SHORT_TEXT")]),
               ("frost", "frost", "bastao", 1, g + [("WORLD_CLOCK", "SHORT_TEXT"), ("STEP_COUNT", "SHORT_TEXT"), ("SUNRISE_SUNSET", "SHORT_TEXT"), ("DAY_OF_WEEK", "SHORT_TEXT")]),
               ("romano", "romano", "bastao", 2, g + [("WORLD_CLOCK", "SHORT_TEXT"), ("STEP_COUNT", "SHORT_TEXT"), ("SUNRISE_SUNSET", "SHORT_TEXT"), ("DAY_OF_WEEK", "SHORT_TEXT")]),
               ("neon", "neon", "espada", 6, g + [("DAY_OF_WEEK", "SHORT_TEXT"), ("STEP_COUNT", "SHORT_TEXT"), ("SUNRISE_SUNSET", "SHORT_TEXT"), ("UNREAD_NOTIFICATION_COUNT", "SHORT_TEXT")]),
               ("noir", "noir", "espada", 2, g + [("DAY_OF_WEEK", "SHORT_TEXT"), ("STEP_COUNT", "SHORT_TEXT"), ("SUNRISE_SUNSET", "SHORT_TEXT"), ("UNREAD_NOTIFICATION_COUNT", "SHORT_TEXT")])]
    for fid, tema, estilo, ac, *provs in presets:
        a(f'      <Flavor id="{fid}" displayName="tema_{fid}" icon="icone_tema_{fid}">')
        a(f'        <Configuration id="tema" optionId="{tema}" />')
        a(f'        <Configuration id="estilo" optionId="{estilo}" />')
        a(f'        <Configuration id="acento" optionId="{ac}" />')
        for sid, (prov, tp) in enumerate(provs[0]):
            a(f'        <ComplicationSlot slotId="{sid}"><DefaultProviderPolicy defaultSystemProvider="{prov}" defaultSystemProviderType="{tp}" /></ComplicationSlot>')
        a("      </Flavor>")
    a("    </Flavors>")
    a("  </UserConfigurations>")
    # ---- cena (a ordem do XML é a ordem de desenho: ponteiros e complicações no fim)
    a('  <Scene backgroundColor="#ff000000">')
    # mostrador + engrenagem (some no ambiente)
    a(f'    <Group name="mostrador" {_caixa()}>')
    a('      <Variant mode="AMBIENT" target="alpha" value="0" />')
    a('      <ListConfiguration id="tema">')
    fases = fase_engrenagens()
    for t in TEMAS:
        a(f'        <ListOption id="{t}">')
        a(f'          <Group {_caixa()}>')
        a(f'            <PartImage {_caixa()}><Image resource="fundo_{t}" /></PartImage>')
        for pos, (gx, gy, raio, dentes) in ENGRENAGENS.items():
            tam = 2 * raio + 8
            tam += tam % 2
            if pos == "meio":
                expr = f"[SECOND] * 6 + {fases[pos]:.3f}"
            else:
                nm = ENGRENAGENS["meio"][3]
                expr = f"{fases[pos]:.3f} - [SECOND] * {6 * nm / dentes:.4f}"
            a(f'            <PartImage x="{gx - tam // 2}" y="{gy - tam // 2}" width="{tam}" height="{tam}" pivotX="0.5" pivotY="0.5">')
            a(f'              <Image resource="engrenagem_{t}_{pos}" />')
            a(f'              <Transform target="angle" value="{expr}" />')
            a("            </PartImage>")
        a("          </Group>")
        a("        </ListOption>")
    a("      </ListConfiguration>")
    a("    </Group>")
    # mostrador do modo ambiente (AOD): só contornos
    a(f'    <Group name="mostrador_ambiente" {_caixa(" alpha=" + chr(34) + "0" + chr(34))}>')
    a('      <Variant mode="AMBIENT" target="alpha" value="255" />')
    a('      <ListConfiguration id="tema">')
    for t in TEMAS:
        a(f'        <ListOption id="{t}"><Group {_caixa()}><PartImage {_caixa()}><Image resource="ambiente_{t}" /></PartImage></Group></ListOption>')
    a("      </ListConfiguration>")
    a("    </Group>")
    # data (acesa no modo normal, discreta no ambiente)
    a(f'    <Group name="data" {_caixa()}>')
    a('      <Variant mode="AMBIENT" target="alpha" value="130" />')
    a('      <ListConfiguration id="tema">')
    for t, th in TEMAS.items():
        cor = "#%02x%02x%02x" % th.texto
        a(f'        <ListOption id="{t}"><Group {_caixa()}>')
        a("          " + _tpl(190, 340, 100, 24, 17, cor, "%s %s", ["[DAY_OF_WEEK_S]", "[DAY_Z]"], "MEDIUM"))
        a("        </Group></ListOption>")
    a("      </ListConfiguration>")
    a("    </Group>")
    # complicações (3 subdials)
    nomes = ["esq", "dir", "te", "td", "be", "bd"]
    for sid, nome in enumerate(nomes[:2]):
        a(_slot_gauge(nome, sid, *GAUGES[nome], presets[0][4][sid], m))
    for sid, nome in enumerate(nomes[2:], start=2):
        a(_slot_texto(nome, sid, *TEXTOS[nome], presets[0][4][sid]))
    # ponteiros: hora/minuto por tema+estilo
    a(f'    <Group name="ponteiros" {_caixa()}>')
    a('      <ListConfiguration id="tema">')
    for t in TEMAS:
        a(f'        <ListOption id="{t}"><Group {_caixa()}>')
        a('          <ListConfiguration id="estilo">')
        for e in ESTILOS:
            a(f'            <ListOption id="{e}">')
            a("            " + _relogio_interativo(m, e, t))
            a("            </ListOption>")
        a("          </ListConfiguration>")
        a("        </Group></ListOption>")
    a("      </ListConfiguration>")
    a('      <ListConfiguration id="estilo">')
    for e in ESTILOS:
        a(f'        <ListOption id="{e}">')
        a("        " + _relogio_ambiente(m, e))
        a("        </ListOption>")
    a("      </ListConfiguration>")
    a('      <ListConfiguration id="segundos">')
    for modo in ("suave", "mecanico"):
        a(f'        <ListOption id="{modo}">')
        a("        " + _segundos(m, modo))
        a("        </ListOption>")
    a("      </ListConfiguration>")
    a("    </Group>")
    # tampa central + cristal
    a(f'    <Group name="tampa" {_caixa()}>')
    a('      <ListConfiguration id="tema">')
    for t in TEMAS:
        a(f'        <ListOption id="{t}"><Group {_caixa()}><PartImage x="{C - 24}" y="{C - 24}" width="48" height="48"><Image resource="tampa_{t}" /></PartImage></Group></ListOption>')
    a("      </ListConfiguration>")
    a("    </Group>")
    a(f'    <Group name="vidro" {_caixa()}>')
    a('      <Variant mode="AMBIENT" target="alpha" value="0" />')
    a(f'      <PartImage {_caixa()}><Image resource="vidro" /></PartImage>')
    a("    </Group>")
    a("  </Scene>")
    a("</WatchFace>")
    return "\n".join(L) + "\n"
