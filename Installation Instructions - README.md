# 🏥 MedReport - Medical Transcription AI

**Transform audio consultations into structured medical reports using local Gemma 3n models**

*Google Gemma 3n Impact Challenge Submission*

---

## 🚀 Quick Start Installation

### Prerequisites
- **Python 3.8+** (Python 3.9+ recommended)
- **8GB RAM minimum** (16GB recommended)
- **4GB free disk space** for models
- **Microphone access** for audio recording
- **Optional:** NVIDIA GPU with 6GB+ VRAM for faster inference

---

## 📦 Installation Methods

### Method 1: Simple Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/wouk1805/medreport.git
cd medreport

# Create virtual environment (recommended)
python -m venv medreport_env

# Activate virtual environment
# Windows:
medreport_env\Scripts\activate
# macOS/Linux:
source medreport_env/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

### Method 2: Manual Dependency Installation

```bash
# Clone repository
git clone https://github.com/wouk1805/medreport.git
cd medreport

# Core dependencies
pip install sounddevice scipy numpy librosa
pip install torch transformers accelerate safetensors tokenizers bitsandbytes
pip install reportlab PyMuPDF datasets soundfile huggingface-hub pillow

# Install Unsloth for optimized Gemma 3n inference
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Launch application
python main.py
```

### Method 3: GPU Accelerated Installation (NVIDIA only)

```bash
# Clone repository
git clone https://github.com/wouk1805/medreport.git
cd medreport

# Check your CUDA version first
nvidia-smi

# For CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install remaining dependencies
pip install sounddevice scipy numpy librosa transformers accelerate
pip install safetensors tokenizers bitsandbytes reportlab PyMuPDF
pip install datasets soundfile huggingface-hub pillow
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Launch application
python main.py
```

---

## 🔧 System-Specific Setup

### Windows
```cmd
# Install Python 3.9+ from python.org
# tkinter is included by default

# If you have issues with sounddevice:
pip install --upgrade setuptools wheel
pip install sounddevice --force-reinstall
```

### macOS
```bash
# Install Python via Homebrew (recommended)
brew install python@3.9

# If tkinter issues:
brew install python-tk

# For M1/M2 Macs, use:
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Ubuntu/Debian Linux
```bash
# Install system dependencies
sudo apt update
sudo apt install python3.9 python3.9-venv python3.9-dev
sudo apt install python3-tk portaudio19-dev

# Install pip if needed
sudo apt install python3-pip

# Then follow standard installation
```

### CentOS/RHEL Linux
```bash
# Install system dependencies
sudo yum install python39 python39-devel python39-tkinter
sudo yum install portaudio-devel

# Then follow standard installation
```

---

## 🎯 First Run

1. **Launch the application:**
   ```bash
   python main.py
   ```

2. **Initial model download** (first run only):
   - Models will download automatically (~4GB total)
   - Download time: 5-15 minutes depending on internet speed
   - Models are cached locally for future runs

3. **Verify installation:**
   - UI should open with "Models: Loading..." status
   - Wait for "Models: Ready ✅" status
   - Test recording with your microphone

---

## 🔍 Troubleshooting

### Common Issues

**❌ "No module named 'tkinter'"**
```bash
# Ubuntu/Debian:
sudo apt-get install python3-tk

# CentOS/RHEL:
sudo yum install tkinter

# macOS:
brew install python-tk
```

**❌ "Could not load dynamic library 'libcudart.so'"**
```bash
# Your system doesn't have CUDA. Use CPU version:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```

**❌ "sounddevice could not find audio devices"**
```bash
# Check your microphone permissions
# Windows: Settings > Privacy > Microphone
# macOS: System Preferences > Security & Privacy > Microphone
# Linux: Check PulseAudio/ALSA configuration
```

**❌ "OutOfMemoryError"**
- Reduce model batch size (automatically handled)
- Close other applications
- Consider upgrading RAM or using GPU

**❌ "Model download failed"**
```bash
# Check internet connection and try:
pip install --upgrade huggingface-hub
huggingface-cli login  # if using private models
```

### Performance Optimization

**🚀 For faster inference:**
1. Use NVIDIA GPU with CUDA
2. Ensure 16GB+ RAM available
3. Close unnecessary applications
4. Use SSD storage for model cache

**🔧 For lower resource usage:**
- Models will automatically use 4-bit quantization
- CPU inference is supported but slower
- Minimum 8GB RAM required

---

## 📊 System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8+ | 3.9+ |
| **RAM** | 8GB | 16GB+ |
| **Storage** | 4GB free | 10GB+ free |
| **CPU** | Dual-core | Quad-core+ |
| **GPU** | None (CPU mode) | NVIDIA 6GB+ VRAM |
| **OS** | Win10/macOS10.14/Linux | Latest versions |

---

## 🎨 Features

- **🎙️ Real-time audio transcription** using fine-tuned Gemma 3n
- **📄 Structured medical report generation** 
- **💊 Automatic prescription detection** with PDF export
- **🌍 Multi-language support** (English, French, Spanish, etc.)
- **📱 Modern, responsive UI** with professional design
- **🔒 100% local processing** - no data leaves your machine
- **📊 Multiple report formats** (General, Narrative, Custom)

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/wouk1805/medreport/issues)
- **Website:** [wouk1805.com](https://wouk1805.com)

---

## 📜 License

© 2025 Young-wouk KIM