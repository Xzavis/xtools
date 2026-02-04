# XTools 🚀

> **AI-Powered Developer Toolkit** with Dark Neon Cyberpunk UI

[![Version](https://img.shields.io/badge/version-2.0-CB3CFF?style=flat-square)](https://github.com/yourusername/xtools)
[![Python](https://img.shields.io/badge/python-3.8+-0B1739?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.0+-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/license-MIT-21C3FC?style=flat-square)](LICENSE)

![XTools Screenshot](static/screenshot.png)

---

## ✨ Features

### 🤖 AI & ML Tools
- **🧠 Model Hub** - Download models from Hugging Face with resume support
- **🔍 Model Inspector** - Analyze model architecture and parameters
- **🧹 Data Sanitizer** - Clean and validate datasets
- **📊 Data Preparation** - Process JSONL, split/merge datasets
- **📚 RAG Architect** - Build retrieval-augmented generation pipelines
- **💾 VRAM Calculator** - Estimate GPU memory requirements

### 🛠️ Developer Utilities
- **📝 Snippet Lab** - Markdown-powered code snippet manager with dark editor
- **🔄 Converter** - Format conversion tools (JSON ↔ CSV ↔ YAML)
- **📁 File Manager** - Web-based file browser

### 🎨 Design Features
- **Dark Neon Theme** - Cyberpunk-inspired UI with pink/magenta accents
- **Animated Interface** - Smooth transitions and micro-interactions
- **Responsive Design** - Works on desktop and mobile
- **Accessibility** - High contrast, keyboard navigation support

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
Node.js (optional, for asset building)
```

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/xtools.git
cd xtools

# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Access the Application

Open your browser and navigate to: `http://localhost:5000`

---

## 🎨 Design System

XTools uses a custom **Dark Neon** design system with carefully crafted colors and animations.

### Color Palette

```
Primary:    #CB3CFF (Pink/Magenta)
Secondary:  #8951FF (Purple)
Accent:     #21C3FC (Cyan)
Background: #081028 (Deep Blue-Black)
Surface:    #0A1330 (Elevated Dark)
Text:       #FFFFFF / #AEB9E1
```

### Documentation

- **[STYLE_GUIDE.md](STYLE_GUIDE.md)** - Quick reference for using styles
- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Comprehensive design documentation

### CSS Structure

```
static/
├── css/
│   ├── design-system.css    # Core tokens & utilities
│   └── animations.css       # Animation library
└── style.css                # Application styles
```

---

## 📁 Project Structure

```
xtools/
├── app.py                    # Main Flask application
├── hf_handler.py            # HuggingFace integration
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── STYLE_GUIDE.md          # Style documentation
├── DESIGN_SYSTEM.md        # Design system docs
├── LICENSE                 # MIT License
│
├── static/                 # Static assets
│   ├── css/
│   │   ├── design-system.css
│   │   └── animations.css
│   ├── style.css
│   └── js/                 # JavaScript files
│
├── templates/              # Jinja2 templates
│   ├── index.html         # Dashboard
│   ├── sidebar.html       # Navigation sidebar
│   ├── pastebin.html      # Snippet Lab
│   ├── view_paste.html    # Snippet viewer
│   ├── hf_downloader.html # Model downloader
│   ├── intelligence.html  # Model inspector
│   ├── data_preparation.html
│   ├── converter.html
│   ├── file_manager.html
│   └── ...
│
└── pastes/                # Snippet storage (auto-created)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# HuggingFace
export HF_TOKEN="your_token_here"  # For private models

# Server
export PORT=5000
export DEBUG=False

# Storage
export PASTE_STORAGE_PATH="./pastes"
```

### Customization

Edit `static/css/design-system.css` to customize the color palette:

```css
:root {
    --pink-400: #CB3CFF;        /* Change primary color */
    --neutral-800: #081028;     /* Change background */
    /* ... more variables ... */
}
```

---

## 🖼️ Screenshots

### Dashboard
![Dashboard](static/screenshots/dashboard.png)

### Snippet Lab (Dark Editor)
![Snippet Lab](static/screenshots/snippet.png)

### Model Hub
![Model Hub](static/screenshots/modelhub.png)

---

## 🛠️ Development

### Running in Development Mode

```bash
# Debug mode with auto-reload
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Adding New Tools

1. Create route in `app.py`:

```python
@app.route('/new_tool')
def new_tool():
    return render_template('new_tool.html')
```

2. Create template in `templates/new_tool.html`:

```html
{% extends 'base.html' %}
{% block content %}
    <!-- Your tool UI here -->
{% endblock %}
```

3. Add navigation link in `templates/sidebar.html`

---

## 📝 API Endpoints

### Snippet Lab

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/save_paste` | Save new snippet |
| GET | `/paste/<id>` | View snippet |
| GET | `/download/<id>` | Download raw |

### File Operations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/split` | Split files |
| POST | `/merge` | Merge files |
| POST | `/convert` | Format conversion |

### HuggingFace

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/download_hf` | Download model |
| GET | `/download_progress` | Progress stream |

---

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Check code style
flake8 app.py
black app.py --check
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md) before making UI changes.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Flask** - Web framework
- **Bootstrap 5** - Base components
- **Font Awesome** - Icons
- **EasyMDE** - Markdown editor
- **Highlight.js** - Syntax highlighting

---

## 📞 Support

- 📧 Email: support@xtools.dev
- 💬 Discord: [Join our server](https://discord.gg/xtools)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/xtools/issues)

---

<div align="center">

**[⬆ Back to Top](#xtools-)**

Made with 💜 and ☕ by the XTools Team

</div>
