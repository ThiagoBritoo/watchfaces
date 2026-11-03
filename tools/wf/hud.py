"""Base das watchfaces digitais "HUD": fonte bitmap de texto, painéis chanfrados e uma `Cena` que gera
o XML e a prévia a partir da MESMA lista de itens (a prévia nunca diverge do que vai no relógio).

Cores: "@cor" = ColorConfiguration `cor` (índice 0); qualquer outra string é #aarrggbb literal."""
from __future__ import annotations

from datetime import date

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from wf.desenho import SS, fonte, reduzir_por
from wf.kit import C, W, rgb, tint
from wf.lcd_fonte import digito

CARACTERES = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.:%/-+ "
ACENTOS = {"á": "A", "ã": "A", "â": "A", "à": "A", "é": "E", "ê": "E", "í": "I", "ó": "O", "ô": "O", "õ": "O", "ú": "U", "ç": "C"}


# --------------------------------------------------------------------------- fontes bitmap
def fonte_texto(prefixo: str, altura: int, peso: str = "SemiBold", espaco: int = 1) -> tuple[dict, dict]:
    """Letras maiúsculas/dígitos brancos, todas com a mesma altura (altura = tamanho da fonte). Retorna (imagens, mapa)."""
    # tamanho de fonte tal que a altura das maiúsculas = altura
    tam = altura
    f = fonte(peso, tam)
    for t in range(altura, altura * 2):
        f = fonte(peso, t)
        bb = f.getbbox("H", anchor="ls")
        if bb[3] - bb[1] >= altura:
            break
    base = -f.getbbox("H", anchor="ls")[1]
    imgs, mapa = {}, {}
    for ch in CARACTERES:
        larg = int(round(f.getlength(ch if ch != " " else "i")))
        w = max(larg + 2 * espaco, 4)
        im = Image.new("RGBA", (w, altura), (255, 255, 255, 0))
        if ch != " ":
            m = Image.new("L", (w * 3, altura * 3), 0)
            ImageDraw.Draw(m).text((espaco * 3, base * 3), ch, font=fonte(peso, f.size * 3), fill=255, anchor="ls")
            m = m.resize((w, altura), Image.LANCZOS)
            im.putalpha(m)
        n = f"{prefixo}_{ord(ch):x}"
        imgs[n] = im
        mapa[ch] = (n, w, altura)
    return imgs, mapa


def digitos_lcd(prefixo: str, w: int, h: int, e: int, pad: int, fantasma: float = 0.09, colon: int = 18) -> tuple[dict, dict]:
    imgs, mapa = {}, {}
    for ch in "0123456789:":
        im = digito(ch, w, h, e, pad, fantasma) if ch != ":" else digito(ch, colon, h, e, pad, fantasma)
        n = f"{prefixo}_{'colon' if ch == ':' else ch}"
        imgs[n] = im
        mapa[ch] = (n, im.width, im.height)
    return imgs, mapa


def xml_bitmapfont(nome: str, mapa: dict, completo: bool = False) -> str:
    usados = dict(mapa)
    if completo:
        for c in "abcdefghijklmnopqrstuvwxyz":
            usados[c] = mapa[c.upper()]
        for c, b in ACENTOS.items():
            usados[c] = mapa[b]
    esc = {"&": "&amp;", "<": "&lt;", '"': "&quot;"}
    linhas = [f'      <Character name="{esc.get(c, c)}" resource="{r}" width="{w}" height="{h}" />' for c, (r, w, h) in usados.items()]
    return f'    <BitmapFont name="{nome}">\n' + "\n".join(linhas) + "\n    </BitmapFont>"


# --------------------------------------------------------------------------- desenho (assets)
class Tela:
    """Canvas super-amostrado; as coordenadas são em pixels reais (480x480)."""

    def __init__(self) -> None:
        self.n = W * SS
        self.im = Image.new("RGBA", (self.n, self.n), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def p(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def poly(self, pts, cor) -> None:
        self.d.polygon(self.p(pts), fill=cor)

    def linha(self, pts, cor, esp: float = 1.0) -> None:
        self.d.line(self.p(pts), fill=cor, width=max(1, int(round(esp * SS))), joint="curve")

    def contorno(self, pts, cor, esp: float = 1.0) -> None:
        self.linha(list(pts) + [pts[0], pts[1]], cor, esp)

    def retangulo(self, x0, y0, x1, y1, cor, raio: float = 0) -> None:
        self.d.rounded_rectangle([x0 * SS, y0 * SS, x1 * SS, y1 * SS], radius=raio * SS, fill=cor)

    def elipse(self, cx, cy, r, cor=None, contorno=None, esp: float = 1.0) -> None:
        self.d.ellipse([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], fill=cor, outline=contorno, width=int(esp * SS))

    def arco(self, cx, cy, r, a0, a1, cor, esp: float = 2.0) -> None:
        """Ângulos em graus, 0 = 12h, horário."""
        self.d.arc([(cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS], a0 - 90, a1 - 90, fill=cor, width=int(esp * SS))

    def pronto(self) -> Image.Image:
        return reduzir_por(self.im)


def mascara(pts, raio_suave: float = 0) -> Image.Image:
    t = Image.new("L", (W * SS, W * SS), 0)
    ImageDraw.Draw(t).polygon([(x * SS, y * SS) for x, y in pts], fill=255)
    return t


def painel_chanfrado(pts, topo: int = 250, base: int = 196, borda: int = 3, grao: float = 5.0, semente: int = 7) -> Image.Image:
    """Placa em níveis de cinza (o relógio pinta com tintColor): gradiente vertical, borda mais escura (rebaixo),
    filete claro em cima/esquerda e grão fino de LCD. Fica por dentro do polígono `pts`."""
    m = mascara(pts)
    ys = [p[1] for p in pts]
    y0, y1 = min(ys), max(ys)
    yy = np.arange(W * SS, dtype=np.float32)[:, None] / SS
    g = np.clip((yy - y0) / max(1, y1 - y0), 0, 1)
    tom = (topo + (base - topo) * g) * np.ones((1, W * SS), np.float32)
    rng = np.random.default_rng(semente)
    tom = tom + rng.normal(0, grao, (W * SS // SS, W * SS // SS)).repeat(SS, 0).repeat(SS, 1)
    interior = m.filter(ImageFilter.MinFilter(borda * SS * 2 + 1))
    rim = ImageChops.subtract(m, interior)
    arr = np.clip(tom, 0, 255)
    arr = np.where(np.asarray(rim) > 0, arr * 0.62, arr)
    # filete claro: deslocar a máscara 1px p/ baixo-direita e subtrair
    desloc = ImageChops.offset(interior, 2 * SS, 2 * SS)
    hl = ImageChops.subtract(interior, desloc)
    arr = np.where(np.asarray(hl) > 0, np.minimum(arr * 1.12 + 10, 255), arr)
    rgbc = Image.fromarray(arr.astype(np.uint8), "L").convert("RGBA")
    rgbc.putalpha(m)
    return reduzir_por(rgbc)


def sombra_interna(img: Image.Image, desfoque: float = 6, opac: float = 0.45, dy: float = 3) -> Image.Image:
    """Escurece levemente as bordas do conteúdo (efeito de vidro rebaixado)."""
    a = img.getchannel("A")
    inv = ImageChops.invert(a).filter(ImageFilter.GaussianBlur(desfoque))
    inv = ImageChops.offset(inv, 0, int(dy))
    sombra = ImageChops.multiply(inv, a).point(lambda v: int(v * opac))
    esc = Image.new("RGBA", img.size, (0, 0, 0, 0))
    esc.putalpha(sombra)
    out = img.copy()
    out.alpha_composite(esc)
    return out


# --------------------------------------------------------------------------- cena: XML + prévia
class Cena:
    """Lista ordenada de itens. `xml()` e `previa()` leem os mesmos dados."""

    def __init__(self, fontes: dict[str, dict], imagens: dict[str, Image.Image]) -> None:
        self.itens: list[dict] = []
        self.fontes = fontes          # família -> mapa {char: (recurso, w, h)}
        self.imagens = imagens

    # -- itens
    def img(self, res: str, cor: str, x: int = 0, y: int = 0, extra: str = "") -> None:
        im = self.imagens[res]
        self.itens.append(dict(t="img", res=res, cor=cor, x=x, y=y, w=im.width, h=im.height, extra=extra))

    def txt(self, fam: str, x: int, y: int, w: int, fmt: str, params: list[str], prev: str, cor: str, align: str = "CENTER", extra: str = "") -> None:
        h = next(iter(self.fontes[fam].values()))[2]
        self.itens.append(dict(t="txt", fam=fam, x=x, y=y, w=w, h=h, fmt=fmt, params=params, prev=prev, cor=cor, align=align, extra=extra))

    def hora(self, fam: str, x: int, y: int, w: int, fmt: str, prev: str, cor: str, align: str = "START", extra: str = "") -> None:
        h = next(iter(self.fontes[fam].values()))[2]
        self.itens.append(dict(t="hora", fam=fam, x=x, y=y, w=w, h=h, fmt=fmt, prev=prev, cor=cor, align=align, extra=extra))

    def cru(self, xml: str, prev=None) -> None:
        """XML solto (ex.: arcos de progresso); `prev(base)` desenha a prévia equivalente."""
        self.itens.append(dict(t="cru", xml=xml, prev=prev))

    # -- XML
    @staticmethod
    def _cor(c: str) -> str:
        return "[CONFIGURATION.cor.0]" if c == "@cor" else c

    def xml(self, prefixo: str) -> str:
        full = f'x="0" y="0" width="{W}" height="{W}"'
        out = []
        for i, it in enumerate(self.itens):
            t = it["t"]
            if t == "cru":
                out.append(it["xml"])
                continue
            cor = self._cor(it["cor"])
            if t == "img":
                out.append(f'<PartImage x="{it["x"]}" y="{it["y"]}" width="{it["w"]}" height="{it["h"]}" tintColor="{cor}"{it["extra"]}><Image resource="{it["res"]}" /></PartImage>')
                continue
            box = f'x="{it["x"]}" y="{it["y"]}" width="{it["w"]}" height="{it["h"]}"'
            if t == "hora":
                corpo = (f'<DigitalClock {box}{it["extra"]}><TimeText x="0" y="0" width="{it["w"]}" height="{it["h"]}" format="{it["fmt"]}" '
                         f'hourFormat="SYNC_TO_DEVICE" align="{it["align"]}"><BitmapFont family="{it["fam"]}" size="{it["h"]}" /></TimeText></DigitalClock>')
            else:
                ps = "".join(f'<Parameter expression="{p}" />' for p in it["params"])
                corpo = (f'<PartText {box}{it["extra"]}><Text align="{it["align"]}"><BitmapFont family="{it["fam"]}" size="{it["h"]}">'
                         f'<Template><![CDATA[{it["fmt"]}]]>{ps}</Template></BitmapFont></Text></PartText>')
            out.append(f'<Group name="{prefixo}_{i}" {full} tintColor="{cor}">{corpo}</Group>')
        return "\n".join("    " + s for s in out)

    # -- prévia
    def previa(self, paleta: dict[str, tuple], fundo=(0, 0, 0)) -> Image.Image:
        base = Image.new("RGBA", (W, W), fundo + (255,))
        for it in self.itens:
            t = it["t"]
            if t == "cru":
                if it["prev"]:
                    it["prev"](base, paleta)
                continue
            cor = paleta["@cor"] if it["cor"] == "@cor" else rgb(it["cor"])
            alfa = int(it["cor"][1:3], 16) if it["cor"].startswith("#") and len(it["cor"]) == 9 else 255
            cam = Image.new("RGBA", (W, W), (0, 0, 0, 0))
            if t == "img":
                cam.alpha_composite(self.imagens[it["res"]], (it["x"], it["y"])) if it["x"] >= 0 and it["y"] >= 0 else cam.paste(self.imagens[it["res"]], (it["x"], it["y"]))
            else:
                mapa = self.fontes[it["fam"]]
                s = it["prev"].upper().translate(str.maketrans({k.upper(): v for k, v in ACENTOS.items()} | {k: v for k, v in ACENTOS.items()}))
                larg = sum(mapa[ch][1] for ch in s if ch in mapa)
                x = it["x"] + {"START": 0, "CENTER": (it["w"] - larg) // 2, "END": it["w"] - larg}[it["align"]]
                for ch in s:
                    if ch not in mapa:
                        continue
                    r, w, h = mapa[ch]
                    cam.alpha_composite(self.imagens[r], (int(x), it["y"]))
                    x += w
            cam = tint(cam, cor)
            if alfa < 255:
                cam.putalpha(cam.getchannel("A").point(lambda v: v * alfa // 255))
            base.alpha_composite(cam)
        return base


def redondo(base: Image.Image) -> Image.Image:
    mk = Image.new("L", (W * 4, W * 4), 0)
    ImageDraw.Draw(mk).ellipse([0, 0, W * 4 - 1, W * 4 - 1], fill=255)
    out = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    out.paste(base, (0, 0), mk.resize((W, W), Image.LANCZOS))
    return out


def unir(*dicts: dict) -> dict:
    r: dict = {}
    for d in dicts:
        r.update(d)
    return r


DIA_PREVIA = date(2026, 11, 28)
