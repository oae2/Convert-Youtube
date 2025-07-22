# 🚀 YouTube Converter Pro

<div align="center">

![YouTube Converter Pro](https://img.shields.io/badge/YouTube-Converter-red?style=for-the-badge&logo=youtube)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

**Advanced YouTube Video Processing System with Cyberpunk UI**

*A powerful, feature-rich YouTube video converter with real-time conversion tracking and multiple format support.*

</div>

## ✨ Features

- 🎬 **Multi-Format Support**: MP4, MOV, AVI, MKV, WEBM, MP3
- ⚡ **Quality Selection**: 4K, 2K, 1080p, 720p, 480p, Best Available
- 🎯 **Real-time Progress**: Live conversion tracking with detailed status
- 🎨 **Cyberpunk UI**: Modern terminal-style interface with animations
- 🔒 **Privacy Focused**: Local processing, no data collection
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile
- 🛡️ **Quality Verification**: Shows actual file sizes and formats

## ⚠️ Important Disclaimer

**This tool is for educational and personal use only. Please respect content creators' rights and comply with YouTube's Terms of Service. Do not use this tool for:**

- Commercial purposes
- Copyright infringement
- Redistributing copyrighted content
- Violating YouTube's Terms of Service

**Always ensure you have the right to download and convert the content.**

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/youtube-converter-pro.git
cd youtube-converter-pro
```

### 2. Auto Setup (Recommended)

**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### 3. Manual Installation

```bash
pip install -r requirements.txt
```

### 4. Install FFmpeg

#### Windows (using Chocolatey):
```bash
choco install ffmpeg
```

#### macOS (using Homebrew):
```bash
brew install ffmpeg
```

#### Ubuntu/Debian:
```bash
sudo apt update && sudo apt install ffmpeg
```

### 5. Start the Backend Server

```bash
python backend_server.py
```

The server will start on `http://localhost:5000`

### 6. Open the Frontend

Open `index.html` in your web browser, or serve it using a local web server:

```bash
# Using Python's built-in server
python -m http.server 8080

# Then open http://localhost:8080
```

## 🚀 Usage

1. **Start the backend server** by running `python backend_server.py`
2. **Open the frontend** in your web browser
3. **Paste a YouTube URL** in the input field
4. **Select your desired format** (MP4, MOV, AVI, etc.)
5. **Choose quality settings** (4K, 1080p, 720p, etc.)
6. **Click "INITIALIZE CONVERSION PROTOCOL"**
7. **Wait for processing** (progress shown in real-time)
8. **Download your converted file** when complete

## 🔧 Technical Details

### Backend (Python Flask)
- **Flask** web server with CORS support
- **yt-dlp** for YouTube video extraction
- **FFmpeg** for video/audio processing
- **Threading** for background processing
- **Real-time progress tracking** via API polling

### Frontend (HTML/CSS/JS)
- **Cyberpunk-themed UI** with CSS animations
- **Responsive design** using CSS Grid and Flexbox
- **Real-time status updates** via fetch API
- **Progress visualization** with custom animations

### Supported Formats
- **Video**: MP4, MOV, AVI, MKV, WEBM
- **Audio**: MP3 (192kbps)
- **Quality**: 4K (2160p), 2K (1440p), 1080p, 720p, 480p

## 📊 Quality & File Size Information

The converter automatically displays:
- Actual quality obtained (may differ from requested if not available)
- File size in MB
- Conversion time
- Format details

## 🔍 Troubleshooting

### Common Issues

**"Cannot connect to backend server"**
- Make sure the backend server is running on port 5000
- Check if Python dependencies are installed correctly

**"FFmpeg not found"**
- Install FFmpeg and ensure it's in your system PATH
- Restart your terminal/command prompt after installation

**"Conversion failed"**
- Check if the YouTube URL is valid and accessible
- Some videos may have restrictions or be unavailable in your region
- Try a different quality setting

**"Download link not working"**
- Make sure the conversion completed successfully
- Check the backend server logs for errors

## 📁 Project Structure

```
youtube-converter-pro/
├── README.md              # This file
├── QUICK_START.md          # Quick setup guide
├── LICENSE                 # MIT License
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── setup.sh               # Linux/Mac auto setup
├── setup.bat              # Windows auto setup
├── backend_server.py      # Flask backend server
└── index.html             # Frontend interface
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚡ Performance Notes

- Conversion speed depends on video length and selected quality
- Higher quality videos take longer to process
- File sizes vary significantly based on quality settings:
  - 4K: ~200-500MB for 10-minute video
  - 1080p: ~100-200MB for 10-minute video
  - 720p: ~50-100MB for 10-minute video

## 🛡️ Security & Privacy

- All processing is done locally on your machine
- No data is sent to external servers (except YouTube for video access)
- Temporary files are automatically cleaned up
- No user data collection or tracking

## 🆘 Support

If you encounter any issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Look at existing [GitHub Issues](https://github.com/yourusername/youtube-converter-pro/issues)
3. Create a new issue with detailed information about your problem

## 🙏 Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube video extraction
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [FFmpeg](https://ffmpeg.org/) - Video processing

---

<div align="center">

**⭐ If you found this project helpful, please give it a star! ⭐**

Made with ❤️ for the open source community

</div>