# face_recognition_for_work
# FaceRecognition_VER2

![Python](https://img.shields.io/badge/Python-3.13-blue)
![OpenCV](https://img.shields.io/badge/OpenCV-4.10-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview
`FaceRecognition_VER2`는 웹캠을 이용한 얼굴 인식 애플리케이션으로, 사용자를 인증하고 로그를 기록합니다. Python과 OpenCV를 기반으로 개발되었으며, `.exe`로 배포 가능합니다.

## Features
- **얼굴 인식**: 등록된 얼굴을 웹캠으로 인식.
- **로그 기록**: 인증 시 `verified_logs`에 시간과 이름 기록.
- **GUI**: PySide6로 간단한 인터페이스 제공.
- **배포**: PyInstaller로 단일 `.exe` 파일 생성.

## Requirements
- Python 3.13+
- OpenCV (`opencv-python`)
- PySide6
- PyInstaller (배포용)
