"""Deney yapraklarındaki 'Kısa cevap ve doğrulama notları' alanlarının metinleri.
Hem ek dosyada hem de doldurulmuş yaprakta aynı metin kullanılır."""

KISA_CEVAPLAR = {
    1: [
        ("İlk tahminim",
         "0101 + 0011 = 1000, elde 0. 1111 + 0001 ve 1111 + 0000 + 1 için 0000 ve elde 1, "
         "1111 + 1111 + 1 için 1111 ve elde 1 bekledim."),
        ("Bağımsız kontrolüm",
         "512 testin hepsinde elde·16 + toplamı Python'un normal toplamasıyla karşılaştırdım, hiç hata çıkmadı."),
        ("Karşı örneğim",
         "1111 + 0001'de son elde atılırsa sonuç 0000 kalıyor, yani 16 kayboluyor. Genel olarak kayıp elde·2ⁿ."),
        ("YZ beyanı",
         "Claude'dan kod taslağı aldım. Dört işlemi önce elle çözdüm, sonra 512 testle karşılaştırdım."),
    ],
    2: [
        ("İlk tahminim",
         "1110 − 0011 = +1011, 0011 − 1110 = −1011, 1000 − 0001 = +0111, 0101 − 0101 = 0, "
         "0011 − 0000 = +0011 olur diye düşündüm."),
        ("Bağımsız kontrolüm",
         "256 çiftin hepsini iki yöntemle ayrı ayrı hesaplayıp Python'daki M − N ile karşılaştırdım. "
         "İkisinde de hata çıkmadı."),
        ("Karşı örneğim",
         "0000 − 0000: 0000'ın 2 tümleyeni yine 0000, toplamada elde çıkmıyor ama sonuç negatif değil, 0. "
         "Bu yüzden +1'i başlangıç eldesi olarak verdim."),
        ("YZ beyanı",
         "YZ ile kod yazdım. N = 0 durumunu ayrıca denedim, karar kuralını buna göre kurdum."),
    ],
    3: [
        ("İlk tahminim",
         "1011 × 101 = 55 = 0110111, 10111 × 110 = 138 = 10001010, 11001 × 1010 = 250 = 011111010 "
         "çıkacağını hesapladım."),
        ("Bağımsız kontrolüm",
         "Kısmi çarpımların onlu değerlerini elle topladım (11 + 0 + 44 = 55 gibi) ve 10 testte iki sürümü "
         "onlu çarpımla karşılaştırdım."),
        ("Karşı örneğim",
         "11 × 11 = 1001 (9). n + m − 1 = 3 bitle en fazla 7 yazılabildiği için 3 bit yetmiyor."),
        ("YZ beyanı",
         "Claude'dan kod taslağı aldım. Üç kısmi çarpım tablosunu elle toplayarak kontrol ettim."),
    ],
    4: [
        ("İlk tahminim",
         "10110 ÷ 100 için Q = 101, R = 10; 1101 ÷ 10 için Q = 110, R = 1; 111 ÷ 11 için Q = 10, R = 1 "
         "ve kesrin bitmeyeceğini düşündüm."),
        ("Bağımsız kontrolüm",
         "Her işlemde Q·d + R = D ve R < d koşullarına ayrı ayrı baktım, sonuçları Python'un // ve % "
         "operatörleriyle karşılaştırdım."),
        ("Karşı örneğim",
         "Aradaki sıfırı atan sürüm 10110 ÷ 100 için Q = 11 veriyor: 3·4 + 2 = 14, 22 değil. "
         "Q·d + R kontrolü bunu yakalıyor."),
        ("YZ beyanı",
         "YZ ile kod yazdım. Sıfır böleni ve sınır durumlarını kendim deneyip sonuçları kontrol ettim."),
    ],
}
