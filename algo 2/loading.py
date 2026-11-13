import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QPixmap, QColor, QFont, QPainter


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Application")
        self.setGeometry(300, 300, 600, 500)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        title = QLabel("Welcome to the Main Application!")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px;")

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.status = QLabel("Loading data...")

        layout.addStretch()
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.progress)
        layout.addStretch()
        layout.addWidget(self.status)
        layout.addStretch()

        # Simulasi loading data dengan timer
        self.value = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)

    def update_progress(self):
        self.value += 1
        self.progress.setValue(self.value)
        if self.value >= 100:
            self.timer.stop()
            self.status.setText("Data siap!")


def create_splash():
    pixmap = QPixmap(400, 250)
    pixmap.fill(QColor("#2b5797"))
    painter = QPainter(pixmap)
    painter.setPen(Qt.white)
    painter.setFont(QFont("Arial", 20, QFont.Bold))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "My Application")
    painter.end()
    return QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)


def tunggu(ms):
    """Jeda tanpa membekukan UI."""
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Tampilkan splash sebelum app.exec_()
    splash = create_splash()
    splash.show()

    pesan = ["Memuat modul...", "Menyiapkan database...",
             "Memuat pengaturan...", "Hampir selesai..."]
    for teks in pesan:
        splash.showMessage(teks, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        app.processEvents()          # jaga UI tetap responsif
        tunggu(500)                  # simulasi pekerjaan loading

    window = MainWindow()
    window.show()
    splash.finish(window)            # splash hilang

    sys.exit(app.exec_())
