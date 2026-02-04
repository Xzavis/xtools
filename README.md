# XTools 🚀

> **AI-Powered Developer Toolkit** with Modern shadcn/ui Design

[![Version](https://img.shields.io/badge/version-4.0-18181b?style=flat-square)](https://github.com/yourusername/xtools)
[![Python](https://img.shields.io/badge/python-3.8+-2563eb?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.0+-000000?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/license-MIT-16a34a?style=flat-square)](LICENSE)

![XTools Screenshot](static/screenshot.png)

---

## ✨ Features

### 🤖 AI & ML Tools
- **🧠 Model Hub** - Download models from Hugging Face with resume support
- **🔍 Model Inspector** - Analyze model architecture and parameters
- **🧹 Data Sanitizer** - Clean and validate datasets
- **📊 Data Preparation** - Process JSONL, split/merge/tokenize datasets
- **📚 RAG Architect** - Build retrieval-augmented generation pipelines
- **💾 VRAM Calculator** - Estimate GPU memory requirements for LLMs

### 🛠️ Developer Utilities
- **📝 Snippet Lab** - Code snippet manager with syntax highlighting editor
- **🔄 Converter** - Format conversion tools (JSON ↔ CSV ↔ YAML ↔ TOML)
- **📁 File Operations** - File splitting, merging, and validation

### 🎨 Design Features
- **Modern Light Theme** - Clean shadcn/ui inspired design
- **HSL Color System** - Flexible CSS custom properties
- **Responsive Design** - Works on desktop and mobile
- **Accessibility** - High contrast, keyboard navigation support
- **Lucide Icons** - Consistent icon system throughout

---

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
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

XTools uses a custom **shadcn/ui-inspired** design system with HSL color variables.

### Color Palette (HSL)

```css
--background: 0 0% 100%      /* White */
--foreground: 222.2 84% 4.8% /* Slate 900 */
--primary: 222.2 47.4% 11.2% /* Slate 900 */
--secondary: 210 40% 96.1%   /* Slate 100 */
--muted: 210 40% 96.1%       /* Slate 100 */
--border: 214.3 31.8% 91.4%  /* Slate 200 */
```

### Documentation

- **[STYLE_GUIDE.md](STYLE_GUIDE.md)** - Coding style and conventions
- **[DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)** - Comprehensive design documentation

### CSS Structure

```
static/
└── css/
    └── shadcn-theme.css    # All theme variables & components
```

---

## 📁 Project Structure

```
xtools/
├── app.py                    # Main Flask application
├── hf_handler.py            # HuggingFace integration
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── STYLE_GUIDE.md          # Coding style guide
├── DESIGN_SYSTEM.md        # Design system docs
├── LICENSE                 # MIT License
│
├── static/                 # Static assets
│   └── css/
│       └── shadcn-theme.css   # Theme & components
│
├── templates/              # Jinja2 templates
│   ├── index.html         # Dashboard
│   ├── sidebar.html       # Navigation sidebar
│   ├── pastebin.html      # Snippet Lab (CodeMirror)
│   ├── view_paste.html    # Snippet viewer
│   ├── hf_downloader.html # Model downloader
│   ├── intelligence.html  # Model inspector & sanitizer
│   ├── data_preparation.html  # Data processing pipeline
│   ├── compute.html       # VRAM Calculator
│   ├── rag.html           # RAG Architect
│   ├── converter.html     # Format converter
│   └── preview_jsonl.html # JSONL previewer
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

Edit `static/css/shadcn-theme.css` to customize the theme:

```css
:root {
    --primary: 222.2 47.4% 11.2%;    /* Change primary color */
    --radius: 0.5rem;                 /* Change border radius */
    /* ... more variables ... */
}
```

---

## 🖼️ Screenshots

### Dashboard
Clean dashboard with tool cards and quick stats.

### Snippet Lab
Full-featured CodeMirror editor with syntax highlighting, templates, and auto-save.

### Model Hub
Download and manage Hugging Face models with progress tracking.

### VRAM Calculator
Calculate GPU memory requirements for LLM inference.

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
<!DOCTYPE html>
<html>
<head>
    <title>My Tool - XTools</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/shadcn-theme.css') }}">
</head>
<body>
    {% include 'sidebar.html' %}
    <div class="main-content">
        <!-- Your tool UI here -->
    </div>
</body>
</html>
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

### Data Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/clean_jsonl` | Clean JSONL data |
| POST | `/tokenize_jsonl` | Tokenize dataset |
| POST | `/validate_dataset` | Validate dataset |

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
- **Bootstrap 5** - Grid system (optional)
- **Lucide Icons** - Beautiful icon system
- **CodeMirror 5** - Syntax highlighting editor
- **Prism.js** - Code display highlighting

---

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/xtools/issues)

---

<div align="center">

**[⬆ Back to Top](#xtools-)**

Made with 💜 and ☕ by the XTools Team

</div>
