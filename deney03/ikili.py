"""Mantık Devreleri - Ders 3 / İkili Aritmetik deney yaprakları 1-4.

Ana hesaplar yalnızca bit düzeyinde (karakter '0'/'1' ve mantık işlemleri) yapılır.
Hazır aritmetik (int(), +, -, *, //, %) yalnızca test referanslarında ve
onlu gösterimlerde kullanılır.
"""

# ---------------------------------------------------------------------------
# Ortak yardımcılar
# ---------------------------------------------------------------------------

def dogrula(bitler, ad="girdi"):
    """Boş girdi ve geçersiz bit için ret kuralı."""
    if not isinstance(bitler, str) or len(bitler) == 0:
        raise ValueError(f"{ad}: boş girdi kabul edilmez")
    for ch in bitler:
        if ch not in "01":
            raise ValueError(f"{ad}: geçersiz bit '{ch}' (yalnızca 0/1)")


def tersle(bitler):
    """Her biti tersler (1 tümleyeni)."""
    return "".join("1" if b == "0" else "0" for b in bitler)


def sola_doldur(bitler, genislik):
    return "0" * (genislik - len(bitler)) + bitler


def bas_sifir_at(bitler):
    i = 0
    while i < len(bitler) - 1 and bitler[i] == "0":
        i += 1
    return bitler[i:]


# ---------------------------------------------------------------------------
# Yaprak 1 - Elde adımlarını gösteren ikili toplayıcı
# ---------------------------------------------------------------------------

def tam_toplayici(a, b, c):
    """Bir sütun: (sonuç biti, çıkan elde). a, b, c in {0, 1}."""
    s = a ^ b ^ c
    c_out = (a & b) | (c & (a ^ b))
    return s, c_out


def dogruluk_tablosu():
    satirlar = []
    for a in (0, 1):
        for b in (0, 1):
            for c in (0, 1):
                s, co = tam_toplayici(a, b, c)
                satirlar.append((a, b, c, s, co))
    return satirlar


def topla(A, B, elde0=0):
    """n bitlik A + B + elde0. Döner: (toplam, son_elde, sütun_kaydı).

    sütun_kaydı satırı: (ağırlık i, a_i, b_i, gelen elde, sonuç biti, çıkan elde)
    """
    dogrula(A, "A")
    dogrula(B, "B")
    if len(A) != len(B):
        raise ValueError(f"farklı uzunluk: {len(A)} ve {len(B)} bit")
    if elde0 not in (0, 1):
        raise ValueError("başlangıç eldesi 0 ya da 1 olmalı")
    n = len(A)
    c = elde0
    sonuc = [""] * n
    kayit = []
    for i in range(n):              # sağdan sola: ağırlık 2^i
        a = 1 if A[n - 1 - i] == "1" else 0
        b = 1 if B[n - 1 - i] == "1" else 0
        s, co = tam_toplayici(a, b, c)
        kayit.append((i, a, b, c, s, co))
        sonuc[n - 1 - i] = "1" if s else "0"
        c = co
    return "".join(sonuc), c, kayit


# ---------------------------------------------------------------------------
# Yaprak 2 - Borç alma ve 2 tümleyeniyle çıkarma
# ---------------------------------------------------------------------------

def _borcla_cikar_ham(M, N):
    """Sabit genişlikte M - N, borç alarak. Döner: (fark, son_borç, kayıt)."""
    n = len(M)
    borc = 0
    fark = [""] * n
    kayit = []
    for i in range(n):
        m = 1 if M[n - 1 - i] == "1" else 0
        k = 1 if N[n - 1 - i] == "1" else 0
        d = m ^ k ^ borc
        b_out = ((1 - m) & k) | ((1 - (m ^ k)) & borc)
        kayit.append((i, m, k, borc, d, b_out))
        fark[n - 1 - i] = "1" if d else "0"
        borc = b_out
    return "".join(fark), borc, kayit


def cikar_borc(M, N):
    """Doğrudan çıkarma. Döner: (işaret, büyüklük, kayıtlar).

    Son borç 1 ise M < N'dir; büyüklük aynı yöntemle N - M hesaplanarak bulunur.
    """
    dogrula(M, "M")
    dogrula(N, "N")
    if len(M) != len(N):
        raise ValueError("farklı uzunluk")
    fark, borc, kayit = _borcla_cikar_ham(M, N)
    kayitlar = {"M-N": kayit, "son_borc": borc}
    if borc == 0:
        # sıfır durumu ayrıca: işaretsiz "0"
        return ("+" if "1" in fark else "0"), fark, kayitlar
    buyukluk, _, kayit2 = _borcla_cikar_ham(N, M)
    kayitlar["N-M"] = kayit2
    return "-", buyukluk, kayitlar


def _tumleyen_topla_ham(X, Y, elde0):
    """2 tümleyeni yöntemi için kendi tam toplayıcı zinciri (cikar_borc'u çağırmaz)."""
    n = len(X)
    c = elde0
    s = [""] * n
    kayit = []
    for i in range(n):
        a = 1 if X[n - 1 - i] == "1" else 0
        b = 1 if Y[n - 1 - i] == "1" else 0
        t, co = tam_toplayici(a, b, c)
        kayit.append((i, a, b, c, t, co))
        s[n - 1 - i] = "1" if t else "0"
        c = co
    return "".join(s), c, kayit


def cikar_tumleyen(M, N):
    """M - N = M + (N'nin 1 tümleyeni) + 1. '+1' başlangıç eldesi olarak girer.

    Son elde 1 -> M >= N, sonuç doğrudan toplamdır.
    Son elde 0 -> M < N, büyüklük = toplamın 2 tümleyeni.
    """
    dogrula(M, "M")
    dogrula(N, "N")
    if len(M) != len(N):
        raise ValueError("farklı uzunluk")
    n = len(M)
    N1 = tersle(N)
    toplam, son_elde, kayit = _tumleyen_topla_ham(M, N1, 1)
    kayitlar = {"N_1tum": N1, "M+N'+1": kayit, "son_elde": son_elde}
    if son_elde == 1:
        if "1" in toplam:
            return "+", toplam, kayitlar
        return "0", toplam, kayitlar
    T1 = tersle(toplam)
    buyukluk, _, kayit2 = _tumleyen_topla_ham(T1, "0" * n, 1)
    kayitlar["buyukluk"] = kayit2
    return "-", buyukluk, kayitlar


def iki_tumleyeni(N):
    """Sabit genişlikte 2 tümleyeni (taşan elde atılır). Döner: (sonuç, atılan elde)."""
    s, c, _ = _tumleyen_topla_ham(tersle(N), "0" * len(N), 1)
    return s, c


def cikar_tumleyen_hatali(M, N):
    """Hatalı yaklaşım: önce 2 tümleyenini ayrı hesaplayıp kesmek, sonra eldesiz toplamak.
    'Son elde yoksa negatif' kuralı burada N = 0 için yanlış karar verir."""
    N2, _ = iki_tumleyeni(N)
    toplam, son_elde, _ = _tumleyen_topla_ham(M, N2, 0)
    return ("+" if son_elde == 1 else "-"), toplam, son_elde


# ---------------------------------------------------------------------------
# Yaprak 3 - Kısmi çarpımlarla ikili çarpıcı
# ---------------------------------------------------------------------------

def kismi_carpim(A, b_i, i, genislik):
    """i konumundaki çarpan biti için: b_i = 1 ise A, değilse 0...0;
    sağa i adet 0 eklenerek i kez sola kaydırılır, n+m bite sola sıfırla doldurulur."""
    taban = A if b_i == "1" else "0" * len(A)
    return sola_doldur(taban + "0" * i, genislik)


def carp(A, B, sifirlari_atla=False):
    """A (n bit) x B (m bit) -> n+m bit. Döner: (çarpım, kısmi_çarpımlar, toplama_sayısı).

    Sayım kuralı: biriktirici 0...0 ile başlar; biriktiriciye eklenen her kısmi
    çarpım bir toplama çağrısıdır. v1: m çağrı, v2 (sıfırları atla): B'deki 1 sayısı.
    """
    dogrula(A, "çarpılan")
    dogrula(B, "çarpan")
    n, m = len(A), len(B)
    g = n + m
    acc = "0" * g
    kismiler = []
    cagri = 0
    for i in range(m):
        b_i = B[m - 1 - i]
        pp = kismi_carpim(A, b_i, i, g)
        kismiler.append((i, b_i, pp))
        if sifirlari_atla and b_i == "0":
            continue
        acc, son_elde, _ = topla(acc, pp, 0)
        cagri += 1
        assert son_elde == 0, "n+m bit yetmedi (olmamalı)"
    return acc, kismiler, cagri


# ---------------------------------------------------------------------------
# Yaprak 4 - Bölüm, kalan ve kesirli bölme
# ---------------------------------------------------------------------------

def buyuk_esit(X, Y):
    """X >= Y ? (baştaki sıfırlar atılarak; önce uzunluk, sonra soldan ilk farklı bit)."""
    X, Y = bas_sifir_at(X), bas_sifir_at(Y)
    if len(X) != len(Y):
        return len(X) > len(Y)
    for x, y in zip(X, Y):
        if x != y:
            return x == "1"
    return True


def _fark(X, Y):
    """X >= Y varsayımıyla X - Y (borçlu çıkarma), baştaki sıfırlar atılmış."""
    g = max(len(X), len(Y))
    f, borc, _ = _borcla_cikar_ham(sola_doldur(X, g), sola_doldur(Y, g))
    assert borc == 0
    return bas_sifir_at(f)


def bol(D, d, kesir_basamak=0):
    """Soldan sağa uzun bölme. Döner: sözlük (Q, R, adimlar, kesir, kesir_adim, tam_mi)."""
    dogrula(D, "bölünen")
    dogrula(d, "bölen")
    if "1" not in d:
        raise ZeroDivisionError("bölen sıfır: bölme tanımsız, girdi reddedildi")
    if not (0 <= kesir_basamak <= 8):
        raise ValueError("kesir basamağı 0..8 olmalı")
    r = "0"
    q = []
    adimlar = []
    for j, bit in enumerate(D):
        parca = bas_sifir_at(r + bit)          # kalanı sola kaydır, sıradaki biti indir
        if buyuk_esit(parca, d):
            qb = "1"
            r = _fark(parca, d)
        else:
            qb = "0"
            r = parca
        q.append(qb)
        adimlar.append((j + 1, parca, qb, r))
    Q = bas_sifir_at("".join(q))
    R = r
    kesir = []
    kesir_adim = []
    gorulen = {R: 0}
    tekrar = None
    while R != "0" and len(kesir) < kesir_basamak:
        parca = bas_sifir_at(R + "0")
        if buyuk_esit(parca, d):
            fb = "1"
            R = _fark(parca, d)
        else:
            fb = "0"
            R = parca
        kesir.append(fb)
        kesir_adim.append((len(kesir), parca, fb, R))
        if R in gorulen and tekrar is None and R != "0":
            tekrar = (gorulen[R], len(kesir), R)
        gorulen.setdefault(R, len(kesir))
    return {
        "Q": Q, "R": r, "adimlar": adimlar,
        "kesir": "".join(kesir), "kesir_adim": kesir_adim,
        "tam_mi": R == "0", "tekrar": tekrar,
    }


def bol_hatali(D, d):
    """Hatalı sürüm: bölen sığmadığında bölüme 0 yazmayı atlar (sıfır biti düşer)."""
    r = "0"
    q = []
    for bit in D:
        parca = bas_sifir_at(r + bit)
        if buyuk_esit(parca, d):
            q.append("1")
            r = _fark(parca, d)
        else:
            r = parca                      # HATA: q.append("0") unutuldu
    return bas_sifir_at("".join(q) or "0"), r
