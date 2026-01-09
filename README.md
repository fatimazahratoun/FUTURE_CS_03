# 🔐 Secure File Sharing System

A secure file sharing web application with AES-256 encryption, built with Python Flask.

## ✨ Features

- ✅ **AES-256-GCM Encryption** - Military-grade encryption for all files
- ✅ **Three Download Options** - Auto-decrypt, encrypted file + key, or offline decryption
- ✅ **Per-File Unique Keys** - Each file gets its own encryption key
- ✅ **Separate Key Storage** - Keys stored separately from encrypted files
- ✅ **Modern Web Interface** - Responsive design with real-time feedback
- ✅ **Security Overview** - Detailed security documentation and implementation

## 🛠️ Technologies

- **Backend:** Python 3.12 + Flask
- **Encryption:** PyCryptodome (AES-256-GCM)
- **Frontend:** HTML5, CSS3, JavaScript
- **Database:** Filesystem-based storage
- **Security:** HTTPS-ready, input validation, secure key management

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/yourusername/secure-file-sharing.git
cd secure-file-sharing

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt