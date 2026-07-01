import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QPushButton, QLabel, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class AdminPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Attendance - Admin Panel")
        self.setGeometry(300, 150, 400, 500)

        layout = QVBoxLayout()

        title = QLabel("Smart Attendance System")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Buttons
        btn_register = QPushButton("Register Student")
        btn_capture = QPushButton("Capture Faces")
        btn_train = QPushButton("Train Model")
        btn_attendance = QPushButton("Start Attendance")
        btn_dashboard = QPushButton("Open Dashboard")

        # Connect buttons
        btn_register.clicked.connect(lambda: self.run_script("register_student.py"))
        btn_capture.clicked.connect(lambda: self.run_script("capture_faces.py"))
        btn_train.clicked.connect(lambda: self.run_script("train_model.py"))
        btn_attendance.clicked.connect(lambda: self.run_script("main.py"))
        btn_dashboard.clicked.connect(lambda: self.run_script("dashboard_pro.py"))

        # Add to layout
        for btn in [btn_register, btn_capture, btn_train, btn_attendance, btn_dashboard]:
            btn.setMinimumHeight(50)
            layout.addWidget(btn)

        self.setLayout(layout)

    def run_script(self, script_name):
        try:
            subprocess.Popen(["python", script_name])
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminPanel()
    window.show()
    sys.exit(app.exec_())