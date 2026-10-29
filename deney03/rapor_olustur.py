"""Ek cevap dosyasını (deney03_cevaplar.pdf) ve doldurulmuş deney yaprağını üretir.

Çalıştırma:  python3 rapor_olustur.py [orijinal_deney_03.pdf]
"""
import os
import sys
from html import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

import kisisel
from kisa_cevaplar import KISA_CEVAPLAR
from testler import hepsi

BURASI = os.path.dirname(os.path.abspath(__file__))
DV = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", DV + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DVB", DV + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DVM", DV + "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")

LACIVERT = colors.HexColor("#1F3A5F")
CERCEVE = colors.HexColor("#9AA7B6")
GOVDE = ParagraphStyle("govde", fontName="DV", fontSize=9.5, leading=13.5, spaceAfter=5)
KUCUK = ParagraphStyle("kucuk", parent=GOVDE, fontSize=8.5, leading=11.5)
HUCRE = ParagraphStyle("hucre", fontName="DV", fontSize=8, leading=9.5, alignment=TA_CENTER)
HUCRE_B = ParagraphStyle("hucreb", parent=HUCRE, fontName="DVB")
HUCRE_SOL = ParagraphStyle("hucresol", parent=HUCRE, alignment=0)
BASLIK = ParagraphStyle("baslik", fontName="DVB", fontSize=15, leading=19, spaceAfter=2)
ALTBASLIK = ParagraphStyle("altbaslik", fontName="DV", fontSize=10.5, leading=14, spaceAfter=8,
                           textColor=colors.HexColor("#4A5568"))
ALT = ParagraphStyle("alt", fontName="DVB", fontSize=11, leading=14, spaceBefore=9, spaceAfter=4,
                     textColor=LACIVERT)
KOD = ParagraphStyle("kod", fontName="DVM", fontSize=7, leading=8.6)


def P(t, s=GOVDE):
    return Paragraph(t, s)


def h(t, kalin=False):
    """Tablo hücresi (alt/üst simge yazılabilsin diye Paragraph)."""
    return Paragraph(str(t), HUCRE_B if kalin else HUCRE)


def tablo(veri, gen, baslik_satir=1):
    veri = [[c if isinstance(c, Paragraph) else h(c, r < baslik_satir) for c in satir]
            for r, satir in enumerate(veri)]
    t = Table(veri, colWidths=gen, repeatRows=baslik_satir)
    stil = [("GRID", (0, 0), (-1, -1), 0.4, CERCEVE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]
    if baslik_satir:
        stil.append(("BACKGROUND", (0, 0), (-1, baslik_satir - 1), colors.HexColor("#E3EAF2")))
    t.setStyle(TableStyle(stil))
    return t


def isaretli(x):
    """Onlu sayıyı gerçek eksi işaretiyle yazar."""
    return f"−{-x}" if x < 0 else str(x)


def sutun_kaydi(kayit, satir_adlari):
    """Kayıt satırları (i, x, y, giren, sonuç, çıkan): sütunlar bit konumu, satırlar adımlar."""
    n = len(kayit)
    sira = range(n - 1, -1, -1)
    veri = [["Konum i"] + [str(i) for i in sira],
            ["Ağırlık 2<sup>i</sup>"] + [str(2 ** i) for i in sira]]
    for k, ad in enumerate(satir_adlari):
        veri.append([ad] + [str(kayit[i][k + 1]) for i in sira])
    t = tablo(veri, [3.3 * cm] + [1.1 * cm] * n)
    t.setStyle(TableStyle([("BACKGROUND", (0, 1), (0, -1), colors.HexColor("#F3F6F9"))]))
    return t


def kayit_blogu(baslik, kayit, adlar):
    return KeepTogether([P(baslik, KUCUK), sutun_kaydi(kayit, adlar), Spacer(1, 5)])


# ---------------------------------------------------------------------------

def yaprak1_bolum(s):
    b = [P("Deney Yaprağı 1", BASLIK), P("Elde adımlarını gösteren ikili toplayıcı", ALTBASLIK)]
    b.append(P("1. Bir sütunun sonuç ve elde tablosu", ALT))
    b.append(P("Her sütunda iki biti (a, b) ve sağdan gelen eldeyi (c) topluyorum. Toplam 0 ile 3 "
               "arasında olduğu için iki bitle yazılıyor: soldaki bit çıkan elde, sağdaki bit sonuç biti. "
               "Tabloyu kurduktan sonra şu ifadeleri çıkardım: S = a ⊕ b ⊕ c ve "
               "C<sub>out</sub> = a·b + c·(a ⊕ b)."))
    veri = [["a", "b", "c (gelen)", "a + b + c", "S (sonuç)", "C<sub>out</sub> (çıkan)"]]
    veri += [list(st[:3]) + [sum(st[:3])] + list(st[3:]) for st in s["tablo"]]
    b.append(tablo(veri, [1.4 * cm] * 2 + [2 * cm, 2 * cm, 2 * cm, 2.6 * cm]))
    b.append(Spacer(1, 6))
    b.append(P("Algoritmayı sağdan sola çalışacak şekilde yazdım. Elde, başlangıç eldesiyle başlıyor; "
               "her i konumunda A<sub>i</sub>, B<sub>i</sub> ve gelen elde tam toplayıcıya giriyor, çıkan "
               "elde bir sonraki sütuna geçiyor. Her adımda ağırlığı (2<sup>i</sup>), girdi bitlerini, "
               "gelen eldeyi, sonuç bitini ve çıkan eldeyi kaydediyorum. Döngü bittiğinde elimde kalan elde "
               "son eldedir. Kod Ek A'da: tam_toplayici() ve topla()."))

    b.append(P("2. Dört işlem", ALT))
    b.append(P("Programı çalıştırmadan önce sonuçları elle hesapladım (“Elle beklenen” sütunu), sonra "
               "program çıktısıyla karşılaştırdım. İki sütunda da önce son elde, sonra 4 bitlik toplam yazıyor."))
    veri = [["İşlem", "Başl. elde", "Elle beklenen", "Program", "Değer: C·16 + S", "Uyuyor mu?"]]
    for k in s["islemler"]:
        A, B = k["A"], k["B"]
        deger = k["C"] * 16 + int(k["S"], 2)
        veri.append([f"{A} + {B}", k["c0"], f"{k['beklenen'][1]} {k['beklenen'][0]}",
                     f"{k['C']} {k['S']}", f"{deger} ({int(A, 2)} + {int(B, 2)} + {k['c0']})",
                     "evet" if k["uyum"] else "hayır"])
    b.append(tablo(veri, [2.7 * cm, 1.7 * cm, 2.4 * cm, 2 * cm, 3.6 * cm, 1.8 * cm]))
    b.append(Spacer(1, 7))
    for k in s["islemler"]:
        b.append(kayit_blogu(f"<b>{k['A']} + {k['B']}</b>, başlangıç eldesi {k['c0']}: toplam {k['S']}, "
                             f"son elde {k['C']}", k["kayit"],
                             ["A<sub>i</sub>", "B<sub>i</sub>", "gelen elde", "sonuç S<sub>i</sub>", "çıkan elde"]))

    t, hata = s["kapsamli"]
    b.append(P("3. 512 test", ALT))
    b.append(P(f"0000 ile 1111 arasındaki bütün A, B çiftlerini iki başlangıç eldesiyle denedim: "
               f"16 × 16 × 2 = {t} test. Her testte programın verdiği değeri (C·2<sup>4</sup> + S), "
               f"Python'un normal toplamasıyla bulduğum A + B + c0 ile karşılaştırdım. "
               f"<b>{t} testin hepsi tuttu, hata sayısı {hata}.</b>"))

    b.append(P("4. Hatalı girdiler ve son eldenin anlamı", ALT))
    b.append(P("Şu durumlarda fonksiyon girdiyi reddedip ne olduğunu söyleyen bir hata mesajı veriyor: "
               "A veya B boşsa, içinde 0 ve 1 dışında bir karakter varsa, A ile B'nin uzunlukları farklıysa ve "
               "başlangıç eldesi 0 ya da 1 değilse. Her biri için bir test yaptım:"))
    veri = [["Durum", "A", "B", "Başl. elde", "Programın cevabı"]]
    for ad, A, B, c0, sonuc in s["retler"]:
        veri.append([Paragraph(ad, HUCRE_SOL), A if A else "(boş)", B, c0,
                     Paragraph(escape(sonuc), HUCRE_SOL)])
    b.append(tablo(veri, [3.4 * cm, 1.5 * cm, 1.5 * cm, 1.7 * cm, 7.8 * cm]))
    b.append(Spacer(1, 6))
    b.append(P("n bitlik bir toplamada gerçek sonuç A + B + c0 = C·2<sup>n</sup> + S olur. En büyük toplam "
               "(2<sup>n</sup> − 1) + (2<sup>n</sup> − 1) + 1 = 2<sup>n+1</sup> − 1 olduğu için sonucu yazmak "
               "n + 1 bit gerektiriyor; bu fazladan bit son eldedir. Son eldeyi yok sayarsak elimizde yalnızca "
               "S kalıyor ve <b>C·2<sup>n</sup></b> kadar değer kayboluyor. C = 1 olduğunda kayıp tam olarak "
               "2<sup>n</sup>, yani n = 4 için 16."))
    veri = [["İşlem", "S", "Son elde", "Gerçek toplam", "Elde atılınca", "Kayıp"]]
    for A, B, c0, S, C, gercek, kalan, kayip in s["kayip"]:
        veri.append([f"{A} + {B} + {c0}", S, C, gercek, kalan, f"{kayip} = 2<sup>4</sup>"])
    b.append(tablo(veri, [3.4 * cm, 1.6 * cm, 1.6 * cm, 2.4 * cm, 2.4 * cm, 2 * cm]))
    b.append(Spacer(1, 4))
    b.append(P("Sınır örneği olarak 1111 + 0001'i seçtim: doğru sonuç 1 0000 (16), ama son elde atılınca "
               "0000 kalıyor. Yani iki pozitif sayının toplamı sıfır gibi görünüyor. İşaretsiz toplamada "
               "taşma olduğunu bize son elde gösteriyor.", KUCUK))
    return b


def yaprak2_bolum(s):
    b = [PageBreak(), P("Deney Yaprağı 2", BASLIK), P("Borç alma ve 2 tümleyeniyle çıkarma", ALTBASLIK)]
    b.append(P("1. İki ayrı algoritma", ALT))
    b.append(P("<b>Borç alarak çıkarma (cikar_borc):</b> Sağdan sola her sütunda fark biti "
               "D = m ⊕ n ⊕ b, çıkan borç B<sub>out</sub> = m'·n + (m ⊕ n)'·b. İşlem bitince borç kalmadıysa "
               "M ≥ N'dir ve fark doğrudan sonuçtur. Fark 0000 çıkarsa sonucu işaretsiz “0” olarak veriyorum. "
               "Son borç 1 ise M &lt; N'dir; sonuca eksi işareti koyuyorum ve büyüklüğü aynı yöntemle "
               "N − M hesaplayarak buluyorum."))
    b.append(P("<b>2 tümleyeniyle çıkarma (cikar_tumleyen):</b> M − N = M + N' + 1. N'nin bitlerini "
               "ters çeviriyorum ve +1'i toplayıcıya başlangıç eldesi olarak veriyorum. Bu fonksiyonun kendi "
               "toplayıcı döngüsü var, cikar_borc'u hiç çağırmıyor. Son elde 1 ise M ≥ N ve sonuç toplamın "
               "kendisi. Son elde 0 ise M &lt; N; büyüklüğü bulmak için toplamın 2 tümleyenini alıyorum "
               "(bitleri ters çevirip 1 ekliyorum)."))

    b.append(P("2. Beş işlem", ALT))
    veri = [["İşlem", "Onlu", "Borç yöntemi:<br/>son borç", "Borç yöntemi:<br/>sonuç",
             "2 tümleyeni:<br/>son elde", "2 tümleyeni:<br/>sonuç", "Doğru<br/>sonuç"]]
    gost = lambda i, x: "0" if i == "0" else ("−" if i == "-" else "+") + x
    for k in s["islemler"]:
        i1, b1, k1 = k["borc"]
        i2, b2, k2 = k["tum"]
        veri.append([f"{k['M']} − {k['N']}", f"{int(k['M'], 2)} − {int(k['N'], 2)}", k1["son_borc"],
                     gost(i1, b1), k2["son_elde"], gost(i2, b2), isaretli(k["ref"])])
    b.append(tablo(veri, [2.5 * cm, 1.8 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 1.6 * cm]))
    b.append(Spacer(1, 5))
    b.append(P("Her işlemin ara kayıtları aşağıda. Tablolarda sütunlar bit konumlarını, satırlar o "
               "konumdaki bitleri, borcu veya eldeyi gösteriyor.", KUCUK))
    for k in s["islemler"]:
        i1, b1, k1 = k["borc"]
        i2, b2, k2 = k["tum"]
        b.append(P(f"{k['M']} − {k['N']}", ALT))
        b.append(kayit_blogu("Borç zinciri (M − N):", k1["M-N"],
                             ["M<sub>i</sub>", "N<sub>i</sub>", "gelen borç", "fark D<sub>i</sub>", "çıkan borç"]))
        if "N-M" in k1:
            b.append(kayit_blogu("Son borç 1 çıktı, sonuç negatif. Büyüklük için N − M:", k1["N-M"],
                                 ["N<sub>i</sub>", "M<sub>i</sub>", "gelen borç", "fark D<sub>i</sub>",
                                  "çıkan borç"]))
        b.append(kayit_blogu(f"2 tümleyeni: N' = {k2['N_1tum']}, M + N' + 1 (başlangıç eldesi 1), "
                             f"son elde {k2['son_elde']}:", k2["M+N'+1"],
                             ["M<sub>i</sub>", "N'<sub>i</sub>", "gelen elde", "toplam", "çıkan elde"]))
        if "buyukluk" in k2:
            b.append(kayit_blogu("Son elde 0 çıktı, sonuç negatif. Büyüklük = ters çevrilmiş toplam + 1:",
                                 k2["buyukluk"], ["ters çevr. toplam", "eklenen", "gelen elde", "büyüklük",
                                                  "çıkan elde"]))
        b.append(P(f"Sonuç: <b>{gost(i1, b1)}</b> (onlu {isaretli(k['ref'])}). İki yöntem aynı sonucu verdi.",
                   KUCUK))

    t, h1, h2, ilk = s["kapsamli"]
    b.append(P("3. 256 çiftin hepsi", ALT))
    b.append(P(f"M ve N için 0–15 aralığındaki bütün {t} çifti iki yöntemle de hesapladım ve sonucu Python'da "
               f"M − N ile karşılaştırdım. Sonucun 0 olduğu durumlarda işaretsiz “0” verilip verilmediğine de "
               f"baktım. Borç yönteminde {h1}, 2 tümleyeni yönteminde {h2} hata çıktı. "
               + ("Uyumsuz çift olmadığı için düzeltme gerekmedi." if ilk is None else f"İlk hatalı çift: {ilk}.")))

    b.append(P("4. “Son elde yoksa sonuç mutlaka negatiftir” iddiası", ALT))
    tum0, _ = s["sifir_tumleyen"]
    yanlis = s["iddia_yanlis"]
    b.append(P(f"N'nin 2 tümleyenini ayrı bir adımda ve 4 bitle hesaplarsak: 0000'ı ters çevirince 1111, "
               f"1 ekleyince 1 0000 oluyor. 4 bite sığmayan 1 atılıyor ve 0000'ın 2 tümleyeni yine "
               f"<b>{tum0}</b> çıkıyor. Bundan sonra M + 0000 toplamında hiç elde oluşmuyor."))
    b.append(P(f"Bu şekilde (önce tümleyeni ayrı al, sonra eldesiz topla) çalışan bir sürüm yazıp 256 çifti "
               f"denedim. İddia {len(yanlis)} çiftte yanlış karar verdi ve hepsinde N = 0000 idi. "
               f"<b>En küçük karşı örnek 0000 − 0000:</b> toplam 0000, son elde 0, ama sonuç 0 ve negatif "
               f"değil. Aynı şekilde 0011 − 0000'da da elde yok, sonuç ise +3."))
    b.append(P("Doğru karar kuralı: çıkarmayı tek seferde M + N' + 1 olarak yapmak, yani +1'i başlangıç "
               "eldesi olarak vermek. N = 0 iken N' = 1111 olur ve 1111 + 1 her zaman elde üretir. Programda "
               "M = 0000, 0011 ve 1111 için N = 0 denedim, üçünde de son elde 1 çıktı. Kural şu: "
               "<b>son elde 1 ise M ≥ N</b> (sonuç pozitif veya sıfır, büyüklük toplamın kendisi), "
               "<b>son elde 0 ise M &lt; N</b> (sonuç negatif, büyüklük toplamın 2 tümleyeni). Tümleyen ayrı "
               "hesaplanacaksa N = 0 durumunu ayrıca ele almak gerekiyor."))
    return b


def yaprak3_bolum(s):
    b = [PageBreak(), P("Deney Yaprağı 3", BASLIK), P("Kısmi çarpımlarla ikili çarpıcı", ALTBASLIK)]
    b.append(P("1. Kısmi çarpım ve kaydırma kuralı", ALT))
    b.append(P("Çarpanın i konumundaki biti b<sub>i</sub> ise (bitleri sağdan 0'dan başlayarak "
               "numaralandırdım) kısmi çarpım PP<sub>i</sub> = b<sub>i</sub>·A·2<sup>i</sup> olur. "
               "b<sub>i</sub> = 1 ise A'yı, 0 ise n tane sıfırı alıyorum, sağına i tane 0 ekleyerek i kez "
               "sola kaydırıyorum ve soldan sıfırla doldurup n + m bite tamamlıyorum. Sonra kısmi çarpımları "
               "Yaprak 1'deki toplayıcıyla n + m bitlik bir toplama ekliyorum. Asıl hesapta Python'un "
               "çarpmasını veya sayıya çevirmeyi kullanmadım. Kod Ek A'da: kismi_carpim() ve carp()."))

    b.append(P("2. Kısmi çarpım tabloları", ALT))
    for t in s["tablolar"]:
        A, B = t["A"], t["B"]
        n, m = len(A), len(B)
        veri = [["i", "b<sub>i</sub>", f"PP<sub>i</sub> ({n + m} bit)", "Onlu katkı"]]
        for (i, b_i, pp), katki in zip(t["kismiler"], t["katkilar"]):
            veri.append([i, b_i, pp, f"{b_i}·{int(A, 2)}·2<sup>{i}</sup> = {katki}"])
        veri.append(["", h("Toplam", True), h(t["P"], True),
                     h(f"{' + '.join(str(x) for x in t['katkilar'])} = {int(t['P'], 2)}", True)])
        uyum = "tuttu" if int(t["P"], 2) == t["ref"] else "tutmadı"
        b.append(KeepTogether([
            P(f"<b>{A} × {B}</b> (n = {n}, m = {m}, sonuç {n + m} bit): <b>{t['P']}</b>. "
              f"Kontrol için onlu çarptım: {int(A, 2)} × {int(B, 2)} = {t['ref']}, {uyum}.", KUCUK),
            tablo(veri, [1 * cm, 1.6 * cm, 4.2 * cm, 5.2 * cm]), Spacer(1, 7)]))

    b.append(P("3. Testler ve sıfır satırları atlayan ikinci sürüm", ALT))
    b.append(P("Toplama sayısını şöyle saydım: toplam 0 ile başlıyor ve ona eklenen her kısmi çarpım bir "
               "toplama sayılıyor. Birinci sürüm çarpanın bütün bitlerini işlediği için m toplama yapıyor. "
               "İkinci sürüm b<sub>i</sub> = 0 olan satırları atlıyor, bu yüzden çarpandaki 1 sayısı kadar "
               "toplama yapıyor (çarpan 0 ise hiç)."))
    veri = [["Test", "A", "B", "Sürüm 1", "Sürüm 2", "Toplama<br/>sayısı 1", "Toplama<br/>sayısı 2",
             "Onlu", "Uyuyor<br/>mu?"]]
    for ad, A, B, P1, P2, c1, c2, ref, ok in s["testler"]:
        ad = ad.replace("2^2", "2<sup>2</sup>").replace("2^3", "2<sup>3</sup>").replace(" x ", " × ")
        veri.append([Paragraph(ad, HUCRE_SOL), A, B, P1, P2, c1, c2, ref, "evet" if ok else "hayır"])
    b.append(KeepTogether([
        tablo(veri, [2.8 * cm, 1.2 * cm, 1.5 * cm, 2 * cm, 2 * cm, 1.8 * cm, 1.8 * cm, 1.2 * cm, 1.7 * cm]),
        Spacer(1, 4),
        P("İki sürüm bütün testlerde aynı sonucu verdi, sadece toplama sayıları farklı. Sıfır satırı "
          "eklemek sonucu değiştirmediği için atlamak güvenli.", KUCUK)]))

    b.append(P("4. Sonuç neden n + m bit?", ALT))
    b.append(P("n bitlik en büyük sayı 2<sup>n</sup> − 1, m bitlik en büyük sayı 2<sup>m</sup> − 1. Bunları "
               "çarpınca (2<sup>n</sup> − 1)(2<sup>m</sup> − 1) = 2<sup>n+m</sup> − 2<sup>n</sup> − "
               "2<sup>m</sup> + 1 çıkıyor ve bu 2<sup>n+m</sup>'den küçük. Yani en büyük çarpım bile n + m "
               "bite sığıyor. Örneğin 1111 × 1111 = 225 = 11100001 (8 bit)."))
    b.append(P("n + m − 1 bit ise her zaman yetmiyor: <b>11 × 11 = 3 × 3 = 9 = 1001</b>. Burada "
               "n + m − 1 = 3 bit ve 3 bitle en fazla 7 yazılabiliyor, 9 için 4 bit lazım. n veya m 1 olduğunda "
               "çarpım 2<sup>n</sup> − 1'i geçmediği için n + m − 1 bit yetiyor; bu yüzden en küçük karşı "
               "örnek n = m = 2 ile çıkıyor."))
    return b


def bolme_tablosu(adimlar, kesir=False):
    veri = [["Kesir adımı" if kesir else "Adım", "İncelenen parça", "Bölüm biti", "Kalan"]]
    veri += [list(a) for a in adimlar]
    return tablo(veri, [2.2 * cm, 3.4 * cm, 2.2 * cm, 2.4 * cm])


def yaprak4_bolum(s):
    b = [PageBreak(), P("Deney Yaprağı 4", BASLIK), P("Bölüm, kalan ve kesirli bölme algoritması", ALTBASLIK)]
    b.append(P("1. Soldan sağa bölme", ALT))
    b.append(P("Kalanı 0 ile başlatıyorum ve bölünenin bitlerini soldan sağa tek tek indiriyorum. İncelenen "
               "parça, kalanın sağına sıradaki bitin eklenmesiyle oluşuyor. Parça bölenden büyük veya eşitse "
               "bölüme 1 yazıyorum ve parçadan böleni çıkarıyorum (Yaprak 2'deki borçlu çıkarma). Değilse "
               "bölüme 0 yazıyorum ve parça olduğu gibi kalan oluyor. Karşılaştırmayı da bit düzeyinde "
               "yaptım: baştaki sıfırları atıp önce uzunluklara, uzunluklar eşitse soldan ilk farklı bite "
               "bakıyorum. Bölen sıfırsa fonksiyon hata verip duruyor. Asıl hesapta hazır bölme ve kalan "
               "operatörü yok. Kod Ek A'da: buyuk_esit() ve bol()."))

    b.append(P("2 ve 3. Üç işlem, bölüm/kalan kontrolü ve kesirli devam", ALT))
    for r in s["islemler"]:
        D, d = r["D"], r["d"]
        Qv, Rv, dv = int(r["Q"], 2), int(r["R"], 2), int(d, 2)
        blok = [P(f"{D} ÷ {d} ({int(D, 2)} ÷ {dv})", ALT), bolme_tablosu(r["adimlar"]), Spacer(1, 4),
                P(f"Q = <b>{r['Q']}</b> ({Qv}), R = <b>{r['R']}</b> ({Rv}). "
                  f"Birinci kontrol: Q·d + R = {Qv}·{dv} + {Rv} = {Qv * dv + Rv}, bu D'ye eşit. "
                  f"İkinci kontrol: 0 ≤ R = {Rv} &lt; d = {dv}, bu da sağlanıyor. "
                  f"Python'un // ve % operatörleri de Q = {r['ref'][0]}, R = {r['ref'][1]} verdi.", KUCUK)]
        b.append(KeepTogether(blok))
        blok = []
        if r["kesir_adim"]:
            blok += [Spacer(1, 3), bolme_tablosu(r["kesir_adim"], kesir=True), Spacer(1, 3)]
        isaret = "=" if r["tam_mi"] else "≈"
        kesirli = f"{r['Q']}.{r['kesir']}" if r["kesir"] else r["Q"]
        yaklasik = Qv + sum(int(x) / 2 ** (i + 1) for i, x in enumerate(r["kesir"]))
        if r["tam_mi"]:
            not_ = "Kalan sıfırlandığı için kesirli kısım burada bitti, fazladan sıfır eklemedim."
        else:
            a, c, _ = r["tekrar"]
            not_ = (f"Kalanlar 1, 10, 1, 10 diye tekrar ediyor; bir kalan ikinci kez gelince basamaklar da "
                    f"tekrar etmeye başlıyor (“{r['kesir'][a:c]}” devri). Kesir hiç bitmiyor, 8 basamakta kestim.")
        blok.append(P(f"Kesirli sonuç: {D} ÷ {d} {isaret} <b>{kesirli}</b> (ikili). Onlu olarak "
                      f"{yaklasik:.8g}; gerçek değer {r['deger']:.8g}. {not_}", KUCUK))
        b.append(KeepTogether(blok))

    b.append(P("İki kontrol neden birlikte gerekli?", ALT))
    b.append(P("Sadece D = Q·d + R'ye bakmak yetmiyor. 10110 ÷ 100 için Q = 100 (4), R = 110 (6) alırsam "
               "4·4 + 6 = 22 tutuyor ama R ≥ d olduğu için bölme bitmemiş demektir (Q = 0, R = D zaten her "
               "zaman tutar). Sadece 0 ≤ R &lt; d'ye bakmak da yetmiyor: Q = 100, R = 10 bu koşulu sağlıyor "
               "ama 4·4 + 2 = 18, 22 değil. İki koşul birlikte sağlanınca Q ve R tek türlü belirleniyor."))
    b.append(P("Durma koşulları (111 ÷ 11)", ALT))
    b.append(P("Tam bölme, bölünende indirilecek bit kalmayınca duruyor. 111'in 3 biti olduğu için 3 adımda "
               "Q = 10, R = 1 kesinleşiyor. Kesirli bölmede ise kalanın sağına 0 ekleyerek devam ediyorum. "
               "Kalan 0 olursa sonuç tamamlanmış oluyor ve “=” yazıyorum; 8 basamağa ulaşırsam kesip "
               "“≈” yazıyorum. 111 ÷ 11'de kalanlar 1 ve 10 arasında gidip geliyor, hiç 0 olmuyor: "
               "7/3 = 10.0101... (ikili), 8 basamakla 10.01010101. 10110 ÷ 100 ve 1101 ÷ 10'da ise ilk kesir "
               "basamağında kalan 0 olduğu için sonuç “=” ile bitti."))

    b.append(P("4. Sınır testleri", ALT))
    yaz = lambda x: ", ".join(x) if isinstance(x, tuple) else x
    veri = [["Durum", "D", "d", "Beklenen Q, R", "Program", "Uyuyor mu?"]]
    for ad, D, d, bek, goz, ok in s["sinir"]:
        veri.append([Paragraph(ad, HUCRE_SOL), D, d, yaz(bek), Paragraph(escape(yaz(goz)), HUCRE_SOL),
                     "evet" if ok else "hayır"])
    b.append(tablo(veri, [3.4 * cm, 1.4 * cm, 1.3 * cm, 2.4 * cm, 5.9 * cm, 1.8 * cm]))
    b.append(Spacer(1, 6))
    b.append(P("Bölümde sıfır bitinin yanlışlıkla atılmasını göstermek için bol_hatali() diye bir sürüm "
               "yazdım: bölen sığmadığında bölüme 0 yazmayı unutuyor. Baştaki sıfırlarda bunun zararı yok, "
               "ama aradaki sıfırlar kaybolunca bölüm değişiyor:"))
    veri = [["D ÷ d", "Doğru Q", "Hatalı Q", "Hatalı R", "Q·d + R kontrolü"]]
    for D, d, Q, Qh, Rh, ok in s["hatali"]:
        top = int(Qh, 2) * int(d, 2) + int(Rh, 2)
        veri.append([f"{D} ÷ {d}", Q, Qh, Rh,
                     f"{int(Qh, 2)}·{int(d, 2)} + {int(Rh, 2)} = {top}, D = {int(D, 2)}: "
                     + ("tuttu" if ok else "hata yakalandı")])
    b.append(KeepTogether([tablo(veri, [2.8 * cm, 1.8 * cm, 1.8 * cm, 1.8 * cm, 6.6 * cm]), Spacer(1, 4),
                           P("Örneğin 10110 ÷ 100'de doğru bölüm 101. Ortadaki 0 atılınca 11 (3) çıkıyor ve 3·4 + 2 = 14 "
               "olduğu için D = Q·d + R kontrolü hatayı yakalıyor. Kalan doğru kaldığı için R &lt; d kontrolü "
               "tek başına bunu fark edemezdi; bu da iki kontrolün neden birlikte gerektiğine bir örnek.", KUCUK)]))
    return b


def kisa_cevap_bolumu():
    b = [PageBreak(), P("Kısa cevaplar", BASLIK),
         P("Deney yapraklarındaki “Kısa cevap ve doğrulama notları” alanlarına yazdıklarım", ALTBASLIK)]
    for no in range(1, 5):
        b.append(P(f"Deney Yaprağı {no}", ALT))
        veri = [[P(f"<b>{ad}</b>", KUCUK), P(escape(metin, quote=False), KUCUK)]
                for ad, metin in KISA_CEVAPLAR[no]]
        t = Table(veri, colWidths=[3.8 * cm, 13.2 * cm])
        t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, CERCEVE),
                               ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F3F6F9")),
                               ("VALIGN", (0, 0), (-1, -1), "TOP")]))
        b.append(t)
    return b


def kod_eki():
    b = [PageBreak(), P("Ek A: Kod (Python 3)", BASLIK),
         P("ikili.py dört yaprağın algoritmalarını, testler.py istenen testleri içeriyor. "
           "Testleri çalıştırmak için: python3 testler.py", ALTBASLIK)]
    for ad in ("ikili.py", "testler.py"):
        with open(os.path.join(BURASI, ad), encoding="utf-8") as f:
            b.append(P(ad, ALT))
            b.append(Preformatted(f.read().rstrip(), KOD))
    return b


def kapak():
    def orta(boyut, kalin=False):
        return ParagraphStyle("k", fontName="DVB" if kalin else "DV", fontSize=boyut,
                              leading=boyut * 1.4, alignment=TA_CENTER)
    bilgi = Table([[P("<b>Ad Soyad</b>"), P(kisisel.AD_SOYAD)],
                   [P("<b>Öğrenci No</b>"), P(kisisel.OGRENCI_NO)],
                   [P("<b>Şube / Grup</b>"), P(kisisel.SUBE_GRUP)],
                   [P("<b>Tarih</b>"), P(kisisel.TARIH)]], colWidths=[3.6 * cm, 7 * cm])
    bilgi.setStyle(TableStyle([("LINEBELOW", (0, 0), (-1, -1), 0.5, CERCEVE),
                               ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    icerik = ["Deney Yaprağı 1: İkili toplayıcı", "Deney Yaprağı 2: Borç alma ve 2 tümleyeniyle çıkarma",
              "Deney Yaprağı 3: Kısmi çarpımlarla çarpıcı", "Deney Yaprağı 4: Bölüm, kalan ve kesirli bölme",
              "Kısa cevaplar", "Ek A: Kod"]
    return [Spacer(1, 3.5 * cm), P("MARMARA ÜNİVERSİTESİ", orta(13, True)),
            P("Teknoloji Fakültesi, Bilgisayar Mühendisliği Bölümü", orta(10.5)),
            Spacer(1, 2 * cm), P("Mantık Devreleri", orta(22, True)),
            P("Ders 3: İkili Aritmetik", orta(14)), Spacer(1, 0.3 * cm),
            P("Deney yaprakları 1–4 için ek dosya", orta(11)),
            Spacer(1, 2.2 * cm), bilgi, Spacer(1, 2 * cm),
            P("<b>İçindekiler</b>", orta(10.5)), P("<br/>".join(icerik), orta(9.5))]


def sayfa_alti(c, doc):
    c.saveState()
    c.setFont("DV", 7.5)
    c.setFillColor(colors.HexColor("#5A6472"))
    c.drawString(2 * cm, 1.2 * cm,
                 f"Mantık Devreleri, Ders 3 ek dosyası · {kisisel.AD_SOYAD} · {kisisel.OGRENCI_NO}")
    c.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(doc.page))
    c.restoreState()


def ek_dosya_olustur(cikti):
    s = hepsi()
    doc = SimpleDocTemplate(cikti, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            title="Mantık Devreleri Deney 3 Ek Dosya", author=kisisel.AD_SOYAD)
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
