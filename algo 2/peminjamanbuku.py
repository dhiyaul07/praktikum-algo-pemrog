import sys
from datetime import date
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PyQt5.QtCore import Qt


class LibraryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistem Peminjaman Buku")
        self.setGeometry(200, 200, 850, 550)

        self.init_db()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tabs.addTab(self.build_tab_buku(), "Kelola Buku")
        self.tabs.addTab(self.build_tab_pinjam(), "Pinjam Buku")
        self.tabs.addTab(self.build_tab_kembali(), "Kembalikan Buku")
        self.tabs.addTab(self.build_tab_laporan(), "Laporan")

        self.tabs.currentChanged.connect(self.refresh_all)
        self.refresh_all()

    # ---------------- Database ----------------
    def init_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("library.db")
        if not self.db.open():
            QMessageBox.critical(self, "Error", "Database tidak bisa dibuka!")
            return
        q = QSqlQuery()
        q.exec_("""CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT,
                    stock INTEGER NOT NULL DEFAULT 1)""")
        q.exec_("""CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    borrower TEXT NOT NULL,
                    loan_date TEXT,
                    return_date TEXT,
                    status TEXT DEFAULT 'active')""")

    # ---------------- Tab 1: Kelola Buku ----------------
    def build_tab_buku(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.books_model = QSqlTableModel()
        self.books_model.setTable("books")
        self.books_model.select()
        self.books_view = QTableView()
        self.books_view.setModel(self.books_model)
        self.books_view.setSelectionBehavior(QTableView.SelectRows)

        form = QFormLayout()
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.stock_input = QSpinBox()
        self.stock_input.setRange(1, 999)
        form.addRow("Judul:", self.title_input)
        form.addRow("Penulis:", self.author_input)
        form.addRow("Stok:", self.stock_input)

        btns = QHBoxLayout()
        add_btn = QPushButton("Tambah Buku")
        del_btn = QPushButton("Hapus Buku")
        add_btn.clicked.connect(self.add_book)
        del_btn.clicked.connect(self.delete_book)
        btns.addWidget(add_btn)
        btns.addWidget(del_btn)

        layout.addWidget(QLabel("Daftar Buku:"))
        layout.addWidget(self.books_view)
        layout.addLayout(form)
        layout.addLayout(btns)
        return tab

    def add_book(self):
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Peringatan", "Judul buku harus diisi!")
            return
        q = QSqlQuery()
        q.prepare("INSERT INTO books (title, author, stock) VALUES (?, ?, ?)")
        q.addBindValue(title)
        q.addBindValue(self.author_input.text().strip())
        q.addBindValue(self.stock_input.value())
        q.exec_()
        self.title_input.clear()
        self.author_input.clear()
        self.stock_input.setValue(1)
        self.refresh_all()

    def delete_book(self):
        idx = self.books_view.currentIndex()
        if not idx.isValid():
            QMessageBox.warning(self, "Peringatan", "Pilih buku dulu!")
            return
        book_id = self.books_model.data(self.books_model.index(idx.row(), 0))
        q = QSqlQuery()
        q.prepare("SELECT COUNT(*) FROM loans WHERE book_id=? AND status='active'")
        q.addBindValue(book_id)
        q.exec_()
        q.next()
        if q.value(0) > 0:
            QMessageBox.warning(self, "Peringatan",
                                "Buku sedang dipinjam, tidak bisa dihapus.")
            return
        q = QSqlQuery()
        q.prepare("DELETE FROM books WHERE id=?")
        q.addBindValue(book_id)
        q.exec_()
        self.refresh_all()

    # ---------------- Tab 2: Pinjam Buku ----------------
    def build_tab_pinjam(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form = QFormLayout()
        self.book_combo = QComboBox()
        self.borrower_input = QLineEdit()
        form.addRow("Pilih Buku:", self.book_combo)
        form.addRow("Nama Peminjam:", self.borrower_input)

        loan_btn = QPushButton("Pinjam Buku")
        loan_btn.clicked.connect(self.loan_book)

        layout.addLayout(form)
        layout.addWidget(loan_btn)
        layout.addStretch()
        return tab

    def load_combo(self):
        self.book_combo.clear()
        q = QSqlQuery("SELECT id, title, stock FROM books WHERE stock > 0")
        while q.next():
            self.book_combo.addItem(f"{q.value(1)} (stok: {q.value(2)})", q.value(0))

    def loan_book(self):
        borrower = self.borrower_input.text().strip()
        book_id = self.book_combo.currentData()
        if book_id is None:
            QMessageBox.warning(self, "Peringatan", "Tidak ada buku yang tersedia!")
            return
        if not borrower:
            QMessageBox.warning(self, "Peringatan", "Nama peminjam harus diisi!")
            return
        q = QSqlQuery()
        q.prepare("INSERT INTO loans (book_id, borrower, loan_date, status) "
                  "VALUES (?, ?, ?, 'active')")
        q.addBindValue(book_id)
        q.addBindValue(borrower)
        q.addBindValue(date.today().isoformat())
        q.exec_()
        q = QSqlQuery()
        q.prepare("UPDATE books SET stock = stock - 1 WHERE id=?")
        q.addBindValue(book_id)
        q.exec_()
        self.borrower_input.clear()
        QMessageBox.information(self, "Sukses", "Buku berhasil dipinjam.")
        self.refresh_all()

    # ---------------- Tab 3: Kembalikan Buku ----------------
    def build_tab_kembali(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self.loans_model = QSqlTableModel()
        self.loans_model.setTable("loans")
        self.loans_model.setFilter("status = 'active'")
        self.loans_model.select()
        self.loans_view = QTableView()
        self.loans_view.setModel(self.loans_model)
        self.loans_view.setSelectionBehavior(QTableView.SelectRows)

        return_btn = QPushButton("Kembalikan Buku")
        return_btn.clicked.connect(self.return_book)

        layout.addWidget(QLabel("Peminjaman Aktif:"))
        layout.addWidget(self.loans_view)
        layout.addWidget(return_btn)
        return tab

    def return_book(self):
        idx = self.loans_view.currentIndex()
        if not idx.isValid():
            QMessageBox.warning(self, "Peringatan", "Pilih peminjaman dulu!")
            return
        row = idx.row()
        loan_id = self.loans_model.data(self.loans_model.index(row, 0))
        book_id = self.loans_model.data(self.loans_model.index(row, 1))
        q = QSqlQuery()
        q.prepare("UPDATE loans SET status='returned', return_date=? WHERE id=?")
        q.addBindValue(date.today().isoformat())
        q.addBindValue(loan_id)
        q.exec_()
        q = QSqlQuery()
        q.prepare("UPDATE books SET stock = stock + 1 WHERE id=?")
        q.addBindValue(book_id)
        q.exec_()
        QMessageBox.information(self, "Sukses", "Buku berhasil dikembalikan.")
        self.refresh_all()

    # ---------------- Tab 4: Laporan ----------------
    def build_tab_laporan(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.report_label = QLabel()
        self.report_label.setStyleSheet("font-size: 16px;")
        refresh_btn = QPushButton("Refresh Laporan")
        refresh_btn.clicked.connect(self.update_report)
        layout.addWidget(self.report_label)
        layout.addWidget(refresh_btn)
        layout.addStretch()
        return tab

    def scalar(self, sql):
        q = QSqlQuery(sql)
        q.next()
        return q.value(0) or 0

    def update_report(self):
        total_judul = self.scalar("SELECT COUNT(*) FROM books")
        total_stok = self.scalar("SELECT SUM(stock) FROM books")
        aktif = self.scalar("SELECT COUNT(*) FROM loans WHERE status='active'")
        kembali = self.scalar("SELECT COUNT(*) FROM loans WHERE status='returned'")
        self.report_label.setText(
            "LAPORAN PERPUSTAKAAN\n\n"
            f"Total judul buku        : {total_judul}\n"
            f"Total stok tersedia     : {total_stok}\n"
            f"Peminjaman aktif        : {aktif}\n"
            f"Peminjaman dikembalikan : {kembali}")

    # ---------------- Refresh ----------------
    def refresh_all(self, *args):
        self.books_model.select()
        self.loans_model.select()
        self.load_combo()
        self.update_report()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LibraryApp()
    window.show()
    sys.exit(app.exec_())
