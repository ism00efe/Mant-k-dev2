"""Orijinal deney_03.pdf'teki başlık alanlarını, kısa cevapları ve imzayı doldurur."""
import io
import json
import os

from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

import kisisel
from kisa_cevaplar import KISA_CEVAPLAR

# Form Arial ile yazılmış; Liberation Sans aynı ölçülere sahip.
pdfmetrics.registerFont(TTFont("LS", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"))
FONT = "LS"

BURASI = os.path.dirname(os.path.abspath(__file__))
SAYFA_Y = 792.0
SAG_KENAR = 556.0
SATIR_ARASI = 21.2227          # ardışık cevap satırları arası dikey mesafe (pt)
# Her sayfada "İlk tahminim" satırının üst kenarı (pdftotext -bbox ile ölçüldü)
ILK_YMIN = {1: 400.7016, 2: 388.4591, 3: 412.9441, 4: 412.9441}
# Noktalı alanların başladığı x (İlk, Bağımsız, Karşı, YZ)
NOKTA_X = [112.1069, 145.3759, 120.5638, 301.1550]
# Başlık alanları: (noktaların x başı, x sonu, üst kenar y, alt kenar y) - dört sayfada aynı
BASLIK_ALANLARI = {
    "ad": (105.07, 230.08, 109.34, 120.51),
    "no": (294.55, 383.45, 109.34, 120.51),
    "tarih": (83.38, 150.06, 123.56, 134.73),
    "grup": (217.87, 284.54, 123.56, 134.73),
    "imza": (320.10, 386.77, 123.56, 134.73),
}


def _y(ust):
    return SAYFA_Y - ust


def _sil(c, x0, x1, ust, alt):
    c.setFillColorRGB(1, 1, 1)
    c.rect(x0 - 0.5, _y(alt) - 1.5, x1 - x0 + 1, alt - ust + 2, stroke=0, fill=1)


def _sar(metin, boyut, genislik):
    satirlar, satir = [], ""
    for kelime in metin.split():
        aday = (satir + " " + kelime).strip()
        if stringWidth(aday, FONT, boyut) <= genislik:
            satir = aday
        else:
            satirlar.append(satir)
            satir = kelime
    if satir:
        satirlar.append(satir)
    return satirlar


def _baslik_yaz(c, alan, metin):
    x0, x1, ust, alt = BASLIK_ALANLARI[alan]
    _sil(c, x0, x1, ust, alt)
    c.setFillColorRGB(0, 0, 0)
    c.setFont(FONT, 10)
    c.drawString(x0 + 1, _y(alt) + 2.4, metin)


def _imza_ciz(c, imza):
    """İmza çizgilerini İmza alanına, oranı koruyarak vektör olarak çizer."""
    x0, x1, ust, alt = BASLIK_ALANLARI["imza"]
    _sil(c, x0, x1, ust, alt)
    cizgiler = [[tuple(map(float, p.split(","))) for p in s.split()]
                for s in imza["cizgiler"].split(";") if s.strip()]
    xs = [p[0] for s in cizgiler for p in s]
    ys = [p[1] for s in cizgiler for p in s]
    gx, gy = max(max(xs) - min(xs), 1), max(max(ys) - min(ys), 1)
    hedef_y = 15.0                                   # 121.5 ile 136.5 arası, üstteki satıra taşmaz
    olcek = min(hedef_y / gy, (x1 - x0 - 4) / gx)
    sol = x0 + 4
    taban = _y(ust + 1.5)                            # en üst nokta bu y'ye gelir
    c.setStrokeColorRGB(0.05, 0.1, 0.3)
    c.setLineWidth(0.9)
    c.setLineCap(1)
    c.setLineJoin(1)
    for s in cizgiler:
        yol = c.beginPath()
        for k, (px, py) in enumerate(s):
            x, y = sol + (px - min(xs)) * olcek, taban - (py - min(ys)) * olcek
            yol.moveTo(x, y) if k == 0 else yol.lineTo(x, y)
        if len(s) == 1:
            yol.lineTo(x + 0.2, y)
        c.drawPath(yol, stroke=1, fill=0)


def _cevap_yaz(c, x0, ust, metin, yukseklik):
    """ust: alanın üst kenarı (sayfanın üstünden). Noktaları siler, metni sığdırır."""
    genislik = SAG_KENAR - x0
    for boyut in (8.5, 8, 7.5, 7, 6.5):
        aralik = boyut * 1.18
        satirlar = _sar(metin, boyut, genislik)
        if len(satirlar) * aralik <= yukseklik:
            break
    c.setFillColorRGB(1, 1, 1)
    c.rect(x0 - 1, _y(ust) - yukseklik, genislik + 1, yukseklik + 0.5, stroke=0, fill=1)
    c.setFillColorRGB(0, 0, 0)
    c.setFont(FONT, boyut)
    y = _y(ust) - (yukseklik - len(satirlar) * aralik) / 2 - boyut
    for s in satirlar:
        c.drawString(x0, y, s)
        y -= aralik


def doldur(girdi, cikti):
    with open(os.path.join(BURASI, "imza.json"), encoding="utf-8") as f:
        imza = json.load(f)
    okuyucu = PdfReader(girdi)
    yazici = PdfWriter()
    for no, sayfa in enumerate(okuyucu.pages, start=1):
        tampon = io.BytesIO()
        c = canvas.Canvas(tampon, pagesize=(612, SAYFA_Y))
        _baslik_yaz(c, "ad", kisisel.AD_SOYAD)
        _baslik_yaz(c, "no", kisisel.OGRENCI_NO)
        _baslik_yaz(c, "tarih", kisisel.TARIH)
        _baslik_yaz(c, "grup", kisisel.SUBE_GRUP)
        _imza_ciz(c, imza)
        for k, (x0, (_, metin)) in enumerate(zip(NOKTA_X, KISA_CEVAPLAR[no])):
            ust = ILK_YMIN[no] + k * SATIR_ARASI - 3.5
            _cevap_yaz(c, x0, ust, metin, SATIR_ARASI - (0.5 if k < 3 else 1.5))
        c.save()
        tampon.seek(0)
        sayfa.merge_page(PdfReader(tampon).pages[0])
        yazici.add_page(sayfa)
    with open(cikti, "wb") as f:
        yazici.write(f)
