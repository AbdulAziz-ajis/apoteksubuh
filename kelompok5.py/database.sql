CREATE DATABASE perusahaan1;

USE perusahaan1;

CREATE TABLE barang_barang (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_obat VARCHAR(255),
    merek_obat VARCHAR(255),
    stok_obat INT,
    harga DECIMAL(10, 2)
);

CREATE TABLE pegawai (
  pegawai_id INT PRIMARY KEY,
  nama_pegawai VARCHAR(255) NOT NULL,
  alamat VARCHAR(255) NOT NULL,
  no_hp VARCHAR(20) NOT NULL
);

CREATE TABLE pembeli (
  id_pembeli INT PRIMARY KEY,
  nama_pembeli VARCHAR(255) NOT NULL
);

CREATE TABLE riwayat_transaksi (
  id_pembeli INT NOT NULL,
  nama_pembeli VARCHAR(255) NOT NULL,
  nama_obat VARCHAR(255) NOT NULL,
  harga_obat DECIMAL(10, 2) NOT NULL,
  jumlah_stok_yang_dibeli INT NOT NULL,
  total_harga DECIMAL(10, 2) NOT NULL,
  tgl_waktu TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (id_pembeli) REFERENCES pembeli(id_pembeli) ON DELETE CASCADE ON UPDATE CASCADE
);