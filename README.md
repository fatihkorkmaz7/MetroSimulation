# Metro Seyahat Rehberim 🚇

Bu proje, metro ağı üzerinde en az aktarma ve en hızlı rota bulma işlemlerini gerçekleştiren bir Python uygulamasıdır. Kullanıcılar başlangıç ve hedef istasyonlarını seçerek, iki nokta arasındaki en uygun rotayı bulabilirler. Ayrıca favori rotalarını ekleyebilir ve yolcu simülasyonları yaparak metro ağının yoğunluk haritasını görebilirler.

## Kullanılan Teknolojiler ve Kütüphaneler 🛠️

- **Python**: Projenin temel programlama dili.
- **collections**: Veri yapılarını (defaultdict, deque) kullanmak için.
- **heapq**: Öncelik kuyruğu (priority queue) işlemleri için.
- **typing**: Tip kontrolü ve açıklamalar için.
- **gradio**: Web tabanlı kullanıcı arayüzü oluşturmak için.
- **networkx**: Grafik ve ağ analizleri için.
- **matplotlib**: Grafiklerin görselleştirilmesi için.
- **random**: Rastgele sayı ve seçim işlemleri için.

## Kurulum 🖥️

Projeyi çalıştırmak için gerekli kütüphaneleri yüklemek için aşağıdaki adımları takip edebilirsiniz:

1. Gerekli kütüphaneleri yükleyin:
    ```sh
    pip install gradio networkx matplotlib
    ```

2. Proje dosyasını indirin ve çalıştırın:
    ```sh
    python metro_seyahat_rehberim.py
    ```

3. Çalıştırdıktan sonra konsolda aşağıdaki gibi bir URL görünecektir:
    ```
    Running on local URL:  http://127.0.0.1:7860
    ```

4. Bu URL'ye tıklayarak uygulama arayüzüne erişebilir ve uygulamayı kullanmaya başlayabilirsiniz.

## Algoritmaların Çalışma Mantığı 🤖

### BFS (Breadth-First Search) Algoritması

BFS algoritması, bir grafikte en kısa yolu bulmak için kullanılır. Bu projede, iki istasyon arasındaki en az aktarmalı rotayı bulmak için BFS algoritması kullanılmıştır.

1. Başlangıç istasyonundan başlar.
2. Komşu istasyonları ziyaret eder ve her komşuyu bir kuyruğa ekler.
3. Hedef istasyona ulaşana kadar bu işlemi tekrarlar.
4. Hedef istasyona ulaşıldığında, ziyaret edilen istasyonların yolunu döndürür.

### A* Algoritması

A* algoritması, hedefe en hızlı şekilde ulaşmak için kullanılır. Bu projede, iki istasyon arasındaki en hızlı rotayı bulmak için kullanılmıştır.

1. Başlangıç istasyonundan başlar ve toplam süreyi 0 olarak başlatır.
2. Komşu istasyonları ziyaret eder ve her komşuyu bir öncelik kuyruğuna ekler.
3. Hedef istasyona ulaşana kadar bu işlemi tekrarlar.
4. Hedef istasyona ulaşıldığında, en düşük süreli rotayı döndürür.

### Neden Bu Algoritmaları Kullanıyoruz ❓

- **BFS**: En kısa yol bulma problemi için idealdir ve aktarma sayısını en aza indirmek için kullanılır.
- **A***: Heuristik yaklaşımı ile en hızlı rotayı bulmak için kullanılır ve süreyi minimize eder.

## Örnek Kullanım ve Test Sonuçları 🧪

```markdown
=== Test Senaryoları ===

1. K1'den S10'a:
   - En az aktarmalı rota: Kızılay (K1) -> Kızılay (S10)
   - En hızlı rota (1 dakika): Kızılay (K1) -> Kızılay (S10)

2. Y1'den T10'a:
   - En az aktarmalı rota: Kızılay (Y1) -> Kızılay (K1) -> Ulus (K2) -> Yeni Mahalle (K3) -> OSB (K4) -> Akköprü (K5) -> Sanayi (K6) -> Gimat (K7) -> Gimat (T9) -> Ostim (T10)
   - En hızlı rota (26 dakika): Kızılay (Y1) -> Kızılay (K1) -> Ulus (K2) -> Yeni Mahalle (K3) -> Yeni Mahalle (T2) -> Batıkent (T1) -> Batıkent (K8) -> Ergazi (K9) -> Ostim (K10) -> Ostim (T10)

3. M1'den K10'a:
   - En az aktarmalı rota: AŞTİ (M1) -> Kızılay (M2) -> Sıhhiye (M3) -> Gar (M4) -> Gar (S1) -> Gar (T3) -> Yeni Mahalle (T2) -> Batıkent (T1) -> Batıkent (K8) -> Ergazi (K9) -> Ostim (K10)
   - En hızlı rota (27 dakika): AŞTİ (M1) -> Kızılay (M2) -> Kızılay (S10) -> Kızılay (K1) -> Ulus (K2) -> Yeni Mahalle (K3) -> Yeni Mahalle (T2) -> Batıkent (T1) -> Batıkent (K8) -> Ergazi (K9) -> Ostim (K10)
```

## Projeyi Geliştirme Fikirleri 💡

- **Gerçek Zamanlı Veri Entegrasyonu**: Metro sefer saatleri ve yoğunluk bilgilerini gerçek zamanlı olarak entegre etmek, kullanıcıların daha doğru ve güncel bilgilere ulaşmasını sağlar. Gerçek veriler ile duraklar arası sürelerin ve durakların tamamen doğru olduğu bir sistem düzenlemesi yapılabilir.
- **Alternatif Algoritmalar**: Alternatif yolları bulmak için farklı algoritmalar ekleyerek kullanıcıya çeşitli seçenekler sunulabilir.
- **Kullanıcı Geri Bildirimi Sistemi**: Kullanıcıların geri bildirimlerini toplayarak ve analiz ederek uygulamayı sürekli olarak geliştirmek mümkün olabilir.
- **Mobil Uygulama Geliştirme**: Projeyi mobil uyumlu hale getirerek daha geniş bir kullanıcı kitlesine ulaşabilir ve kullanıcı deneyimini artırabiliriz.
- **Yolcu Yoğunluğu Analizi**: Yolcu yoğunluğunu analiz ederek, daha etkili güzergahlar ve sefer saatleri önerilebilir. Bu sayede metro sisteminin verimliliği artırılabilir.
- **Kişiselleştirilmiş Rota Önerileri**: Kullanıcıların geçmiş tercihlerini ve alışkanlıklarını dikkate alarak kişiselleştirilmiş rota önerileri sunulabilir.
- **Daha Detaylı Görselleştirme**: Metro ağının daha detaylı ve etkileşimli görselleştirmeleri ekleyerek kullanıcıların daha iyi bir anlayış kazanmasını sağlayabiliriz.
- **Sesli Rehberlik**: Kullanıcıların görme engelli olması durumunda sesli rehberlik sağlayarak, erişilebilirliği artırabiliriz.
- **Kapsamlı Test Senaryoları**: Geniş bir yelpazede test senaryoları oluşturarak, uygulamanın farklı durumlarda nasıl performans gösterdiğini ölçebiliriz.