import sys
import os
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QHeaderView, QFileDialog
)

DB_NAME = "students.db"


class SmartDashboard(QMainWindow):
    def _init_(self):
        super()._init_()
        self.setWindowTitle("Smart Attendance Dashboard")
        self.setMinimumSize(1000, 650)

        # Tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.today_tab = QWidget()
        self.month_tab = QWidget()

        self.tabs.addTab(self.today_tab, "Today")
        self.tabs.addTab(self.month_tab, "Monthly Summary")

        self.setup_today_tab()
        self.setup_month_tab()

    # =========================
    # TODAY TAB
    # =========================
    def setup_today_tab(self):
        layout = QVBoxLayout()

        title = QLabel("Today Attendance")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        self.today_table = QTableWidget()
        self.today_table.setColumnCount(4)
        self.today_table.setHorizontalHeaderLabels(
            ["Name", "Reg No", "Department", "Time"]
        )
        self.today_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.today_table)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_today_data)
        layout.addWidget(refresh_btn)

        self.today_tab.setLayout(layout)
        self.load_today_data()

    def load_today_data(self):
        if not os.path.exists(DB_NAME):
            self.today_table.setRowCount(0)
            return

        today = datetime.now().strftime("%Y-%m-%d")

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            SELECT s.name, s.reg_no, s.dept, a.time
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.date = ?
            ORDER BY a.time
        """, (today,))

        rows = cur.fetchall()
        conn.close()

        self.today_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                self.today_table.setItem(r, c, QTableWidgetItem(str(val)))

    # =========================
    # MONTH TAB
    # =========================
    def setup_month_tab(self):
        layout = QVBoxLayout()

        title = QLabel("Monthly Attendance Summary")
        title.setStyleSheet("font-size:18px; font-weight:bold;")
        layout.addWidget(title)

        self.month_table = QTableWidget()
        self.month_table.setColumnCount(2)
        self.month_table.setHorizontalHeaderLabels(
            ["Name", "Days Present"]
        )
        self.month_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.month_table)

        generate_btn = QPushButton("Generate Report")
        generate_btn.clicked.connect(self.load_month_data)
        layout.addWidget(generate_btn)

        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        layout.addWidget(export_btn)

        self.month_tab.setLayout(layout)
        self.load_month_data()

    def load_month_data(self):
        if not os.path.exists(DB_NAME):
            self.month_table.setRowCount(0)
            return

        month_str = datetime.now().strftime("%Y-%m")

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            SELECT s.name, COUNT(*)
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.date LIKE ?
            GROUP BY s.name
            ORDER BY s.name
        """, (f"{month_str}%",))

        data = cur.fetchall()
        conn.close()

        self.month_table.setRowCount(len(data))
        for r, row in enumerate(data):
            for c, val in enumerate(row):
                self.month_table.setItem(r, c, QTableWidgetItem(str(val)))

    # =========================
    # EXPORT CSV
    # =========================
    def export_csv(self):
        if self.month_table.rowCount() == 0:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV", "", "CSV Files (*.csv)"
        )
        if not path:
            return

        rows = self.month_table.rowCount()
        cols = self.month_table.columnCount()

        with open(path, "w", encoding="utf-8") as f:
            headers = [
                self.month_table.horizontalHeaderItem(c).text()
                for c in range(cols)
            ]
            f.write(",".join(headers) + "\n")

            for r in range(rows):
                rowdata = []
                for c in range(cols):
                    item = self.month_table.item(r, c)
                    rowdata.append(item.text() if item else "")
                f.write(",".join(rowdata) + "\n")


# =========================
# RUN APP
# =========================
if _name_ == "_main_":
    app = QApplication(sys.argv)

    # 🎨 Light Blue + White Theme
    app.setStyleSheet("""
    QMainWindow {
        background: #eaf4ff;
    }

    QTabWidget::pane {
        border: 0;
        background: white;
    }

    QTabBar::tab {
        background: #cfe8ff;
        color: #0b3d91;
        padding: 10px;
        margin: 2px;
        border-radius: 6px;
        font-weight: bold;
    }

    QTabBar::tab:selected {
        background: #ffffff;
        color: #002366;
    }

    QLabel {
        color: #0b3d91;
    }

    QPushButton {
        background: #4da3ff;
        color: white;
        padding: 8px;
        border-radius: 8px;
        font-weight: bold;
    }

    QPushButton:hover {
        background: #1e90ff;
    }

    QTableWidget {
        background: white;
        gridline-color: #d0e7ff;
        font-size: 13px;
    }

    QHeaderView::section {
        background: #b8dcff;
        padding: 6px;
        border: none;
        font-weight: bold;
    }
    """)

    window = SmartDashboard()
    window.show()
    sys.exit(app.exec_())