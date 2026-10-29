"""Ek cevap dosyasını (deney03_cevaplar.pdf) ve doldurulmuş deney yaprağını üretir.

Çalıştırma:  python3 deney03/rapor_olustur.py [orijinal_deney_03.pdf]
"""
import os
from html import escape
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

from testler import hepsi
from kisa_cevaplar import KISA_CEVAPLAR

BURASI = os.path.dirname(os.path.abspath(__file__))
FONT_DIZIN = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FONT_DIZIN + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", FONT_DIZIN + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVM", FONT_DIZIN + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")

GOVDE = ParagraphStyle("govde", fontName="DV", fontSize=9.5, leading=13, spaceAfter=4)
KUCUK = ParagraphStyle("kucuk", parent=GOVDE, fontSize=8.5, leading=11)
BASLIK = ParagraphStyle("baslik", fontName="DVB", fontSize=15, leading=19, spaceAfter=6)
ALT = ParagraphStyle("alt", fontName="DVB", fontSize=11, leading=14, spaceBefore=8, spaceAfter=4,
                     textColor=colors.HexColor("#1F3A5F"))
KAPAK = ParagraphStyle("kapak", fontName="DVB", fontSize=20, leading=26, alignment=TA_CENTER)
KOD = ParagraphStyle("kod", fontName="DVM", fontSize=6.6, leading=8.2)


def P(t, s=GOVDE):
    return Paragraph(t, s)


def tablo(veri, gen=None, baslik_satir=1, kucuk=False, sol=False):
    fs = 7.5 if kucuk else 8.5
    t = Table(veri, colWidths=gen, hAlign="LEFT" if sol else "CENTER", repeatRows=baslik_satir)
    stil = [("FONT", (0, 0), (-1, -1), "DV", fs),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#8899AA")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5)]
    if baslik_satir:
        stil += [("BACKGROUND", (0, 0), (-1, baslik_satir - 1), colors.HexColor("#DCE6F0")),
                 ("FONT", (0, 0), (-1, baslik_satir - 1), "DVB", fs)]
    t.setStyle(TableStyle(stil))
    return t


def sutun_kaydi(kayit, satir_adlari):
    """kayıt satırları (i, x, y, giren, sonuç, çıkan) -> sütunları bit konumu olan tablo."""
    n = len(kayit)
    bas = ["Konum i"] + [str(i) for i in range(n - 1, -1, -1)]
    agirlik = ["Ağırlık 2^i"] + [str(2 ** i) for i in range(n - 1, -1, -1)]
    satirlar = [bas, agirlik]
    for k, ad in enumerate(satir_adlari):
        satirlar.append([ad] + [str(kayit[i][k + 1]) for i in range(n - 1, -1, -1)])
    return tablo(satirlar, gen=[3.4 * cm] + [1.1 * cm] * n, kucuk=True)


# ---------------------------------------------------------------------------

def yaprak1_bolum(s):
    h = [P("Deney Yaprağı 1 — Elde adımlarını gösteren ikili toplayıcı", BASLIK)]
    h.append(P("1. Tek sütunun sonuç/elde tablosu ve algoritma", ALT))
    h.append(P("Bir sütunda iki bit (a, b) ve gelen elde c toplanır; 0–3 arası değer iki bitle "
               "(çıkan elde, sonuç) yazılır. Mantık ifadeleri: <b>S = a ⊕ b ⊕ c</b>, "
               "<b>C<sub>out</sub> = a·b + c·(a ⊕ b)</b>."))
    veri = [["a", "b", "c (gelen)", "a+b+c", "S (sonuç)", "C_out (çıkan)"]]
    for a, b, c, t, co in s["tablo"]:
        veri.append([a, b, c, a + b + c, t, co])
    h.append(tablo(veri, gen=[1.4 * cm] * 3 + [1.6 * cm, 2 * cm, 2.4 * cm]))
    h.append(Spacer(1, 4))
    h.append(P("Algoritma (n bit, sağdan sola): c ← başlangıç eldesi; i = 0 … n−1 için "
               "(S<sub>i</sub>, c) ← tam_toplayıcı(A<sub>i</sub>, B<sub>i</sub>, c) ve kayda "
               "(2<sup>i</sup>, A<sub>i</sub>, B<sub>i</sub>, gelen c, S<sub>i</sub>, çıkan c) yazılır; "
               "döngü sonundaki c son eldedir. Kod: <i>ikili.py → tam_toplayici(), topla()</i> (Ek A)."))

    h.append(P("2. Dört işlem — programdan önce yazılan beklenen sonuçlar ve işlem kayıtları", ALT))
    veri = [["İşlem", "c0", "Beklenen C S", "Program: S", "Son elde", "Değer C·16+S", "Uyum"]]
    for k in s["islemler"]:
        A, B = k["A"], k["B"]
        beklenen = f"{k['beklenen'][1]} {k['beklenen'][0]}"
        deger = k["C"] * 16 + int(k["S"], 2)
        veri.append([f"{A} + {B}", k["c0"], beklenen, k["S"], k["C"],
                     f"{deger} = {int(A, 2)}+{int(B, 2)}+{k['c0']}", "✓" if k["uyum"] else "✗"])
    h.append(tablo(veri, gen=[2.6 * cm, 0.9 * cm, 2.6 * cm, 2 * cm, 1.6 * cm, 3.4 * cm, 1.1 * cm]))
    h.append(Spacer(1, 4))
    for k in s["islemler"]:
        h.append(KeepTogether([
            P(f"<b>{k['A']} + {k['B']}, başlangıç eldesi {k['c0']}</b> → toplam {k['S']}, "
              f"son elde {k['C']}", KUCUK),
            sutun_kaydi(k["kayit"], ["A_i", "B_i", "gelen elde", "sonuç S_i", "çıkan elde"]),
            Spacer(1, 5)]))

    t, hata = s["kapsamli"]
    h.append(P("3. 512 testlik kapsamlı sınama", ALT))
    h.append(P(f"Tüm A, B ∈ {{0000 … 1111}} ve c0 ∈ {{0, 1}}: 16 × 16 × 2 = <b>{t}</b> test. "
               f"Her testte n bitlik çıktı ile son eldenin birlikte taşıdığı değer "
               f"<b>C·2<sup>4</sup> + S</b> onlu referans <b>A + B + c0</b> (hazır aritmetik) ile "
               f"karşılaştırıldı. Sonuç: <b>{t} test, {hata} hata</b>."))
    g = "; ".join(f"n={n}: {tt} test, {hh} hata" for n, tt, hh in s["genel"])
    h.append(P(f"Ek denetim (aynı kod, farklı n): {g}.", KUCUK))

    h.append(P("4. Ret kuralları ve son eldenin anlamı", ALT))
    h.append(P("Kurallar: (i) A veya B boş dizgi ise ret; (ii) 0/1 dışında karakter içeriyorsa ret; "
               "(iii) A ve B uzunlukları farklı ise ret; (iv) başlangıç eldesi 0/1 değilse ret. "
               "Hepsi <i>ValueError</i> ile açık mesaj verir."))
    veri = [["Durum", "A", "B", "c0", "Gözlenen"]]
    for ad, A, B, c0, sonuc in s["retler"]:
        veri.append([ad, repr(A), B, c0, Paragraph(sonuc, KUCUK)])
    h.append(tablo(veri, gen=[3.6 * cm, 1.4 * cm, 1.4 * cm, 0.9 * cm, 8.6 * cm]))
    h.append(Spacer(1, 4))
    h.append(P("n bitlik toplayıcının gerçek sonucu <b>A + B + c0 = C·2<sup>n</sup> + S</b>'dir; en büyük değer "
               "(2<sup>n</sup>−1)+(2<sup>n</sup>−1)+1 = 2<sup>n+1</sup>−1 olduğundan n+1 bit gerekir ve "
               "(n+1). bit son eldedir. Son elde yok sayılırsa kalan yalnızca S = (A+B+c0) mod 2<sup>n</sup> "
               "olur; kaybedilen değer <b>C·2<sup>n</sup></b>, yani C = 1 iken tam olarak "
               "<b>2<sup>n</sup></b> (n = 4 için 16)."))
    veri = [["İşlem", "S", "Son elde", "Gerçek", "Elde atılınca", "Kayıp"]]
    for A, B, c0, S, C, gercek, kalan, kayip in s["kayip"]:
        veri.append([f"{A}+{B}+{c0}", S, C, gercek, kalan, f"{kayip} = 2^4"])
    h.append(tablo(veri, gen=[3.4 * cm, 1.6 * cm, 1.6 * cm, 1.6 * cm, 2.4 * cm, 2 * cm]))
    h.append(P("Sınır örneği: 1111 + 0001 = 1 0000 (16); elde atılınca 0000 = 0 kalır. Bu, iki pozitif "
               "sayının toplamının sıfır görünmesi demektir; işaretsiz taşma (overflow) göstergesi son eldedir.",
               KUCUK))
    return h


def cikarma_kaydi(baslik, kayit, adlar):
    return KeepTogether([P(baslik, KUCUK), sutun_kaydi(kayit, adlar), Spacer(1, 4)])


def yaprak2_bolum(s):
    h = [PageBreak(), P("Deney Yaprağı 2 — Borç alma ve 2 tümleyeniyle çıkarma", BASLIK)]
    h.append(P("1. İki bağımsız algoritma", ALT))
    h.append(P("<b>(a) Borç alarak doğrudan çıkarma</b> (<i>cikar_borc</i>): sağdan sola her sütunda "
               "fark biti <b>D = m ⊕ n ⊕ b</b>, çıkan borç <b>B<sub>out</sub> = m'·n + (m ⊕ n)'·b</b>. "
               "Son borç 0 ise M ≥ N ve sonuç fark dizisidir (fark 0000 ise sonuç “0”, işaretsiz). "
               "Son borç 1 ise M &lt; N: işaret “−”, büyüklük aynı yöntemle N − M hesaplanarak bulunur."))
    h.append(P("<b>(b) 2 tümleyeniyle çıkarma</b> (<i>cikar_tumleyen</i>): M − N = M + N' + 1. N'nin bitleri "
               "terslenir, “+1” başlangıç eldesi olarak toplayıcıya girer (kendi tam toplayıcı zinciri; "
               "<i>cikar_borc</i>'u çağırmaz). Son elde 1 → M ≥ N, sonuç toplamın kendisi (0000 ise “0”). "
               "Son elde 0 → M &lt; N, büyüklük = toplamın 2 tümleyeni (tersle + 1)."))

    h.append(P("2. Beş işlemin iki yöntemle çözümü", ALT))
    veri = [["İşlem", "Onlu", "Borç: son borç", "Borç: sonuç", "2 tüm.: son elde", "2 tüm.: sonuç", "Ref."]]
    for k in s["islemler"]:
        i1, b1, k1 = k["borc"]
        i2, b2, k2 = k["tum"]
        gost = lambda i, b: "0" if i == "0" else ("−" if i == "-" else "+") + b
        veri.append([f"{k['M']} − {k['N']}", f"{int(k['M'], 2)} − {int(k['N'], 2)}", k1["son_borc"],
                     gost(i1, b1), k2["son_elde"], gost(i2, b2), k["ref"]])
    h.append(tablo(veri, gen=[2.6 * cm, 1.8 * cm, 2.3 * cm, 2.2 * cm, 2.6 * cm, 2.3 * cm, 1.2 * cm]))
    h.append(Spacer(1, 4))
    for k in s["islemler"]:
        i1, b1, k1 = k["borc"]
        i2, b2, k2 = k["tum"]
        h.append(P(f"<b>{k['M']} − {k['N']}</b>", ALT))
        h.append(cikarma_kaydi("(a) Borç zinciri M − N", k1["M-N"],
                               ["M_i", "N_i", "gelen borç", "fark D_i", "çıkan borç"]))
        if "N-M" in k1:
            h.append(cikarma_kaydi("(a) Son borç 1 → negatif; büyüklük için N − M", k1["N-M"],
                                   ["N_i", "M_i", "gelen borç", "fark D_i", "çıkan borç"]))
        h.append(cikarma_kaydi(f"(b) N' = {k2['N_1tum']}; M + N' + 1 (başlangıç eldesi 1), "
                               f"son elde {k2['son_elde']}", k2["M+N'+1"],
                               ["M_i", "N'_i", "gelen elde", "toplam", "çıkan elde"]))
        if "buyukluk" in k2:
            h.append(cikarma_kaydi("(b) Son elde 0 → negatif; büyüklük = toplamın 2 tümleyeni "
                                   "(terslenmiş toplam + 1)", k2["buyukluk"],
                                   ["tersl. toplam", "0", "gelen elde", "büyüklük", "çıkan elde"]))
        sonuc = "0 (sıfır, işaretsiz)" if i1 == "0" else ("−" if i1 == "-" else "+") + b1
        h.append(P(f"Sonuç: <b>{sonuc}</b> (onlu {k['ref']}); iki yöntem aynı.", KUCUK))

    t, h1, h2, ilk = s["kapsamli"]
    h.append(P("3. 256 operand çiftinin sınanması", ALT))
    h.append(P(f"M, N ∈ 0…15 için 16 × 16 = <b>{t}</b> çift. Her çiftte işaret+büyüklük onlu referans "
               f"M − N ile ve sıfır durumunun “0” olarak verilmesi ayrıca karşılaştırıldı. "
               f"Borç yöntemi: <b>{h1} hata</b>; 2 tümleyeni yöntemi: <b>{h2} hata</b>. "
               f"{'Uyumsuz çift bulunmadı; düzeltme gerekmedi.' if ilk is None else f'İlk hatalı çift: {ilk}.'}"))

    h.append(P("4. “Son elde yoksa sonuç mutlaka negatiftir” iddiası", ALT))
    tum0, atilan = s["sifir_tumleyen"]
    h.append(P(f"N'nin 2 tümleyeni ayrı bir adımda 4 bitle hesaplanırsa: 0000 → tersle 1111 → +1 → "
               f"1 0000; sabit genişlikte taşan {atilan} atılır ve <b>2tüm(0000) = {tum0}</b> olur "
               f"(sıfırın 2 tümleyeni yine sıfırdır). Sonra M + 0000 toplamında hiçbir zaman elde oluşmaz."))
    yanlis = s["iddia_yanlis"]
    h.append(P(f"Bu “ayrı tümle, sonra eldesiz topla” sürümüyle 256 çift tarandı: iddia <b>{len(yanlis)}</b> "
               f"çiftte yanlış karar verdi ve hepsinde N = 0000 (M = 0000 … 1111). "
               f"<b>En küçük karşı örnek: 0000 − 0000</b> → toplam 0000, son elde 0, fakat gerçek sonuç 0 "
               f"(negatif değil). Benzer biçimde 0011 − 0000: son elde yok, sonuç +3."))
    h.append(P("Karar kuralı: Çıkarma tek geçişte <b>M + N' + 1</b> olarak yapılmalı (“+1” başlangıç eldesi). "
               "N = 0 iken N' = 1111 ve 1111 + 1 her zaman son elde üretir; doğru yöntemde N = 0 için "
               + ", ".join(f"M={m} → son elde {c}" for m, c in s["dogru_n0"]) +
               ". Böylece: <b>son elde 1 ⇔ M ≥ N</b> (sonuç ≥ 0; büyüklük toplamın kendisi, 0000 ise sıfır); "
               "<b>son elde 0 ⇔ M &lt; N</b> (sonuç negatif; büyüklük toplamın 2 tümleyeni). "
               "2 tümleyeni ayrı hesaplanacaksa N = 0 özel durumu (sonuç = M, işaret +/0) ayrıca ele alınmalıdır."))
    return h


def yaprak3_bolum(s):
    h = [PageBreak(), P("Deney Yaprağı 3 — Kısmi çarpımlarla ikili çarpıcı", BASLIK)]
    h.append(P("1. Kısmi çarpım ve kaydırma kuralı", ALT))
    h.append(P("Çarpan B'nin i konumundaki biti b<sub>i</sub> (sağdan 0'dan başlayarak) için kısmi çarpım "
               "<b>PP<sub>i</sub> = (b<sub>i</sub> · A) ≪ i</b>: b<sub>i</sub> = 1 ise A, b<sub>i</sub> = 0 ise "
               "n tane 0 alınır; sağına i adet 0 eklenerek i kez sola kaydırılır ve soldan sıfırla n+m bite "
               "tamamlanır (başlangıç sıfırları korunur). Çarpım <b>P = Σ PP<sub>i</sub></b>; toplama, "
               "Yaprak 1'deki bit düzeyindeki <i>topla()</i> ile n+m bitlik biriktiriciye yapılır. Ana sonuçta "
               "hazır çarpma ya da tam sayıya dönüşüm kullanılmaz (<i>kismi_carpim(), carp()</i>, Ek A)."))

    h.append(P("2. Hizalı kısmi çarpım tabloları", ALT))
    for t in s["tablolar"]:
        A, B = t["A"], t["B"]
        n, m = len(A), len(B)
        veri = [["i", "b_i", f"PP_i ({n + m} bit)", "Onlu katkı"]]
        for (i, b_i, pp), katki in zip(t["kismiler"], t["katkilar"]):
            veri.append([i, b_i, pp, f"{b_i}·{int(A, 2)}·2^{i} = {katki}"])
        veri.append(["", "Σ", t["P"], f"{' + '.join(str(x) for x in t['katkilar'])} = {int(t['P'], 2)}"])
        tb = tablo(veri, gen=[1 * cm, 1.2 * cm, 4.2 * cm, 5.4 * cm])
        tb.setStyle(TableStyle([("FONT", (0, -1), (-1, -1), "DVB", 8.5),
                                ("FONT", (2, 1), (2, -1), "DVM", 8.5)]))
        h.append(KeepTogether([
            P(f"<b>{A} × {B}</b> (n = {n}, m = {m}, çıktı {n + m} bit): "
              f"P = <b>{t['P']}</b>. Bağımsız denetim: {int(A, 2)} × {int(B, 2)} = {t['ref']} "
              f"{'✓' if int(t['P'], 2) == t['ref'] else '✗'}", KUCUK), tb, Spacer(1, 6)]))

    h.append(P("3. Testler ve sıfır kısmi çarpımı atlayan ikinci sürüm", ALT))
    h.append(P("Sayım kuralı: biriktirici 0…0 ile başlar; biriktiriciye eklenen her kısmi çarpım bir toplama "
               "çağrısıdır. Sürüm 1 her biti işler → <b>m</b> çağrı. Sürüm 2 b<sub>i</sub> = 0 olan satırları "
               "atlar → <b>B'deki 1 sayısı</b> kadar çağrı (çarpan 0 ise hiç çağrı yok)."))
    veri = [["Test", "A", "B", "Sürüm 1", "Sürüm 2", "Çağrı v1", "Çağrı v2", "Ref.", "Uyum"]]
    for ad, A, B, P1, P2, c1, c2, ref, ok in s["testler"]:
        veri.append([ad, A, B, P1, P2, c1, c2, ref, "✓" if ok else "✗"])
    h.append(tablo(veri, gen=[3.3 * cm, 1.3 * cm, 1.4 * cm, 2.2 * cm, 2.2 * cm, 1.4 * cm, 1.4 * cm,
                              1.1 * cm, 1 * cm], kucuk=True))
    t, hh = s["kapsamli"]
    h.append(P(f"Ek tarama: n, m = 1…6 bitlik tüm operand çiftleri ({t} çarpım) için iki sürüm hem birbiriyle "
               f"hem de onlu referansla karşılaştırıldı: <b>{hh} hata</b>. İki sürüm her zaman aynı sonucu verir; "
               f"fark yalnızca toplama sayısındadır (sıfır satır eklemek sonucu değiştirmez).", KUCUK))

    h.append(P("4. Çıktı genişliği gerekçesi", ALT))
    h.append(P("n bitlik en büyük işaretsiz sayı 2<sup>n</sup>−1, m bitlik 2<sup>m</sup>−1'dir. Üst sınır: "
               "(2<sup>n</sup>−1)(2<sup>m</sup>−1) = 2<sup>n+m</sup> − 2<sup>n</sup> − 2<sup>m</sup> + 1 "
               "&lt; 2<sup>n+m</sup> (n, m ≥ 1 için 2<sup>n</sup> + 2<sup>m</sup> − 1 &gt; 0). Dolayısıyla her "
               "çarpım n+m bite sığar; örn. 1111 × 1111 = 225 = 11100001 (8 bit)."))
    h.append(P("n+m−1 bit her zaman yetmez: <b>11 × 11 = 3 × 3 = 9 = 1001</b>; n+m−1 = 3 bit en çok 7'yi "
               "gösterir, 9 için 4 bit gerekir. (n veya m = 1 iken çarpım ≤ 2<sup>n</sup>−1 olduğundan n+m−1 bit "
               "yeter; bu yüzden en küçük karşı örnek n = m = 2'dir.) Öte yandan en soldaki bitleri 1 olan operandlarda "
               "çarpım ≥ 2<sup>n−1</sup>·2<sup>m−1</sup> = 2<sup>n+m−2</sup> olduğundan en az n+m−1 bit her zaman gerekir."))
    return h


def bolme_tablosu(adimlar, kesir=False):
    bas = ["Kesir adımı" if kesir else "Adım", "İncelenen parça", "Bölüm biti", "Kalan"]
    veri = [bas] + [[a, p, q, r] for a, p, q, r in adimlar]
    return tablo(veri, gen=[2 * cm, 3.4 * cm, 2.2 * cm, 2.4 * cm])


def yaprak4_bolum(s):
    h = [PageBreak(), P("Deney Yaprağı 4 — Bölüm, kalan ve kesirli bölme", BASLIK)]
    h.append(P("1. Soldan sağa bölme algoritması", ALT))
    h.append(P("Kalan r = 0 ile başlanır. Bölünenin her biti için (soldan sağa): incelenen parça = "
               "r'nin sağına sıradaki bitin indirilmesi (r·2 + bit). Parça ≥ d ise bölüm biti 1 ve r = parça − d "
               "(bit düzeyinde borçlu çıkarma), değilse bölüm biti 0 ve r = parça. Karşılaştırma bit düzeyindedir "
               "(önce anlamlı uzunluk, sonra soldan ilk farklı bit). Bölen yalnızca sıfırlardan oluşuyorsa "
               "<i>ZeroDivisionError</i> ile açıkça reddedilir. Hazır bölme/kalan operatörü kullanılmaz "
               "(<i>buyuk_esit(), bol()</i>, Ek A)."))

    h.append(P("2–3. Üç işlem: tam bölüm, kalan ve kesirli devam", ALT))
    for r in s["islemler"]:
        D, d = r["D"], r["d"]
        isaret = "=" if r["tam_mi"] else "≈"
        kesirli = f"{r['Q']}.{r['kesir']}" if r["kesir"] else r["Q"]
        blok = [P(f"<b>{D} ÷ {d}</b>  ({int(D, 2)} ÷ {int(d, 2)})", ALT),
                bolme_tablosu(r["adimlar"]), Spacer(1, 3),
                P(f"Q = <b>{r['Q']}</b> ({int(r['Q'], 2)}), R = <b>{r['R']}</b> ({int(r['R'], 2)}). "
                  f"Kontrol 1: Q·d + R = {int(r['Q'], 2)}·{int(d, 2)} + {int(r['R'], 2)} = "
                  f"{int(r['Q'], 2) * int(d, 2) + int(r['R'], 2)} = D {'✓' if r['kontrol1'] else '✗'}; "
                  f"Kontrol 2: 0 ≤ R = {int(r['R'], 2)} &lt; d = {int(d, 2)} {'✓' if r['kontrol2'] else '✗'}. "
                  f"Referans (//, %): {r['ref']}.", KUCUK)]
        if r["kesir_adim"]:
            blok += [Spacer(1, 3), bolme_tablosu(r["kesir_adim"], kesir=True), Spacer(1, 3)]
        tekrar = ""
        if r["tekrar"]:
            a, b, kal = r["tekrar"]
            tekrar = (f" Kalan {kal} ({int(kal, 2)}) kesir adımı {a}'dan sonra adım {b}'de yeniden görüldü → "
                      f"basamaklar “{r['kesir'][a:b]}” periyoduyla tekrar eder; kesir hiç bitmez, 8 basamakta kesildi.")
        blok.append(P(f"Kesirli sonuç: {D} ÷ {d} {isaret} <b>{kesirli}</b>₂ "
                      f"(onlu {isaret} {int(r['Q'], 2) + sum(int(b) / 2 ** (i + 1) for i, b in enumerate(r['kesir'])):.8g}; "
                      f"gerçek {r['deger']:.8g}).{tekrar}", KUCUK))
        h.append(KeepTogether(blok))

    h.append(P("İki koşul neden birlikte gerekli?", ALT))
    h.append(P("Yalnızca D = Q·d + R yetmez: 10110 ÷ 100 için Q = 100 (4), R = 110 (6) de 4·4 + 6 = 22 sağlar, "
               "ama R ≥ d olduğundan bölüm eksiktir (Q = 0, R = D de her zaman sağlar). Yalnızca 0 ≤ R &lt; d de "
               "yetmez: Q = 100, R = 10 bu koşulu sağlar fakat 4·4 + 2 = 18 ≠ 22. İki koşul birlikte (Q, R) çiftini "
               "<b>tek</b> olarak belirler (bölme teoremi)."))
    h.append(P("Durma koşulları (111 ÷ 11 üzerinden)", ALT))
    h.append(P("<b>Tam bölme</b> bölünenin bit sayısı kadar adımda kesin olarak durur (111 için 3 adım): "
               "indirilecek bit kalmadığında Q = 10, R = 1 kesinleşir. <b>Kesirli bölme</b> ise kalandan devam "
               "eder (kalanın sağına 0 indirilir); (a) kalan 0 olursa sonuç tamamlanmıştır ve “=” yazılır, "
               "(b) 8 basamağa ulaşılırsa kesilir ve “≈” yazılır. 111 ÷ 11'de kalanlar 1 → 10 → 1 → 10 … biçiminde "
               "tekrar eder; bir kalan yeniden görüldüğünde kesir periyodiktir ve asla 0'a ulaşmaz: "
               "7/3 = 10.0101…₂ ≈ 10.01010101₂. 10110 ÷ 100 ve 1101 ÷ 10 ise 1 kesir basamağında kalan 0 "
               "olduğundan “=” ile tamamlanır (ek sıfır üretilmedi)."))

    h.append(P("4. Sınır testleri", ALT))
    veri = [["Durum", "D", "d", "Beklenen Q, R", "Gözlenen Q, R", "Uyum"]]
    for ad, D, d, bek, goz, ok in s["sinir"]:
        yaz = lambda x: ", ".join(x) if isinstance(x, tuple) else x
        veri.append([ad, D, d, yaz(bek), Paragraph(yaz(goz), KUCUK), "✓" if ok else "✗"])
    h.append(tablo(veri, gen=[3.4 * cm, 1.5 * cm, 1.3 * cm, 2.6 * cm, 6 * cm, 1.1 * cm]))
    h.append(Spacer(1, 4))
    h.append(P("Bölümde sıfır bitinin yanlış atılması: <i>bol_hatali()</i> bölen sığmadığında bölüme 0 yazmayı "
               "atlar. Bu hata baştaki sıfırlarda zararsızdır, ama ara sıfırlarda bölümü bozar:"))
    veri = [["D ÷ d", "Doğru Q", "Hatalı Q", "Hatalı R", "Q·d + R = D ?"]]
    for D, d, Q, Qh, Rh, ok in s["hatali"]:
        veri.append([f"{D} ÷ {d}", Q, Qh, Rh,
                     f"{int(Qh, 2)}·{int(d, 2)}+{int(Rh, 2)} = {int(Qh, 2) * int(d, 2) + int(Rh, 2)} "
                     f"{'=' if ok else '≠'} {int(D, 2)} → {'geçer' if ok else 'YAKALANDI'}"])
    h.append(tablo(veri, gen=[2.8 * cm, 2 * cm, 2 * cm, 2 * cm, 6.4 * cm]))
    h.append(P("Örn. 10110 ÷ 100: doğru bölüm 101'dir; ortadaki 0 atılınca 11 (3) çıkar ve 3·4 + 2 = 14 ≠ 22 "
               "olduğundan D = Q·d + R kontrolü hatayı yakalar (kalan doğru olduğu için R &lt; d kontrolü tek "
               "başına yakalayamaz — iki kontrolün birlikte gerekliliğine bir örnek daha).", KUCUK))
    t, hh = s["kapsamli"]
    h.append(P(f"Ek tarama: D 1–8 bit, d = 1…15 tüm kombinasyonlar ({t} bölme) // ve % ile karşılaştırıldı: "
               f"<b>{hh} hata</b>.", KUCUK))
    return h


def kisa_cevap_bolumu():
    h = [PageBreak(), P("Kısa cevap ve doğrulama notları (deney yapraklarına yazılanlar)", BASLIK)]
    for no in range(1, 5):
        h.append(P(f"Deney Yaprağı {no}", ALT))
        veri = [[P(f"<b>{ad}</b>", KUCUK), P(escape(metin, quote=False), KUCUK)] for ad, metin in KISA_CEVAPLAR[no]]
        t = Table(veri, colWidths=[3.6 * cm, 13.4 * cm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#8899AA")),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        h.append(t)
    return h


def kod_eki():
    h = [PageBreak(), P("Ek A — Kod (Python 3)", BASLIK),
         P("Çalıştırma: <font name='DVM'>python3 testler.py</font> (tüm testler), "
           "<font name='DVM'>python3 rapor_olustur.py</font> (bu dosya).", KUCUK)]
    for ad in ("ikili.py", "testler.py"):
        with open(os.path.join(BURASI, ad), encoding="utf-8") as f:
            h.append(P(ad, ALT))
            h.append(Preformatted(f.read(), KOD))
    return h


def sayfa_alti(c, doc):
    c.saveState()
    c.setFont("DV", 7.5)
    c.drawString(2 * cm, 1.2 * cm, "Mantık Devreleri — Ders 3 / İkili Aritmetik — Deney 3 ek dosyası")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Sayfa {doc.page}")
    c.restoreState()


def kapak():
    return [Spacer(1, 5 * cm), P("MARMARA ÜNİVERSİTESİ", KAPAK),
            P("Teknoloji Fakültesi / Bilgisayar Mühendisliği Bölümü",
              ParagraphStyle("k2", parent=GOVDE, alignment=TA_CENTER, fontSize=11)),
            Spacer(1, 1 * cm), P("MANTIK DEVRELERİ — Ders 3 / İkili Aritmetik", KAPAK),
            P("Deney Yaprakları 1–4: Ek Dosya (kod, işlem kayıtları, test özetleri, gerekçeler)",
              ParagraphStyle("k3", parent=GOVDE, alignment=TA_CENTER, fontSize=11)),
            Spacer(1, 2 * cm),
            tablo([["Ad Soyad", " " * 40], ["Öğrenci No", ""], ["Şube / Grup", ""], ["Tarih", ""]],
                  gen=[4 * cm, 8 * cm], baslik_satir=0),
            Spacer(1, 1.5 * cm),
            P("İçindekiler: Yaprak 1 — İkili toplayıcı · Yaprak 2 — Çıkarma · Yaprak 3 — Çarpıcı · "
              "Yaprak 4 — Bölme · Kısa cevaplar · Ek A — Kod",
              ParagraphStyle("k4", parent=GOVDE, alignment=TA_CENTER))]


def ek_dosya_olustur(cikti):
    s = hepsi()
    doc = SimpleDocTemplate(cikti, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="Deney 3 - Ek Dosya", author="")
    hikaye = kapak() + [PageBreak()]
    hikaye += yaprak1_bolum(s[1]) + yaprak2_bolum(s[2]) + yaprak3_bolum(s[3]) + yaprak4_bolum(s[4])
    hikaye += kisa_cevap_bolumu() + kod_eki()
    doc.build(hikaye, onFirstPage=lambda c, d: None, onLaterPages=sayfa_alti)


if __name__ == "__main__":
    ek_dosya_olustur(os.path.join(BURASI, "deney03_cevaplar.pdf"))
    if len(sys.argv) > 1:
        from yaprak_doldur import doldur
        doldur(sys.argv[1], os.path.join(BURASI, "deney_03_doldurulmus.pdf"))
    print("tamam")
