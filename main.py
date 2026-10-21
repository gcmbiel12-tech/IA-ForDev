import sys

from PySide6.QtWidgets import QApplication
from ui.styles.classic_hack import APP_STYLE
from ui.windows.chat_window import ChatWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("I.AForDev")
    app.setStyle("Fusion")
    app.setStyleSheet(APP_STYLE)

    window = ChatWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
