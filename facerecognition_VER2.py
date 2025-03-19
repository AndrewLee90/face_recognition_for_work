import os
import cv2
import numpy as np
from datetime import datetime
import sys
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget,
    QPushButton, QHBoxLayout, QMessageBox, QDialog, QLineEdit
)

class Thread(QThread):
    updateFrame = Signal(QImage)
    recognizedUser = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status = False
        self.cap = None

        # PyInstaller 실행 시 임시 경로 설정
        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.cascade_file = os.path.join(self.base_dir, "haarcascade_frontalface_default.xml")
        print(f"Haarcascade 파일 경로: {self.cascade_file}")
        
        # 파일 존재 여부 확인
        if not os.path.exists(self.cascade_file):
            raise FileNotFoundError(f"Haarcascade 파일을 찾을 수 없습니다: {self.cascade_file}")
        if not os.path.isfile(self.cascade_file):
            raise FileNotFoundError(f"Haarcascade 경로는 파일이 아님: {self.cascade_file}")

        self.face_cascade = cv2.CascadeClassifier()
        if not self.face_cascade.load(self.cascade_file):
            raise ValueError(f"Haarcascade 파일 로드 실패: {self.cascade_file}. 파일이 손상되었거나 형식이 잘못되었을 수 있습니다.")

        self.data_path = os.path.join(self.base_dir, "known_faces")
        print(f"known_faces 경로: {self.data_path}")
        self.known_faces = []
        self.known_names = []

    def load_known_faces(self):
        print(f"Loading known faces from: {self.data_path}")
        if not os.path.exists(self.data_path):
            print(f"오류: {self.data_path} 폴더가 존재하지 않습니다.")
            return
        for filename in os.listdir(self.data_path):
            print(f"파일 발견: {filename}")
            if filename.lower().endswith(".jpg"):
                img_path = os.path.join(self.data_path, filename)
                print(f"이미지 경로: {img_path}")
                img = cv2.imread(img_path, cv2.IMREAD_COLOR)
                if img is None:
                    print(f"이미지 로드 실패: {img_path}")
                    continue
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                self.known_faces.append(gray)
                self.known_names.append(filename.split(".")[0])
                print(f"로드된 파일: {filename}")
        print(f"총 로드된 얼굴 수: {len(self.known_faces)}")

    def run(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("웹캠을 열 수 없습니다.")
            return
        while self.status:
            ret, frame = self.cap.read()
            if not ret:
                print("프레임 읽기 실패")
                continue

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5)
            print(f"감지된 얼굴 수: {len(faces)}")

            for (x, y, w, h) in faces:
                face = gray_frame[y:y + h, x:x + w]
                name = self.recognize_face(face)
                print(f"인식된 이름: {name}")
                self.recognizedUser.emit(name)
                if name != "Unknown":
                    self.status = False
                break

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = color_frame.shape
            img = QImage(color_frame.data, w, h, ch * w, QImage.Format_RGB888)
            scaled_img = img.scaled(640, 480, Qt.AspectRatioMode.KeepAspectRatio)
            self.updateFrame.emit(scaled_img)

        self.cap.release()

    def recognize_face(self, face):
        if not self.known_faces:
            print("등록된 얼굴 데이터가 없습니다.")
            return "Unknown"
        for known_face, name in zip(self.known_faces, self.known_names):
            try:
                resized_face = cv2.resize(face, (known_face.shape[1], known_face.shape[0]))
                resized_face = cv2.equalizeHist(resized_face)
                known_face = cv2.equalizeHist(known_face)
                result = cv2.matchTemplate(resized_face, known_face, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)
                print(f"유사도: {max_val}")
                if max_val > 0.2:
                    return name
            except Exception as e:
                print(f"얼굴 비교 오류: {e}")
                continue
        return "Unknown"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Check for Work")
        self.resize(800, 600)

        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)

        self.thread = Thread(self)
        self.thread.updateFrame.connect(self.setImage)
        self.thread.recognizedUser.connect(self.handleRecognition)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.startThread)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.label)
        main_layout.addLayout(button_layout)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

        self.initFaceData()
        self.centerWindow()

    def centerWindow(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def initFaceData(self):
        self.thread.load_known_faces()
        self.log_dir = os.path.join(self.thread.base_dir, "verified_logs")
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
            print(f"로그 폴더 생성: {self.log_dir}")

    @Slot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    @Slot(str)
    def handleRecognition(self, name):
        if name != "Unknown":
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setText(f"{name}님 인증되었습니다.")
            msg_box.setWindowTitle("Face Check")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            verified_filename = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            verified_filepath = os.path.join(self.log_dir, verified_filename)
            print(f"로그 파일 경로: {verified_filepath}")
            with open(verified_filepath, "w", encoding="utf-8") as file:
                file.write(f"Name: {name}\nVerified at: {current_time}\n")
            print(f"로그 기록 완료: {verified_filename}")

            self.thread.status = False

    def startThread(self):
        self.thread.status = True
        self.thread.start()

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.resize(300, 150)

        self.layout = QVBoxLayout()
        self.id_label = QLabel("ID:")
        self.id_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.checkLogin)

        self.layout.addWidget(self.id_label)
        self.layout.addWidget(self.id_input)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)

        self.setLayout(self.layout)
        self.authenticated = False
        self.centerWindow()

    def centerWindow(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def checkLogin(self):
        if self.id_input.text() == "admin" and self.password_input.text() == "admin":
            self.authenticated = True
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid ID or Password!")

if __name__ == "__main__":
    app = QApplication([])
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.Accepted and login_dialog.authenticated:
        window = MainWindow()
        window.show()
        app.exec()