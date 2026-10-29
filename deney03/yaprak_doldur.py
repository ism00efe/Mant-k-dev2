"""Orijinal deney_03.pdf'teki kısa cevap alanlarının üzerine metin yerleştirir."""
import io

from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from kisa_cevaplar import KISA_CEVAPLAR

SAYFA_Y = 792.0
SAG_KENAR = 556.0
SATIR_ARASI = 21.2227          # ardışık alanlar arası dikey mesafe (pt)
# Her sayfada "İlk tahminim" satırının üst kenarı (pdftotext -bbox ile ölçüldü)
ILK_YMIN = {1: 400.7016, 2: 388.4591, 3: 412.9441, 4: 412.9441}
# Noktalı alanların başladığı x (İlk, Bağımsız, Karşı, YZ)
NOKTA_X = [112.1069, 145.3759, 120.5638, 301.1550]


def _sar(metin, font, boyut, genislik):
    satirlar, satir = [], ""
    for kelime in metin.split():
        aday = (satir + " " + kelime).strip()
        if stringWidth(aday, font, boyut) <= genislik:
            satir = aday
        else:
            satirlar.append(satir)
            satir = kelime
    if satir:
        satirlar.append(satir)
    return satirlar


def _alan_yaz(c, x0, ymin_ust, metin, yukseklik):
    """ymin_ust: üstten ölçülen alan üst kenarı. Alanı beyazla örtüp metni sığdırır."""
    genislik = SAG_KENAR - x0
    for boyut in (7.0, 6.6, 6.2, 5.8, 5.4, 5.0):
        satirlar = _sar(metin, "DV", boyut, genislik)
        aralik = boyut * 1.15
        if len(satirlar) * aralik <= yukseklik:
            break
    ust = SAYFA_Y - ymin_ust
    c.setFillColorRGB(1, 1, 1)
    c.rect(x0 - 1, ust - yukseklik, genislik + 1, yukseklik + 0.5, stroke=0, fill=1)
    c.setFillColorRGB(0.05, 0.15, 0.45)
    c.setFont("DV", boyut)
    toplam = len(satirlar) * aralik
    y = ust - (yukseklik - toplam) / 2 - boyut
    for s in satirlar:
        c.drawString(x0, y, s)
        y -= aralik


def doldur(girdi, cikti):
    okuyucu = PdfReader(girdi)
    yazici = PdfWriter()
    for no, sayfa in enumerate(okuyucu.pages, start=1):
        tampon = io.BytesIO()
        c = canvas.Canvas(tampon, pagesize=(612, SAYFA_Y))
        for k, (x0, (_, metin)) in enumerate(zip(NOKTA_X, KISA_CEVAPLAR[no])):
            # alan: kendi satırının 3.5 pt üstünden bir sonraki etiketin 3 pt üstüne kadar
            ymin = ILK_YMIN[no] + k * SATIR_ARASI - 3.5
            yuk = SATIR_ARASI - 0.5 if k < 3 else SATIR_ARASI - 1.5
            _alan_yaz(c, x0, ymin, metin, yuk)
        c.save()
        tampon.seek(0)
        sayfa.merge_page(PdfReader(tampon).pages[0])
        yazici.add_page(sayfa)
    with open(cikti, "wb") as f:
        yazici.write(f)
