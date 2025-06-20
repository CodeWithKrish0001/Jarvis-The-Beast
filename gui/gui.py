import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt

class JarvisGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S")
        self.setStyleSheet("background-color: black;")
        self.showFullScreen()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)

        # Absolute path to the GIF
        gif_path = os.path.join(os.path.dirname(__file__), "assets", "Jarvis.gif")
        movie = QMovie(gif_path)
        self.gif_label.setMovie(movie)
        movie.start()

        layout.addWidget(self.gif_label)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = JarvisGUI()
    window.show()
    sys.exit(app.exec_())
