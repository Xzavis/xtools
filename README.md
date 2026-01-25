# 🛠️ Xtools // Terminal Interface V3

**Xtools** is a high-performance, minimalist web-based utility suite designed for AI developers and data engineers. Built with a **Dark Neubrutalism** aesthetic, it provides a centralized command center for handling large datasets, neural model weights, and semantic data processing.

![Platform Status](https://img.shields.io/badge/Status-Live-ccff00?style=for-the-badge&logo=probot&logoColor=black)
![UI Style](https://img.shields.io/badge/UI-Neubrutalism-7000FF?style=for-the-badge)
![Tech Stack](https://img.shields.io/badge/Stack-Python_Flask_Pandas-white?style=for-the-badge)

---

## 🚀 CORE_MODULES

### 1. **MODEL_HUB (HuggingFace Integration)**
*   **Sequential Retrieval**: Robust, sequential file downloading with automatic **3x retry logic** and exponential backoff.
*   **Smart Select**: One-click selection for specific file types (e.g., `.jsonl`, `.safetensors`).
*   **Live Preview**: Instant browser-side preview for `.jsonl` and `.jsonl.gz` datasets immediately after download.
*   **HF_Transfer Support**: Leverages maximum bandwidth for multi-gigabyte weight transfers.

### 2. **NEURAL_INTELLIGENCE_SUITE**
*   **Neural Inspector**: Deep-dive into `.safetensors` or `.jsonl` structural geometry. Map layers, inspect dtypes, and export layer IDs without loading weights into RAM.
*   **Dataset Sanitizer**: Industrial-grade data refinery for `.csv`, `.json`, `.jsonl`, and `.jsonl.gz`. 
    *   **Deduplication**: Safe deduplication even for nested JSON structures.
    *   **Null Mapping**: Identify missing pointers in your training data.
    *   **Schema Analysis**: Instant record counting and payload size calculation.

### 3. **OPERATIONS & UTILITIES**
*   **Split/Merge Engine**: Handle multi-gigabyte files by partitioning them into segments.
*   **Universal Converter**: Transcode between Image (JPG/PNG/WEBP/PDF), Data (JSON/CSV/XLSX/YAML), and Document (MD/HTML) formats.
*   **VRAM Calculator**: Precision hardware projection for LLM deployment.
*   **Snippet Lab**: Persistent markdown storage for prompts and code snippets.

---

## 🛠️ INSTALLATION_GUIDE

### 1. Prerequisites
*   **Python 3.9+**
*   **HF_TOKEN** (Optional, but recommended for private repos and higher rate limits)

### 2. Setup Sequence
```bash
# Clone the repository
git clone https://github.com/yourusername/xtools.git
cd xtools

# Initialize Virtual Environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Dependencies
pip install -r requirements.txt
```

### 3. Execution
```bash
python app.py
```
> **Pro Tip:** Xtools automatically enables `HF_HUB_ENABLE_HF_TRANSFER=1` for maximum download speeds. Ensure you have a stable connection.

---

## 📖 STEP_BY_STEP_USAGE

### A. Downloading a Dataset
1. Navigate to **Model Hub**.
2. Enter the Repo ID (e.g., `yuecao0119/MMInstruct-GPT4V`).
3. Click **START_SCAN**.
4. Use **SMART_SELECT_JSONL** to pick data files.
5. Enable **DISK_DIRECT_WRITE** and choose your local folder.
6. Click **EXECUTE_TRANSFER**. If a file fails, Xtools will retry up to 3 times automatically.
7. Click **VIEW_JSONL** in the log to inspect the data immediately.

### B. Analyzing Neural Weights
1. Navigate to **Neural Inspector**.
2. Enter the path to your `.safetensors` file.
3. Click **INSPECT** to see the full layer map, shapes, and precision (fp16/bf16).
4. Use the **Filter** bar to find specific weights (e.g., `q_proj`).

### C. Cleaning a Dataset
1. Navigate to **Dataset Sanitizer**.
2. Load your `.csv` or `.jsonl.gz` file.
3. Click **ANALYZE** to check for duplicates and nulls.
4. Click **EXECUTE_DEDUPLICATION** to generate a clean version of your manifest.

---

## 📄 LICENSE

Distributed under the **MIT License**. See `LICENSE` for more information.



---

**XTOOLS_V3 // BUILT_FOR_THE_AI_ERA**
