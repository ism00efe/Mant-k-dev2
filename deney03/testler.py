"""Deney 3 testleri. Referans değerler hazır aritmetikle (int, +, -, *, //, %) hesaplanır.

Çalıştırma:  python3 testler.py
"""
from itertools import product

from ikili import (topla, dogruluk_tablosu, cikar_borc, cikar_tumleyen,
                   cikar_tumleyen_hatali, iki_tumleyeni, carp, bol, bol_hatali)


def ikili(x, n):
    return format(x, f"0{n}b")


def onlu_isaretli(isaret, buyukluk):
    v = int(buyukluk, 2)
    return -v if isaret == "-" else v


# ------------------------------- Yaprak 1 ----------------------------------

def yaprak1():
    sonuc = {"tablo": dogruluk_tablosu()}
    islemler = [("0101", "0011", 0, "1000", 0), ("1111", "0001", 0, "0000", 1),
                ("1111", "0000", 1, "0000", 1), ("1111", "1111", 1, "1111", 1)]
    kayitlar = []
    for A, B, c0, beklenen_s, beklenen_c in islemler:
        s, c, kayit = topla(A, B, c0)
        kayitlar.append({"A": A, "B": B, "c0": c0, "S": s, "C": c, "kayit": kayit,
                         "beklenen": (beklenen_s, beklenen_c),
                         "uyum": (s, c) == (beklenen_s, beklenen_c)})
    sonuc["islemler"] = kayitlar

    n = 4
    toplam_test = hata = 0
    for a, b, c0 in product(range(16), range(16), (0, 1)):
        s, c, _ = topla(ikili(a, n), ikili(b, n), c0)
        toplam_test += 1
        if c * 2 ** n + int(s, 2) != a + b + c0:
            hata += 1
    sonuc["kapsamli"] = (toplam_test, hata)


    retler = []
    for A, B, c0, aciklama in [("", "0101", 0, "boş girdi"),
                                ("01a1", "0011", 0, "geçersiz bit"),
                                ("101", "0011", 0, "farklı uzunluk"),
                                ("0101", "0011", 2, "geçersiz başlangıç eldesi")]:
        try:
            topla(A, B, c0)
            retler.append((aciklama, A, B, c0, "KABUL EDİLDİ (HATA)"))
        except ValueError as e:
            retler.append((aciklama, A, B, c0, f"ret: {e}"))
    sonuc["retler"] = retler

    # son eldeyi yok sayma: kayıp = c * 2^n ; en büyük kayıp örneği
    kayip = []
    for A, B, c0 in [("1111", "0001", 0), ("1111", "1111", 1), ("1000", "1000", 0)]:
        s, c, _ = topla(A, B, c0)
        gercek = int(A, 2) + int(B, 2) + c0
        kayip.append((A, B, c0, s, c, gercek, int(s, 2), gercek - int(s, 2)))
    sonuc["kayip"] = kayip
    return sonuc


# ------------------------------- Yaprak 2 ----------------------------------

def yaprak2():
    sonuc = {}
    islemler = ["1110-0011", "0011-1110", "1000-0001", "0101-0101", "0011-0000"]
    kayitlar = []
    for s in islemler:
        M, N = s.split("-")
        i1, b1, k1 = cikar_borc(M, N)
        i2, b2, k2 = cikar_tumleyen(M, N)
        kayitlar.append({"M": M, "N": N, "borc": (i1, b1, k1), "tum": (i2, b2, k2),
                         "ref": int(M, 2) - int(N, 2)})
    sonuc["islemler"] = kayitlar

    test = hata1 = hata2 = 0
    ilk_hata = None
    for m, k in product(range(16), range(16)):
        M, N = ikili(m, 4), ikili(k, 4)
        ref = m - k
        i1, b1, _ = cikar_borc(M, N)
        i2, b2, _ = cikar_tumleyen(M, N)
        test += 1
        ok1 = onlu_isaretli(i1, b1) == ref and (i1 == "0") == (ref == 0)
        ok2 = onlu_isaretli(i2, b2) == ref and (i2 == "0") == (ref == 0)
        hata1 += not ok1
        hata2 += not ok2
        if (not ok1 or not ok2) and ilk_hata is None:
            ilk_hata = (M, N)
    sonuc["kapsamli"] = (test, hata1, hata2, ilk_hata)

    # "Son elde yoksa sonuç mutlaka negatiftir" iddiası
    yanlis = []
    for m, k in product(range(16), range(16)):
        M, N = ikili(m, 4), ikili(k, 4)
        isaret, toplam, c = cikar_tumleyen_hatali(M, N)
        if (isaret == "-") != (m - k < 0):
            yanlis.append((M, N, toplam, c))
    sonuc["iddia_yanlis"] = yanlis
    sonuc["sifir_tumleyen"] = iki_tumleyeni("0000")
    # doğru yöntemde (M + N' + 1) N = 0 için son elde
    sonuc["dogru_n0"] = [(ikili(m, 4), cikar_tumleyen(ikili(m, 4), "0000")[2]["son_elde"])
                         for m in (0, 3, 15)]
    return sonuc


# ------------------------------- Yaprak 3 ----------------------------------

def yaprak3():
    sonuc = {}
    tablolar = []
    for A, B in [("1011", "101"), ("10111", "110"), ("11001", "1010")]:
        P, kismiler, cagri = carp(A, B)
        tablolar.append({"A": A, "B": B, "P": P, "kismiler": kismiler,
                         "katkilar": [int(pp, 2) for _, _, pp in kismiler],
                         "ref": int(A, 2) * int(B, 2)})
    sonuc["tablolar"] = tablolar

    testler = [("1011", "0", "çarpan sıfır"), ("1011", "1", "çarpan bir"),
               ("1011", "100", "çarpan 2^2"), ("101", "1000", "çarpan 2^3"),
               ("1011", "111", "çarpan tüm 1"), ("1111", "1111", "iki operand tüm 1"),
               ("0", "101", "çarpılan sıfır"), ("1", "1", "1 x 1"),
               ("11", "11", "n+m-1 karşı örneği"), ("110", "10001", "seyrek çarpan")]
    satirlar = []
    for A, B, ad in testler:
        P1, _, c1 = carp(A, B)
        P2, _, c2 = carp(A, B, sifirlari_atla=True)
        ref = int(A, 2) * int(B, 2)
        satirlar.append((ad, A, B, P1, P2, c1, c2, ref,
                         int(P1, 2) == ref and P1 == P2 and len(P1) == len(A) + len(B)
                         and c2 == B.count("1")))
    sonuc["testler"] = satirlar

    return sonuc


# ------------------------------- Yaprak 4 ----------------------------------

def yaprak4():
    sonuc = {}
    islemler = []
    for D, d in [("10110", "100"), ("1101", "10"), ("111", "11")]:
        r = bol(D, d, kesir_basamak=8)
        Dv, dv, Qv, Rv = int(D, 2), int(d, 2), int(r["Q"], 2), int(r["R"], 2)
        r.update(D=D, d=d, kontrol1=(Qv * dv + Rv == Dv), kontrol2=(0 <= Rv < dv),
                 ref=(Dv // dv, Dv % dv), deger=Dv / dv)
        islemler.append(r)
    sonuc["islemler"] = islemler

    sinir = []
    for D, d, ad, beklenen in [("0", "101", "sıfır bölünen", ("0", "0")),
                               ("000", "11", "sıfır bölünen (3 bit)", ("0", "0")),
                               ("11", "101", "bölen > bölünen", ("0", "11")),
                               ("101", "101", "eşit operandlar", ("1", "0")),
                               ("1011", "1011", "eşit operandlar", ("1", "0"))]:
        r = bol(D, d)
        sinir.append((ad, D, d, beklenen, (r["Q"], r["R"]), (r["Q"], r["R"]) == beklenen))
    try:
        bol("1010", "000")
        sinir.append(("sıfır bölen", "1010", "000", "ret", "KABUL EDİLDİ", False))
    except ZeroDivisionError as e:
        sinir.append(("sıfır bölen", "1010", "000", "ret", f"ret: {e}", True))
    sonuc["sinir"] = sinir

    hatali = []
    for D, d in [("10110", "100"), ("1101", "10"), ("100100", "11")]:
        Qh, Rh = bol_hatali(D, d)
        Q = bol(D, d)["Q"]
        hatali.append((D, d, Q, Qh, Rh,
                       int(Qh, 2) * int(d, 2) + int(Rh, 2) == int(D, 2)))
    sonuc["hatali"] = hatali

    return sonuc


def hepsi():
    return {1: yaprak1(), 2: yaprak2(), 3: yaprak3(), 4: yaprak4()}


if __name__ == "__main__":
    s = hepsi()
    print("Yaprak 1: 512 test, hata:", s[1]["kapsamli"][1])
    print("Yaprak 2: 256 çift, hata (borç, 2 tümleyeni):", s[2]["kapsamli"][1:3])
    print("Yaprak 3: testler uyumlu:", all(t[-1] for t in s[3]["testler"]))
    print("Yaprak 4: sınır testleri uyumlu:", all(t[-1] for t in s[4]["sinir"]))
