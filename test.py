# student panel - test.py
import sys
import os
import subprocess
import datetime
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QTime
from PyQt6.QtGui import QFont
from database import process_scan 


class BarcodeListenerThread(QThread):
    scan_received = pyqtSignal(str)

    def run(self):
        print("==================================================")
        print(" Smartboard Barcode Attendance Listener (Active) ")
        print("==================================================")
        print("Listening for scans... (Press Ctrl+C to stop)\n")

        while True:
            try:
                scanned_code = sys.stdin.readline().strip()
                if scanned_code:
                    process_scan(scanned_code)
                    self.scan_received.emit(scanned_code)
            except (KeyboardInterrupt, Exception):
                print("\nShutting down attendance listener.")
                break


class ClassroomDashboard(QWidget):
    def __init__(self, current_class_name="Class 6 A"):
        super().__init__()
        
        # Display selected class name in top left
        self.selected_class_name = current_class_name

        # Schedule structure with start/end QTime objects for evaluation
        self.full_schedule_structure = [
            ("1", "10:15 AM - 11:00 AM", QTime(10, 15), QTime(11, 0), False, 1),
            ("2", "11:00 AM - 11:40 AM", QTime(11, 0), QTime(11, 40), False, 2),
            ("-", "11:40 AM - 11:45 AM", QTime(11, 40), QTime(11, 45), True, None),
            ("3", "11:45 AM - 12:25 PM", QTime(11, 45), QTime(12, 25), False, 3),
            ("4", "12:25 PM - 01:05 PM", QTime(12, 25), QTime(13, 5), False, 4),
            ("-", "01:05 PM - 01:45 PM", QTime(13, 5), QTime(13, 45), True, None),
            ("5", "01:45 PM - 02:25 PM", QTime(13, 45), QTime(14, 25), False, 5),
            ("6", "02:25 PM - 03:05 PM", QTime(14, 25), QTime(15, 5), False, 6),
            ("-", "03:05 PM - 03:10 PM", QTime(15, 5), QTime(15, 10), True, None),
            ("7", "03:10 PM - 03:50 PM", QTime(15, 10), QTime(15, 50), False, 7),
            ("8", "03:50 PM - 04:30 PM", QTime(15, 50), QTime(16, 30), False, 8),
        ]

        # Master Routine Matrix
        self.all_routines = {
            # --- CLASS 6 ---
            "Class 6 A": {
                1: {1: ("English", "DRG"), 2: ("Maths", "IPG"), 3: ("Science", "YS"), 4: ("Social", "TPK"), 5: ("Nepali", "SRG")},
                2: {1: ("Maths", "IPG"), 2: ("English", "DRG"), 3: ("Nepali", "SRG"), 4: ("Science", "YS"), 5: ("Computer", "PL")},
                3: {1: ("Science", "YS"), 2: ("Nepali", "SRG"), 3: ("English", "DRG"), 4: ("Maths", "IPG"), 5: ("Social", "TPK")},
                4: {1: ("Social", "TPK"), 2: ("Science", "YS"), 3: ("Maths", "IPG"), 4: ("English", "DRG"), 5: ("Local Cu.", "TNS")},
                5: {1: ("Nepali", "SRG"), 2: ("Local Cu.", "TNS"), 3: ("Computer", "PL"), 4: ("Science", "YS"), 5: ("English", "DRG")},
                6: {1: ("Computer", "PL"), 2: ("Social", "TPK"), 3: ("Local Cu.", "TNS"), 4: ("Maths", "IPG"), 5: ("Nepali", "SPG")},
                7: {}
            },
            "Class 6 B": {
                1: {1: ("Maths", "IPG"), 2: ("English", "DRG"), 3: ("Nepali", "SRG"), 4: ("Science", "YS"), 5: ("Social", "TPK")},
                2: {1: ("English", "DRG"), 2: ("Science", "YS"), 3: ("Maths", "IPG"), 4: ("Computer", "PL"), 5: ("Nepali", "SRG")},
                3: {1: ("Nepali", "SRG"), 2: ("Maths", "IPG"), 3: ("Science", "YS"), 4: ("Social", "TPK"), 5: ("English", "DRG")},
                4: {1: ("Science", "YS"), 2: ("English", "DRG"), 3: ("Social", "TPK"), 4: ("Local Cu.", "TNS"), 5: ("Maths", "IPG")},
                5: {1: ("Local Cu.", "TNS"), 2: ("Nepali", "SRG"), 3: ("Science", "YS"), 4: ("English", "DRG"), 5: ("Computer", "PL")},
                6: {1: ("Social", "TPK"), 2: ("Computer", "PL"), 3: ("Maths", "IPG"), 4: ("Nepali", "SPG"), 5: ("Local Cu.", "TNS")},
                7: {}
            },

            # --- CLASS 7 ---
            "Class 7 A": {
                1: {1: ("Nepali", "SRG"), 2: ("English", "DRG"), 3: ("Maths", "IPG"), 4: ("Science", "YS"), 5: ("Social", "TPK")},
                2: {1: ("English", "DRG"), 2: ("Maths", "IPG"), 3: ("Science", "YS"), 4: ("Nepali", "SRG"), 5: ("Computer", "PL")},
                3: {1: ("Maths", "IPG"), 2: ("Science", "YS"), 3: ("Social", "TPK"), 4: ("English", "DRG"), 5: ("Local Cu.", "TNS")},
                4: {1: ("Science", "YS"), 2: ("Nepali", "SRG"), 3: ("Computer", "PL"), 4: ("Maths", "IPG"), 5: ("Social", "TPK")},
                5: {1: ("Social", "TPK"), 2: ("Computer", "PL"), 3: ("English", "DRG"), 4: ("Local Cu.", "TNS"), 5: ("Nepali", "SPG")},
                6: {1: ("Local Cu.", "TNS"), 2: ("Social", "TPK"), 3: ("Nepali", "SRG"), 4: ("Science", "YS"), 5: ("Maths", "IPG")},
                7: {}
            },
            "Class 7 B": {
                1: {1: ("Science", "YS"), 2: ("Maths", "IPG"), 3: ("English", "DRG"), 4: ("Nepali", "SRG"), 5: ("Social", "TPK")},
                2: {1: ("Nepali", "SRG"), 2: ("Social", "TPK"), 3: ("Computer", "PL"), 4: ("Science", "YS"), 5: ("English", "DRG")},
                3: {1: ("English", "DRG"), 2: ("Local Cu.", "TNS"), 3: ("Maths", "IPG"), 4: ("Science", "YS"), 5: ("Nepali", "SRG")},
                4: {1: ("Maths", "IPG"), 2: ("Science", "YS"), 3: ("Social", "TPK"), 4: ("English", "DRG"), 5: ("Computer", "PL")},
                5: {1: ("Computer", "PL"), 2: ("English", "DRG"), 3: ("Nepali", "SPG"), 4: ("Local Cu.", "TNS"), 5: ("Social", "TPK")},
                6: {1: ("Social", "TPK"), 2: ("Nepali", "SRG"), 3: ("Science", "YS"), 4: ("Maths", "IPG"), 5: ("Local Cu.", "TNS")},
                7: {}
            },

            # --- CLASS 8 ---
            "Class 8 A": {
                1: {1: ("Maths", "IPG"), 2: ("Science", "YS"), 3: ("English", "DRG"), 4: ("Nepali", "SRG"), 5: ("Social", "TPK")},
                2: {1: ("Science", "YS"), 2: ("Nepali", "SRG"), 3: ("Social", "TPK"), 4: ("English", "DRG"), 5: ("Maths", "IPG")},
                3: {1: ("English", "DRG"), 2: ("Social", "TPK"), 3: ("Computer", "PL"), 4: ("Science", "YS"), 5: ("Local Cu.", "TNS")},
                4: {1: ("Nepali", "SRG"), 2: ("Computer", "PL"), 3: ("Maths", "IPG"), 4: ("Social", "TPK"), 5: ("English", "DRG")},
                5: {1: ("Computer", "PL"), 2: ("Maths", "IPG"), 3: ("Science", "YS"), 4: ("Local Cu.", "TNS"), 5: ("Nepali", "SPG")},
                6: {1: ("Social", "TPK"), 2: ("Local Cu.", "TNS"), 3: ("English", "DRG"), 4: ("Nepali", "SRG"), 5: ("Science", "YS")},
                7: {}
            },
            "Class 8 B": {
                1: {1: ("English", "DRG"), 2: ("Nepali", "SRG"), 3: ("Maths", "IPG"), 4: ("Science", "YS"), 5: ("Computer", "PL")},
                2: {1: ("Maths", "IPG"), 2: ("Social", "TPK"), 3: ("English", "DRG"), 4: ("Nepali", "SRG"), 5: ("Science", "YS")},
                3: {1: ("Science", "YS"), 2: ("Computer", "PL"), 3: ("Local Cu.", "TNS"), 4: ("Maths", "IPG"), 5: ("Social", "TPK")},
                4: {1: ("Social", "TPK"), 2: ("English", "DRG"), 3: ("Science", "YS"), 4: ("Computer", "PL"), 5: ("Nepali", "SRG")},
                5: {1: ("Nepali", "SRG"), 2: ("Science", "YS"), 3: ("Maths", "IPG"), 4: ("English", "DRG"), 5: ("Local Cu.", "TNS")},
                6: {1: ("Local Cu.", "TNS"), 2: ("Maths", "IPG"), 3: ("Nepali", "SPG"), 4: ("Social", "TPK"), 5: ("English", "DRG")},
                7: {}
            },

            # --- CLASS 9 ---
            "Class 9 A": {
                1: {1: ("English", "DRG"), 2: ("Maths", "IPG"), 3: ("Science", "PA"), 4: ("Nepali", "SRG"), 5: ("Opt. Maths", "BK")},
                2: {1: ("Maths", "IPG"), 2: ("Science", "PA"), 3: ("Nepali", "SRG"), 4: ("Social", "TPK"), 5: ("English", "DRG")},
                3: {1: ("Science", "PA"), 2: ("Nepali", "SRG"), 3: ("Opt. Maths", "BK"), 4: ("English", "DRG"), 5: ("Computer", "PL")},
                4: {1: ("Nepali", "SRG"), 2: ("Social", "TPK"), 3: ("English", "DRG"), 4: ("Science", "PA"), 5: ("Maths", "IPG")},
                5: {1: ("Social", "TPK"), 2: ("English", "DRG"), 3: ("Maths", "IPG"), 4: ("Opt. Maths", "BK"), 5: ("Nepali", "SPG")},
                6: {1: ("Opt. Maths", "BK"), 2: ("Computer", "PL"), 3: ("Social", "TPK"), 4: ("Maths", "IPG"), 5: ("Science", "PA")},
                7: {}
            },
            "Class 9 B": {
                1: {1: ("Science", "PA"), 2: ("Opt. Maths", "BK"), 3: ("English", "DRG"), 4: ("Maths", "IPG"), 5: ("Nepali", "SRG")},
                2: {1: ("English", "DRG"), 2: ("Nepali", "SRG"), 3: ("Maths", "IPG"), 4: ("Opt. Maths", "BK"), 5: ("Social", "TPK")},
                3: {1: ("Maths", "IPG"), 2: ("Social", "TPK"), 3: ("Science", "PA"), 4: ("Computer", "PL"), 5: ("English", "DRG")},
                4: {1: ("Opt. Maths", "BK"), 2: ("Science", "PA"), 3: ("Nepali", "SRG"), 4: ("English", "DRG"), 5: ("Social", "TPK")},
                5: {1: ("Nepali", "SRG"), 2: ("Maths", "IPG"), 3: ("Social", "TPK"), 4: ("Science", "PA"), 5: ("Computer", "PL")},
                6: {1: ("Computer", "PL"), 2: ("English", "DRG"), 3: ("Opt. Maths", "BK"), 4: ("Nepali", "SPG"), 5: ("Maths", "IPG")},
                7: {}
            },

            # --- CLASS 10 ---
            "Class 10 A": {
                1: {2: ("English", "DRG"), 3: ("Nepali", "SRG"), 4: ("Nepali", "SRG"), 5: ("Nepali", "SRG"), 6: ("Nepali", "SPG")},
                2: {1: ("English", "DRG"), 2: ("English", "DRG"), 3: ("Nepali", "SRG"), 4: ("Nepali", "SRG"), 5: ("Nepali", "SRG"), 6: ("Nepali", "SPG")},
                3: {2: ("English", "DRG"), 3: ("Nepali", "SRG"), 4: ("Nepali", "SRG"), 5: ("Nepali", "SRG"), 6: ("Nepali", "SPG")},
                4: {2: ("English", "DRG"), 3: ("English", "DRG"), 4: ("Social", "TPK"), 5: ("Science", "PA"), 6: ("Social", "TPK")},
                5: {2: ("Local Cu.", "TNS"), 3: ("English II", "SS"), 4: ("Computer", "PL"), 5: ("English II", "SS"), 6: ("Science", "PG")},
                6: {2: ("Social", "TPK"), 3: ("Social", "TPK"), 4: ("Local Cu.", "TNS"), 6: ("Nepali", "SPG")},
                7: {}
            },
            "Class 10 B": {
                1: {1: ("Science", "PA"), 2: ("English", "DRG"), 3: ("Nepali", "SRG"), 4: ("Social", "TPK"), 5: ("Local Cu.", "TNS")},
                2: {1: ("Nepali", "SRG"), 2: ("Maths", "IPG"), 3: ("English", "DRG"), 4: ("Computer", "PL"), 5: ("Science", "PA")},
                3: {1: ("Social", "TPK"), 2: ("Nepali", "SRG"), 3: ("Science", "PA"), 4: ("English II", "SS"), 5: ("Maths", "IPG")},
                4: {1: ("Maths", "IPG"), 2: ("Local Cu.", "TNS"), 3: ("Social", "TPK"), 4: ("Nepali", "SRG"), 5: ("English", "DRG")},
                5: {1: ("English II", "SS"), 2: ("Computer", "PL"), 3: ("Maths", "IPG"), 4: ("Science", "PG"), 5: ("Social", "TPK")},
                6: {1: ("Computer", "PL"), 2: ("Science", "PA"), 3: ("English", "DRG"), 4: ("Maths", "IPG"), 5: ("Nepali", "SPG")},
                7: {}
            },

            # --- CLASS 11 ---
            "Class 11 A": {
                1: {1: ("Physics", "RKB"), 2: ("Chemistry", "DNB"), 3: ("Mathematics", "IPG"), 4: ("English", "DRG"), 5: ("Biology", "KPS")},
                2: {1: ("Chemistry", "DNB"), 2: ("Physics", "RKB"), 3: ("English", "DRG"), 4: ("Mathematics", "IPG"), 5: ("Computer Sci.", "PL")},
                3: {1: ("Mathematics", "IPG"), 2: ("English", "DRG"), 3: ("Biology", "KPS"), 4: ("Physics", "RKB"), 5: ("Chemistry", "DNB")},
                4: {1: ("English", "DRG"), 2: ("Biology", "KPS"), 3: ("Physics", "RKB"), 4: ("Chemistry", "DNB"), 5: ("Nepali", "SRG")},
                5: {1: ("Computer Sci.", "PL"), 2: ("Mathematics", "IPG"), 3: ("Chemistry", "DNB"), 4: ("Physics", "RKB"), 5: ("Nepali", "SRG")},
                6: {1: ("Nepali", "SRG"), 2: ("Physics Lab", "RKB"), 3: ("Chem Lab", "DNB"), 4: ("Bio Lab", "KPS"), 5: ("Mathematics", "IPG")},
                7: {}
            },
            "Class 11 B": {
                1: {1: ("Chemistry", "DNB"), 2: ("Physics", "RKB"), 3: ("English", "DRG"), 4: ("Biology", "KPS"), 5: ("Mathematics", "IPG")},
                2: {1: ("Physics", "RKB"), 2: ("Mathematics", "IPG"), 3: ("Chemistry", "DNB"), 4: ("Computer Sci.", "PL"), 5: ("English", "DRG")},
                3: {1: ("English", "DRG"), 2: ("Biology", "KPS"), 3: ("Physics", "RKB"), 4: ("Chemistry", "DNB"), 5: ("Nepali", "SRG")},
                4: {1: ("Biology", "KPS"), 2: ("Chemistry", "DNB"), 3: ("Mathematics", "IPG"), 4: ("Nepali", "SRG"), 5: ("Physics", "RKB")},
                5: {1: ("Mathematics", "IPG"), 2: ("Nepali", "SRG"), 3: ("Computer Sci.", "PL"), 4: ("Physics", "RKB"), 5: ("Chemistry", "DNB")},
                6: {1: ("Chem Lab", "DNB"), 2: ("Physics Lab", "RKB"), 3: ("Nepali", "SRG"), 4: ("Mathematics", "IPG"), 5: ("Computer Lab", "PL")},
                7: {}
            },
            "Class 11 C": {
                1: {1: ("Programming", "PL"), 2: ("Database", "PL"), 3: ("Mathematics", "IPG"), 4: ("English", "DRG"), 5: ("Nepali", "SRG")},
                2: {1: ("Database", "PL"), 2: ("Programming", "PL"), 3: ("English", "DRG"), 4: ("Mathematics", "IPG"), 5: ("Computer Network", "PL")},
                3: {1: ("Mathematics", "IPG"), 2: ("English", "DRG"), 3: ("Nepali", "SRG"), 4: ("Programming", "PL"), 5: ("Database", "PL")},
                4: {1: ("English", "DRG"), 2: ("Nepali", "SRG"), 3: ("Programming", "PL"), 4: ("Database", "PL"), 5: ("Web Dev", "PL")},
                5: {1: ("Computer Network", "PL"), 2: ("Mathematics", "IPG"), 3: ("Database", "PL"), 4: ("Programming", "PL"), 5: ("Web Dev", "PL")},
                6: {1: ("Web Dev", "PL"), 2: ("Coding Lab", "PL"), 3: ("Hardware Lab", "PL"), 4: ("English", "DRG"), 5: ("Nepali", "SRG")},
                7: {}
            },
            "Class 11 D": {
                1: {1: ("Database", "PL"), 2: ("Mathematics", "IPG"), 3: ("Programming", "PL"), 4: ("Nepali", "SRG"), 5: ("English", "DRG")},
                2: {1: ("Computer Network", "PL"), 2: ("English", "DRG"), 3: ("Database", "PL"), 4: ("Programming", "PL"), 5: ("Mathematics", "IPG")},
                3: {1: ("Programming", "PL"), 2: ("Database", "PL"), 3: ("English", "DRG"), 4: ("Nepali", "SRG"), 5: ("Computer Network", "PL")},
                4: {1: ("Mathematics", "IPG"), 2: ("Web Dev", "PL"), 3: ("English", "DRG"), 4: ("Programming", "PL"), 5: ("Database", "PL")},
                5: {1: ("Web Dev", "PL"), 2: ("Programming", "PL"), 3: ("Mathematics", "IPG"), 4: ("Nepali", "SRG"), 5: ("Computer Network", "PL")},
                6: {1: ("Coding Lab", "PL"), 2: ("Hardware Lab", "PL"), 3: ("Web Dev", "PL"), 4: ("Nepali", "SRG"), 5: ("English", "DRG")},
                7: {}
            },

            # --- CLASS 12 ---
            "Class 12 A": {
                1: {1: ("Physics II", "RKB"), 2: ("Chemistry II", "DNB"), 3: ("Mathematics II", "IPG"), 4: ("Nepali", "SRG"), 5: ("English", "DRG")},
                2: {1: ("Chemistry II", "DNB"), 2: ("Physics II", "RKB"), 3: ("Nepali", "SRG"), 4: ("Mathematics II", "IPG"), 5: ("Biology II", "KPS")},
                3: {1: ("Mathematics II", "IPG"), 2: ("Nepali", "SRG"), 3: ("Biology II", "KPS"), 4: ("Physics II", "RKB"), 5: ("Chemistry II", "DNB")},
                4: {1: ("Nepali", "SRG"), 2: ("Biology II", "KPS"), 3: ("Physics II", "RKB"), 4: ("Chemistry II", "DNB"), 5: ("English", "DRG")},
                5: {1: ("English", "DRG"), 2: ("Mathematics II", "IPG"), 3: ("Chemistry II", "DNB"), 4: ("Physics II", "RKB"), 5: ("Computer Sci.", "PL")},
                6: {1: ("Computer Sci.", "PL"), 2: ("Physics Lab", "RKB"), 3: ("Chem Lab", "DNB"), 4: ("Mathematics II", "IPG"), 5: ("English", "DRG")},
                7: {}
            },
            "Class 12 B": {
                1: {1: ("Chemistry II", "DNB"), 2: ("Physics II", "RKB"), 3: ("Biology II", "KPS"), 4: ("English", "DRG"), 5: ("Mathematics II", "IPG")},
                2: {1: ("Physics II", "RKB"), 2: ("Biology II", "KPS"), 3: ("Chemistry II", "DNB"), 4: ("Mathematics II", "IPG"), 5: ("Nepali", "SRG")},
                3: {1: ("Biology II", "KPS"), 2: ("Chemistry II", "DNB"), 3: ("Physics II", "RKB"), 4: ("Nepali", "SRG"), 5: ("English", "DRG")},
                4: {1: ("Mathematics II", "IPG"), 2: ("Physics II", "RKB"), 3: ("Nepali", "SRG"), 4: ("Chemistry II", "DNB"), 5: ("Computer Sci.", "PL")},
                5: {1: ("Nepali", "SRG"), 2: ("English", "DRG"), 3: ("Physics II", "RKB"), 4: ("Chemistry II", "DNB"), 5: ("Mathematics II", "IPG")},
                6: {1: ("Physics Lab", "RKB"), 2: ("Chem Lab", "DNB"), 3: ("Bio Lab", "KPS"), 4: ("English", "DRG"), 5: ("Mathematics II", "IPG")},
                7: {}
            },
            "Class 12 C": {
                1: {1: ("Adv Programming", "PL"), 2: ("Software Eng", "PL"), 3: ("Business Math II", "IPG"), 4: ("Nepali", "SRG"), 5: ("English", "DRG")},
                2: {1: ("Software Eng", "PL"), 2: ("Adv Programming", "PL"), 3: ("Nepali", "SRG"), 4: ("Business Math II", "IPG"), 5: ("Cyber Security", "PL")},
                3: {1: ("Business Math II", "IPG"), 2: ("Nepali", "SRG"), 3: ("English", "DRG"), 4: ("Adv Programming", "PL"), 5: ("Software Eng", "PL")},
                4: {1: ("Nepali", "SRG"), 2: ("English", "DRG"), 3: ("Adv Programming", "PL"), 4: ("Software Eng", "PL"), 5: ("Data Structures", "PL")},
                5: {1: ("English", "DRG"), 2: ("Business Math II", "IPG"), 3: ("Software Eng", "PL"), 4: ("Adv Programming", "PL"), 5: ("Data Structures", "PL")},
                6: {1: ("Data Structures", "PL"), 2: ("Project Work", "PL"), 3: ("Software Lab", "PL"), 4: ("English", "DRG"), 5: ("Nepali", "SRG")},
                7: {}
            },
            "Class 12 D": {
                1: {1: ("Software Eng", "PL"), 2: ("Business Math II", "IPG"), 3: ("Adv Programming", "PL"), 4: ("English", "DRG"), 5: ("Nepali", "SRG")},
                2: {1: ("Adv Programming", "PL"), 2: ("Cyber Security", "PL"), 3: ("Software Eng", "PL"), 4: ("Nepali", "SRG"), 5: ("Business Math II", "IPG")},
                3: {1: ("Cyber Security", "PL"), 2: ("Adv Programming", "PL"), 3: ("Nepali", "SRG"), 4: ("Business Math II", "IPG"), 5: ("English", "DRG")},
                4: {1: ("Data Structures", "PL"), 2: ("Software Eng", "PL"), 3: ("English", "DRG"), 4: ("Nepali", "SRG"), 5: ("Adv Programming", "PL")},
                5: {1: ("Business Math II", "IPG"), 2: ("Data Structures", "PL"), 3: ("English", "DRG"), 4: ("Software Eng", "PL"), 5: ("Nepali", "SRG")},
                6: {1: ("Project Work", "PL"), 2: ("Software Lab", "PL"), 3: ("Data Structures", "PL"), 4: ("Nepali", "SRG"), 5: ("English", "DRG")},
                7: {}
            }
        }
        
        self.init_ui()
        self.start_listener()

        # Set up real-time timer for clock and schedule updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_live_time_and_status)
        self.timer.start(1000)
        self.update_live_time_and_status()

    def start_listener(self):
        self.listener_thread = BarcodeListenerThread()
        self.listener_thread.start()

    def open_cal(self):
        cal_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cal.py")
        subprocess.Popen([sys.executable, cal_path], cwd=os.path.dirname(cal_path))
        self.close()

    def open_db(self):
        subprocess.Popen([sys.executable, "database.py"])
        self.close()

    def open_help(self):
        help_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "help.py")
        subprocess.Popen([sys.executable, help_path], cwd=os.path.dirname(help_path))
        QApplication.quit()
        sys.exit()

    def handle_logout(self):
        reply = QMessageBox.question(
            self, 'Confirm Logout', 'Are you sure you want to log out?', 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            admin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "adminpage.py")
            subprocess.Popen([sys.executable, admin_path], cwd=os.path.dirname(admin_path))
            self.close()
            QApplication.quit()
            sys.exit()

    def update_live_time_and_status(self):
        now = datetime.datetime.now()
        
        # 1. Update Real-Time Clock & Date in Header
        self.clock_lbl.setText(now.strftime("%I:%M:%S %p"))
        self.date_lbl.setText(now.strftime("%A, %d %B %Y"))

        # 2. Update Dynamic Period/Class Block
        py_weekday = now.weekday()
        day_map = {6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
        current_routine_day = day_map[py_weekday]

        selected_routine = self.all_routines.get(self.selected_class_name, {})
        today_classes = selected_routine.get(current_routine_day, {})

        if current_routine_day == 7:
            # Weekend Holiday
            self.curr_card.setStyleSheet("background-color: #243547; border-radius: 12px;")
            self.badge.setText("Holiday")
            self.badge.setStyleSheet("background-color: #3b4d61; color: #a4b3c1; border-radius: 10px; padding: 4px 8px; font-weight: bold; font-size: 10px;")
            self.period_lbl.setText("Weekend  •  All Day")
            self.subj_lbl.setText("Holiday (Saturday)")
            self.teacher_lbl.setText("Teacher: -")
        else:
            current_qtime = QTime.currentTime()
            active_block = None

            for p_num, time_str, start_t, end_t, is_break, p_idx in self.full_schedule_structure:
                if start_t <= current_qtime <= end_t:
                    active_block = (p_num, time_str, is_break, p_idx)
                    break

            if active_block:
                p_num, time_str, is_break, p_idx = active_block
                if is_break:
                    self.curr_card.setStyleSheet("background-color: #902a2a; border-radius: 12px;")
                    self.badge.setText("Break")
                    self.badge.setStyleSheet("background-color: #c0392b; color: #ffffff; border-radius: 10px; padding: 4px 8px; font-weight: bold; font-size: 10px;")
                    self.period_lbl.setText(f"Break  •  {time_str}")
                    self.subj_lbl.setText("☕ Break Time")
                    self.teacher_lbl.setText("Teacher: -")
                else:
                    subj, teacher = today_classes.get(p_idx, ("Free Period", "-"))
                    self.curr_card.setStyleSheet("background-color: #243547; border-radius: 12px;")
                    self.badge.setText("Ongoing")
                    self.badge.setStyleSheet("background-color: #1e3d34; color: #2ecc71; border-radius: 10px; padding: 4px 8px; font-weight: bold; font-size: 10px;")
                    self.period_lbl.setText(f"Period {p_num}  •  {time_str}")
                    self.subj_lbl.setText(subj)
                    self.teacher_lbl.setText(f"Teacher: {teacher}")
            else:
                self.curr_card.setStyleSheet("background-color: #243547; border-radius: 12px;")
                self.badge.setText("Offline")
                self.badge.setStyleSheet("background-color: #3b4d61; color: #a4b3c1; border-radius: 10px; padding: 4px 8px; font-weight: bold; font-size: 10px;")
                self.period_lbl.setText("School Hours Closed")
                self.subj_lbl.setText("No Active Class")
                self.teacher_lbl.setText("Teacher: -")

    def update_schedule_table(self):
        py_weekday = datetime.datetime.now().weekday()
        day_map = {6: 1, 0: 2, 1: 3, 2: 4, 3: 5, 4: 6, 5: 7}
        current_routine_day = day_map[py_weekday]

        selected_routine = self.all_routines.get(self.selected_class_name, {})
        today_classes = selected_routine.get(current_routine_day, {})

        data = []
        if current_routine_day == 7:
            data.append(("-", "All Day", "🎉 Weekend Holiday", "-"))
        else:
            for p_num, time_str, _, _, is_break, p_idx in self.full_schedule_structure:
                if is_break:
                    data.append((p_num, time_str, "☕ Break", "-"))
                else:
                    subj, teacher = today_classes.get(p_idx, ("-", "-"))
                    data.append((p_num, time_str, subj, teacher))

        self.table.setRowCount(len(data))
        for row, period in enumerate(data):
            for col, item in enumerate(period):
                item_widget = QTableWidgetItem(item)
                if period[2] in ["☕ Break", "🎉 Weekend Holiday"]:
                    item_widget.setForeground(Qt.GlobalColor.darkGray)
                self.table.setItem(row, col, item_widget)
        self.table.selectRow(0)

    def init_ui(self):
        self.setWindowTitle(f"Classroom Display System - {self.selected_class_name}")
        self.resize(1100, 650)
        self.setStyleSheet("background-color: #1a2936; color: #ffffff; font-family: 'Segoe UI', sans-serif;")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Sidebar Navigation
        sidebar = QFrame()
        sidebar.setFixedWidth(70)
        sidebar.setStyleSheet("background-color: #15222e; border-right: 1px solid #243547;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(15)
        
        btn_bell = QPushButton("🔔")
        btn_home = QPushButton("🏠")
        btn_cal = QPushButton("📅")
        
        btn_cal.clicked.connect(self.open_cal)
        
        nav_buttons = [btn_bell, btn_home, btn_cal]
        for btn in nav_buttons:
            btn.setFixedSize(50, 45)
            btn.setFont(QFont("Segoe UI", 12))
            btn.setStyleSheet(
                "QPushButton { background-color: transparent; color: #8c9fae; border-radius: 8px; border: none; } "
                "QPushButton:hover { background-color: #243547; color: #ffffff; }"
            )
            sidebar_layout.addWidget(btn)
            
        btn_home.setStyleSheet("background-color: #2a3e52; color: #3498db; border-radius: 8px;")
        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)
        
        # Content Area
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 20, 30, 20)
        content_layout.setSpacing(15)
        
        # Top Header Banner
        top_banner = QHBoxLayout()
        
        self.class_title = QLabel(self.selected_class_name)
        self.class_title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.class_title.setStyleSheet("color: #ffffff;")
        
        time_box = QVBoxLayout()
        self.clock_lbl = QLabel("")
        self.clock_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.clock_lbl.setStyleSheet("color: #a4b3c1;")
        
        self.date_lbl = QLabel("")
        self.date_lbl.setFont(QFont("Segoe UI", 10))
        self.date_lbl.setStyleSheet("color: #6a7e90;")
        
        time_box.addWidget(self.clock_lbl)
        time_box.addWidget(self.date_lbl)
        
        # Restored "Mark Your Attendance" Button
        btn_attendance = QPushButton("📋 Mark Your Attendance")
        btn_attendance.setStyleSheet(
            "QPushButton { background-color: #3498db; color: #ffffff; border-radius: 8px; padding: 10px 18px; font-weight: bold; font-size: 13px; border: none; } "
            "QPushButton:hover { background-color: #2980b9; }"
        )
        btn_attendance.clicked.connect(self.open_db)
        
        top_banner.addWidget(self.class_title)
        top_banner.addStretch()
        top_banner.addLayout(time_box)
        top_banner.addSpacing(20)
        top_banner.addWidget(btn_attendance)
        content_layout.addLayout(top_banner)
        
        # Currently Card Block
        self.curr_card = QFrame()
        self.curr_card.setStyleSheet("background-color: #243547; border-radius: 12px;")
        curr_layout = QVBoxLayout(self.curr_card)
        curr_layout.setContentsMargins(20, 15, 20, 15)
        
        curr_head = QHBoxLayout()
        curr_title = QLabel("Currently")
        curr_title.setFont(QFont("Segoe UI", 11))
        curr_title.setStyleSheet("color: #8c9fae;")
        
        self.badge = QLabel("Ongoing")
        self.badge.setStyleSheet("background-color: #1e3d34; color: #2ecc71; border-radius: 10px; padding: 4px 8px; font-weight: bold; font-size: 10px;")
        
        curr_head.addWidget(curr_title)
        curr_head.addStretch()
        curr_head.addWidget(self.badge)
        
        self.period_lbl = QLabel("-")
        self.period_lbl.setStyleSheet("color: #6a7e90; font-size: 11px; margin-top: 4px;")
        
        self.subj_lbl = QLabel("-")
        self.subj_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.subj_lbl.setStyleSheet("color: #ffffff;")
        
        self.teacher_lbl = QLabel("Teacher: -")
        self.teacher_lbl.setStyleSheet("color: #a4b3c1; font-size: 12px;")
        
        curr_layout.addLayout(curr_head)
        curr_layout.addWidget(self.period_lbl)
        curr_layout.addWidget(self.subj_lbl)
        curr_layout.addWidget(self.teacher_lbl)
        
        # Substitutions Card Block
        sub_card = QFrame()
        sub_card.setStyleSheet("background-color: #243547; border-radius: 12px;")
        sub_layout = QVBoxLayout(sub_card)
        sub_layout.setContentsMargins(20, 15, 20, 15)
        
        sub_title = QLabel("Today's Substitutions")
        sub_title.setFont(QFont("Segoe UI", 11))
        sub_title.setStyleSheet("color: #8c9fae;")
        
        sub_msg1 = QLabel("No substitutions for today.")
        sub_msg1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_msg1.setStyleSheet("color: #6a7e90; margin-top: 15px;")
        
        sub_msg2 = QLabel("Enjoy your classes!")
        sub_msg2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_msg2.setStyleSheet("color: #a4b3c1; font-size: 11px;")
        
        sub_layout.addWidget(sub_title)
        sub_layout.addWidget(sub_msg1)
        sub_layout.addWidget(sub_msg2)
        sub_layout.addStretch()
        
        top_cards_layout = QHBoxLayout()
        top_cards_layout.setSpacing(15)
        top_cards_layout.addWidget(self.curr_card, 1)
        top_cards_layout.addWidget(sub_card, 1)
        content_layout.addLayout(top_cards_layout)
        
        # Table Frame
        table_container = QFrame()
        table_container.setStyleSheet("background-color: #243547; border-radius: 12px;")
        table_box_layout = QVBoxLayout(table_container)
        table_box_layout.setContentsMargins(15, 15, 15, 15)
        
        table_head = QHBoxLayout()
        routine_lbl = QLabel("Today's Routine")
        routine_lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        routine_lbl.setStyleSheet("color: #ffffff;")
        
        table_head.addWidget(routine_lbl)
        table_head.addStretch()
        table_box_layout.addLayout(table_head)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Period", "Time", "Subject", "Teacher"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(
            "QTableWidget { background-color: transparent; color: #e1e8ed; border: none; } "
            "QHeaderView::section { background-color: transparent; color: #6a7e90; font-weight: bold; border: none; padding-bottom: 8px; } "
            "QTableWidget::item { padding: 6px; border-bottom: 1px solid #1a2936; } "
            "QTableWidget::item:selected { background-color: #2c4257; color: #ffffff; }"
        )
        
        table_box_layout.addWidget(self.table)
        content_layout.addWidget(table_container)
        
        # Load Routine Table Data
        self.update_schedule_table()
        
        # Footer Bar
        footer = QFrame()
        footer.setStyleSheet("background-color: #15222e; border-radius: 8px;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(15, 8, 15, 8)
        
        quote_lbl = QLabel("Discipline is the bridge between goals and achievement.")
        quote_lbl.setStyleSheet("color: #8c9fae; font-size: 11px;")
        
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(10)
        
        btn_help = QPushButton("❓ Help")
        btn_help.setStyleSheet(
            "QPushButton { background-color: #243547; color: #ffffff; border-radius: 6px; padding: 5px 12px; font-size: 11px; border: none; } "
            "QPushButton:hover { background-color: #34495e; }"
        )
        btn_help.clicked.connect(self.open_help)

        btn_logout = QPushButton("🚪 Logout")
        btn_logout.setStyleSheet(
            "QPushButton { background-color: #c0392b; color: #ffffff; border-radius: 6px; padding: 5px 12px; font-size: 11px; border: none; font-weight: bold; } "
            "QPushButton:hover { background-color: #e74c3c; }"
        )
        btn_logout.clicked.connect(self.handle_logout)

        actions_layout.addWidget(btn_help)
        actions_layout.addWidget(btn_logout)

        footer_layout.addWidget(quote_lbl)
        footer_layout.addStretch()
        footer_layout.addLayout(actions_layout)
        
        content_layout.addWidget(footer)
        main_layout.addWidget(content_area)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Extract arguments passed from classselect.py
    if len(sys.argv) >= 3:
        target_class = f"Class {sys.argv[1]} {sys.argv[2]}"
    elif len(sys.argv) == 2:
        raw_arg = sys.argv[1]
        target_class = raw_arg if raw_arg.startswith("Class ") else f"Class {raw_arg}"
    else:
        target_class = "Class 6 A"

    window = ClassroomDashboard(target_class)
    window.show()
    sys.exit(app.exec())

DATA_FILE = "data.json"

def get_transferred_data():
    if not os.path.exists(DATA_FILE):
        return {"substitutions": [], "notices": []}
    
    with open(DATA_FILE, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    data = get_transferred_data()
    
    print("=== TRANSFERRED SUBSTITUTIONS ===")
    for sub in data.get("substitutions", []):
        print(f"Class: {sub['class']}-{sub['section']} | Period: {sub['period']} | Absent: {sub['absent']} | Substitute: {sub['substitute']} | Time: {sub['time']}")
        
    print("\n=== TRANSFERRED NOTICES ===")
    for notice in data.get("notices", []):
        print(f"Title: {notice['title']} | Target: Classes {notice['lower']}-{notice['upper']} | File: {notice['file']}\nContent: {notice['content']}\n")

