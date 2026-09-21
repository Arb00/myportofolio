Nama : Muhammad Sabri

NPM  : 2506623793

Kelas: PBP C

### Tugas 1

#### 1. Penggunaan Elemen Semantik HTML (`<section>`, `<article>`, `<aside>`)
* **Penggunaan `<section>`:** Digunakan untuk mengelompokkan konten secara terstruktur berdasarkan bagian tersendiri, seperti profil, pengalaman, hobi, dan pendidikan.
* **Alasan Tidak Menggunakan `<article>` dan `<aside>`:** Saat ini kedua elemen tersebut belum diterapkan karena penyesuaian kebutuhan struktur halaman yang sederhana serta arahan dari rekomendasi AI.
* **Rencana Pengembangan:** Elemen `<article>` dan `<aside>` direncanakan akan diterapkan pada iterasi berikutnya, khususnya saat membuat halaman detail untuk bagian pengalaman kerja atau proyek.

---

#### 2. Tantangan Responsivitas Layout & Penggunaan Alat Bantu AI
* **Kendala yang Dihadapi:** Terjadi penataan letak (*layouting*) gambar yang tidak konsisten saat tampilan berpindah dari ukuran layar *desktop* ke ukuran layar lainnya (responsivitas).
* **Solusi & Peran AI:** Masalah penataan responsif berhasil diselesaikan dengan bantuan AI.
* **Pendekatan Evaluasi:** Evaluasi dilakukan fokus pada hasil tampilan visual (*output*) yang dihasilkan oleh AI untuk memastikan tata letak sudah sesuai dengan ekspektasi di berbagai ukuran layar.

---

#### 3. Keterbatasan Web Statis & Rencana Pengembangan Interaktif
* **Keterbatasan Web Statis:** Tidak dapat menerima input atau interaksi dinamis secara langsung dari pengguna (*user feedback/interactivity*).
* **Rencana Fitur Interaktif:** Ingin mengintegrasikan fitur permainan interaktif yang dapat dimainkan pengguna saat mengunjungi situs, seperti permainan catur melawan bot (*Chess AI*).

AI disclosure :
- Claude Sonnet : Saya menggunakan claude model sonnet untuk membuat 3 section tambahan yaitu section Experience, Hobby, dan Education.
                  Pada section Experience saya membuat sketsa seperti pulau-pulau yang menjelaskan secara singkat pengalaman saya. jika gambarnya di pencet maka akan mengarah ke halaman baru yang akan menjelaskan lebih detail(saat ini belum bisa). Saya ingin membuat bagian detailnya itu agak sedikit unik dan berwarna karena bagian utamanya agak minimalis. Saya menggunakan claude untuk proses codingnya. file index.html, experience.html, style.css, script.js, dan data.js dibuat menggunakan claude sonnet. Tujuan file experience adalah untuk halaman baru yang akan ditampilkan saat gambar-gambar di page pengalaman di tekan(Masih belum bisa dipencet sekarang dan tidak saya push). data.js adalah file yang memudahkan untuk mengubah isi konten dari website. script.js adalah file untuk membuat web bekerja dengan baik seperti mengarahkan page pengalaman di awal ke page baru.
- link claude  : https://claude.ai/share/61eb4d44-1735-432a-89c3-8c86561130ae
- ChatGPT      :  Saya menggunakan ChatGPT untuk mengenerate gambar-gambar yang saya gunakan di page halaman. Gambar-gambar hasil generate 
                  adalah logo basket dan logo teater.
- link ChatGPT tugas 1 : https://chatgpt.com/share/6a9e6d45-ffbc-83ec-9bf2-87c973575472

note : experience akan dibuat jadi folder dan ditambahkan beberapa file html yang akan menjelaskan masing-masing pengalaman

- ChatGPT      : Pada tugas 2 saya menggunakan chatGPT untuk lebih memahami cara penggunaan django dan saya menjadi paham bagaimana cara 
                 membuat code rapi dan membuat superuser atau akun admin untuk bisa menambah data dengan lebih baik. Saya jadi paham penggunaan model.py, urls.py, dan views.py. Saya juga menggunakan ChatGP untuk mengotak-atik html css pada awalnya.
- link ChatGPT tugas 2 : https://chatgpt.com/share/6aa81190-d0d8-83ec-8aaa-d57ce699a69b

- Claude sonnet : Saya menggunakan claude pada tugas 2 ini untuk membantu optimalisasi css dan html karena dari awal saya menggunakan 
                  claude untuk proses itu. jadi saya rasa claude adalah pilihan paling tepat karena sudah memahami kerangka awal html css.
- link claude sonnet tugas 2 : https://claude.ai/share/61eb4d44-1735-432a-89c3-8c86561130ae

- Gemini : Saya menggunakan gemini untuk bertanya hal-hal yang tidak terlalu penting karena gemini bisa mengirim gambar dan text dalam 
           jumlah yang besar sehingga gemini menjadi pilihan saya untuk bertanya. pada awalnya juga saya mencoba menggunakan gemini untuk html dan css namun hasilnya kurang bagus jadi saya tidak menggunakannya.
- link Gemini : https://share.gemini.google/HANvtNMyHhdJ

### Tugas 2 :

#### 1. Alur Kerja Komponen MVT (Model-View-Template) dan Routing URL pada Django
* **Routing URL:** Saat pengguna mengakses URL, permintaan pertama kali akan diproses oleh `urls.py` tingkat *project* sebagai pintu utama. Dari sana, rute permintaan akan diarahkan (*include*) ke `urls.py` milik *app* yang relevan.
* **View (Logika Bisnis):** *View* bertindak sebagai pengendali logika bisnis. *View* merespons permintaan dengan mengambil data yang dibutuhkan dari *Model*, lalu meneruskannya ke *Template*.
* **Model (Struktur Data):** *Model* mendefinisikan struktur dan skema data sesuai kebutuhan aplikasi (misalnya menentukan atribut data yang dibutuhkan pada bagian *experience* atau *education*).
* **Template (Tampilan):** *Template* berfungsi sebagai fondasi antarmuka web (HTML) dinamis, sehingga saat data pada *database* diperbarui, tampilan web akan menyesuaikan secara otomatis tanpa perlu mengubah struktur HTML.

---

#### 2. Keunggulan Penggunaan Model Dibandingkan Pengkodean Hardcode pada Template
* **Efisiensi dan Skalabilitas:** Mengelola data melalui *Model* jauh lebih efisien dibandingkan menuliskan data secara manual (*hardcode*) pada *Template*.
* **Kemudahan Pembaruan Data:** Jika terdapat data dalam jumlah besar (seperti katalog barang pada aplikasi *e-commerce*), penambahan atau perubahan data secara manual satu per satu pada HTML sangat tidak efektif. Penggunaan *Model* memungkinkan data dikelola secara dinamis, terstruktur, dan mudah diperbarui melalui *database*.

---

#### 3. Peran `makemigrations` dan `migrate` dalam Pengelolaan Database
* **Keterkaitan Kedua Perintah:** Kedua perintah ini wajib dijalankan secara berurutan agar setiap perubahan pada *Model* dapat diterapkan ke basis data.
* **`makemigrations`:** Berfungsi untuk mendeteksi perubahan pada *Model* dan membuat berkas migrasi baru sebagai *blueprint* (rancangan) perubahan struktur basis data.
* **`migrate`:** Berfungsi untuk mengeksekusi berkas *blueprint* yang telah dibuat oleh `makemigrations` dan mengaplikasikannya secara nyata ke dalam basis data.

---

- chat antigravity : 
Load older messages
Conversation Log
gw mau commit apa aja nih sarannya
Secara umum, implementasi kita saat ini:

1. Untuk Tutorial 03 (Form dan Data Delivery)
Sudah 100% SESUAI dan LENGKAP dengan dokumen PDF tutorial yang kamu kirimkan:

 Skeleton base.html & menu navigasi Projects.
 Model Project & migrasi database.
 ProjectForm berbasis ModelForm.
 View create_project (tambah project).
 View delete_project (hapus project).
 View get_projects_json (data delivery JSON) & show_projects (deserialisasi data).
 Template project.html, projects_form.html, dan modal konfirmasi hapus.
2. Catatan Khusus untuk Tugas 3 (Individual Assignment 3)
Jika tujuanmu adalah untuk pengumpulan Tugas 3 (IA3) yang dinilai di SCELE, perhatikan checklist berikut:

Fitur Update / Edit Data: Di checklist Tugas 3 biasanya diminta lengkap CRUD:
Create (sudah ada)
Delete (sudah ada)
Data Delivery JSON (sudah ada)
Update / Edit data menggunakan form → saat ini belum ada tombol/fitur edit data proyek. (Bisa langsung kita tambahkan jika kamu mau agar nilainya maksimal!).
Jawaban Pertanyaan & AI Disclosure di README.md: Untuk Tugas 3 wajib ada jawaban 5 pertanyaan reflektif (data delivery, XML vs JSON, is_valid(), CSRF token, step-by-step) dan AI Disclosure.
Saran Pesan Commit
Jika ingin langsung commit sekarang, ada 2 opsi gaya commit yang umum dan rapi:

Opsi A: 1 Commit Lengkap (Paling Praktis)
Cocok jika ingin langsung dibungkus satu kesatuan fitur:

bash


git add .
git commit -m "feat: Implement Project model, form, views, and data delivery"
(Atau mengikuti gaya commit kamu sebelumnya: git commit -m "Implement project form, views, and data delivery")

Opsi B: Atomic Commits (Bertahap & Disukai Asdos)
Commit Model & Migrasi:
bash


git add main/models.py main/admin.py main/migrations/0005_project.py
git commit -m "feat(model): Add Project model, admin registration, and migrations"
Commit Form, Views & URLs:
bash


git add main/forms.py main/views.py main/urls.py
git commit -m "feat(views): Add ProjectForm, CRUD views, and JSON/XML delivery"
Commit Templates & Styling:
bash


git add templates/ static/
git commit -m "feat(ui): Add project list, add-form, and modal delete templates"
Commit Unit Tests:
bash


git add main/tests.py
git commit -m "test: Add comprehensive unit tests for Project features"
Mau kita tambahkan sekalian fitur Edit / Update Project agar checklist Tugas 3 kamu 100% lengkap, atau mau langsung commit yang ini dulu?

9:09 PM
gw mau commit dlu baru nanti commit lagi
Siap! Kamu bisa commit pekerjaan Tutorial 03 ini dulu.

Jalankan perintah ini di terminal:

bash


git add .
git commit -m "feat: Implement project model, form, views, and data delivery"
File yang akan masuk ke dalam commit ini:

main/models.py, main/admin.py, main/migrations/0005_project.py
main/forms.py, main/views.py, main/urls.py
templates/project.html, templates/projects_form.html, templates/components/project_delete_modal.html
templates/base.html, static/css/style.css
main/tests.py
(Atau jika mau saya yang jalankan perintah commit-nya langsung dari sini, beri tahu saja ya!)

Setelah selesai di-commit, kabari ya agar kita bisa langsung lanjut tambahkan fitur Edit / Update Project untuk commit berikutnya!

9:12 PM
gw malas, lu aja yang jalanin
Beres! Sudah saya commit dengan pesan:

text


[master c72caf1] feat: Implement project model, form, views, and data delivery
 12 files changed, 664 insertions(+), 12 deletions(-)
 create mode 100644 main/migrations/0005_project.py
 create mode 100644 templates/components/project_delete_modal.html
 create mode 100644 templates/project.html
 create mode 100644 templates/projects_form.html
Status git sekarang: working tree clean.

Sekarang, mau kita lanjut tambahkan fitur Edit / Update Project (agar checklist CRUD Tugas 3 kamu lengkap), atau ada hal lain yang mau dikerjakan dulu?

9:14 PM
lanjut
9:21 PM
lanjut
Fitur Edit / Update Project sudah berhasil dibuat, diuji, dan di-commit!

Apa yang Baru Saja Dilakukan:
View edit_project: Menerima project_id, memuat data via ProjectForm(instance=project), dan menyimpan perubahan ke database.
URL Routing: Menambahkan rute /projects/<uuid:project_id>/edit/ di 
main/urls.py
.
Template: Membuat 
templates/projects_edit.html
 yang menampilkan form edit dengan data terisi otomatis.
UI Button: Menambahkan tombol Edit di setiap kartu proyek pada 
templates/project.html
.
Unit Tests: Menambahkan 2 test case baru untuk menguji fungsionalitas GET dan valid POST pada view edit (seluruh 32 tests lulus 100%).
Git Commit:
text


[master 912d9e2] feat: Add edit project feature, template, and tests
 5 files changed, 90 insertions(+)
 create mode 100644 templates/projects_edit.html
Sekarang seluruh checklist kode Tugas 3 (Create, Read/Delivery JSON, Update, Delete) sudah 100% lengkap!

Langkah terakhir sebelum pengumpulan tugas biasanya adalah mengisi Jawaban Pertanyaan Teori Tugas 3 & AI Disclosure di 
README.md
.

Mau langsung saya bantu buatkan draf jawaban pertanyaan dan AI disclosure untuk Tugas 3 di README.md?

10:16 PM
gaskeun
10:26 PM
lanjut
User cancelled agent execution.
11:01 PM


### TUGAS 3 :
### 1. ModelForm dan CSRF Token
* **Alasan Menggunakan ModelForm:**
  * **Efisiensi (DRY):** *Field* form dibuat otomatis berdasarkan skema model tanpa perlu menulis tag HTML manual.
  * **Validasi Otomatis:** Memvalidasi tipe data dan batasan atribut model langsung di sisi server.
  * **Penyimpanan Praktis:** Menyimpan data ke database cukup dengan memanggil method `.save()`.
  * **Keamanan:** Membantu menyaring input untuk mencegah celah keamanan seperti *SQL Injection*.
* **Fungsi `{% csrf_token %}`:**
  * Mencegah serangan **CSRF (*Cross-Site Request Forgery*)**.
  * Menghasilkan token rahasia unik untuk mencocokkan data form yang dikirim dengan sesi pengguna resmi.

### 2. JSON vs XML
* **Ukuran Ringan:** Tanpa tag pembuka/penutup yang panjang sehingga menghemat *bandwidth*.
* **Integrasi Native JavaScript:** Dapat langsung di-*parse* menjadi objek JavaScript tanpa pembacaan DOM XML.
* **Keterbacaan:** Menggunakan format *key-value* dan *array* yang lebih ringkas serta mudah dipahami.

### 3. Alur JSON Response & Serialization
* **Alur Pengembalian Data:**
  1. **Request:** Klien mengirim HTTP Request ke URL *view*.
  2. **Query:** *View* mengambil data dari basis data menggunakan ORM Django (`Model.objects.all()`).
  3. **Serialize:** Data *QuerySet* atau objek model dikonversi ke struktur data terstandar (JSON).
  4. **Response:** Data dikembalikan via `JsonResponse` ke klien.
* **Urgensi Serialization:**
  * Objek model Django adalah objek Python kompleks di memori server yang tidak bisa ditransmisikan langsung melalui protokol HTTP.
  * Serialisasi mengonversi objek tersebut menjadi format teks standar (JSON) agar dapat diproses oleh *frontend* atau aplikasi klien.