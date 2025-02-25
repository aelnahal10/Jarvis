from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtGui import QFont, QColor, QTextCursor
from PyQt5.QtCore import Qt
import sys
import threading
from Jarvis.main import process_command, speak

class JarvisGUI(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Jarvis AI - Virtual Assistant")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #121212;")

        # Title
        self.title_label = QLabel("JARVIS AI", self)
        self.title_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.title_label.setStyleSheet("color: cyan; text-align: center;")
        self.title_label.setAlignment(Qt.AlignCenter)

        # Terminal Output (Log Display)
        self.log_display = QTextEdit(self)
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Courier", 12))
        self.log_display.setStyleSheet("color: #00FF00; background-color: black;")
        
        # Buttons
        self.start_button = QPushButton("Start Listening", self)
        self.start_button.setFont(QFont("Arial", 14))
        self.start_button.setStyleSheet("background-color: green; color: white; padding: 10px;")
        self.start_button.clicked.connect(self.start_listening)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setFont(QFont("Arial", 14))
        self.stop_button.setStyleSheet("background-color: red; color: white; padding: 10px;")
        self.stop_button.clicked.connect(self.close)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.log_display)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def log_message(self, message):
        """Updates the GUI terminal with new messages."""
        self.log_display.append(message)
        self.log_display.moveCursor(QTextCursor.End)

    def start_listening(self):
        """Starts the voice recognition process."""
        self.log_message("Listening for commands...")
        thread = threading.Thread(target=self.listen_for_commands, daemon=True)
        thread.start()

    def listen_for_commands(self):
        """Handles user voice input and logs responses."""
        while True:
            command = input("Enter command (or speak when mic is enabled): ").strip()  # Replace with speech recognition in full implementation
            if command:
                self.log_message(f"You: {command}")
                response = process_command(command)
                self.log_message(f"Jarvis: {response}")
                speak(response)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisGUI()
    window.show()
    sys.exit(app.exec_())
