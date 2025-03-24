from collections import defaultdict, deque
import heapq
from typing import Dict, List, Tuple, Optional
import gradio as gr
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random


class Istasyon:
    def __init__(self, idx: str, ad: str, hat: str):
        self.idx = idx
        self.ad = ad
        self.hat = hat
        self.komsular: List[Tuple['Istasyon', int]] = []  # (istasyon, süre) tuple'ları

    def komsu_ekle(self, istasyon: 'Istasyon', sure: int):
        self.komsular.append((istasyon, sure))

    def __lt__(self, other: 'Istasyon'):
        return self.idx < other.idx


class MetroAgi:
    def __init__(self):
        self.istasyonlar: Dict[str, Istasyon] = {}
        self.hatlar: Dict[str, List[Istasyon]] = defaultdict(list)
        self.favori_rotalar: List[str] = []  # Favori rotaları saklamak için

    def istasyon_ekle(self, idx: str, ad: str, hat: str) -> None:
        if idx not in self.istasyonlar:
            istasyon = Istasyon(idx, ad, hat)
            self.istasyonlar[idx] = istasyon
            self.hatlar[hat].append(istasyon)

    def baglanti_ekle(self, istasyon1_id: str, istasyon2_id: str, sure: int) -> None:
        istasyon1 = self.istasyonlar[istasyon1_id]
        istasyon2 = self.istasyonlar[istasyon2_id]
        istasyon1.komsu_ekle(istasyon2, sure)
        istasyon2.komsu_ekle(istasyon1, sure)

    def en_az_aktarma_bul(self, baslangic_id: str, hedef_id: str) -> Optional[List[Istasyon]]:
        if hedef_id not in self.istasyonlar or baslangic_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]

        kuyruk = deque([(baslangic, [baslangic])])  # (mevcut_istasyon, gidilen_yol)
        ziyaret_edilen = set()  # Ziyaret edilen istasyonlar

        while kuyruk:
            mevcut_istasyon, yol = kuyruk.popleft()

            if mevcut_istasyon.idx == hedef.idx:
                return yol  # İstasyona varıldı

            ziyaret_edilen.add(mevcut_istasyon.idx)  # İstasyon ziyaret edildi

            for komsu, _ in mevcut_istasyon.komsular:
                if komsu.idx not in ziyaret_edilen:
                    kuyruk.append((komsu, yol + [komsu]))

        return None  # Rota bulunamadı

    def en_hizli_rota_bul(self, baslangic_id: str, hedef_id: str) -> Optional[Tuple[List[Istasyon], int]]:
        if hedef_id not in self.istasyonlar or baslangic_id not in self.istasyonlar:
            return None

        baslangic = self.istasyonlar[baslangic_id]
        hedef = self.istasyonlar[hedef_id]

        pq = [(0, baslangic, [baslangic])]  # (toplam_sure, mevcut_istasyon, yol)
        ziyaret_edilen = set()  # Ziyaret edilen istasyonlar

        while pq:
            toplam_sure, mevcut_istasyon, yol = heapq.heappop(pq)  # En düşük süreli rota

            if mevcut_istasyon.idx == hedef.idx:
                return (yol, toplam_sure)  # Hedefe ulaşıldı

            if mevcut_istasyon.idx in ziyaret_edilen:
                continue

            ziyaret_edilen.add(mevcut_istasyon.idx)

            for komsu, sure in mevcut_istasyon.komsular:
                if komsu.idx not in ziyaret_edilen:
                    yeni_toplam_sure = toplam_sure + sure
                    heapq.heappush(pq, (yeni_toplam_sure, komsu, yol + [komsu]))

        return None  # Rota bulunamadı

    def agi_gorsellestir(self) -> str:
        G = nx.Graph()

        # İstasyonları ekleme
        for istasyon in self.istasyonlar.values():
            G.add_node(istasyon.idx, label=istasyon.ad, hat=istasyon.hat)

        # Bağlantıları ekleme
        for istasyon in self.istasyonlar.values():
            for komsu, sure in istasyon.komsular:
                G.add_edge(istasyon.idx, komsu.idx, weight=sure)

        # Ağ görselleştirmesi için boyut ayarlama kısmı
        pos = nx.spring_layout(G, seed=42, k=0.5, iterations=100)
        plt.figure(figsize=(16, 12))

        # Düğümlerin çizim bölümü
        hat_colors = {'Kırmızı Hat': 'red', 'Mavi Hat': 'blue', 'Turuncu Hat': 'orange', 'Yeşil Hat': 'green',
                      'Sarı Hat': 'yellow'}
        node_colors = [hat_colors[istasyon.hat] for istasyon in self.istasyonlar.values()]
        nx.draw(G, pos, with_labels=True, labels=nx.get_node_attributes(G, 'label'), node_color=node_colors,
                font_weight='bold', node_size=700, font_size=10)

        # Etiketleri çizimi
        edge_labels = nx.get_edge_attributes(G, 'weight')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

        legend_handles = [mpatches.Patch(color=color, label=hat) for hat, color in hat_colors.items()]
        plt.legend(handles=legend_handles, loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=3)

        # Grafik kaydedildi ve dosya yolu döndürülüyor
        plt.title("Metro Ağı")
        plt.savefig('metro_agi.png', bbox_inches='tight')
        plt.close()
        return 'metro_agi.png'

    def yolcu_simulasyonu(self, yolcu_sayisi: int) -> Dict[str, List[str]]:

        # İstasyon yoğunluk ağırlıkları
        # Bu kısımdaki ağırlıklar şunun için önemli: İstasyonların seçimi belli bir yoğunluğa göre seçiliyor her istasyonun seçilme ihttimali aynı değil
        # Aynı zamanda istasyonlara belirli bir değer vermek yoğun olacak istasyonların seçilmesi için de önemli
        istasyon_agirliklari = {
            "K1": 10, "K2": 5, "K3": 3, "K4": 2, "K5": 3, "K6": 5, "K7": 4, "K8": 6, "K9": 3, "K10": 4,
            "M1": 6, "M2": 8, "M3": 5, "M4": 7, "M5": 3, "M6": 4, "M7": 5, "M8": 6, "M9": 4, "M10": 5,
            "T1": 4, "T2": 3, "T3": 5, "T4": 4, "T5": 3, "T6": 5, "T7": 4, "T8": 3, "T9": 4, "T10": 5,
            "Y1": 8, "Y2": 5, "Y3": 4, "Y4": 3, "Y5": 4, "Y6": 5, "Y7": 4, "Y8": 3, "Y9": 4, "Y10": 5,
            "S1": 7, "S2": 5, "S3": 4, "S4": 3, "S5": 5, "S6": 4, "S7": 3, "S8": 5, "S9": 4, "S10": 6
        }

        agirlikli_istasyonlar = [key for key in istasyon_agirliklari for _ in range(istasyon_agirliklari[key])]

        # Oluşturduğum bu listeye her simülasyon sonucu bulunan rota eklenir ve en son bu liste yazdırılır
        yolcu_hareketleri = defaultdict(list)

        for yolcu_id in range(1, yolcu_sayisi + 1):
            # Başlangıç ve bitiş noktası rastgele seçiliyor
            baslangic_id = random.choice(agirlikli_istasyonlar)
            hedef_id = random.choice(agirlikli_istasyonlar)

            while hedef_id == baslangic_id:
                hedef_id = random.choice(agirlikli_istasyonlar)

            # Kodumuzda 2 farklı rota türü vardı burada da rastgele bir seçim yapılıyor
            rota_turu = random.choice(["En Az Aktarma", "En Hızlı Rota"])
            rota = metro_rota_bul(baslangic_id, hedef_id, rota_turu)
            yolcu_hareketleri[f"Yolcu {yolcu_id}"].append(f"{baslangic_id} -> {hedef_id}: {rota}")

        return yolcu_hareketleri


# Örnek Kullanım
if __name__ == "__main__":
    metro = MetroAgi()

    # İstasyonlar ekleme

    # Not: İstasyonlar hayali olarak eklendi gerçek rotadan farklı yerlerde bulunmaktadır

    # Kırmızı Hat
    kirmizi_istasyonlar = ["Kızılay", "Ulus", "Yeni Mahalle", "OSB", "Akköprü", "Sanayi", "Gimat", "Batıkent", "Ergazi",
                           "Ostim"]
    kirmizi_sureler = [2, 3, 4, 5, 3, 4, 6, 5, 4]
    for idx, ad in enumerate(kirmizi_istasyonlar, start=1):
        metro.istasyon_ekle(f"K{idx}", ad, "Kırmızı Hat")

    # Mavi Hat
    mavi_istasyonlar = ["AŞTİ", "Kızılay", "Sıhhiye", "Gar", "Maltepe", "Beşevler", "Bahçelievler", "Emek", "Bilkent",
                        "ODTÜ"]
    mavi_sureler = [3, 2, 4, 3, 5, 4, 3, 5, 4]
    for idx, ad in enumerate(mavi_istasyonlar, start=1):
        metro.istasyon_ekle(f"M{idx}", ad, "Mavi Hat")

    # Turuncu Hat
    turuncu_istasyonlar = ["Batıkent", "Yeni Mahalle", "Gar", "Keçiören", "Etlik", "Aşağıeğlence", "Yenimahalle",
                           "Sanayi", "Gimat", "Ostim"]
    turuncu_sureler = [4, 3, 5, 4, 3, 5, 4, 3, 5]
    for idx, ad in enumerate(turuncu_istasyonlar, start=1):
        metro.istasyon_ekle(f"T{idx}", ad, "Turuncu Hat")

    # Yeşil Hat
    yesil_istasyonlar = ["Kızılay", "Necatibey", "Kurtuluş", "Aydınlık", "Mamak", "Abidinpaşa", "Akdere", "Dikimevi",
                         "Cebeci", "Kuyubaşı"]
    yesil_sureler = [2, 3, 4, 5, 3, 4, 5, 4, 3]
    for idx, ad in enumerate(yesil_istasyonlar, start=1):
        metro.istasyon_ekle(f"Y{idx}", ad, "Yeşil Hat")

    # Sarı Hat
    sari_istasyonlar = ["Gar", "Ulus", "Sıhhiye", "Maltepe", "Çankaya", "Gölbaşı", "Emek", "Bilkent", "ODTÜ",
                        "Kızılay"]
    sari_sureler = [2, 3, 4, 3, 5, 4, 3, 5, 6]
    for idx, ad in enumerate(sari_istasyonlar, start=1):
        metro.istasyon_ekle(f"S{idx}", ad, "Sarı Hat")

    # Bağlantılar ekleme

    # Kırmızı Hat bağlantıları
    for i in range(len(kirmizi_istasyonlar) - 1):
        metro.baglanti_ekle(f"K{i + 1}", f"K{i + 2}", kirmizi_sureler[i])

    # Mavi Hat bağlantıları
    for i in range(len(mavi_istasyonlar) - 1):
        metro.baglanti_ekle(f"M{i + 1}", f"M{i + 2}", mavi_sureler[i])

    # Turuncu Hat bağlantıları
    for i in range(len(turuncu_istasyonlar) - 1):
        metro.baglanti_ekle(f"T{i + 1}", f"T{i + 2}", turuncu_sureler[i])

    # Yeşil Hat bağlantıları
    for i in range(len(yesil_istasyonlar) - 1):
        metro.baglanti_ekle(f"Y{i + 1}", f"Y{i + 2}", yesil_sureler[i])

    # Sarı Hat bağlantıları
    for i in range(len(sari_istasyonlar) - 1):
        metro.baglanti_ekle(f"S{i + 1}", f"S{i + 2}", sari_sureler[i])


    # Hat aktarma bağlantıları burada ekleniyor
    # Kızılay
    metro.baglanti_ekle("K1", "Y1", 2)
    metro.baglanti_ekle("K1", "S10", 2)
    metro.baglanti_ekle("M2", "Y1", 2)
    metro.baglanti_ekle("M2", "S10", 2)

    # Gar
    metro.baglanti_ekle("M4", "S1", 2)
    metro.baglanti_ekle("T3", "S1", 2)

    # Ulus
    metro.baglanti_ekle("K2", "S2", 2)

    # Batıkent
    metro.baglanti_ekle("K8", "T1", 2)

    # Yeni Mahalle
    metro.baglanti_ekle("K3", "T2", 2)

    # Sanayi
    metro.baglanti_ekle("K6", "T8", 2)

    # Gimat
    metro.baglanti_ekle("K7", "T9", 2)

    # Ostim
    metro.baglanti_ekle("K10", "T10", 2)

    # Sıhhiye
    metro.baglanti_ekle("M3", "S3", 2)


    # Maltepe
    metro.baglanti_ekle("M5", "S4", 1)

    # Emek
    metro.baglanti_ekle("M8", "S7", 1)

    # Bilkent
    metro.baglanti_ekle("M9", "S8", 1)

    # ODTÜ
    metro.baglanti_ekle("M10", "S9", 1)

    # Test senaryoları

    # Konsol kısmına da örnek senaryo yazdırmak amacıyla burada örnekler var.
    # Uygulamalı olarak test etmek için run işlemi sonrası konsolda gelecek local URL ye tıkladıktan sonra açılan arayüz ile test yapılabilir
    print("\n=== Test Senaryoları ===")

    # Senaryo 1:
    print("\n1. K1'den S10'a:")
    rota = metro.en_az_aktarma_bul("K1", "S10")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(f"{i.ad} ({i.idx})" for i in rota))

    sonuc = metro.en_hizli_rota_bul("K1", "S10")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(f"{i.ad} ({i.idx})" for i in rota))

    # Senaryo 2:
    print("\n2. Y1'den T10'a:")
    rota = metro.en_az_aktarma_bul("Y1", "T10")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(f"{i.ad} ({i.idx})" for i in rota))

    sonuc = metro.en_hizli_rota_bul("Y1", "T10")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(f"{i.ad} ({i.idx})" for i in rota))

    # Senaryo 3:
    print("\n3. M1'den K10'a:")
    rota = metro.en_az_aktarma_bul("M1", "K10")
    if rota:
        print("En az aktarmalı rota:", " -> ".join(f"{i.ad} ({i.idx})" for i in rota))

    sonuc = metro.en_hizli_rota_bul("M1", "K10")
    if sonuc:
        rota, sure = sonuc
        print(f"En hızlı rota ({sure} dakika):", " -> ".join(f"{i.ad} ({i.idx})" for i in rota))


# En az aktarma ya da en hızlı rota seçimi bilgileri ile kullanıcının varmak istediği yere göre rotanın bulunması için oluşturulan fonksiyon yapısı
# Bu kısım gradio kısmında rota işlemlerinin olduğu yerde kullanılıyor
def metro_rota_bul(baslangic_id: str, hedef_id: str, rota_turu: str) -> str:
    if rota_turu == "En Az Aktarma":
        rota = metro.en_az_aktarma_bul(baslangic_id, hedef_id)
        if rota:
            return " -> ".join([ist.ad for ist in rota])
        else:
            return "Rota bulunamadı"
    elif rota_turu == "En Hızlı Rota":
        rota, sure = metro.en_hizli_rota_bul(baslangic_id, hedef_id) or (None, None)
        if rota:
            return " -> ".join([ist.ad for ist in rota]) + f" (Süre: {sure} dk)"
        else:
            return "Rota bulunamadı"
    else:
        return "Geçersiz rota türü"



# Tüm istasyon ID'lerini ve adlarını listeleme kısmı
istasyon_secenekleri = {f"{istasyon.ad} ({istasyon.idx})": istasyon.idx for istasyon in metro.istasyonlar.values()}



# Gradio arayüzünde uygulamayı test edebilmek için oluşturulan bölüm
with gr.Blocks() as arayuz:
    gr.Markdown("## METRO SEYAHAT REHBERİM 🚇")

    with gr.Row():
        baslangic = gr.Dropdown(label="Başlangıç İstasyonu", choices=list(istasyon_secenekleri.keys()))
        hedef = gr.Dropdown(label="Hedef İstasyonu", choices=list(istasyon_secenekleri.keys()))

    rota_turu = gr.Radio(label="Rota Türü", choices=["En Az Aktarma", "En Hızlı Rota"])

    buton = gr.Button("Rota Bul")
    sonuc = gr.Textbox(label="Sonuç")

    # Favori rota ekleme butonu ve favori rotaları listeleme
    favori_buton = gr.Button("Favori Rota Ekle")
    favori_liste = gr.Textbox(label="Favori Rotalarım", lines=5, interactive=False)

    def arayuz_fonksiyon(baslangic_ad, hedef_ad, rota_turu):
        baslangic_id = istasyon_secenekleri[baslangic_ad]
        hedef_id = istasyon_secenekleri[hedef_ad]
        return metro_rota_bul(baslangic_id, hedef_id, rota_turu)

    def favori_ekle(rota):
        if rota not in metro.favori_rotalar:
            metro.favori_rotalar.append(rota)
        return "\n".join(metro.favori_rotalar)

    buton.click(fn=arayuz_fonksiyon, inputs=[baslangic, hedef, rota_turu], outputs=sonuc)
    favori_buton.click(fn=favori_ekle, inputs=sonuc, outputs=favori_liste)

    gorsel_sonuc = gr.Image(value=metro.agi_gorsellestir(), label="Metro Ağı")

    # Yolcu simülasyonu başlatma butonu ve sonuçları listeleme
    yolcu_sayisi = gr.Slider(label="Yolcu Sayısı", minimum=1, maximum=100, step=1, value=10)
    simulasyon_buton = gr.Button("Yolcu Simülasyonu Başlat")
    simulasyon_sonuc = gr.Textbox(label="Yolcu Hareketleri", lines=10, interactive=False)

    def simulasyon_fonksiyon(yolcu_sayisi):
        yolcu_hareketleri = metro.yolcu_simulasyonu(yolcu_sayisi)
        hareketler = [f"{yolcu}: {', '.join(rotalar)}" for yolcu, rotalar in yolcu_hareketleri.items()]
        return "\n".join(hareketler)

    simulasyon_buton.click(fn=simulasyon_fonksiyon, inputs=yolcu_sayisi, outputs=simulasyon_sonuc)

arayuz.launch()