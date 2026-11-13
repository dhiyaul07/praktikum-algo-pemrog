import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class SourceList(QListWidget):
    """List asal: item hanya bisa di-drag keluar."""
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)


class TargetList(QListWidget):
    """List tujuan: menerima drop dari SourceList dan bisa diatur ulang."""
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event):
        if event.source() is not None:
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        source = event.source()
        if source is self:
            # diatur ulang di dalam list yang sama
            super().dropEvent(event)
        elif isinstance(source, SourceList):
            # salin item dari list kiri
            for item in source.selectedItems():
                self.addItem(item.text())
            event.setDropAction(Qt.CopyAction)
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
