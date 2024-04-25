# conda activate webservicep2plending webservicep2plending
# uvicorn main:app --reload


from typing import Union  # Mengimpor Union untuk petunjuk tipe
from fastapi import FastAPI, Response, Request, HTTPException  # Mengimpor komponen yang diperlukan dari FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Mengimpor CORSMiddleware untuk mengaktifkan CORS
import sqlite3  # Mengimpor SQLite3 untuk operasi basis data

app = FastAPI()  # Membuat sebuah instance FastAPI

app.add_middleware( # Mendefinisikan penambahan middleware ke aplikasi FastAPI
    CORSMiddleware, # Menambahkan middleware CORSMiddleware untuk mengatur CORS di aplikasi
    allow_origins=["*"], # Mengizinkan permintaan dari semua asal dengan menggunakan "*"
    allow_credentials=True, # Mengizinkan kredensial dalam permintaan dengan mengatur allow_credentials ke True
    allow_methods=["*"], # Mengizinkan metode HTTP apa pun dalam permintaan dengan mengatur allow_methods ke "*"
    allow_headers=["*"], # Mengizinkan penggunaan header apa pun dalam permintaan dengan mengatur allow_headers ke "*"
)

@app.get("/")  # Mendefinisikan rute untuk endpoint root
def read_root():  # Fungsi untuk menangani permintaan ke endpoint root
    return {"Hello": "World"}  # Mengembalikan respons JSON sederhana

@app.get("/mahasiswa/{nim}")  # Mendefinisikan rute dengan parameter jalur
def ambil_mhs(nim: str):  # Fungsi untuk menangani permintaan untuk mengambil data mahasiswa berdasarkan ID
    return {"nama": "Budi Martami"}  # Mengembalikan data mahasiswa palsu

@app.get("/mahasiswa2/")  # Mendefinisikan rute lain
def ambil_mhs2(nim: str):  # Fungsi untuk menangani permintaan (dimaksudkan untuk mengambil data mahasiswa tetapi didefinisikan dengan tidak benar)
    return {"nama": "Budi Martami 2"}  # Mengembalikan data mahasiswa palsu

@app.get("/daftar_mhs/")  # Mendefinisikan rute untuk mengambil daftar mahasiswa
def daftar_mhs(id_prov: str, angkatan: str):  # Fungsi untuk menangani permintaan untuk mengambil daftar mahasiswa
    return {"query": " idprov: {}  ; angkatan: {} ".format(id_prov, angkatan), "data": [{"nim": "1234"}, {"nim": "1235"}]}  # Mengembalikan data mahasiswa palsu

@app.get("/init/")  # Mendefinisikan rute untuk menginisialisasi basis data
def init_db():  # Fungsi untuk menginisialisasi basis data
    try: # Mencoba menjalankan kode di dalam blok try
        DB_NAME = "upi.db"  # Nama file basis data
        con = sqlite3.connect(DB_NAME)  # Menghubungkan ke basis data SQLite
        cur = con.cursor()  # Membuat objek kursor
        create_table = """ CREATE TABLE mahasiswa( 
            ID          INTEGER PRIMARY KEY AUTOINCREMENT,
            nim         TEXT            NOT NULL,
            nama        TEXT            NOT NULL,
            id_prov     TEXT            NOT NULL,
            angkatan    TEXT            NOT NULL,
            tinggi_badan  INTEGER
        )  
        """
        cur.execute(create_table)  # Menjalankan SQL untuk membuat tabel
        con.commit()  # Melakukan komit transaksi
    except: # Menangkap pengecualian yang mungkin terjadi selama eksekusi kode di dalam blok try
        return ({"status": "terjadi error"})  # Mengembalikan pesan kesalahan jika terjadi pengecualian
    finally: # Blok finally akan selalu dieksekusi, terlepas dari apakah terjadi pengecualian atau tidak
        con.close()  # Menutup koneksi basis data
    return ({"status": "ok, db dan tabel berhasil dicreate"})  # Mengembalikan pesan keberhasilan

from pydantic import BaseModel  # Mengimpor BaseModel untuk validasi data
from typing import Optional  # Mengimpor Optional untuk mendefinisikan bidang opsional dalam model

class Mhs(BaseModel):  # Mendefinisikan sebuah model Pydantic dengan nama Mhs
    nim: str  # Mendefinisikan atribut nim dengan tipe data string
    nama: str  # Mendefinisikan atribut nama dengan tipe data string
    id_prov: str  # Mendefinisikan atribut id_prov dengan tipe data string
    angkatan: str  # Mendefinisikan atribut angkatan dengan tipe data string
    tinggi_badan: Optional[int] | None = None  # Mendefinisikan atribut tinggi_badan dengan tipe data opsional integer atau None

@app.post("/tambah_mhs/", response_model=Mhs, status_code=201)  # Mendefinisikan rute untuk menambahkan mahasiswa baru
def tambah_mhs(m: Mhs, response: Response, request: Request):  # Fungsi untuk menangani permintaan untuk menambahkan mahasiswa baru
    try: # Mencoba menjalankan blok kode di dalamnya
        DB_NAME = "upi.db"  # Nama file basis data
        con = sqlite3.connect(DB_NAME)  # Menghubungkan ke basis data SQLite
        cur = con.cursor()  # Membuat objek kursor
        cur.execute("""insert into mahasiswa (nim,nama,id_prov,angkatan,tinggi_badan) values ( "{}","{}","{}","{}",{})""".format(m.nim, m.nama, m.id_prov, m.angkatan, m.tinggi_badan))  # Menjalankan SQL untuk menyisipkan catatan baru ke dalam tabel 'mahasiswa'
        con.commit()  # Melakukan komit transaksi untuk menyimpan perubahan ke dalam basis data
    except: # Menangkap pengecualian yang mungkin terjadi selama eksekusi blok try
        print("oioi error")  # Mencetak pesan kesalahan jika terjadi pengecualian
        return ({"status": "terjadi error"})  # Mengembalikan pesan kesalahan
    finally: # Blok finally akan selalu dieksekusi, terlepas dari apakah terjadi pengecualian atau tidak
        con.close()  # Menutup koneksi basis data
    response.headers["Location"] = "/mahasiswa/{}".format(m.nim)  # Mengatur header respons untuk lokasi sumber daya yang baru dibuat
    print(m.nim) # Mencetak NIM mahasiswa yang baru dibuat ke dalam konsol
    print(m.nama) # Mencetak nama mahasiswa yang baru dibuat ke dalam konsol
    print(m.angkatan) # Mencetak tahun angkatan mahasiswa yang baru dibuat ke dalam konsol
    return m  # Mengembalikan data mahasiswa yang baru dibuat

@app.get("/tampilkan_semua_mhs/")  # Mendefinisikan rute untuk mengambil semua mahasiswa
def tampil_semua_mhs():  # Fungsi untuk menangani permintaan untuk mengambil semua mahasiswa
    try: # Mencoba menjalankan blok kode di dalamnya
        DB_NAME = "upi.db"  # Nama file basis data
        con = sqlite3.connect(DB_NAME)  # Menghubungkan ke basis data SQLite
        cur = con.cursor()  # Membuat objek kursor
        recs = [] # Membuat daftar kosong untuk menyimpan hasil query
        for row in cur.execute("select * from mahasiswa"):  # Menjalankan kueri semua catatan dari tabel mahasiswa
            recs.append(row) # Menambahkan setiap baris hasil kueri ke dalam daftar recs
    except: # Menangkap pengecualian yang mungkin terjadi selama eksekusi blok try
        return ({"status": "terjadi error"})  # Mengembalikan pesan kesalahan jika terjadi pengecualian
    finally: # Blok finally akan selalu dieksekusi, terlepas dari apakah terjadi pengecualian atau tidak
        con.close()  # Menutup koneksi basis data
    return {"data": recs}  # Mengembalikan data mahasiswa yang diambil

from fastapi.encoders import jsonable_encoder  # Mengimpor jsonable_encoder untuk pengkodean JSON

@app.put("/update_mhs_put/{nim}", response_model=Mhs)  # Mendefinisikan rute untuk memperbarui mahasiswa menggunakan metode PUT
def update_mhs_put(response: Response, nim: str, m: Mhs):  # Fungsi untuk menangani permintaan untuk memperbarui mahasiswa menggunakan metode PUT
    try: # Mencoba menjalankan blok kode di dalamnya
        DB_NAME = "upi.db"  # Nama file basis data
        con = sqlite3.connect(DB_NAME)  # Menghubungkan ke basis data SQLite
        cur = con.cursor()  # Membuat objek kursor
        cur.execute("select * from mahasiswa where nim = ?", (nim,))  # Menjalankan kueri basis data untuk catatan yang ada
        existing_item = cur.fetchone() # Mengambil satu baris hasil kueri
    except Exception as e: # Menangkap pengecualian yang mungkin terjadi selama eksekusi blok try
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Menaikkan HTTPException jika terjadi pengecualian
    if existing_item:  # Jika catatan ada
        print(m.tinggi_badan) # Mencetak tinggi badan dari objek yang diterima ke konsol
        cur.execute("update mahasiswa set nama = ?, id_prov = ?, angkatan=?, tinggi_badan=? where nim=?", (m.nama, m.id_prov, m.angkatan, m.tinggi_badan, nim))  # Menjalankan SQL untuk memperbarui catatan
        con.commit()  # Melakukan komit transaksi
        response.headers["location"] = "/mahasiswa/{}".format(m.nim)  # Mengatur header respons untuk lokasi sumber daya yang diperbarui
    else:  # Jika catatan tidak ada
        print("item not found") # Mencetak pesan bahwa item tidak ditemukan ke konsol
        raise HTTPException(status_code=404, detail="Item Not Found")  # Menaikkan HTTPException dengan kode status 404
    con.close()  # Menutup koneksi basis data
    return m  # Mengembalikan data mahasiswa yang diperbarui

class MhsPatch(BaseModel):  # Mendefinisikan model Pydantic untuk memperbarui data mahasiswa
    nama: str | None = "kosong" # Atribut nama yang dapat berupa string atau None, dan diatur default sebagai "kosong"
    id_prov: str | None = "kosong" # Atribut id_prov yang dapat berupa string atau None, dan diatur default sebagai "kosong"
    angkatan: str | None = "kosong" # Atribut angkatan yang dapat berupa string atau None, dan diatur default sebagai "kosong"
    tinggi_badan: Optional[int] | None = -9999  # Atribut tinggi_badan yang dapat berupa integer opsional atau None, dan diatur default sebagai -9999

@app.patch("/update_mhs_patch/{nim}", response_model=MhsPatch)  # Mendefinisikan rute untuk memperbarui mahasiswa menggunakan metode PATCH
def update_mhs_patch(response: Response, nim: str, m: MhsPatch):  # Fungsi untuk menangani permintaan untuk memperbarui mahasiswa menggunakan metode PATCH
    try: # Mencoba menjalankan blok kode di dalamnya
        print(str(m)) # Mencetak representasi string dari objek m ke konsol
        DB_NAME = "upi.db"  # Nama file basis data
        con = sqlite3.connect(DB_NAME)  # Menghubungkan ke basis data SQLite
        cur = con.cursor()  # Membuat objek kursor
        cur.execute("select * from mahasiswa where nim = ?", (nim,))  # Menjalankan kueri basis data untuk catatan yang ada
        existing_item = cur.fetchone() # Mengambil satu baris hasil kueri
    except Exception as e: # Menangkap pengecualian yang mungkin terjadi selama eksekusi blok try
        raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Menaikkan HTTPException jika terjadi pengecualian
    if existing_item:  # Jika catatan ada, lakukan update
        sqlstr = "update mahasiswa set "  # Membangun string SQL untuk update
        if m.nama != "kosong":  # Memeriksa apakah bidang nama akan diperbarui
            if m.nama != None: # Memeriksa apakah nilai atribut nama tidak None
                sqlstr = sqlstr + " nama = '{}' ,".format(m.nama) # Jika nilai atribut nama tidak None, tambahkan pernyataan SQL untuk memperbarui nama
            else: # Jika catatan tidak ada
                sqlstr = sqlstr + " nama = null ," # Jika nilai atribut nama None, tambahkan pernyataan SQL untuk mengatur nilai nama menjadi null

        if m.angkatan != "kosong":  # Memeriksa apakah bidang angkatan akan diperbarui
            if m.angkatan != None: # Memeriksa apakah nilai atribut angkatan tidak None
                sqlstr = sqlstr + " angkatan = '{}' ,".format(m.angkatan) # Jika nilai atribut angkatan tidak None, tambahkan pernyataan SQL untuk memperbarui angkatan
            else: # Jika catatan tidak ada
                sqlstr = sqlstr + " angkatan = null ," # Jika nilai atribut angkatan None, tambahkan pernyataan SQL untuk mengatur nilai angkatan menjadi null

        if m.id_prov != "kosong":  # Memeriksa apakah bidang id_prov akan diperbarui
            if m.id_prov != None: # Memeriksa apakah nilai atribut id_prov tidak None
                sqlstr = sqlstr + " id_prov = '{}' ,".format(m.id_prov) # Jika nilai atribut id_prov tidak None, tambahkan pernyataan SQL untuk memperbarui id_prov
            else: # Jika catatan tidak ada
                sqlstr = sqlstr + " id_prov = null, " # Jika nilai atribut id_prov None, tambahkan pernyataan SQL untuk mengatur nilai id_prov menjadi null

        if m.tinggi_badan != -9999:  # Memeriksa apakah bidang tinggi_badan akan diperbarui
            if m.tinggi_badan != None: # Memeriksa apakah nilai atribut tinggi_badan tidak None
                sqlstr = sqlstr + " tinggi_badan = {} ,".format(m.tinggi_badan) # Jika nilai atribut tinggi_badan tidak None, tambahkan pernyataan SQL untuk memperbarui tinggi_badan
            else: # Jika catatan tidak ada
                sqlstr = sqlstr + " tinggi_badan = null ," # Jika nilai atribut tinggi_badan None, tambahkan pernyataan SQL untuk mengatur nilai tinggi_badan menjadi null

        sqlstr = sqlstr[:-1] + " where nim='{}' ".format(nim)  # Menghapus koma di akhir dan menyelesaikan string SQL
        print(sqlstr) # Mencetak string SQL yang akan dieksekusi untuk memperbarui catatan
        try: # Mencoba menjalankan blok kode di dalamnya
            cur.execute(sqlstr)  # Menjalankan SQL untuk memperbarui catatan
            con.commit()  # Melakukan komit transaksi
            response.headers["location"] = "/mahasixswa/{}".format(nim)  # Mengatur header respons untuk lokasi sumber daya yang diperbarui
        except Exception as e: # Menangkap pengecualian yang mungkin terjadi selama eksekusi blok try
            raise HTTPException(status_code=500, detail="Terjadi exception: {}".format(str(e)))  # Menaikkan HTTPException jika terjadi pengecualian

    else:  # Jika catatan tidak ada
        raise HTTPException(status_code=404, detail="Item Not Found")  # Menaikkan HTTPException dengan kode status 404
    con.close()  # Menutup koneksi basis data
    return m  # Mengembalikan data mahasiswa yang diperbarui

@app.delete("/delete_mhs/{nim}")  # Mendefinisikan rute untuk menghapus seorang mahasiswa
def delete_mhs(nim: str):  # Fungsi untuk menangani permintaan untuk menghapus seorang mahasiswa
    try: # Mencoba menjalankan blok kode di dalamnya
        DB_NAME = "upi.db"  # Nama file basis data
        con = sqlite3.connect(DB_NAME)  # Menghubungkan ke basis data SQLite
        cur = con.cursor()  # Membuat objek kursor
        sqlstr = "delete from mahasiswa  where nim='{}'".format(nim)  # Membangun string SQL untuk menghapus catatan
        print(sqlstr)  # Pernyataan debug
        cur.execute(sqlstr)  # Menjalankan SQL untuk menghapus catatan
        con.commit()  # Melakukan komit transaksi
    except: # Menangkap pengecualian yang mungkin terjadi selama eksekusi blok try
        return ({"status": "terjadi error"})  # Mengembalikan pesan kesalahan jika terjadi pengecualian
    finally: # Blok finally akan selalu dieksekusi, terlepas dari apakah terjadi pengecualian atau tidak
        con.close()  # Menutup koneksi basis data setelah selesai menjalankan operasi
    return {"status": "ok"}  # Mengembalikan pesan keberhasilan setelah selesai menghapus catatan
