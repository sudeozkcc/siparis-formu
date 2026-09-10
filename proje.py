import streamlit as st
import pandas as pd
from datetime import date
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Sayfa Yapılandırması
st.set_page_config(page_title="PANTHERA - Sipariş Giriş Portalı", layout="wide")

# ==========================================
# E-POSTA GÖNDERİM FONKSİYONU
# ==========================================
def siparis_mailleri_gonder(siparis_detaylari, musteri_eposta):
    # SİSTEM VE SİZİN E-POSTA BİLGİLERİNİZ
    SMTP_SUNUCU = "smtp.gmail.com"
    SMTP_PORT = 587
    SISTEM_EPOSTA = "sistem.panthera@gmail.com"  # Bildirimleri gönderen sistem maili
    SISTEM_SIFRE = "xxxx xxxx xxxx xxxx"          # Gmail Uygulama Şifresi
    
    SIZIN_EPOSTANIZ = "operasyon@sirketiniz.com"   # Siparişlerin düşmesini istediğiniz KENDİ mail adresiniz

    # -------------------------------------------------------------
    # 1. SİZE GİDECEK MAİL İÇERİĞİ (Detaylı Sipariş Bildirimi)
    # -------------------------------------------------------------
    konu_yonetici = f"🚨 YENİ SİPARİŞ GELMİŞTİR: {siparis_detaylari['Firma']} - İrsaliye: {siparis_detaylari['İrsaliye']}"
    body_yonetici = f"""
    <h2>PANTHERA Sipariş Portalı - Yeni Sipariş Düştü</h2>
    <p>Aşağıdaki müşteri yeni bir sipariş oluşturdu:</p>
    <hr>
    <ul>
        <li><b>Sipariş Veren Firma:</b> {siparis_detaylari['Firma']}</li>
        <li><b>Yetkili Adı Soyadı:</b> {siparis_detaylari['Yetkili']}</li>
        <li><b>Müşteri E-Posta:</b> {musteri_eposta}</li>
        <li><b>İrsaliye Numarası:</b> {siparis_detaylari['İrsaliye']}</li>
        <li><b>Teslimat Noktası / Depo:</b> {siparis_detaylari['Depo Kodu']}</li>
        <li><b>Teslimat Adresi:</b> {siparis_detaylari['Adres']}</li>
        <li><b>Planlanan Teslim Tarihi:</b> {siparis_detaylari['Teslim Tarihi']}</li>
    </ul>
    <h3>Yük ve Palet Detayları:</h3>
    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse;">
        <tr style="background-color: #f2f2f2;">
            <th>Kategori</th>
            <th>Koli</th>
            <th>Palet Sayısı</th>
            <th>Ağırlık (KG)</th>
        </tr>
        <tr>
            <td><b>Kuru Yük</b></td>
            <td>{siparis_detaylari['Koli']}</td>
            <td>{siparis_detaylari['Kuru Palet']}</td>
            <td>{siparis_detaylari['Kuru KG']} KG</td>
        </tr>
        <tr>
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
    <p><b>Açıklama / Notlar:</b> {siparis_detaylari['Açıklama']}</p>
    """

    # -------------------------------------------------------------
    # 2. MÜŞTERİYE GİDECEK MAİL İÇERİĞİ (Otomatik Alındı Teyidi)
    # -------------------------------------------------------------
    konu_musteri = f"✅ Siparişiniz Alındı - {siparis_detaylari['Firma']} ({siparis_detaylari['İrsaliye']})"
    body_musteri = f"""
    <h2>PANTHERA Sipariş Sistemi</h2>
    <p>Sayın <b>{siparis_detaylari['Yetkili']}</b>,</p>
    <p>Oluşturduğunuz sipariş talebiniz başarıyla bize ulaşmıştır ve işleme alınmıştır.</p>
    <hr>
    <p><b>Sipariş Özetiniz:</b></p>
    <ul>
        <li><b>İrsaliye No:</b> {siparis_detaylari['İrsaliye']}</li>
        <li><b>Teslimat Noktası:</b> {siparis_detaylari['Depo Kodu']}</li>
        <li><b>Teslim Tarihi:</b> {siparis_detaylari['Teslim Tarihi']}</li>
        <li><b>Toplam Palet:</b> {siparis_detaylari['Kuru Palet'] + siparis_detaylari['Soğuk Palet'] + siparis_detaylari['Donuk Palet']} Palet</li>
    </ul>
    <p>Sipariş sürecinizle ilgili bir değişiklik olduğunda tarafınıza bilgilendirme yapılacaktır.</p>
    <hr>
    <p><i>PANTHERA Lojistik Otomasyon Sistemi</i></p>
    """

    try:
        server = smtplib.SMTP(SMTP_SUNUCU, SMTP_PORT)
        server.starttls()
        server.login(SISTEM_EPOSTA, SISTEM_SIFRE)

        # Mail 1: Size Giden Sipariş Bildirimi
        msg1 = MIMEMultipart()
        msg1['From'] = f"PANTHERA Sipariş Formu <{SISTEM_EPOSTA}>"
        msg1['To'] = SIZIN_EPOSTANIZ
        msg1['Reply-To'] = musteri_eposta  # Siz yanıtlaya bastığınızda müşteriye gitsin
        msg1['Subject'] = konu_yonetici
        msg1.attach(MIMEText(body_yonetici, 'html'))
        server.send_message(msg1)

        # Mail 2: Müşteriye Giden Bilgilendirme Teyidi
        msg2 = MIMEMultipart()
        msg2['From'] = f"PANTHERA Sipariş Sistemi <{SISTEM_EPOSTA}>"
        msg2['To'] = musteri_eposta
        msg2['Subject'] = konu_musteri
        msg2.attach(MIMEText(body_musteri, 'html'))
        server.send_message(msg2)

        server.quit()
        return True
    except Exception as e:
        print("E-posta Gönderim Hatası:", e)
        return False


# ==========================================
# VERİ TABANI (Depo ve Adres Kodları)
# ==========================================
if 'depo_db' not in st.session_state:
    st.session_state.depo_db = [
        {
            "kod": "001 - BİM / Konya Depo (Karatay)",
            "firma": "BİM",
            "il": "Konya",
            "ilce": "Karatay",
            "adres": "Fevzi Çakmak Mah. 10542. Sk. No:12",
            "posta_kodu": "42050"
        },
        {
            "kod": "002 - BİM / Konya Depo (Selçuklu)",
            "firma": "BİM",
            "il": "Konya",
            "ilce": "Selçuklu",
            "adres": "Organize Sanayi Bölgesi 5. Sok No:8",
            "posta_kodu": "42250"
        },
        {
            "kod": "008 - Diğer / Özel Müşteri Adresi",
            "firma": "Diğer",
            "il": "İstanbul",
            "ilce": "Kadıköy",
            "adres": "Bağdat Caddesi No:100",
            "posta_kodu": "34724"
        }
    ]

tab1, tab2 = st.tabs(["📝 Müşteri Sipariş Formu", "⚙️ Yönetici - Adres / Depo Ekle"])

# ==========================================
# SEKMELER 1: MÜŞTERİ SİPARİŞ FORMU
# ==========================================
with tab1:
    st.title("PANTHERA Sipariş Giriş Portalı")
    
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        siparis_veren = st.text_input("Sipariş Veren Firma Adı *")
    with col_f2:
        yetkili_ad = st.text_input("Yetkili Adı Soyadı *")
    with col_f3:
        musteri_eposta = st.text_input("E-Posta Adresiniz (Onay Maili Gelecektir) *")
    with col_f4:
        siparis_tarihi = st.date_input("Sipariş Tarihi", value=date.today())

    st.markdown("---")
    st.subheader("Teslimat Noktası ve Adres Seçimi")

    kod_listesi = [item["kod"] for item in st.session_state.depo_db]
    secilen_kod = st.selectbox(
        "Teslimat Noktası / Depo Kodu (Örn: bim konya, 001 vb.):",
        options=["Seçiniz..."] + kod_listesi,
        index=0
    )

    secilen_depo_detay = next((x for x in st.session_state.depo_db if x["kod"] == secilen_kod), None)

    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
    with col_a1:
        il = st.text_input("Şehir", value=secilen_depo_detay["il"] if secilen_depo_detay else "", disabled=True)
    with col_a2:
        ilce = st.text_input("İlçe", value=secilen_depo_detay["ilce"] if secilen_depo_detay else "", disabled=True)
    with col_a3:
        posta_kodu = st.text_input("Posta Kodu", value=secilen_depo_detay["posta_kodu"] if secilen_depo_detay else "", disabled=True)
    with col_a4:
        yetkili_iletisim = st.text_input("Teslimat Noktası İletişim / Tel")

    acik_adres = st.text_area("Açık Adres", value=secilen_depo_detay["adres"] if secilen_depo_detay else "", disabled=True)

    st.markdown("---")
    st.subheader("Yük ve Yükleme Detayları (Sayı Zorunlu)")

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        irsaliye_no = st.text_input("İrsaliye Numarası *")
        teslim_tarihi = st.date_input("Planlanan Teslim Tarihi", value=date.today())
        aciklama = st.text_input("Açıklama / Notlar")
    
    with col_d2:
        koli_sayisi = st.number_input("Koli Sayısı", min_value=0, step=1, value=0)
        kuru_palet = st.number_input("Kuru Palet Sayısı", min_value=0, step=1, value=0)
        soguk_palet = st.number_input("Soğuk Palet (+4°C) Sayısı", min_value=0, step=1, value=0)
        donuk_palet = st.number_input("Donuk Palet (-18°C) Sayısı", min_value=0, step=1, value=0)

    with col_d3:
        kuru_kg = st.number_input("Kuru Yük KG", min_value=0.0, step=0.5, value=0.0)
        soguk_kg = st.number_input("Soğuk Yük (+4°C) KG", min_value=0.0, step=0.5, value=0.0)
        donuk_kg = st.number_input("Donuk Yük (-18°C) KG", min_value=0.0, step=0.5, value=0.0)

    st.markdown("---")
    
    # Sipariş Gönderim
    if st.button("🚀 Siparişi Oluştur ve Gönder", use_container_width=True):
        if not siparis_veren or not irsaliye_no or not musteri_eposta or secilen_kod == "Seçiniz...":
            st.error("Lütfen Firma Adı, İrsaliye No, E-Posta adresinizi ve Teslimat Noktasını doldurunuz!")
        else:
            siparis_verileri = {
                "Firma": siparis_veren,
                "Yetkili": yetkili_ad,
                "İrsaliye": irsaliye_no,
                "Depo Kodu": secilen_kod,
                "Adres": f"{acik_adres} {ilce}/{il} PK:{posta_kodu}",
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
            
            with st.spinner("Siparişiniz iletiliyor..."):
                eposta_durum = siparis_mailleri_gonder(siparis_verileri, musteri_eposta)
            
            if eposta_durum:
                st.success(f"Siparişiniz operasyon ekibimize iletilmiştir! Onay teyidi '{musteri_eposta}' adresinize gönderildi.")
            else:
                st.warning("Sipariş kaydedildi ancak e-posta gönderimi sağlanamadı.")

# ==========================================
# SEKMELER 2: YÖNETİCİ PANATİ (ADRES / DEPO EKLEME)
# ==========================================
with tab2:
    st.header("Sisteme Yeni Depo veya Özel Adres Ekleme")
    
    with st.form("yeni_adres_formu"):
        yeni_kod = st.text_input("Depo/Adres Kodu (Örn: 009 - BİM / Antalya Depo)")
        yeni_firma = st.text_input("Firma / Müşteri Adı")
        yeni_il = st.text_input("Şehir (İl) *")
        yeni_ilce = st.text_input("İlçe *")
        yeni_adres = st.text_area("Açık Adres *")
        yeni_pk = st.text_input("Posta Kodu *")

        form_submit = st.form_submit_button("Yeni Depo / Adresi Kaydet")

        if form_submit:
            if not yeni_kod or not yeni_il or not yeni_ilce or not yeni_adres or not yeni_pk:
                st.error("Hata: İl, İlçe, Açık Adres ve Posta Kodu alanlarını doldurmak zorunludur!")
            else:
                st.session_state.depo_db.append({
                    "kod": yeni_kod,
                    "firma": yeni_firma,
                    "il": yeni_il,
                    "ilce": yeni_ilce,
                    "adres": yeni_adres,
                    "posta_kodu": yeni_pk
                })
                st.success(f"'{yeni_kod}' sisteme eklendi!")
