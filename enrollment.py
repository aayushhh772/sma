import sys
import cv2
import numpy as np
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QSizePolicy
)
from insightface.app import FaceAnalysis
from database import (
    save_student_embedding,
    get_student,
    normalize_student_id
)

CAMERA_INDEX = 0
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
DETECTION_SIZE = (640, 640)
REQUIRED_SAMPLES = 5
MIN_FACE_SIZE = 80
MIN_DETECTION_SCORE = 0.60
PROCESS_EVERY_N_FRAMES = 5
RECOGNITION_FRAME_WIDTH = 640

BLUE = "#247EAE"
BLUE_DARK = "#1E547A"
BLUE_LIGHT = "#EAF2F8"
TEXT = "#1F2F43"
BORDER = "#79B9DE"
PAGE_BG = "#DDEAF4"
SUCCESS = "#1F8A5B"
SUCCESS_LIGHT = "#E8F6EF"
ERROR = "#C0392B"
ERROR_LIGHT = "#FDEDEC"
MUTED = "#65788A"


class EnrollmentWindow(QWidget):

    def __init__(self, previous_window=None):
        super().__init__()

        self.previous_window = previous_window
        self.returning_to_previous = False

        self.setWindowTitle(
            "SOS Hermann Gmeiner School Gandaki Facial Enrollment"
        )
        self.resize(1280, 800)
        self.setMinimumSize(1000, 650)

        self.face_app = None
        self.camera = None
        self.current_frame = None
        self.current_face = None
        self.captured_embeddings = []
        self.frame_counter = 0
        self.last_faces = []
        self.last_valid_face = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera)

        self.setup_ui()

    def go_back(self):
        self.returning_to_previous = True

        self.stop_camera()

        if self.previous_window is not None:
            self.previous_window.show()
            self.previous_window.raise_()
            self.previous_window.activateWindow()

        self.close()

    def closeEvent(self, event):
        self.stop_camera()

        if self.returning_to_previous:
            event.accept()
            return

        if self.previous_window is not None:
            self.previous_window.show()
            self.previous_window.raise_()
            self.previous_window.activateWindow()

        event.accept()

    def setup_ui(self):
        self.setStyleSheet(
            f"""
            QWidget {{
                background: {PAGE_BG};
                color: {TEXT};
                font-family: "Segoe UI";
            }}
            QLineEdit {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
                min-height: 18px;
            }}
            QLineEdit:focus {{
                border: 2px solid {BLUE};
            }}
            QPushButton {{
                background: {BLUE};
                color: white;
                border: 1px solid #1D6F9C;
                border-radius: 10px;
                padding: 11px;
                font-size: 13px;
                font-weight: 600;
                min-height: 18px;
            }}
            QPushButton:hover {{
                background: {BLUE_DARK};
            }}
            QPushButton:disabled {{
                background: #B8C7D3;
                color: #E9EEF2;
                border-color: #B8C7D3;
            }}
            QProgressBar {{
                background: white;
                border: 1px solid {BORDER};
                border-radius: 8px;
                text-align: center;
                min-height: 22px;
            }}
            QProgressBar::chunk {{
                background: {BLUE};
                border-radius: 7px;
            }}
            """
        )

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)

        header = self.create_header()
        main.addWidget(header)

        content = QHBoxLayout()
        content.setContentsMargins(25, 25, 25, 25)
        content.setSpacing(20)

        student_panel = self.create_student_panel()
        student_panel.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding
        )

        camera_panel = self.create_camera_panel()
        camera_panel.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )

        content.addWidget(student_panel, 3)
        content.addWidget(camera_panel, 7)

        main.addLayout(content, 1)

        footer = QLabel(
            "SOS Hermann Gmeiner School Gandaki Facial Enrollment System"
        )
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setMinimumHeight(30)
        footer.setStyleSheet(
            f"""
            background: {BLUE_LIGHT};
            color: {BLUE};
            font-size: 11px;
            """
        )
        main.addWidget(footer)

        self.setLayout(main)

    def create_header(self):
        header = QFrame()
        header.setMinimumHeight(95)
        header.setMaximumHeight(120)
        header.setStyleSheet(
            f"""
            background: {BLUE};
            border-bottom: 1px solid #8BC7E7;
            """
        )

        layout = QHBoxLayout(header)
        layout.setContentsMargins(32, 15, 32, 15)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        title = QLabel("Student Enrollment")
        title.setStyleSheet(
            "color: white; font-size: 24px; font-weight: 700;"
        )

        subtitle = QLabel("GANDAKI PORTAL Facial Enrollment")
        subtitle.setStyleSheet(
            "color: #D9E8F5; font-size: 13px;"
        )

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)

        layout.addLayout(title_layout)
        layout.addStretch()

        back_button = QPushButton("← Back to Dashboard")
        back_button.setFixedSize(175, 40)
        back_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        back_button.setStyleSheet(
            """
            QPushButton {
                background: white;
                color: #247EAE;
                border: 1px solid #D9E8F5;
                border-radius: 9px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 700;
            }

            QPushButton:hover {
                background: #EAF2F8;
                color: #1E547A;
            }

            QPushButton:pressed {
                background: #D9E8F5;
            }
            """
        )

        back_button.clicked.connect(self.go_back)

        layout.addWidget(back_button)

        return header

    def create_student_panel(self):
        panel = QFrame()
        panel.setMinimumWidth(330)
        panel.setStyleSheet(
            f"""
            QFrame {{
                background: {BLUE_LIGHT};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
            """
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(22, 22, 22, 22)
        layout.setSpacing(12)

        heading = QLabel("Student Enrollment")
        heading.setStyleSheet(
            f"color: {BLUE_DARK}; font-size: 21px; font-weight: 700; border: none;"
        )
        layout.addWidget(heading)

        description = QLabel(
            "Enter the student's information, start the camera, "
            "capture facial samples, and save the enrollment."
        )
        description.setWordWrap(True)
        description.setStyleSheet(
            f"color: {BLUE}; font-size: 12px; border: none;"
        )
        layout.addWidget(description)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Student Name")
        layout.addWidget(self.name_input)

        self.student_id_input = QLineEdit()
        self.student_id_input.setPlaceholderText("Student ID")
        layout.addWidget(self.student_id_input)

        self.class_input = QLineEdit()
        self.class_input.setPlaceholderText("Class")
        layout.addWidget(self.class_input)

        self.section_input = QLineEdit()
        self.section_input.setPlaceholderText("Section")
        layout.addWidget(self.section_input)

        self.start_button = QPushButton("Start Camera")
        self.start_button.clicked.connect(self.start_camera)
        layout.addWidget(self.start_button)

        self.capture_button = QPushButton("Capture Face Sample")
        self.capture_button.setEnabled(False)
        self.capture_button.clicked.connect(self.capture_face_sample)
        layout.addWidget(self.capture_button)

        self.save_button = QPushButton("Save Enrollment")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_enrollment)
        layout.addWidget(self.save_button)

        progress_title = QLabel(
            f"FACIAL SAMPLES ({REQUIRED_SAMPLES} REQUIRED)"
        )
        progress_title.setStyleSheet(
            f"color: {BLUE_DARK}; font-size: 11px; font-weight: 700; border: none; margin-top: 8px;"
        )
        layout.addWidget(progress_title)

        self.progress = QProgressBar()
        self.progress.setRange(0, REQUIRED_SAMPLES)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.status = QLabel(
            "Enter student information and start the camera."
        )
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(85)
        self.status.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.MinimumExpanding
        )
        self.status.setStyleSheet(
            f"""
            background: white;
            color: {MUTED};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 12px;
            font-size: 12px;
            """
        )
        layout.addWidget(self.status)

        layout.addStretch()

        return panel

    def create_camera_panel(self):
        panel = QFrame()
        panel.setStyleSheet(
            f"""
            QFrame {{
                background: {BLUE_LIGHT};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
            """
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)

        title = QLabel("Enrollment Camera")
        title.setStyleSheet(
            f"color: {BLUE_DARK}; font-size: 19px; font-weight: 700; border: none;"
        )
        layout.addWidget(title)

        self.camera_view = QLabel("Camera is not active")
        self.camera_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_view.setMinimumSize(400, 300)
        self.camera_view.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        self.camera_view.setStyleSheet(
            "background: #0B243D; color: white; border-radius: 12px; font-size: 16px;"
        )
        layout.addWidget(self.camera_view, 1)

        instruction = QLabel(
            "Keep one face clearly visible. Capture samples with "
            "slightly different natural angles and expressions."
        )
        instruction.setWordWrap(True)
        instruction.setStyleSheet(
            f"color: {BLUE}; font-size: 11px; border: none; padding: 5px;"
        )
        layout.addWidget(instruction)

        return panel

    def initialize_face_system(self):
        if self.face_app is not None:
            return True

        self.status.setText("Loading InsightFace buffalo_l...")
        QApplication.processEvents()

        try:
            print("========================================")
            print("Loading InsightFace buffalo_l...")
            print("========================================")

            self.face_app = FaceAnalysis(
                name="buffalo_l",
                providers=["CPUExecutionProvider"]
            )

            print("FaceAnalysis object created.")

            self.face_app.prepare(
                ctx_id=-1,
                det_size=DETECTION_SIZE
            )

            print("InsightFace buffalo_l loaded successfully.")
            print("========================================")

            return True

        except Exception as error:
            import traceback

            print()
            print("========================================")
            print("INSIGHTFACE MODEL ERROR")
            print("========================================")
            print(str(error))
            print()
            traceback.print_exc()
            print("========================================")

            self.face_app = None

            QMessageBox.critical(
                self,
                "Model Error",
                "Could not load the facial recognition model.\n\n"
                f"{type(error).__name__}: {error}\n\n"
                "See the PyCharm Run console for the full error."
            )

            self.status.setText(
                "Face recognition model failed to load."
            )

            return False
    def validate_student_information(self):
        name = self.name_input.text().strip()
        raw_id = self.student_id_input.text().strip()
        student_id = normalize_student_id(raw_id) or raw_id
        class_number = self.class_input.text().strip()
        section = self.section_input.text().strip().upper()

        if not name:
            QMessageBox.warning(
                self,
                "Missing Name",
                "Enter the student's name."
            )
            return None

        if not student_id:
            QMessageBox.warning(
                self,
                "Missing Student ID",
                "Enter a student ID."
            )
            return None

        if not class_number:
            QMessageBox.warning(
                self,
                "Missing Class",
                "Enter the student's class."
            )
            return None

        if not section:
            QMessageBox.warning(
                self,
                "Missing Section",
                "Enter the student's section."
            )
            return None

        return {
            "name": name,
            "student_id": student_id,
            "class_number": class_number,
            "section": section
        }

    def start_camera(self):
        student = self.validate_student_information()

        if student is None:
            return

        if not self.initialize_face_system():
            return

        self.captured_embeddings = []
        self.progress.setValue(0)
        self.save_button.setEnabled(False)
        self.frame_counter = 0
        self.last_faces = []
        self.last_valid_face = None
        self.current_face = None

        self.camera = cv2.VideoCapture(
            CAMERA_INDEX,
            cv2.CAP_ANY
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            CAMERA_WIDTH
        )

        self.camera.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            CAMERA_HEIGHT
        )

        self.camera.set(
            cv2.CAP_PROP_BUFFERSIZE,
            1
        )

        if not self.camera.isOpened():
            QMessageBox.critical(
                self,
                "Camera Error",
                "The camera could not be opened."
            )

            self.camera.release()
            self.camera = None
            return

        self.capture_button.setEnabled(True)
        self.start_button.setEnabled(False)

        self.status.setText(
            "Camera ready. Position one face clearly in the frame."
        )

        self.timer.start(30)

    def detect_faces(self, frame):
        original_height, original_width = frame.shape[:2]

        if original_width > RECOGNITION_FRAME_WIDTH:
            scale = RECOGNITION_FRAME_WIDTH / original_width

            resized_height = int(
                original_height * scale
            )

            recognition_frame = cv2.resize(
                frame,
                (
                    RECOGNITION_FRAME_WIDTH,
                    resized_height
                )
            )
        else:
            recognition_frame = frame
            scale = 1.0

        try:
            faces = self.face_app.get(
                recognition_frame
            )
        except Exception:
            return [], None

        if scale != 1.0:
            for face in faces:
                face.bbox = face.bbox / scale

        return faces, recognition_frame

    def update_camera(self):
        if self.camera is None:
            return

        success, frame = self.camera.read()

        if not success:
            return

        self.current_frame = frame.copy()
        self.frame_counter += 1

        if self.frame_counter % PROCESS_EVERY_N_FRAMES == 0:
            faces, _ = self.detect_faces(frame)

            self.last_faces = faces
            self.last_valid_face = None

            if len(faces) == 1:
                face = faces[0]

                x1, y1, x2, y2 = map(
                    int,
                    face.bbox
                )

                width = x2 - x1
                height = y2 - y1

                score = float(
                    getattr(
                        face,
                        "det_score",
                        0.0
                    )
                )

                if (
                    width >= MIN_FACE_SIZE
                    and height >= MIN_FACE_SIZE
                    and score >= MIN_DETECTION_SCORE
                    and getattr(
                        face,
                        "embedding",
                        None
                    ) is not None
                ):
                    self.last_valid_face = face
                    self.current_face = face
                else:
                    self.current_face = None
            else:
                self.current_face = None

        display = frame.copy()
        faces = self.last_faces

        if len(faces) == 1:
            face = faces[0]

            x1, y1, x2, y2 = map(
                int,
                face.bbox
            )

            if self.current_face is not None:
                cv2.rectangle(
                    display,
                    (x1, y1),
                    (x2, y2),
                    (46, 204, 113),
                    3
                )

                cv2.putText(
                    display,
                    "FACE READY",
                    (x1, max(30, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (46, 204, 113),
                    2,
                    cv2.LINE_AA
                )
            else:
                cv2.rectangle(
                    display,
                    (x1, y1),
                    (x2, y2),
                    (52, 152, 219),
                    3
                )

                cv2.putText(
                    display,
                    "MOVE CLOSER",
                    (x1, max(30, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (52, 152, 219),
                    2,
                    cv2.LINE_AA
                )

        elif len(faces) > 1:
            for face in faces:
                x1, y1, x2, y2 = map(
                    int,
                    face.bbox
                )

                cv2.rectangle(
                    display,
                    (x1, y1),
                    (x2, y2),
                    (52, 152, 219),
                    3
                )

            cv2.putText(
                display,
                "ONLY ONE FACE PLEASE",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (52, 152, 219),
                2,
                cv2.LINE_AA
            )

        else:
            cv2.putText(
                display,
                "LOOK AT THE CAMERA",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (52, 152, 219),
                2,
                cv2.LINE_AA
            )

        rgb = cv2.cvtColor(
            display,
            cv2.COLOR_BGR2RGB
        )

        image = QImage(
            rgb.data,
            rgb.shape[1],
            rgb.shape[0],
            rgb.strides[0],
            QImage.Format.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.camera_view.setPixmap(
            pixmap.scaled(
                self.camera_view.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.FastTransformation
            )
        )

    def capture_face_sample(self):
        if self.current_face is None:
            self.status.setText(
                "No valid face detected. Ensure exactly one face is visible and move closer if necessary."
            )
            return

        embedding = np.asarray(
            self.current_face.embedding,
            dtype=np.float32
        ).flatten()

        if (
            embedding.size == 0
            or not np.all(np.isfinite(embedding))
        ):
            self.status.setText(
                "Invalid facial embedding detected."
            )
            return

        norm = np.linalg.norm(embedding)

        if norm <= 0:
            self.status.setText(
                "Invalid facial embedding detected."
            )
            return

        embedding = embedding / norm

        self.captured_embeddings.append(
            embedding.tolist()
        )

        sample_count = len(
            self.captured_embeddings
        )

        self.progress.setValue(
            sample_count
        )

        if sample_count < REQUIRED_SAMPLES:
            self.status.setText(
                f"Sample {sample_count}/{REQUIRED_SAMPLES} captured. Capture {REQUIRED_SAMPLES - sample_count} more."
            )
        else:
            self.capture_button.setEnabled(False)
            self.save_button.setEnabled(True)
            self.status.setText(
                "All facial samples captured. You can now save enrollment."
            )

    def save_enrollment(self):
        student = self.validate_student_information()

        if student is None:
            return

        if len(self.captured_embeddings) < REQUIRED_SAMPLES:
            QMessageBox.warning(
                self,
                "More Samples Required",
                f"Capture {REQUIRED_SAMPLES} facial samples before saving."
            )
            return

        try:
            existing_student = get_student(
                student["student_id"]
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Database Error",
                f"Could not check existing enrollment.\n\n{error}"
            )
            return

        if existing_student is not None:
            answer = QMessageBox.question(
                self,
                "Student Already Enrolled",
                "This student already has enrollment data. \n\nReplace the existing facial embeddings?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if answer != QMessageBox.StandardButton.Yes:
                return

        try:
            save_student_embedding(
                student["student_id"],
                student["class_number"],
                student["section"],
                self.captured_embeddings,
                student["name"]
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                "Enrollment Error",
                f"Could not save enrollment.\n\n{error}"
            )

            self.status.setText(
                "Enrollment could not be saved."
            )

            return

        self.status.setText(
            f"✓ {student['name']} successfully enrolled.\n"
            f"{len(self.captured_embeddings)} facial embeddings saved."
        )

        self.status.setStyleSheet(
            f"""
            background: {SUCCESS_LIGHT};
            color: {SUCCESS};
            border: 1px solid #9BD6B6;
            border-radius: 12px;
            padding: 12px;
            font-size: 12px;
            font-weight: 600;
            """
        )

        QMessageBox.information(
            self,
            "Enrollment Complete",
            f"{student['name']} has been successfully enrolled."
        )

        self.clear_enrollment_form()

    def clear_enrollment_form(self):
        self.captured_embeddings = []
        self.progress.setValue(0)
        self.capture_button.setEnabled(False)
        self.save_button.setEnabled(False)
        self.start_button.setEnabled(True)

        self.name_input.clear()
        self.student_id_input.clear()
        self.class_input.clear()
        self.section_input.clear()

        self.stop_camera()

        self.status.setStyleSheet(
            f"""
            background: white;
            color: {MUTED};
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 12px;
            font-size: 12px;
            """
        )

        self.status.setText(
            "Enter student information and start the camera."
        )

    def stop_camera(self):
        self.timer.stop()

        if self.camera is not None:
            self.camera.release()
            self.camera = None

        self.current_frame = None
        self.current_face = None
        self.last_faces = []
        self.last_valid_face = None

        self.camera_view.clear()
        self.camera_view.setText(
            "Camera is not active"
        )

    def closeEvent(self, event):
        self.stop_camera()

        if self.returning_to_previous:
            event.accept()
            return

        if self.previous_window is not None:
            self.previous_window.show()
            self.previous_window.raise_()
            self.previous_window.activateWindow()

        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = EnrollmentWindow()
    window.show()

    sys.exit(app.exec())
