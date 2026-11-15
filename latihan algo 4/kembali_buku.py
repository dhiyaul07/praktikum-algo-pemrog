import os
import sys
from datetime import datetime, timedelta
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QDate
import db_helper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def rupiah(nilai):
    return "Rp " + f"{nilai:,.0f}".replace(",", ".")


class KembaliBukuWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(KembaliBukuWindow, self).__init__()
        # Load UI
        uic.loadUi(os.path.join(BASE_DIR, 'kembali_buku.ui'), self)

        # Initialize Database
        db_helper.init_db()

        self.selected_loan = None  # (tanggal_pinjam, durasi) dari baris terpilih
        self.dateKembali.setDate(QDate.currentDate())

        # Connect buttons & signals
        self.btnKembalikan.clicked.connect(self.return_book)
        self.btnBersihkan.clicked.connect(self.clear_fields)
        self.btnKembali.clicked.connect(self.close)
        self.tablePeminjaman.itemSelectionChanged.connect(self.on_table_select)
        self.dateKembali.dateChanged.connect(self.update_denda)

        # Adjust table headers
        self.tablePeminjaman.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.refresh()

    def refresh(self):
        self.load_active_loans()
        self.clear_fields()

    def load_active_loans(self):
        self.tablePeminjaman.setRowCount(0)
        loans = db_helper.get_active_loans()
        for row_number, row_data in enumerate(loans):
            self.tablePeminjaman.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                item = QtWidgets.QTableWidgetItem(str(data))
                self.tablePeminjaman.setItem(row_number, column_number, item)

    def on_table_select(self):
        selected_rows = self.tablePeminjaman.selectionModel().selectedRows()
        if not selected_rows:
            return
        row = selected_rows[0].row()
        id_pinjam = self.tablePeminjaman.item(row, 0).text()
        tanggal_pinjam = self.tablePeminjaman.item(row, 4).text()
        durasi = int(self.tablePeminjaman.item(row, 5).text())

        jatuh_tempo = datetime.strptime(tanggal_pinjam, "%Y-%m-%d") + timedelta(days=durasi)

        self.txtIdPinjam.setText(id_pinjam)
        self.txtNamaPeminjam.setText(self.tablePeminjaman.item(row, 1).text())
        self.txtJudulBuku.setText(self.tablePeminjaman.item(row, 3).text())
        self.txtTanggalPinjam.setText(tanggal_pinjam)
        self.txtJatuhTempo.setText(jatuh_tempo.strftime("%Y-%m-%d"))
        self.selected_loan = (tanggal_pinjam, durasi)
        self.update_denda()

    def update_denda(self):
        if not self.selected_loan:
            self.lblDendaValue.setText(rupiah(0))
            return
        tanggal_pinjam, durasi = self.selected_loan
        tanggal_kembali = self.dateKembali.date().toString("yyyy-MM-dd")
        terlambat, denda = db_helper.hitung_denda(tanggal_pinjam, durasi, tanggal_kembali)
        if terlambat > 0:
            self.lblDendaValue.setText(f"{rupiah(denda)}  (terlambat {terlambat} hari)")
        else:
            self.lblDendaValue.setText(rupiah(0) + "  (tepat waktu)")

    def return_book(self):
        id_pinjam = self.txtIdPinjam.text().strip()
        if not id_pinjam or not self.selected_loan:
            QtWidgets.QMessageBox.warning(self, "Pengembalian Gagal",
                                          "Pilih peminjaman dari tabel terlebih dahulu!")
            return

        tanggal_pinjam, durasi = self.selected_loan
        tanggal_kembali = self.dateKembali.date().toString("yyyy-MM-dd")
        if tanggal_kembali < tanggal_pinjam:
            QtWidgets.QMessageBox.warning(self, "Validasi Gagal",
                                          "Tanggal kembali tidak boleh sebelum tanggal pinjam!")
            return

        terlambat, denda = db_helper.hitung_denda(tanggal_pinjam, durasi, tanggal_kembali)
        reply = QtWidgets.QMessageBox.question(
            self, "Konfirmasi Pengembalian",
            f"Kembalikan buku untuk peminjaman {id_pinjam}?\n"
            f"Keterlambatan: {terlambat} hari\nDenda: {rupiah(denda)}",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if reply != QtWidgets.QMessageBox.Yes:
            return

        success, message = db_helper.return_book(id_pinjam, tanggal_kembali, denda)
        if success:
            QtWidgets.QMessageBox.information(self, "Berhasil", message)
            self.refresh()
        else:
            QtWidgets.QMessageBox.critical(self, "Gagal", message)

    def clear_fields(self):
        self.txtIdPinjam.clear()
        self.txtNamaPeminjam.clear()
        self.txtJudulBuku.clear()
        self.txtTanggalPinjam.clear()
        self.txtJatuhTempo.clear()
        self.dateKembali.setDate(QDate.currentDate())
        self.selected_loan = None
        self.tablePeminjaman.clearSelection()
        self.update_denda()