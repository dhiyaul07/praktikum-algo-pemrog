import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QMimeData


class SourceList(QListWidget):
    """List asal: item di-drag keluar sambil membawa data MIME (teks)."""
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setDefaultDropAction(Qt.CopyAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def mimeData(self, items):
        # MIME data transfer: bungkus teks item ke dalam QMimeData
        mime = QMimeData()
        mime.setText("\n".join(item.text() for item in items))
        return mime


class TargetList(QListWidget):
    """List tujuan: menerima drop (MIME) dari list kiri dan bisa diatur ulang."""
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def dragEnterEvent(self, event):
        if event.source() is self:
            super().dragEnterEvent(event)          # atur ulang di list sendiri
        elif event.mimeData().hasText():
            event.acceptProposedAction()           # terima data MIME teks
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.source() is self:
            super().dragMoveEvent(event)
        elif event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.source() is self:
            super().dropEvent(event)               # reorder item
        elif event.mimeData().hasText():
            for text in event.mimeData().text().split("\n"):
                self.addItem(text)                 # ambil teks dari MIME data
            event.setDropAction(Qt.CopyAction)     # item di kiri tetap ada
            event.accept()
        else:
            event.ignore()


class DragDropDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Drag and Drop Demo")
        self.setGeometry(300, 300, 700, 450)

        main_layout = QHBoxLayout()

        # Kiri: source
        left = QVBoxLayout()
        left.addWidget(QLabel("Source (drag from here):"))
        self.source = SourceList()
        self.source.addItems(["Apple", "Banana", "Cherry", "Date", "Elderberry"])
        left.addWidget(self.source)

        # Kanan: target
        right = QVBoxLayout()
        right.addWidget(QLabel("Target (drop here):"))
        self.target = TargetList()
        right.addWidget(self.target)
        self.clear_btn = QPushButton("Clear Target")
        self.clear_btn.clicked.connect(self.target.clear)
        right.addWidget(self.clear_btn)

        main_layout.addLayout(left)
        main_layout.addLayout(right)
        self.setLayout(main_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DragDropDemo()
    window.show()
    sys.exit(app.exec_())
