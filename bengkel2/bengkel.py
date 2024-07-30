from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "secret_key"  # Kunci rahasia untuk sesi Flask

# Koneksi ke Database MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Gantilah dengan password database Anda
    database="db_bengkel"
)
cursor = db.cursor()

@app.route('/')
def index():
    # Fungsi untuk menampilkan halaman utama
    return render_template('index.html')

@app.route('/data_pelanggan', methods=['GET', 'POST'])
def data_pelanggan():
    if request.method == 'POST':
        # Ambil data dari form
        nama = request.form['nama']
        merk_motor = request.form['merk_motor']
        jenis_motor = request.form['jenis_motor']
        tahun_motor = request.form['tahun_motor']

        # Cek apakah semua data telah diisi
        if not nama or not merk_motor or not jenis_motor or not tahun_motor:
            flash("Semua data harus diisi!", "error")
            return redirect(url_for('data_pelanggan'))

        # Menyimpan data pelanggan ke database
        cursor.execute(
            "INSERT INTO pelanggan (nama, merk_motor, jenis_motor, tahun_motor) VALUES (%s, %s, %s, %s)",
            (nama, merk_motor, jenis_motor, tahun_motor)
        )
        db.commit()

        flash("Data pelanggan berhasil disimpan!", "success")
        return redirect(url_for('menu'))

    return render_template('data_pelanggan.html')

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    # Ambil kategori dari query string
    kategori = request.args.get('kategori')
    
    # Menentukan default value untuk kategori
    if kategori is None:
        kategori = ['Rutin', 'Sparepart', 'Lengkap']
    elif isinstance(kategori, str):
        kategori = [kategori]

    # Mapping kategori ke layanan yang sesuai
    layanan_mapping = {
        'Rutin': ['Ganti Oli', 'Ganti Kanvas Rem'],
        'Sparepart': ['Ganti Ban', 'Ganti Rantai'],
        'Lengkap': ['Servis Keseluruhan Motor Matic', 'Servis Keseluruhan Motor Bebek']
    }

    # Tentukan layanan berdasarkan kategori
    layanan_tersedia = []
    for kat in kategori:
        if kat in layanan_mapping:
            layanan_tersedia.extend(layanan_mapping[kat])

    # Siapkan query untuk mengambil layanan yang sesuai
    if layanan_tersedia:
        placeholders = ','.join(['%s'] * len(layanan_tersedia))
        query = f"SELECT id, nama, harga FROM layanan WHERE nama IN ({placeholders})"
        cursor.execute(query, layanan_tersedia)
        layanan = cursor.fetchall()
    else:
        layanan = []

    # Variabel global untuk menyimpan layanan terpilih dan total biaya
    global total_biaya
    global layanan_terpilih

    if request.method == 'POST':
        # Ambil ID servis dari form
        servis_id = request.form.get('servis_id')
        cursor.execute("SELECT nama, harga FROM layanan WHERE id = %s", (servis_id,))
        servis = cursor.fetchone()
        
        if servis:
            nama_servis, harga = servis
            total_biaya += harga
            layanan_terpilih.append({"nama": nama_servis, "harga": harga})
            flash(f"Anda memilih jasa {nama_servis} dengan harga Rp{harga}", "success")

        return redirect(url_for('menu', kategori=kategori))

    return render_template('menu.html', layanan=layanan, kategori=kategori)

@app.route('/bayar', methods=['GET', 'POST'])
def bayar():
    global total_biaya, layanan_terpilih

    if not layanan_terpilih:
        flash("Belum ada servis yang dipilih!", "error")
        return redirect(url_for('menu'))

    # Membuat rincian pembayaran
    rincian_pembayaran = "\n".join([f"{layanan['nama']} - Rp{layanan['harga']}" for layanan in layanan_terpilih])
    rincian_pembayaran += f"\n\nTotal biaya yang harus dibayar: Rp{total_biaya}"

    # Reset total biaya dan layanan terpilih setelah pembayaran
    total_biaya = 0
    layanan_terpilih = []

    return render_template('bayar.html', rincian=rincian_pembayaran)

if __name__ == "__main__":
    total_biaya = 0
    layanan_terpilih = []
    app.run(debug=True)
