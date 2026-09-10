import streamlit as st
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------------------------------------------------------------
# Sayfa Yapılandırması & Özel CSS (Koyu Mavi / Beyaz Tema)
# -------------------------------------------------------------
st.set_page_config(page_title="Panthera Lojistik Sipariş Portalı", layout="wide", page_icon="🚚")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    
    .header-banner {
        background: linear-gradient(135deg, #002060 0%, #004080 100%);
        color: white;
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .header-banner h1 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        margin: 0;
        letter-spacing: 1.5px;
    }
    .header-banner p { color: #d1e2ff; margin-top: 8px; font-size: 1.1rem; }

    .section-title {
        color: #002060;
        font-weight: 600;
        border-bottom: 2px solid #002060;
        padding-bottom: 6px;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    .stButton>button {
        background-color: #002060 !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 12px 28px !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 10px rgba(0,32,96,0.2);
    }
    .stButton>button:hover {
        background-color: #004080 !important;
        box-shadow: 0 6px 15px rgba(0,64,128,0.3);
        transform: translateY(-1px);
    }
    </style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# E-POSTA GÖNDERİM FONKSİYONU (Çoklu Gönderici & Çoklu Alıcı)
# -------------------------------------------------------------
def siparis_mailleri_gonder(siparis_detaylari, musteri_epostaları_raw):
    SMTP_SUNUCU = "smtp.gmail.com"
    SMTP_PORT = 587

    # ---------------------------------------------------------
    # ⚠️ 1. SİSTEM GÖNDERİCİ MAİLLERİ (Birden fazla tanımlanabilir)
    # Her hesap için "Uygulama Şifresi" girilmelidir.
    # ---------------------------------------------------------
    SISTEM_GONDERICI_HESAPLAR = [
        {"eposta": "yildizsususu@gmail.com", "sifre": "mcghpjgagzzwioha"},
        # {"eposta": "sistem2@pantheralojistik.com.tr", "sifre": "yyyy yyyy yyyy yyyy"} <-- İkinci yedek sistem maili
    ]

    # ---------------------------------------------------------
    # ⚠️ 2. HEDEF OPERASYON / İÇ EKİP ALICILARI (Çoklu Alıcı)
    # ---------------------------------------------------------
    HEDEF_OPERASYON_ALICILARI = [
        "sudeozkoc@pantheralojistik.com.tr",
        
        
    ]
    # ---------------------------------------------------------

    # 3. Müşterinin girdiği mail(leri) ayrıştır (virgül veya noktalı virgül ile çoklu yazabilir)
    musteri_eposta_listesi = [
        e.strip() for e in musteri_epostaları_raw.replace(";", ",").split(",") if e.strip()
    ]

    # Mail Şablonları
    konu_yonetici = f"🚨 YENİ SİPARİŞ: {siparis_detaylari['Firma']} - İrsaliye: {siparis_detaylari['İrsaliye']}"
    body_yonetici = f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #002060;">Panthera Lojistik - Yeni Sipariş Bildirimi</h2>
        <p><b>Aşağıdaki müşteri yeni bir sipariş kaydı oluşturdu:</b></p>
        <hr style="border: 1px solid #002060;">
        <ul>
            <li><b>Sipariş Veren Firma:</b> {siparis_detaylari['Firma']}</li>
            <li><b>Yetkili Adı Soyadı:</b> {siparis_detaylari['Yetkili']}</li>
            <li><b>Müşteri İletişim E-Posta(ları):</b> {', '.join(musteri_eposta_listesi)}</li>
            <li><b>İrsaliye Numarası:</b> {siparis_detaylari['İrsaliye']}</li>
            <li><b>Planlanan Teslim Tarihi:</b> {siparis_detaylari['Teslim Tarihi']}</li>
        </ul>
        
        <h3 style="color: #002060;">Teslimat Adresi Bilgileri</h3>
        <p>
            <b>Teslimat Noktası:</b> {siparis_detaylari['Depo Kodu']}<br>
            <b>Açık Adres:</b> {siparis_detaylari['Adres']}<br>
            <b>İl / İlçe:</b> {siparis_detaylari['İlçe']} / {siparis_detaylari['İl']}<br>
            <b>Posta Kodu:</b> {siparis_detaylari['Posta Kodu']}<br>
            <b>Teslimat Kontak/Tel:</b> {siparis_detaylari['Yetkili Tel']}
        </p>

        <h3 style="color: #002060;">Yük ve Palet Detayları</h3>
        <table border="1" cellpadding="8" cellspacing="0" style="border-collapse: collapse; width: 100%; border-color: #ddd;">
            <tr style="background-color: #002060; color: white;">
                <th>Kategori</th>
                <th>Koli Sayısı</th>
                <th>Palet Sayısı</th>
                <th>Ağırlık (KG)</th>
            </tr>
            <tr>
                <td><b>Kuru Yük</b></td>
                <td>{siparis_detaylari['Koli']}</td>
                <td>{siparis_detaylari['Kuru Palet']}</td>
                <td>{siparis_detaylari['Kuru KG']} KG</td>
            </tr>
            <tr style="background-color: #f9f9f9;">
                <td><b>Soğuk Yük (+4°C)</b></td>
                <td>-</td>
                <td>{siparis_detaylari['Soğuk Palet']}</td>
                <td>{siparis_detaylari['Soğuk KG']} KG</td>
            </tr>
            <tr>
                <td><b>Donuk Yük (-18°C)</b></td>
                <td>-</td>
                <td>{siparis_detaylari['Donuk Palet']}</td>
                <td>{siparis_detaylari['Donuk KG']} KG</td>
            </tr>
        </table>
        <br>
        <p><b>Açıklama / Özel Notlar:</b> {siparis_detaylari['Açıklama']}</p>
    </div>
    """

    konu_musteri = f"✅ Siparişiniz Alındı - {siparis_detaylari['Firma']} (İrsaliye: {siparis_detaylari['İrsaliye']})"
    body_musteri = f"""
    <div style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #002060;">Panthera Lojistik Sipariş Portalı</h2>
        <p>Sayın <b>{siparis_detaylari['Yetkili']}</b>,</p>
        <p>Sipariş talebiniz operasyon ekibimize başarıyla ulaşmıştır ve işleme alınmıştır.</p>
        <hr style="border: 1px solid #002060;">
        <p><b>Sipariş Özetiniz:</b></p>
        <ul>
            <li><b>İrsaliye No:</b> {siparis_detaylari['İrsaliye']}</li>
            <li><b>Teslimat Adresi:</b> {siparis_detaylari['İlçe']} / {siparis_detaylari['İl']}</li>
            <li><b>Teslim Tarihi:</b> {siparis_detaylari['Teslim Tarihi']}</li>
            <li><b>Toplam Palet:</b> {siparis_detaylari['Kuru Palet'] + siparis_detaylari['Soğuk Palet'] + siparis_detaylari['Donuk Palet']} Palet</li>
        </ul>
        <p>Bizi tercih ettiğiniz için teşekkür ederiz.</p>
        <br>
        <p style="font-size: 0.9rem; color: #666;"><i>Panthera Lojistik Operasyon Ekibi</i></p>
    </div>
    """

    # Gönderici hesaplar üzerinden mail gönderme denemesi
    for gonderici in SISTEM_GONDERICI_HESAPLAR:
        try:
            server = smtplib.SMTP(SMTP_SUNUCU, SMTP_PORT)
            server.starttls()

            print("SMTP ile giriş deneniyor:", gonderici["eposta"])
            server.login(gonderici["eposta"], gonderici["sifre"])

            # 1. Mail: Hedef Operasyon Ekibine Gönderim (Çoklu Alıcı)
            msg1 = MIMEMultipart()
            msg1['From'] = f"Panthera Sipariş Portalı <{gonderici['eposta']}>"
            msg1['To'] = ", ".join(HEDEF_OPERASYON_ALICILARI)
            msg1['Reply-To'] = ", ".join(musteri_eposta_listesi)
            msg1['Subject'] = konu_yonetici
            msg1.attach(MIMEText(body_yonetici, 'html'))
            server.send_message(msg1)

            # 2. Mail: Müşterinin Girdiği Mail(ler)e Onay Gönderimi (Çoklu Müşteri Alıcısı)
            msg2 = MIMEMultipart()
            msg2['From'] = f"Panthera Lojistik <{gonderici['eposta']}>"
            msg2['To'] = ", ".join(musteri_eposta_listesi)
            msg2['Subject'] = konu_musteri
            msg2.attach(MIMEText(body_musteri, 'html'))
            server.send_message(msg2)

            server.quit()
            return True, "Başarılı"
        except Exception as e:
            # Biri hata verirse döngü devam edip sonraki sistem göndericisini dener
            last_error = str(e)
            continue

    return False, last_error


# -------------------------------------------------------------
# HAZIR DEPO VERİTABANI
# -------------------------------------------------------------
HAZIR_DEPOLAR = [
    {
        "kod": "001 - BİM / Konya Depo (Karatay)",
        "il": "Konya",
        "ilce": "Karatay",
        "adres": "Fevzi Çakmak Mah. 10542. Sk. No:12",
        "posta_kodu": "42050"
    },
    {
        "kod": "002 - BİM / Konya Depo (Selçuklu)",
        "il": "Konya",
        "ilce": "Selçuklu",
        "adres": "Organize Sanayi Bölgesi 5. Sok No:8",
        "posta_kodu": "42250"
    },
    {
        "kod": "003 - A101 / Ankara Lojistik Merkezi",
        "il": "Ankara",
        "ilce": "Kazan",
        "adres": "Saray Mah. 100. Yıl Bulvarı No:45",
        "posta_kodu": "06980"
    }
]

# -------------------------------------------------------------
# ARAYÜZ (FRONTEND)
# -------------------------------------------------------------

st.markdown("""
    <div class="header-banner">
        <h1>PANTHERA LOJİSTİK SİPARİŞ PORTALI</h1>
        <p>Lütfen sipariş ve teslimat bilgilerinizi eksiksiz doldurunuz.</p>
    </div>
""", unsafe_allow_html=True)

# 1. BÖLÜM: MÜŞTERİ KİMLİK BİLGİLERİ
st.markdown('<h3 class="section-title">1. Müşteri ve İletişim Bilgileri</h3>', unsafe_allow_html=True)

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    siparis_veren = st.text_input("Sipariş Veren Firma Adı *")
with col_f2:
    yetkili_ad = st.text_input("Sipariş Veren Yetkili Adı Soyadı *")
with col_f3:
    musteri_eposta = st.text_input("E-Posta Adresiniz (Birden fazla ise virgül ile ayırınız) *", help="Örn: ahmet@firma.com, mehmet@firma.com")

# 2. BÖLÜM: TESLİMAT NOKTASI VE ADRES BİLGİLERİ
st.markdown('<h3 class="section-title">2. Teslimat Noktası ve Adres Seçimi</h3>', unsafe_allow_html=True)

depo_secenekleri = ["Seçiniz..."] + [d["kod"] for d in HAZIR_DEPOLAR] + ["➕ Listede Yok / Yeni Adres Gireceğim"]

secilen_depo_kodu = st.selectbox(
    "Teslimat Yapılacak Depo veya Adres *",
    options=depo_secenekleri,
    index=0
)

secilen_hazir_depo = next((d for d in HAZIR_DEPOLAR if d["kod"] == secilen_depo_kodu), None)

if secilen_depo_kodu == "➕ Listede Yok / Yeni Adres Gireceğim":
    st.info("💡 Aradığınız depo listede yoksa aşağıdaki alanlara teslimat yapılacak açık adresi eksiksiz giriniz.")
    
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        il = st.text_input("İl (Şehir) *")
    with col_a2:
        ilce = st.text_input("İlçe *")
    with col_a3:
        posta_kodu = st.text_input("Posta Kodu *")
    with col_a4:
        yetkili_tel = st.text_input("Teslimat Noktası Yetkili/Tel")
    
    acik_adres = st.text_area("Açık Adres (Cadde, Mahalle, Sokak, No) *")

else:
    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        il = st.text_input("İl (Şehir) *", value=secilen_hazir_depo["il"] if secilen_hazir_depo else "", disabled=True)
    with col_a2:
        ilce = st.text_input("İlçe *", value=secilen_hazir_depo["ilce"] if secilen_hazir_depo else "", disabled=True)
    with col_a3:
        posta_kodu = st.text_input("Posta Kodu *", value=secilen_hazir_depo["posta_kodu"] if secilen_hazir_depo else "", disabled=True)
    with col_a4:
        yetkili_tel = st.text_input("Teslimat Noktası Yetkili/Tel")
    
    acik_adres = st.text_area("Açık Adres *", value=secilen_hazir_depo["adres"] if secilen_hazir_depo else "", disabled=True)

# 3. BÖLÜM: YÜK VE İRSALİYE DETAYLARI
st.markdown('<h3 class="section-title">3. Yük ve İrsaliye Detayları</h3>', unsafe_allow_html=True)

col_d1, col_d2, col_d3 = st.columns(3)

with col_d1:
    irsaliye_no = st.text_input("İrsaliye Numarası (İlk 3 Harf + 13 Rakam = 16 Karakter) *", max_chars=16, help="Örn: ABC2026000001234")
    teslim_tarihi = st.date_input("Planlanan Teslim Tarihi *", value=date.today())
    aciklama = st.text_input("Açıklama / Özel Notlar")

with col_d2:
    koli_sayisi = st.number_input("Koli Sayısı", min_value=0, step=1, value=0)
    kuru_palet = st.number_input("Kuru Palet Sayısı", min_value=0, step=1, value=0)
    soguk_palet = st.number_input("Soğuk Palet (+4°C) Sayısı", min_value=0, step=1, value=0)
    donuk_palet = st.number_input("Donuk Palet (-18°C) Sayısı", min_value=0, step=1, value=0)

with col_d3:
    kuru_kg = st.number_input("Kuru Yük KG", min_value=0.0, step=0.5, value=0.0)
    soguk_kg = st.number_input("Soğuk Yük (+4°C) KG", min_value=0.0, step=0.5, value=0.0)
    donuk_kg = st.number_input("Donuk Yük (-18°C) KG", min_value=0.0, step=0.5, value=0.0)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# GÖNDER BUTONU VE KONTROLLER
# -------------------------------------------------------------
if st.button("🚀 Siparişi Onayla ve Gönder", use_container_width=True):
    irsaliye_clean = irsaliye_no.strip()
    
    # 1. Zorunlu Alan Kontrolü
    if not siparis_veren or not yetkili_ad or not musteri_eposta or not irsaliye_clean or secilen_depo_kodu == "Seçiniz...":
        st.error("❌ Lütfen kırmızı yıldızlı (*) zorunlu alanları (Firma, Yetkili, E-Posta, İrsaliye No, Teslimat Noktası) doldurunuz!")
    
    # 2. İrsaliye Numarası Format Kontrolü (Tam 16 Karakter ve İlk 3'ü Harf)
    elif len(irsaliye_clean) != 16 or not irsaliye_clean[:3].isalpha():
        st.error("❌ İrsaliye Numarası geçersiz! İrsaliye No **tam 16 karakter** olmalı ve **ilk 3 karakteri harf** içermelidir (Örn: ABC2026000001234).")
    
    # 3. Yeni Adres Kontrolü
    elif secilen_depo_kodu == "➕ Listede Yok / Yeni Adres Gireceğim" and (not il or not ilce or not acik_adres or not posta_kodu):
        st.error("❌ Yeni adres seçeneğini seçtiniz. Lütfen Şehir, İlçe, Açık Adres ve Posta Kodu alanlarını doldurunuz!")
    
    # 4. Yük Miktarı Kontrolü
    elif (kuru_palet + soguk_palet + donuk_palet) == 0 and koli_sayisi == 0:
        st.warning("⚠️ Lütfen en az bir adet Palet veya Koli miktarı giriniz!")
    
    else:
        siparis_verileri = {
            "Firma": siparis_veren,
            "Yetkili": yetkili_ad,
            "İrsaliye": irsaliye_clean,
            "Depo Kodu": secilen_depo_kodu,
            "İl": il,
            "İlçe": ilce,
            "Posta Kodu": posta_kodu,
            "Adres": acik_adres,
            "Yetkili Tel": yetkili_tel if yetkili_tel else "Belirtilmedi",
            "Teslim Tarihi": str(teslim_tarihi),
            "Koli": koli_sayisi,
            "Kuru Palet": kuru_palet,
            "Soğuk Palet": soguk_palet,
            "Donuk Palet": donuk_palet,
            "Kuru KG": kuru_kg,
            "Soğuk KG": soguk_kg,
            "Donuk KG": donuk_kg,
            "Açıklama": aciklama if aciklama else "Yok"
        }
        
        with st.spinner("Sipariş iletiliyor..."):
            basari, hata_mesaji = siparis_mailleri_gonder(siparis_verileri, musteri_eposta)
        
        if basari:
            st.success(f"🎉 Siparişiniz operasyon ekibimize iletilmiştir! Onay e-postası belirtilen müşteri adres(ler)ine gönderildi.")
            st.balloons()
        else:
            st.error(f"❌ E-posta gönderilemedi! Hata Detayı: {hata_mesaji}")
            st.info("💡 **İpucu:** Lütfen `SISTEM_GONDERICI_HESAPLAR` alanındaki Gmail şifrenizin normal şifre değil, Google 'Uygulama Şifresi' olduğunu doğrulayın.")
