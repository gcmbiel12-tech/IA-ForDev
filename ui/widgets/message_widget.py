from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
)


class MessageWidget(QFrame):
    def __init__(self, author, content, is_user=False):
        super().__init__()
        self.setObjectName("userCard" if is_user else "messageCard")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(7)

        header = QHBoxLayout()
        label = QLabel(author)
        label.setObjectName("messageAuthor")
        header.addWidget(label)
        header.addStretch()

        self.copy_button = None
        if not is_user:
            self.copy_button = QPushButton("[ COPIAR ]")
            self.copy_button.setObjectName("copyButton")
            self.copy_button.clicked.connect(self.copy_content)
            header.addWidget(self.copy_button)

        layout.addLayout(header)

        self.content = QTextEdit()
        self.content.setObjectName("messageContent")
        self.content.setPlainText(content)
        self.content.setReadOnly(True)
        self.content.setFrameShape(QFrame.Shape.NoFrame)
        self.content.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.content.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.content.document().setDefaultFont(QFont("Consolas", 15))
        self.content.document().setDocumentMargin(2)
        layout.addWidget(self.content)

        self.content.document().documentLayout().documentSizeChanged.connect(
            self.adjust_content_height
        )
        self.adjust_content_height()

    def adjust_content_height(self, *_):
        height = int(self.content.document().size().height() + 20)
        self.content.setFixedHeight(max(48, min(height, 650)))

    def copy_content(self):
        QApplication.clipboard().setText(self.content.toPlainText())
        self.copy_button.setText("[ COPIADO ]")
        self.copy_button.setEnabled(False)
        QTimer.singleShot(1200, self.reset_copy_button)

    def reset_copy_button(self):
        if self.copy_button:
            self.copy_button.setText("[ COPIAR ]")
            self.copy_button.setEnabled(True)
