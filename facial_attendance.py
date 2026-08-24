import sys
import time
import logging
from datetime import datetime

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
    QMessageBox,
)

from insightface.app import FaceAnalysis

from database import (
    get_students,
    mark_attendance,
    mark_absent_students_if_due
)


CAMERA_INDEX = 0
MATCH_THRESHOLD = 0.45
PROCESS_EVERY_N_FRAMES = 4
MIN_FACE_SIZE = 80
RECOGNITION_COOLDOWN_SECONDS = 15
ABSENCE_CHECK_INTERVAL_MS = 60 * 1000
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
DETECTION_SIZE = (640, 640)

BLUE = "#247EAE"
BLUE_DARK = "#1E547A"
BLUE_LIGHT = "#EAF2F8"
WHITE = "#F8FAFC"
TEXT = "#1F2F43"
BORDER = "#79B9DE"
MUTED = "#65788A"
PAGE_BG = "#DDEAF4"
CARD_BG = "#F8FAFC"
SUCCESS = "#1F8A5B"
SUCCESS_LIGHT = "#E8F6EF"
ERROR = "#C0392B"
ERROR_LIGHT = "#FDEDEC"
WARNING = "#B7791F"
WARNING_LIGHT = "#FFF7E6"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


class FaceMatcher:

    def __init__(
        self,
        threshold=MATCH_THRESHOLD
    ):
        self.threshold = threshold
        self.students = []

    @staticmethod
    def normalize_embedding(
        embedding
    ):

        if embedding is None:
            return None

        try:

            embedding = np.asarray(
                embedding,
                dtype=np.float32
            ).flatten()

            if embedding.size == 0:
                return None

            if not np.all(
                np.isfinite(embedding)
            ):
                return None

            norm = np.linalg.norm(
                embedding
            )

            if norm <= 0:
                return None

            return embedding / norm

        except Exception as error:

            logger.warning(
                "Invalid embedding ignored: %s",
                error
            )

            return None

    def load_students(self):

        self.students = []

        try:

            database_students = get_students()

        except Exception as error:

            logger.exception(
                "Could not load students from database."
            )

            raise RuntimeError(
                f"Could not load enrolled students: {error}"
            )

        valid_student_count = 0
        valid_embedding_count = 0

        for student in database_students:

            student_id = student.get(
                "student_id",
                ""
            )

            raw_embeddings = student.get(
                "embeddings",
                []
            )

            if not isinstance(
                raw_embeddings,
                list
            ):

                logger.warning(
                    "Skipping invalid embedding data for student %s",
                    student_id
                )

                continue

            normalized_embeddings = []

            for embedding in raw_embeddings:

                normalized = (
                    self.normalize_embedding(
                        embedding
                    )
                )

                if normalized is not None:

                    normalized_embeddings.append(
                        normalized
                    )

                    valid_embedding_count += 1

            if not normalized_embeddings:

                logger.warning(
                    "Student %s has no valid embeddings.",
                    student_id
                )

                continue

            self.students.append({
                "student_id": student_id,
                "name": student.get(
                    "name",
                    ""
                ),
                "class_number": student.get(
                    "class_number",
                    ""
                ),
                "section": student.get(
                    "section",
                    ""
                ),
                "embeddings": normalized_embeddings,
            })

            valid_student_count += 1

        logger.info(
            "Loaded %s enrolled students with %s valid embeddings.",
            valid_student_count,
            valid_embedding_count
        )

        return (
            valid_student_count,
            valid_embedding_count
        )

    def match(
        self,
        query_embedding
    ):

        query_embedding = (
            self.normalize_embedding(
                query_embedding
            )
        )

        if query_embedding is None:

            return None, 0.0

        best_student = None
        best_similarity = -1.0

        for student in self.students:

            for stored_embedding in student[
                "embeddings"
            ]:

                similarity = float(
                    np.dot(
                        query_embedding,
                        stored_embedding
                    )
                )

                if similarity > best_similarity:

                    best_similarity = similarity
                    best_student = student

        if (
            best_student is not None
            and best_similarity >= self.threshold
        ):

            return (
                best_student,
                best_similarity
            )

        return (
            None,
            max(
                best_similarity,
                0.0
            )
        )


class FacialAttendanceWindow(
    QWidget
):

    def __init__(
        self,
        back_callback=None,
        source_class=None
    ):

        super().__init__()

        self.back_callback = back_callback
        self.source_class = source_class

        self.setWindowTitle(
            "SOS Hermann Gmeiner School Gandaki - Facial Attendance"
        )

        self.resize(
            1280,
            800
        )

        self.face_app = None
        self.camera = None
        self.frame_count = 0

        self.matcher = FaceMatcher(
            threshold=MATCH_THRESHOLD
        )

        self.recent_recognitions = {}
        self.current_results = []

        self.timer = QTimer()

        self.timer.timeout.connect(
            self.update_camera
        )
        self.absence_timer = QTimer()
        self.absence_timer.timeout.connect(
            self.check_absence_status
        )
        self.absence_timer.start(
            ABSENCE_CHECK_INTERVAL_MS
        )

        self.setup_ui()

    def setup_ui(self):

        self.setStyleSheet(
            f"""
            QWidget {{
                background: {PAGE_BG};
                color: {TEXT};
                font-family: "Segoe UI";
            }}

            QPushButton {{
                background: {BLUE};
                color: white;
                border: 1px solid #1D6F9C;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background: {BLUE_DARK};
            }}

            QPushButton:disabled {{
                background: #B8C7D3;
                color: #E9EEF2;
                border-color: #B8C7D3;
            }}
            """
        )

        main = QVBoxLayout()

        main.setContentsMargins(
            0,
            0,
            0,
            0
        )

        main.setSpacing(0)

        header = QFrame()

        header.setFixedHeight(
            95
        )

        header.setStyleSheet(
            f"""
            background: {BLUE};
            border-bottom: 1px solid #8BC7E7;
            """
        )

        header_layout = QHBoxLayout(
            header
        )

        header_layout.setContentsMargins(
            32,
            15,
            32,
            15
        )

        self.back_button = QPushButton(
            "← Back to Class Display"
        )

        self.back_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.back_button.setStyleSheet(
            f"""
            QPushButton {{
                background: {BLUE_DARK};
                color: white;
                border: 1px solid #8BC7E7;
                border-radius: 8px;
                padding: 8px 18px;
                font-size: 14px;
                font-weight: 600;
            }}

            QPushButton:hover {{
                background: #153B56;
            }}
            """
        )

        self.back_button.clicked.connect(
            self.on_back_clicked
        )

        header_layout.addWidget(
            self.back_button
        )

        header_layout.addStretch()

        self.enrollment_badge = QLabel(
            "FACE ATTENDANCE"
        )

        self.enrollment_badge.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.enrollment_badge.setFixedSize(
            180,
            36
        )

        self.enrollment_badge.setStyleSheet(
            """
            color: white;
            background: #247EAE;
            border: 1px solid #6B96BB;
            border-radius: 18px;
            font-size: 11px;
            font-weight: 600;
            """
        )

        header_layout.addWidget(
            self.enrollment_badge
        )

        main.addWidget(
            header
        )

        content = QHBoxLayout()

        content.setContentsMargins(
            25,
            25,
            25,
            25
        )

        content.setSpacing(
            20
        )

        left_panel = (
            self.create_status_panel()
        )

        right_panel = (
            self.create_camera_panel()
        )

        content.addWidget(
            left_panel
        )

        content.addWidget(
            right_panel,
            1
        )

        main.addLayout(
            content
        )

        footer = QLabel(
            "SOS Hermann Gmeiner School Gandaki • "
            "Facial Biometric Attendance System"
        )

        footer.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        footer.setFixedHeight(
            30
        )

        footer.setStyleSheet(
            f"""
            background: {BLUE_LIGHT};
            color: {BLUE};
            font-size: 11px;
            """
        )

        main.addWidget(
            footer
        )

        self.setLayout(
            main
        )

    def check_absence_status(self):

        try:

            result = (
                mark_absent_students_if_due()
            )

            if result.get("marked"):
                logger.info(
                    "Daily absence check completed: %s",
                    result
                )

        except Exception:

            logger.exception(
                "Daily absence check failed."
            )

    def on_back_clicked(self):

        self.stop_camera()

        if self.back_callback:

            self.back_callback(
                self.source_class
            )

        else:

            self.close()

    def create_status_panel(
        self
    ):

        panel = QFrame()

        panel.setFixedWidth(
            370
        )

        panel.setStyleSheet(
            f"""
            QFrame {{
                background: {BLUE_LIGHT};
                border: 1px solid {BORDER};
                border-radius: 16px;
            }}
            """
        )

        layout = QVBoxLayout(
            panel
        )

        layout.setContentsMargins(
            22,
            22,
            22,
            22
        )

        layout.setSpacing(
            12
        )

        heading = QLabel(
            "Facial Attendance"
        )

        heading.setStyleSheet(
            f"""
            color: {BLUE_DARK};
            font-size: 21px;
            font-weight: 700;
            border: none;
            """
        )

        layout.addWidget(
            heading
        )

        description = QLabel(
            "Start the camera and allow students to look directly "
            "at it. Recognized students will automatically be "
            "marked present."
        )

        description.setWordWrap(
            True
        )

        description.setStyleSheet(
            f"""
            color: {BLUE};
            font-size: 12px;
            border: none;
            """
        )

        layout.addWidget(
            description
        )

        self.start_button = QPushButton(
            "Start Attendance Camera"
        )

        self.start_button.clicked.connect(
            self.start_camera
        )

        layout.addWidget(
            self.start_button
        )

        self.stop_button = QPushButton(
            "Stop Camera"
        )

        self.stop_button.setEnabled(
            False
        )

        self.stop_button.clicked.connect(
            self.stop_camera
        )

        self.stop_button.setStyleSheet(
            """
            QPushButton {
                background: #6C7A89;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }

            QPushButton:hover {
                background: #4F5B66;
            }

            QPushButton:disabled {
                background: #B8C7D3;
            }
            """
        )

        layout.addWidget(
            self.stop_button
        )

        info_title = QLabel(
            "RECOGNITION STATUS"
        )

        info_title.setStyleSheet(
            f"""
            color: {BLUE_DARK};
            font-size: 11px;
            font-weight: 700;
            border: none;
            margin-top: 8px;
            """
        )

        layout.addWidget(
            info_title
        )

        self.status_card = QFrame()

        self.status_card.setStyleSheet(
            f"""
            background: white;
            border: 1px solid {BORDER};
            border-radius: 12px;
            """
        )

        card_layout = QVBoxLayout(
            self.status_card
        )

        card_layout.setContentsMargins(
            16,
            16,
            16,
            16
        )

        card_layout.setSpacing(
            8
        )

        self.recognition_title = QLabel(
            "WAITING FOR CAMERA"
        )

        self.recognition_title.setStyleSheet(
            f"""
            color: {BLUE};
            font-size: 16px;
            font-weight: 700;
            border: none;
            """
        )

        self.recognition_message = QLabel(
            "Start the camera to begin facial attendance."
        )

        self.recognition_message.setWordWrap(
            True
        )

        self.recognition_message.setStyleSheet(
            f"""
            color: {MUTED};
            font-size: 12px;
            border: none;
            """
        )

        self.student_name_label = QLabel(
            "Name: —"
        )

        self.student_id_label = QLabel(
            "Student ID: —"
        )

        self.class_label = QLabel(
            "Class: —"
        )

        self.section_label = QLabel(
            "Section: —"
        )

        card_layout.addWidget(
            self.recognition_title
        )

        card_layout.addWidget(
            self.recognition_message
        )

        for label in [
            self.student_name_label,
            self.student_id_label,
            self.class_label,
            self.section_label,
        ]:

            label.setStyleSheet(
                f"""
                color: {TEXT};
                font-size: 13px;
                border: none;
                """
            )

            card_layout.addWidget(
                label
            )

        layout.addWidget(
            self.status_card
        )

        self.attendance_status = QLabel(
            "CAMERA NOT STARTED"
        )

        self.attendance_status.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.attendance_status.setWordWrap(
            True
        )

        self.attendance_status.setMinimumHeight(
            70
        )

        self.attendance_status.setStyleSheet(
            f"""
            background: white;
            color: {MUTED};
            border: 1px solid {BORDER};
            border-radius: 12px;
            font-size: 13px;
            font-weight: 700;
            padding: 10px;
            """
        )

        layout.addWidget(
            self.attendance_status
        )

        self.database_info = QLabel(
            "Enrolled students: not loaded"
        )

        self.database_info.setWordWrap(
            True
        )

        self.database_info.setStyleSheet(
            f"""
            background: {BLUE};
            color: white;
            border-radius: 10px;
            padding: 14px;
            font-size: 12px;
            """
        )

        layout.addWidget(
            self.database_info
        )

        layout.addStretch()

        return panel

    def create_camera_panel(
        self
    ):

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

        layout = QVBoxLayout(
            panel
        )

        layout.setContentsMargins(
            18,
            18,
            18,
            18
        )

        title = QLabel(
            "Live Camera Recognition"
        )

        title.setStyleSheet(
            f"""
            color: {BLUE_DARK};
            font-size: 19px;
            font-weight: 700;
            border: none;
            """
        )

        layout.addWidget(
            title
        )

        self.camera_view = QLabel(
            "Camera is not active"
        )

        self.camera_view.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.camera_view.setMinimumSize(
            700,
            520
        )

        self.camera_view.setStyleSheet(
            """
            background: #0B243D;
            color: white;
            border-radius: 12px;
            font-size: 16px;
            """
        )

        layout.addWidget(
            self.camera_view
        )

        note = QLabel(
            f"Recognition runs every "
            f"{PROCESS_EVERY_N_FRAMES} frames • "
            f"Match threshold: "
            f"{MATCH_THRESHOLD:.2f}"
        )

        note.setStyleSheet(
            f"""
            color: {BLUE};
            font-size: 11px;
            border: none;
            padding: 5px;
            """
        )

        layout.addWidget(
            note
        )

        return panel

    def initialize_face_system(
        self
    ):

        try:

            if self.face_app is None:

                self.set_waiting_status(
                    "LOADING MODEL",
                    "Loading InsightFace buffalo_l..."
                )

                QApplication.processEvents()

                self.face_app = FaceAnalysis(
                    name="buffalo_l",
                    providers=[
                        "CPUExecutionProvider"
                    ]
                )

                self.face_app.prepare(
                    ctx_id=-1,
                    det_size=DETECTION_SIZE
                )

                student_count, embedding_count = (
                    self.matcher.load_students()
                )

                self.database_info.setText(
                    f"Enrolled students: {student_count}\n"
                    f"Valid facial samples: {embedding_count}"
                )

                if student_count == 0:

                    QMessageBox.warning(
                        self,
                        "No Enrolled Students",
                        "No valid facial embeddings were found.\n\n"
                        "Run the enrollment system first."
                    )

                    return False

            return True

        except Exception as error:

            logger.exception(
                "Attendance system initialization failed."
            )

            QMessageBox.critical(
                self,
                "Initialization Error",
                "The facial attendance system could not start.\n\n"
                f"{error}"
            )

            return False

    def start_camera(
        self
    ):

        if not self.initialize_face_system():

            self.reset_ui_after_start_failure()

            return

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

        if not self.camera.isOpened():

            QMessageBox.critical(
                self,
                "Camera Error",
                "The camera could not be opened."
            )

            self.camera.release()

            self.camera = None

            return

        self.frame_count = 0

        self.current_results = []

        self.recent_recognitions.clear()

        self.start_button.setEnabled(
            False
        )

        self.stop_button.setEnabled(
            True
        )

        self.set_waiting_status(
            "CAMERA ACTIVE",
            "Waiting for a student to appear..."
        )

        self.attendance_status.setText(
            "READY FOR FACIAL ATTENDANCE"
        )

        self.attendance_status.setStyleSheet(
            f"""
            background: white;
            color: {BLUE};
            border: 1px solid {BORDER};
            border-radius: 12px;
            font-size: 13px;
            font-weight: 700;
            padding: 10px;
            """
        )

        self.timer.start(
            30
        )

    def reset_ui_after_start_failure(
        self
    ):

        self.start_button.setEnabled(
            True
        )

        self.stop_button.setEnabled(
            False
        )

    def stop_camera(
        self
    ):

        self.timer.stop()

        if self.camera is not None:

            self.camera.release()

            self.camera = None

        self.camera_view.clear()

        self.camera_view.setText(
            "Camera is not active"
        )

        self.start_button.setEnabled(
            True
        )

        self.stop_button.setEnabled(
            False
        )

        self.set_waiting_status(
            "CAMERA STOPPED",
            "Start the camera to continue facial attendance."
        )

        self.attendance_status.setText(
            "ATTENDANCE CAMERA STOPPED"
        )

    def update_camera(
        self
    ):

        if self.camera is None:

            return

        success, frame = (
            self.camera.read()
        )

        if not success:

            logger.warning(
                "Camera frame could not be read."
            )

            return

        self.frame_count += 1

        if (
            self.frame_count
            % PROCESS_EVERY_N_FRAMES
            == 0
        ):

            self.process_recognition(
                frame
            )

        display = frame.copy()

        self.draw_recognition_results(
            display
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
            QImage.Format.Format_RGB888,
        )

        pixmap = QPixmap.fromImage(
            image
        )

        self.camera_view.setPixmap(
            pixmap.scaled(
                self.camera_view.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def process_recognition(
        self,
        frame
    ):

        try:

            faces = self.face_app.get(
                frame
            )

        except Exception:

            logger.exception(
                "Face detection failed."
            )

            self.set_unknown_status(
                "Recognition engine error."
            )

            return

        self.current_results = []

        if not faces:

            self.set_waiting_status(
                "SEARCHING FOR FACE",
                "No face detected."
            )

            return

        now = time.monotonic()

        for face in faces:

            try:

                x1, y1, x2, y2 = map(
                    int,
                    face.bbox
                )

                face_width = (
                    x2 - x1
                )

                face_height = (
                    y2 - y1
                )

                if (
                    face_width < MIN_FACE_SIZE
                    or face_height < MIN_FACE_SIZE
                ):

                    self.current_results.append({
                        "bbox": (
                            x1,
                            y1,
                            x2,
                            y2
                        ),
                        "label": "MOVE CLOSER",
                        "recognized": False,
                    })

                    continue

                embedding = getattr(
                    face,
                    "embedding",
                    None
                )

                if embedding is None:

                    self.current_results.append({
                        "bbox": (
                            x1,
                            y1,
                            x2,
                            y2
                        ),
                        "label": "NO EMBEDDING",
                        "recognized": False,
                    })

                    continue

                student, similarity = (
                    self.matcher.match(
                        embedding
                    )
                )

                if student is None:

                    self.current_results.append({
                        "bbox": (
                            x1,
                            y1,
                            x2,
                            y2
                        ),
                        "label": "UNKNOWN",
                        "recognized": False,
                        "similarity": similarity,
                    })

                    self.set_unknown_status(
                        "No matching student found."
                    )

                    continue

                student_id = student[
                    "student_id"
                ]

                last_seen = (
                    self.recent_recognitions.get(
                        student_id,
                        0
                    )
                )

                if (
                    now - last_seen
                    >= RECOGNITION_COOLDOWN_SECONDS
                ):

                    self.recent_recognitions[
                        student_id
                    ] = now

                    self.handle_recognized_student(
                        student,
                        similarity
                    )

                name = (
                    student.get(
                        "name",
                        ""
                    ).strip()
                    or "Student"
                )

                self.current_results.append({
                    "bbox": (
                        x1,
                        y1,
                        x2,
                        y2
                    ),
                    "label": name,
                    "recognized": True,
                    "similarity": similarity,
                })

            except Exception:

                logger.exception(
                    "Error while processing a detected face."
                )

                continue

        self.cleanup_recent_recognitions(
            now
        )

    def handle_recognized_student(
            self,
            student,
            similarity
    ):

        try:

            recorded, attendance_date, attendance_time = (
                mark_attendance(
                    student,
                    similarity
                )
            )

            if attendance_time == "HOLIDAY":
                self.recognition_title.setText(
                    "HOLIDAY"
                )

                self.recognition_message.setText(
                    "Attendance is not allowed today."
                )

                self.attendance_status.setText(
                    "NO ATTENDANCE ON HOLIDAY"
                )

                self.set_error_card()

                return

        except Exception:

            logger.exception(
                "Could not save attendance."
            )

            self.recognition_title.setText(
                "DATABASE ERROR"
            )

            self.recognition_message.setText(
                "Student recognized, but attendance could not be saved."
            )

            self.attendance_status.setText(
                "ATTENDANCE NOT RECORDED"
            )

            self.set_error_card()

            return

        except Exception:

            logger.exception(
                "Could not save attendance."
            )

            self.recognition_title.setText(
                "DATABASE ERROR"
            )

            self.recognition_message.setText(
                "Student recognized, but attendance could not be saved."
            )

            self.attendance_status.setText(
                "ATTENDANCE NOT RECORDED"
            )

            self.set_error_card()

            return

        # Get student information

        name = str(
            student.get(
                "name",
                ""
            )
        ).strip()

        student_id = str(
            student.get(
                "student_id",
                ""
            )
        ).strip()

        class_number = str(
            student.get(
                "class_number",
                ""
            )
        ).strip()

        section = str(
            student.get(
                "section",
                ""
            )
        ).strip()

        # Update student information on the GUI

        self.student_name_label.setText(
            f"Name: {name}"
        )

        self.student_id_label.setText(
            f"Student ID: {student_id}"
        )

        self.class_label.setText(
            f"Class: {class_number}"
        )

        self.section_label.setText(
            f"Section: {section}"
        )

        # Attendance was successfully inserted

        if recorded:

            self.recognition_title.setText(
                "FACE RECOGNIZED"
            )

            self.recognition_message.setText(
                f"Similarity: {similarity:.3f}"
            )

            self.attendance_status.setText(
                "ATTENDANCE RECORDED ✓\n"
                f"{attendance_date} • {attendance_time}"
            )

            self.set_success_card()


        # Attendance already existed for today

        else:

            self.recognition_title.setText(
                "ALREADY PRESENT"
            )

            self.recognition_message.setText(
                f"Similarity: {similarity:.3f}"
            )

            self.attendance_status.setText(
                "ATTENDANCE ALREADY RECORDED TODAY\n"
                f"{attendance_date} • {attendance_time}"
            )

            self.set_success_card()

    def draw_recognition_results(
        self,
        frame
    ):

        for result in self.current_results:

            x1, y1, x2, y2 = result[
                "bbox"
            ]

            recognized = result.get(
                "recognized",
                False
            )

            if recognized:

                color = (
                    46,
                    204,
                    113
                )

            else:

                color = (
                    52,
                    152,
                    219
                )

            label = result.get(
                "label",
                "UNKNOWN"
            )

            similarity = result.get(
                "similarity"
            )

            if (
                recognized
                and similarity is not None
            ):

                label = (
                    f"{label} "
                    f"({similarity:.2f})"
                )

            cv2.rectangle(
                frame,
                (
                    x1,
                    y1
                ),
                (
                    x2,
                    y2
                ),
                color,
                2
            )

            text_y = max(
                30,
                y1 - 10
            )

            cv2.putText(
                frame,
                label,
                (
                    x1,
                    text_y
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                color,
                2,
                cv2.LINE_AA,
            )

    def clear_student_information(
        self
    ):

        self.student_name_label.setText(
            "Name: —"
        )

        self.student_id_label.setText(
            "Student ID: —"
        )

        self.class_label.setText(
            "Class: —"
        )

        self.section_label.setText(
            "Section: —"
        )

    def set_waiting_status(
        self,
        title,
        message
    ):

        self.recognition_title.setText(
            title
        )

        self.recognition_message.setText(
            message
        )

        self.recognition_title.setStyleSheet(
            f"""
            color: {BLUE};
            font-size: 16px;
            font-weight: 700;
            border: none;
            """
        )

        self.status_card.setStyleSheet(
            f"""
            background: white;
            border: 1px solid {BORDER};
            border-radius: 12px;
            """
        )

    def set_unknown_status(
        self,
        message
    ):

        self.recognition_title.setText(
            "FACE NOT RECOGNIZED"
        )

        self.recognition_message.setText(
            message
        )

        self.clear_student_information()

        self.recognition_title.setStyleSheet(
            f"""
            color: {ERROR};
            font-size: 16px;
            font-weight: 700;
            border: none;
            """
        )

        self.status_card.setStyleSheet(
            f"""
            background: {ERROR_LIGHT};
            border: 1px solid #E6A39B;
            border-radius: 12px;
            """
        )

        self.attendance_status.setText(
            "NO ATTENDANCE RECORDED"
        )

    def set_success_card(
        self
    ):

        self.recognition_title.setStyleSheet(
            f"""
            color: {SUCCESS};
            font-size: 16px;
            font-weight: 700;
            border: none;
            """
        )

        self.status_card.setStyleSheet(
            f"""
            background: {SUCCESS_LIGHT};
            border: 1px solid #9BD6B6;
            border-radius: 12px;
            """
        )

        self.attendance_status.setStyleSheet(
            f"""
            background: {SUCCESS_LIGHT};
            color: {SUCCESS};
            border: 1px solid #9BD6B6;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 700;
            padding: 10px;
            """
        )

    def set_error_card(
        self
    ):

        self.recognition_title.setStyleSheet(
            f"""
            color: {ERROR};
            font-size: 16px;
            font-weight: 700;
            border: none;
            """
        )

        self.status_card.setStyleSheet(
            f"""
            background: {ERROR_LIGHT};
            border: 1px solid #E6A39B;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 700;
            padding: 10px;
            """
        )

        self.attendance_status.setStyleSheet(
            f"""
            background: {ERROR_LIGHT};
            color: {ERROR};
            border: 1px solid #E6A39B;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 700;
            padding: 10px;
            """
        )

    def cleanup_recent_recognitions(
        self,
        now
    ):

        expiry = (
            RECOGNITION_COOLDOWN_SECONDS
            * 3
        )

        expired = [
            student_id
            for student_id, timestamp
            in self.recent_recognitions.items()
            if now - timestamp > expiry
        ]

        for student_id in expired:

            del self.recent_recognitions[
                student_id
            ]

    def closeEvent(self, event):

        self.stop_camera()

        if hasattr(
                self,
                "absence_timer"
        ):
            self.absence_timer.stop()

        event.accept()


if __name__ == "__main__":

    app = QApplication(
        sys.argv
    )

    app.setStyle(
        "Fusion"
    )

    window = FacialAttendanceWindow()

    window.show()

    sys.exit(
        app.exec()
    )
