"""Deney yapraklarındaki 'Kısa cevap ve doğrulama notları' alanlarının metinleri.
Hem ek dosyada hem de doldurulmuş yaprakta aynı metin kullanılır."""

YZ = "Kod/tablo taslağında YZ (Claude) kullandım; sonuçları tam tarama testi ve elle hesapla doğruladım."

KISA_CEVAPLAR = {
    1: [
        ("İlk tahminim",
         "0101+0011 = 1000 (C=0); 1111+0001 = 0000 (C=1); 1111+0000+1 = 0000 (C=1); "
         "1111+1111+1 = 1111 (C=1). Gerçek değer = C·2ⁿ + S."),
        ("Bağımsız kontrolüm",
         "16·16·2 = 512 testin hepsinde C·16 + S ile onlu A+B+c0 karşılaştırıldı: 0 hata. "
         "Aynı kod n = 1…8 için de 0 hata verdi."),
        ("Karşı örneğim",
         "Son elde atılırsa 1111+0001 → 0000 (16 yerine 0); kayıp C·2ⁿ = 2⁴ = 16. "
         "1111+1111+1 = 31 → 1111 = 15 kalır."),
        ("YZ beyanı", YZ + " 1111+1111+1 = 11111 elle denetlendi."),
    ],
    2: [
        ("İlk tahminim",
         "1110−0011 = +1011 (11); 0011−1110 = −1011 (−11); 1000−0001 = +0111 (7); "
         "0101−0101 = 0; 0011−0000 = +0011 (3)."),
        ("Bağımsız kontrolüm",
         "256 çiftte borç ve 2 tümleyeni yöntemleri ayrı ayrı onlu M−N ile karşılaştırıldı: "
         "ikisinde de 0 hata, uyumsuz çift yok."),
        ("Karşı örneğim",
         "0000−0000: 2tüm(0000) = 0000 (taşan 1 atılır), 0000+0000 son elde 0 ama sonuç 0, negatif "
         "değil. Doğru kural: M+N'+1 tek geçişte; elde 1 ⇔ M ≥ N."),
        ("YZ beyanı", YZ + " N = 0 durumu ayrıca tarandı."),
    ],
    3: [
        ("İlk tahminim",
         "1011×101 = 0110111 (55); 10111×110 = 10001010 (138); 11001×1010 = 011111010 (250)."),
        ("Bağımsız kontrolüm",
         "Onlu katkılar 11+0+44 = 55, 0+46+92 = 138, 0+50+0+200 = 250; 10 test ve 15876 çarpımlık "
         "tarama 0 hata. Toplama: v1 = m, v2 = B'deki 1 sayısı."),
        ("Karşı örneğim",
         "(2ⁿ−1)(2ᵐ−1) < 2ⁿ⁺ᵐ → n+m bit yeter. 11×11 = 1001 (9) 4 bit ister; "
         "n+m−1 = 3 bit en çok 7 gösterir."),
        ("YZ beyanı", YZ + " Kısmi çarpımlar elle toplandı."),
    ],
    4: [
        ("İlk tahminim",
         "10110÷100: Q = 101, R = 10 (= 101.1); 1101÷10: Q = 110, R = 1 (= 110.1); "
         "111÷11: Q = 10, R = 1 (≈ 10.01010101)."),
        ("Bağımsız kontrolüm",
         "Her işlemde Q·d+R = D ve 0 ≤ R < d ayrı ayrı sağlandı; // ve % ile 7650 bölmelik "
         "tarama 0 hata. 111÷11'de kalanlar 1, 10, 1, 10… tekrar eder."),
        ("Karşı örneğim",
         "Ara sıfırı atan sürüm 10110÷100 için Q = 11 verir: 11·100+10 = 1110 (14) ≠ 10110 (22). "
         "Q = 100, R = 110 de Q·d+R = D sağlar ama R ≥ d."),
        ("YZ beyanı", YZ + " Sıfır bölen reddi sınandı."),
    ],
}
