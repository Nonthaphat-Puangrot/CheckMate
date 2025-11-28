# CheckMate

An intelligent attendance checking system that combines facial recognition and fingerprint scanning for secure and automated student identification.

![CheckMate Logo](Resource/checkmate_new_dark_logo.png)

## Overview

CheckMate is a dual-factor biometric attendance system designed to streamline the attendance process in educational institutions. The system consists of two main components:

1. **CheckMate Device** - Raspberry Pi-based hardware device that captures facial images and fingerprint data
2. **Recognition Server** - Python server that processes biometric data and manages attendance records

## Features

- **Dual Authentication**: Combines facial recognition and fingerprint scanning for enhanced security
- **Real-time Face Detection**: Uses OpenCV and face_recognition library for accurate face detection
- **Fingerprint Integration**: Supports Adafruit fingerprint sensors via serial communication
- **Cloud Integration**: Firebase Realtime Database and Storage for data synchronization
- **Attendance Logging**: Automatic CSV generation with date-wise attendance records
- **User Interface**: Tkinter-based GUI for device operation
- **Real-time Processing**: Multi-threaded architecture for responsive performance

## Technology Stack

### Hardware
- **Raspberry Pi 4** - Main processing unit with serial UART support
- **AS608 (JM-101B) Fingerprint Scanner** - Optical fingerprint sensor module
- **USB Webcam** - For facial image capture

### Software
- **Python 3.x**
- **OpenCV** - Face detection and image processing
- **face_recognition** - Facial recognition powered by dlib
- **Firebase Admin SDK** - Cloud database and storage
- **Adafruit Fingerprint Library** - AS608 fingerprint sensor communication
- **Tkinter** - GUI interface for device control
- **NumPy** - Numerical operations
- **Pillow (PIL)** - Image manipulation

## Project Structure

```
CheckMate/
├── CheckPlate_Device.py      # Main device controller
├── Recognition_Server.py      # Face recognition server
├── face_detection.py          # Face detection module
├── Encoder.py                 # Face encoding generator
├── MainFunc.py                # Core utility functions
├── serviceAccountKey.json     # Firebase credentials (NOT included)
├── Photo/                     # User face images (NOT included)
├── Resource/                  # UI assets and logos
├── output/                    # Attendance CSV files (NOT included)
└── requirements.txt           # Python dependencies
```

## Installation

### Prerequisites

1. **Python 3.7+** installed on your system
2. **Firebase Project** with Realtime Database and Storage enabled
3. **Raspberry Pi** with camera and fingerprint sensor connected

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/CheckMate.git
   cd CheckMate
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Firebase**
   - Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
   - Generate a service account key
   - Download and save it as `serviceAccountKey.json` in the project root
   - Update the Firebase URLs in the code files:
     - `databaseURL`: Your Firebase Realtime Database URL
     - `storageBucket`: Your Firebase Storage bucket name

4. **Hardware Setup**
   - Connect the Adafruit fingerprint sensor to Raspberry Pi UART (`/dev/ttyS0`)
   - Connect USB or CSI camera module
   - Ensure proper power supply for all components

5. **Directory Setup**
   ```bash
   mkdir Photo output
   ```

## Usage

### Device Operation (Raspberry Pi)

Run the CheckMate device interface:
```bash
python CheckPlate_Device.py
```

The device will:
1. Display the main interface
2. Wait for fingerprint scan
3. Capture facial image
4. Upload data to Firebase for processing

### Recognition Server

Run the facial recognition server:
```bash
python Recognition_Server.py
```

The server will:
1. Monitor Firebase for new check-in requests
2. Perform facial recognition matching
3. Log attendance with timestamps
4. Store records in CSV format

### Encoding New Faces

To add new users to the system:
```bash
python Encoder.py
```

This will:
1. Fetch new images from Firebase Storage (`Queue_List/` folder)
2. Generate face encodings
3. Update the encoded database

## Privacy & Security

**Important**: This repository does NOT include:
- `serviceAccountKey.json` - Firebase credentials
- `Photo/` - Personal facial images
- `output/` - Attendance records with personal data
- `*.p` - Encoded face data files

Make sure to:
- Keep your Firebase credentials secure
- Never commit personal images or attendance data
- Use environment variables for sensitive configuration
- Regularly backup your data securely

## Attendance Data

Attendance records are saved in CSV format:
- Location: `output/` directory
- Format: `DD-MM-YYYY.csv` or `YYYY-MM-DD.csv`
- Fields: Username, Timestamp

## Configuration

Update the following paths in the Python files to match your setup:
- Firebase credentials path
- Photo directory location
- Output directory for CSV files
- Serial port for fingerprint sensor (default: `/dev/ttyS0`)

## Contributing

This is a PBL (Project-Based Learning) project. Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests

## License

This project is created as an educational project. Please respect privacy when using biometric data.

## Authors

**Nonthaphat Puangrot**
- GitHub: [@Nonthaphat-Puangrot](https://github.com/Nonthaphat-Puangrot)
Created as a **PBL (Project-Based Learning)** project at **KOSEN-KMITL** for developing an advanced biometric attendance management system.

## Acknowledgments

- OpenCV and face_recognition library developers
- Adafruit for fingerprint sensor libraries
- Firebase for backend infrastructure

