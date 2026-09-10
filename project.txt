import streamlit as st
import pandas as pd
from datetime import date

# Sayfa Yapılandırması
st.set_page_config(page_title="Otomatik Sipariş & Depo Yönetim Sistemi", layout="wide")

# 1. ÖRNEK VERİ TABANI (Depo ve Adres Kodları)
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
            "kod": "003 - A101 / Ankara Lojistik Depo",
            "firma": "A101",
            "il": "Ankara",
            "ilce": "Sincan",
            "adres": "Ankara Sanayi Bölgesi 2. Cadde",
            "posta_kodu": "06935"
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

# YÖNETİCİ VE MÜŞTERİ SEKMELERİ
tab1, tab2 = st.tabs(["📝 Müşteri Sipariş Formu", "⚙️ Yönetici - Adres / Depo Ekle"])

# ==========================================
# SEKMELER 1: MÜŞTERİ SİPARİŞ FORMU
# ==========================================
with tab1:
    st.header("Sipariş Giriş Portalı")
    
    # 1. Firma ve Genel Bilgiler
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        siparis_veren = st.text_input("Sipariş Veren Firma Adı *")
    with col_f2:
        yetkili_ad = st.text_input("Yetkili Adı Soyadı *")
    with col_f3:
        siparis_tarihi = st.date_input("Sipariş Tarihi", value=date.today())

    st.markdown("---")
    st.subheader("Teslimat Noktası ve Adres Seçimi")

    # Arama & Otomatik Tamamlama Kutusu
    kod_listesi = [item["kod"] for item in st.session_state.depo_db]
    secilen_kod = st.selectbox(
        "Teslimat Noktası / Depo Kodu Arayın (Örn: bim konya, 001, a101 vb.):",
        options=["Seçiniz..."] + kod_listesi,
        index=0
    )

    # Seçilen Depoya Göre Adres Bilgilerini Doldurma
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
    st.subheader("Yük ve Yükleme Detayları (Sadece Sayı Girilebilir)")

    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        irsaliye_no = st.text_input("İrsaliye Numarası *")
        teslim_tarihi = st.date_input("Planlanan Teslim Tarihi", value=date.today())
        aciklama = st.text_input("Açıklama / Notlar")
    
    with col_d2:
        # Sayısal alanlar (min_value=0 ve step=1 ile sadece tam sayı zorunluluğu)
        koli_sayisi = st.number_input("Koli Sayısı", min_value=0, step=1, value=0)
        kuru_palet = st.number_input("Kuru Palet Sayısı", min_value=0, step=1, value=0)
        soguk_palet = st.number_input("Soğuk Palet (+4°C) Sayısı", min_value=0, step=1, value=0)
        donuk_palet = st.number_input("Donuk Palet (-18°C) Sayısı", min_value=0, step=1, value=0)

    with col_d3:
        # KG Değerleri (Ondalıklı/Tam sayı girdisi)
        kuru_kg = st.number_input("Kuru Yük KG", min_value=0.0, step=0.5, value=0.0)
        soguk_kg = st.number_input("Soğuk Yük (+4°C) KG", min_value=0.0, step=0.5, value=0.0)
        donuk_kg = st.number_input("Donuk Yük (-18°C) KG", min_value=0.0, step=0.5, value=0.0)

    st.markdown("---")
    if st.button("🚀 Siparişi Oluştur ve Kaydet", use_container_width=True):
        if not siparis_veren or not irsaliye_no or secilen_kod == "Seçiniz...":
            st.error("Lütfen yıldızlı (*) alanları ve Teslimat Noktasını doldurunuz!")
        else:
            st.success("Sipariş başarıyla oluşturuldu ve otomasyon sistemine aktarıldı!")
            st.json({
                "Firma": siparis_veren,
                "İrsaliye": irsaliye_no,
                "Depo Kod": secilen_kod,
                "Adres": f"{acik_adres} {ilce}/{il} PK:{posta_kodu}",
                "Toplam Palet": kuru_palet + soguk_palet + donuk_palet,
                "Toplam KG": kuru_kg + soguk_kg + donuk_kg
            })


# ==========================================
# SEKMELER 2: YÖNETİCİ PANATİ (ADRES / DEPO EKLEME)
# ==========================================
with tab2:
    st.header("Sisteme Yeni Depo veya Özel Adres Ekleme")
    st.info("Eklenecek yeni adreslerde İl, İlçe, Açık Adres ve Posta Kodu alanları zorunludur.")

    with st.form("yeni_adres_formu"):
        yeni_kod = st.text_input("Depo/Adres Kodu (Örn: 009 - BİM / Antalya Depo)", help="Müşterinin listede göreceği format")
        yeni_firma = st.text_input("Firma / Müşteri Adı")
        yeni_il = st.text_input("Şehir (İl) *")
        yeni_ilce = st.text_input("İlçe *")
        yeni_adres = st.text_area("Açık Adres *")
        yeni_pk = st.text_input("Posta Kodu *")

        form_submit = st.form_submit_button("Yeni Depo / Adresi Kaydet")

        if form_submit:
            # Zorunlu alan kontrolü
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
                st.success(f"'{yeni_kod}' başarıyla sisteme eklendi! Müşteri arama listesinde anında görüntülenecektir.")