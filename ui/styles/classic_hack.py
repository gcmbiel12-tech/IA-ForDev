APP_STYLE = """
QWidget {
    background-color: #090d09;
    color: #c8f7c5;
    font-family: Consolas;
    font-size: 14px;
}
QMainWindow { background-color: #090d09; }
QFrame#sidebar {
    background-color: #0d130d;
    border-right: 1px solid #244b24;
}
QLabel#logo {
    color: #55ff55;
    font-size: 25px;
    font-weight: bold;
}
QLabel#subtitle, QLabel#mutedText {
    color: #6ca96c;
    font-size: 12px;
}
QLabel#pageTitle {
    color: #72ff72;
    font-size: 15px;
    font-weight: bold;
}
QLabel#status {
    color: #70d870;
    font-size: 12px;
}
QLabel#projectPath {
    color: #a4dba0;
    font-size: 11px;
}
QFrame#messageCard, QFrame#userCard {
    background-color: #0d150d;
    border: 1px solid #244b24;
    border-radius: 7px;
}
QFrame#userCard { background-color: #101a10; }
QLabel#messageAuthor {
    color: #70ff70;
    font-size: 13px;
    font-weight: bold;
    background: transparent;
    border: none;
}
QTextEdit#messageContent {
    background: transparent;
    color: #d4f5d0;
    border: none;
    font-size: 15px;
    selection-background-color: #285a28;
    selection-color: white;
}
QLineEdit#inputBox {
    background-color: #0c130c;
    border: 1px solid #397139;
    border-radius: 5px;
    padding: 12px;
    color: #c8ffc8;
    font-size: 15px;
}
QPushButton {
    background-color: #102010;
    color: #85ff85;
    border: 1px solid #397139;
    border-radius: 4px;
    padding: 9px 10px;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #1b351b;
    border-color: #70ff70;
}
QPushButton:disabled { color: #557755; }
QPushButton#executeButton {
    background-color: #153015;
    font-weight: bold;
    padding: 12px 16px;
}
QPushButton#copyButton { font-size: 11px; padding: 5px 9px; }
QScrollArea { background-color: #090d09; border: none; }
QScrollBar:vertical {
    background: #0a100a;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: #315b31;
    min-height: 25px;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
"""
