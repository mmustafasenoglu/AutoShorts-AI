import sys
import threading
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox)
from PyQt6.QtCore import pyqtSignal, QObject

from clone_youtube import download_and_upload

class AppSignals(QObject):
    new_log = pyqtSignal(str)
    button_state = pyqtSignal(bool)
    ai_button_state = pyqtSignal(bool)

class PrintRedirector:
    def __init__(self, log_signal):
        self.log_signal = log_signal

    def write(self, text):
        if text:
            self.log_signal.emit(text)

    def flush(self):
        pass

class YouTubeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = AppSignals()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("YouTube Clone & Upload Bot")
        self.resize(750, 550)

        layout = QVBoxLayout()

        # Top Frame (URL and Button)
        top_layout = QHBoxLayout()
        
        self.url_label = QLabel("Video Linki (YT, TikTok, Insta):")
        top_layout.addWidget(self.url_label)
        
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Buraya video linkini yapıştırın...")
        top_layout.addWidget(self.url_entry)
        
        self.start_button = QPushButton("İndir & Yükle")
        self.start_button.clicked.connect(self.start_process)
        top_layout.addWidget(self.start_button)
        
        self.ai_button = QPushButton("Kanal Analizi Yap 🤖")
        self.ai_button.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        self.ai_button.clicked.connect(self.run_ai_analytics)
        top_layout.addWidget(self.ai_button)
        
        layout.addLayout(top_layout)

        # Log Frame
        self.log_label = QLabel("İşlem Takibi (Loglar):")
        layout.addWidget(self.log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("background-color: black; color: lightgreen; font-family: Consolas; font-size: 13px;")
        layout.addWidget(self.log_text)

        self.setLayout(layout)

        # Connect signals
        self.signals.new_log.connect(self.append_log)
        self.signals.button_state.connect(self.set_button_state)
        self.signals.ai_button_state.connect(self.set_ai_button_state)
        
        # Redirect console output to the GUI
        redirector = PrintRedirector(self.signals.new_log)
        sys.stdout = redirector
        sys.stderr = redirector

        print("Sistem hazır. Lütfen bir video linki (YouTube, TikTok, Insta) yapıştırıp 'İndir & Yükle' butonuna basın.")

    def append_log(self, text):
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(text)
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()

    def set_button_state(self, state):
        self.start_button.setEnabled(state)

    def set_ai_button_state(self, state):
        self.ai_button.setEnabled(state)

    def run_ai_analytics(self):
        self.signals.ai_button_state.emit(False)
        self.signals.new_log.emit("\n\n[🤖] Yapay Zeka Kanal Analizi başlatılıyor... Lütfen bekleyin (10-15 saniye sürebilir).\n")
        
        def run():
            try:
                from ai_analytics import perform_analysis
                result = perform_analysis()
                self.signals.new_log.emit("\n=== 🧠 GROQ AI ANALİZ RAPORU ===\n")
                self.signals.new_log.emit(result + "\n")
                self.signals.new_log.emit("================================\n")
            except Exception as e:
                self.signals.new_log.emit(f"\n[!] AI Analizi sırasında hata: {e}\n")
            finally:
                self.signals.ai_button_state.emit(True)
                
        threading.Thread(target=run, daemon=True).start()

    def start_process(self):
        url = self.url_entry.text().strip()
        if not url:
            QMessageBox.critical(self, "Hata", "Lütfen geçerli bir YouTube linki girin.")
            return
            
        self.signals.button_state.emit(False)
        
        def run():
            try:
                print(f"\n--- Başlatılıyor: {url} ---\n")
                download_and_upload(url)
                print("\n--- İşlem Tamamlandı ---")
            except Exception as e:
                print(f"\nBeklenmeyen Hata: {e}")
            finally:
                self.signals.button_state.emit(True)
                
        threading.Thread(target=run, daemon=True).start()

def main():
    app = QApplication(sys.argv)
    ex = YouTubeApp()
    ex.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
