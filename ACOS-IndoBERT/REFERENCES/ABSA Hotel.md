## Pendekatan ABSA Terkini untuk Ulasan Hotel (2020–2025)

Berikut ringkasan 5 paper kunci yang fokus pada ABSA di domain hotel/pariwisata, dengan penekanan aspek layanan, kebersihan, kamar, lokasi, dan fasilitas.

### Ringkasan Komparatif

| Paper & Tahun | Aspek Utama (service/cleanliness/room/location/facilities) | Tipe Model | Sumber Data Ulasan | Metrik Utama | Keterbatasan Utama | Citations |
|---------------|-----------------------------------------------------------|-----------|--------------------|-------------|--------------------|-----------|
| Nadeem et al., 2025 – WSD+BERT+GCN untuk ABSA hotel | Dataset RABSA hotel; mencakup berbagai aspek hotel (service, room, location, facilities) namun tidak dinormalkan eksplisit ke 4–5 kategori standar (Nadeem et al., 2025) | BERT + BiLSTM + **GCN** dengan modul **Word Sense Disambiguation** (graph‑based Transformer) (Nadeem et al., 2025) | RABSA – himpunan ulasan hotel kaya aspek, dikumpulkan dari Booking & TripAdvisor (Nadeem et al., 2025) | Mengungguli baseline ABSA state‑of‑the‑art; metrik tidak dirinci di abstrak tapi laporan adanya peningkatan signifikan (Nadeem et al., 2025) | Fokus pada disambiguasi makna kata; tidak membahas generalisasi lintas-domain/bahasa; aspek masih cukup heterogen (Nadeem et al., 2025) | (Nadeem et al., 2025) |
| Marutho et al., 2024 – SBERT+BigBird untuk ABSA hotel | Contoh eksplisit: location, food, service; dapat dipetakan ke location, facilities/restaurant, service; kebersihan & room tidak didefinisikan khusus (Marutho et al., 2024) | **SBERT** untuk sentence embedding + Bayesian search clustering (topic/aspect discovery) + **BigBird Transformer** untuk klasifikasi (Marutho et al., 2024) | “Hotel review datasets” (domain hotel; platform spesifik tidak disebut) (Marutho et al., 2024) | Akurasi ~**99%** untuk klasifikasi aspek‑sentimen (Marutho et al., 2024) | Akurasi sangat tinggi pada dataset sendiri yang mungkin sempit; kurang detail tentang ukuran/keragaman data dan perbandingan baseline kuat berbasis BERT (Marutho et al., 2024) | (Marutho et al., 2024) |
| Fehle et al., 2023 – ABSA multi-label bahasa Jerman | Aspek kategori multi-label untuk ulasan hotel Jerman; mencakup dimensi layanan, fasilitas, lokasi, dll., namun kategori persis tidak dirinci di abstrak (Fehle et al., 2023) | Berbagai **model BERT‑based Transformer** untuk multi-label ABSA (aspect category + sentiment) (Fehle et al., 2023) | Korpus baru ulasan hotel berbahasa Jerman dari **TripAdvisor**, dianotasi manual (Fehle et al., 2023) | micro‑F1 hingga **0.91** untuk klasifikasi kategori aspek, **0.81** untuk end‑to‑end ABSA (Fehle et al., 2023) | Fokus pada bahasa Jerman; definisi aspek tidak dinormalisasi ke skema internasional; platform tunggal (TripAdvisor) (Fehle et al., 2023) | (Fehle et al., 2023) |
| Azhar & Khodra, 2020 – mBERT untuk ABSA hotel Indonesia | Aspek dikategorikan (misal service, room, location, price) tetapi kategori persis di abstrak tidak dirinci; diarahkan ke domain hotel Indonesia (Azhar & Khodra, 2020) | **Multilingual BERT (mBERT)** + metode transformasi tugas (task transformation) untuk aspect categorization & sentiment classification (Azhar & Khodra, 2020) | Ulasan hotel Indonesia; studi sebelumnya menyebut Google Play travel apps seperti Agoda, Booking, PegiPegi, Traveloka, Tiket.com (Cahyaningtyas, 2021; Azhar & Khodra, 2020) | Peningkatan F1 sekitar **+8%** dibanding baseline CNN+XGBoost (Azhar & Khodra, 2020) | Bergantung pada mBERT umum, belum domain‑tuned; OOV berkurang tetapi tidak dihilangkan; skema aspek tidak sepenuhnya distandarkan (Azhar & Khodra, 2020) | (Azhar & Khodra, 2020; Cahyaningtyas, 2021) |
| Cahyaningtyas et al., 2021 – DL ABSA hotel Indonesia | Enam aspek: **harga, hotel (fasilitas umum), kamar (room), lokasi, pelayanan (service), restoran**; kebersihan tercakup dalam atribut hotel/fasilitas (Cahyaningtyas, 2021) | Perbandingan 8 model DL: RNN, LSTM, GRU, BiLSTM, Attention‑BiLSTM, CNN, CNN‑LSTM, CNN‑BiLSTM; LSTM terbaik untuk klasifikasi aspek, CNN terbaik untuk klasifikasi sentimen aspek (Cahyaningtyas, 2021) | Ulasan hotel Indonesia dari **Agoda, Booking.com, PegiPegi, Traveloka, Tiket.com** (Cahyaningtyas, 2021) | Akurasi aspek: **0.926** dengan LSTM; akurasi sentimen aspek rata‑rata **0.904** dengan CNN (Cahyaningtyas, 2021) | Model berbasis kata tanpa Transformer; aspek “hotel” dan “fasilitas” relatif kasar; tidak menangani aspek implisit atau multi‑label kompleks (Cahyaningtyas, 2021) |

**Figure 1:** Perbandingan pendekatan ABSA 2020–2025 pada ulasan hotel.

## Pola Umum Pendekatan Terbaik (2020–2025)

### Aspek yang Digunakan
- Skema aspek eksplisit yang paling dekat dengan permintaan pengguna (service/cleanliness/room/location/facilities) terdapat pada studi Indonesia: **service, room, location, restoran/food, harga, serta hotel/fasilitas** (Cahyaningtyas, 2021).  
- Studi IndoBERT pada UGC wisata memakai **Service Quality, Cleanliness, Location and Accessibility, Amenities and Facilities, Attractions and Activities** yang sangat sejajar dengan service/cleanliness/location/facilities (Perwira et al., 2025).  
- Studi implicit aspect TripAdvisor menggunakan: **staff service, cleanliness, value for money, location convenience** (Ban, 2025).

### Tipe Model Dominan
- **Transformer‑based (BERT family)** menjadi standar emas:
  - BERT + BiLSTM/GCN untuk eksploitasi struktur graf & WSD (Nadeem et al., 2025).
  - SBERT + BigBird untuk embedding kalimat dan klasifikasi aspek‑sentimen (Marutho et al., 2024).
  - mBERT/IndoBERT/AraBERT untuk bahasa non‑Inggris dan domain pariwisata (Shafiq et al., 2023; Azhar & Khodra, 2020; Fadel et al., 2022; Perwira et al., 2025).
  - BERT‑based multi‑label untuk bahasa Jerman (Fehle et al., 2023).
- **Deep learning non‑Transformer** masih kompetitif di konteks sumber daya terbatas:
  - LSTM/CNN untuk klasifikasi aspek dan sentimen di hotel Indonesia (Cahyaningtyas, 2021).
  - GRU/BiGRU‑CNN‑CRF untuk bahasa Arab hotel reviews (Soliman & Farghaly, 2021).

### Sumber Dataset
- **TripAdvisor**: korpus hotel Jerman (Fehle et al., 2023); studi implicit aspect hotel (TripAdvisor) (Ban, 2025); referensi umum hotel ABSA (Nadeem et al., 2025; Li et al., 2022).
- **Booking.com**: digunakan bersama TripAdvisor untuk RABSA (Nadeem et al., 2025); juga muncul pada korpus multi‑platform Indonesia (Cahyaningtyas, 2021).
- **Agoda, PegiPegi, Traveloka, Tiket.com**: dipakai bersamaan dengan Booking untuk dataset hotel Indonesia (Cahyaningtyas, 2021).
- **Google Reviews**: digunakan untuk wisata/tourism Indonesia dengan aspek service, cleanliness, location, amenities/facilities (Perwira et al., 2025).

### Metrik
- Umumnya **accuracy** dan **F1‑score (micro/macro)**:
  - F1_micro 0.82–0.84 untuk ABSA Vietnam (hotel) dengan BERT‑hierarchical (Tran & Bui, 2020).
  - F1 hingga 0.91 (aspek) dan 0.81 (end‑to‑end ABSA) untuk hotel Jerman dengan BERT (Fehle et al., 2023).
  - F1 +8% vs baseline untuk mBERT hotel Indonesia (Azhar & Khodra, 2020).
  - Akurasi 0.926 (aspek) dan 0.904 (sentimen aspek) pada ulasan hotel multi‑platform Indonesia (Cahyaningtyas, 2021).
  - Akurasi ~99% dengan SBERT+BigBird, perlu dicermati kemungkinan overfitting (Marutho et al., 2024).

### Keterbatasan Umum
- **Skema aspek tidak seragam**; banyak studi mendefinisikan kategori sendiri, sehingga pemetaan ke service/cleanliness/room/location/facilities perlu normalisasi manual (Nadeem et al., 2025; Fehle et al., 2023; Cahyaningtyas, 2021).
- **Bahasa & domain‑spesifik**: model sering dilatih untuk satu bahasa (Arab, Indonesia, Vietnam, Jerman) dan satu domain (hotel), sehingga transfer ke bahasa/platform lain tidak dijamin (Shafiq et al., 2023; Tran & Bui, 2020; Fehle et al., 2023; Azhar & Khodra, 2020; Fadel et al., 2022; Perwira et al., 2025; Cahyaningtyas, 2021).
- **Data anotasi terbatas**: terutama untuk aspek implisit, multi‑label, dan review multi‑aspek (Nadeem et al., 2025; Ban, 2025; Perwira et al., 2025).
- **Kurangnya evaluasi cross‑platform** (TripAdvisor vs Booking vs Google vs Agoda): sebagian besar penelitian memakai satu atau beberapa situs saja (Nadeem et al., 2025; Fehle et al., 2023; Perwira et al., 2025; Cahyaningtyas, 2021).
- **Sedikit yang menangani aspek implisit dan multi‑label secara eksplisit**; ada studi khusus implicit aspect TripAdvisor, tapi tidak berbasis Transformer (Ban, 2025).
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
Azhar, A. N., & Khodra, M. L. (2020). Fine-tuning Pretrained Multilingual BERT Model for Indonesian Aspect-based Sentiment Analysis. *2020 7th International Conference on Advance Informatics: Concepts, Theory and Applications (ICAICTA)*, 1-6. https://doi.org/10.1109/icaicta49861.2020.9428882
 
Ban, L. (2025). Implicit Aspect Analysis for Sentiment Classification: A Case Study on Hotel Reviews. *Journal of Information Systems Engineering and Management*. https://doi.org/10.52783/jisem.v10i45s.9152
 
Cahyaningtyas, S. (2021). Deep Learning for Aspect-Based Sentiment Analysis on Indonesian Hotels Reviews. *Kinetik: Game Technology, Information System, Computer Network, Computing, Electronics, and Control*. https://doi.org/10.22219/kinetik.v6i3.1300
 
Fadel, A. S., Saleh, M., & Abulnaja, O. (2022). Arabic Aspect Extraction Based on Stacked Contextualized Embedding With Deep Learning. *IEEE Access, 10*, 30526-30535. https://doi.org/10.1109/access.2022.3159252
 
Fehle, J., Münster, L., Schmidt, T., & Wolff, C. (2023). Aspect-Based Sentiment Analysis as a Multi-Label Classification Task on the Domain of German Hotel Reviews. 202-218.
 
Li, H.-Y., Yu, B. X. B., Li, G., & Gao, H. (2022). Restaurant survival prediction using customer-generated content: An aspect-based sentiment analysis of online reviews. *Tourism Management*. https://doi.org/10.1016/j.tourman.2022.104707
 
Marutho, D., M., Rustad, S., & P. (2024). Optimizing Aspect-Based Sentiment Analysis Using Sentence Embedding Transformer, Bayesian Search Clustering, and Sparse Attention Mechanism. *Journal of Open Innovation: Technology, Market, and Complexity*. https://doi.org/10.1016/j.joitmc.2024.100211
 
Nadeem, A., Missen, M. S., Reshan, M. S. A., Memon, M. A., Asiri, Y., Nizamani, M. A., Alsulami, M., & Shaikh, A. (2025). Resolving ambiguity in natural language for enhancement of aspect-based sentiment analysis of hotel reviews. *PeerJ Computer Science, 11*. https://doi.org/10.7717/peerj-cs.2635
 
Perwira, R., Permadi, V. A., Purnamasari, D., & Agusdin, R. P. (2025). Domain-Specific Fine-Tuning of IndoBERT for Aspect-Based Sentiment Analysis in Indonesian Travel User-Generated Content. *Journal of Information Systems Engineering and Business Intelligence*. https://doi.org/10.20473/jisebi.11.1.30-40
 
Shafiq, G. M., Hamza, T., Alrahmawy, M., & El-Deeb, R. (2023). Enhancing Arabic Aspect-Based Sentiment Analysis Using End-to-End Model. *IEEE Access, 11*, 142062-142076. https://doi.org/10.1109/access.2023.3342755
 
Soliman, T., & Farghaly, M. F. (2021). Arabic aspect based sentiment analysis using bidirectional GRU based models. *Journal of King Saud University Computer and Information Sciences, 34*, 6652 - 6662. https://doi.org/10.1016/j.jksuci.2021.08.030
 
Tran, O., & Bui, V. T. (2020). A BERT-based Hierarchical Model for Vietnamese Aspect Based Sentiment Analysis. *2020 12th International Conference on Knowledge and Systems Engineering (KSE)*, 269-274. https://doi.org/10.1109/kse50997.2020.9287650
 
