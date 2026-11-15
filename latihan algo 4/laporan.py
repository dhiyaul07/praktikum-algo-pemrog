import os
import sys
from PyQt5 import QtWidgets, uic
import db_helper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class LaporanWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(LaporanWindow, self).__init__()
        # Load UI
        uic.loadUi(os.path.join(BASE_DIR, 'laporan.ui'), self)

        # Initialize Database
        db_helper.init_db()

        self.btnRefresh.clicked.connect(self.refresh)
        self.btnKembali.clicked.connect(self.close)
        self.tableTerpopuler.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.refresh()

    def refresh(self):
        stats = db_helper.get_general_statistics()
        self.lblTotalBuku.setText(str(stats['total_buku']))
        self.lblPinjamAktif.setText(str(stats['active_loans']))
        self.lblTotalDenda.setText("Rp " + f"{stats['total_denda']:,.0f}".replace(",", "."))

        self.tableTerpopuler.setRowCount(0)
        for row_number, row_data in enumerate(db_helper.get_most_borrowed_books()):
            self.tableTerpopuler.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableTerpopuler.setItem(row_number, column_number,
                                             QtWidgets.QTableWidgetItem(str(data)))