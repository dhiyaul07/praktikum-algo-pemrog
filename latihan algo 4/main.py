import os
import sys
from PyQt5 import QtWidgets, uic
import db_helper
from kelola_buku import KelolaBukuWindow
from pinjam_buku import PinjamBukuWindow
from kembali_buku import KembaliBukuWindow
from laporan import LaporanWindow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Load the UI file dynamically
        uic.loadUi(os.path.join(BASE_DIR, 'main.ui'), self)

        # Initialize Database
        db_helper.init_db()

        # Connect buttons to functions
        self.btnKelolaBuku.clicked.connect(self.open_kelola_buku)
        self.btnPinjamBuku.clicked.connect(self.open_pinjam_buku)
        self.btnKembaliBuku.clicked.connect(self.open_kembali_buku)
        self.btnLaporan.clicked.connect(self.open_laporan)
        self.btnKeluar.clicked.connect(self.close)

        # Instances of sub-windows
        self.kelola_buku_win = None
        self.pinjam_buku_win = None
        self.kembali_buku_win = None
        self.laporan_win = None

    def _open(self, attr, window_class):
        win = getattr(self, attr)
        if win is None:
            win = window_class()
            setattr(self, attr, win)
        else:
            win.refresh()  # Refresh data when reopening
        win.show()
        win.raise_()
        win.activateWindow()

    def open_kelola_buku(self):
        self._open('kelola_buku_win', KelolaBukuWindow)

    def open_pinjam_buku(self):
        self._open('pinjam_buku_win', PinjamBukuWindow)

    def open_kembali_buku(self):
        self._open('kembali_buku_win', KembaliBukuWindow)

    def open_laporan(self):
        self._open('laporan_win', LaporanWindow)

    def closeEvent(self, event):
        # Tutup semua jendela anak saat dashboard ditutup
        for attr in ('kelola_buku_win', 'pinjam_buku_win', 'kembali_buku_win', 'laporan_win'):
            win = getattr(self, attr)
            if win is not None:
                win.close()
        event.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())