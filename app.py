import os
# Enable hf_transfer for maximum bandwidth utilization
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

from flask import Flask, render_template, request, jsonify, send_file, make_response, Response, stream_with_context, redirect
import re
import threading
import struct
import json
import csv
import time
import uuid
import shutil
import string
from io import BytesIO
from PIL import Image
import pandas as pd
import requests
import yaml
import markdown
from huggingface_hub import snapshot_download, hf_hub_download, list_repo_files
from hf_handler import HFHandler

app = Flask(__name__)
hf_handler = HFHandler()

progress_status = {"status": "Idle", "percentage": 0}

# --- Helper Functions ---

def parse_size(size_str):
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}
    size_str = size_str.upper().strip()
    match = re.match(r"^(\d+(?:\.\d+)?)([KMG]?B?)$", size_str)
    if not match: return 1024**3
    number, unit = match.groups()
    unit = unit if unit else "B"
    if len(unit) == 1 and unit != "B": unit += "B"
    return int(float(number) * units.get(unit, 1))

def get_paste_filepath(paste_id):
    paste_dir = os.path.join(os.getcwd(), 'pastes')
    if not os.path.exists(paste_dir):
        return None
    for filename in os.listdir(paste_dir):
        if filename.endswith(f"_{paste_id}.json"):
            return os.path.join(paste_dir, filename)
    return None

# --- Logic Functions (Threaded) ---

def split_logic(file_path, chunk_size_str, dest_path=None):
    global progress_status
    try:
        if not os.path.exists(file_path):
            progress_status = {"status": "Error: File not found", "percentage": 0}
            return

        chunk_size = parse_size(chunk_size_str)
        file_size = os.path.getsize(file_path)
        base_name = os.path.basename(file_path)
        dir_name = dest_path if dest_path and os.path.exists(dest_path) else os.path.dirname(file_path)
        
        if dest_path and not os.path.exists(dest_path):
            os.makedirs(dest_path, exist_ok=True)

        name_no_ext, ext = os.path.splitext(base_name)
        import math
        total_parts = math.ceil(file_size / chunk_size)

        with open(file_path, 'rb') as f:
            part_num = 1
            bytes_processed = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk: break
                
                part_name = os.path.join(dir_name, f"{name_no_ext}-part{part_num:03d}{ext}")
                with open(part_name, 'wb') as chunk_file:
                    chunk_file.write(chunk)
                
                bytes_processed += len(chunk)
                progress_status["percentage"] = int((bytes_processed / file_size) * 100)
                progress_status["status"] = f"Splitting: Part {part_num} of {total_parts}..."
                part_num += 1
        
        progress_status = {"status": f"Success: Split into {total_parts} parts!", "percentage": 100}
    except Exception as e:
        progress_status = {"status": f"Error: {str(e)}", "percentage": 0}

def merge_logic(first_part_path):
    global progress_status
    try:
        dir_name = os.path.dirname(first_part_path) or '.'
        file_name_with_part = os.path.basename(first_part_path)
        
        match = re.search(r'(.+?)[-.]part\d+(.*)', file_name_with_part)
        if not match:
            match = re.search(r'(.+?)\.\d{3}$', file_name_with_part)
            if not match:
                progress_status = {"status": "Error: Invalid part format", "percentage": 0}
                return
            base_output_name = match.group(1)
        else:
            base_output_name = match.group(1) + match.group(2)

        prefix = match.group(1)
        suffix = match.group(2) if len(match.groups()) > 1 else ""
        
        parts = sorted([os.path.join(dir_name, f) for f in os.listdir(dir_name) 
                       if f.startswith(prefix) and (suffix in f) and (("-part" in f) or re.search(r'\.\d{3}$', f))])
        
        if not parts:
            progress_status = {"status": "Error: Parts not found", "percentage": 0}
            return

        total_parts = len(parts)
        output_full_path = os.path.join(dir_name, base_output_name)
        
        with open(output_full_path, 'wb') as outfile:
            for i, part in enumerate(parts):
                progress_status["status"] = f"Merging: Part {i+1}/{total_parts}..."
                with open(part, 'rb') as infile:
                    outfile.write(infile.read())
                progress_status["percentage"] = int(((i+1) / total_parts) * 100)

        progress_status = {"status": f"Success: Combined into {base_output_name}", "percentage": 100}
    except Exception as e:
        progress_status = {"status": f"Error: {str(e)}", "percentage": 0}

def convert_to_json_logic(file_path):
    global progress_status
    try:
        if not os.path.exists(file_path):
            progress_status = {"status": "Error: File not found", "percentage": 0}
            return

        file_size = os.path.getsize(file_path)
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        dir_name = os.path.dirname(file_path)
        output_path = os.path.join(dir_name, f"{base_name}_converted.json")

        if file_path.endswith('.safetensors'):
            progress_status = {"status": "Extracting Safetensors Header...", "percentage": 50}
            with open(file_path, 'rb') as f:
                header_size_bytes = f.read(8)
                header_size = struct.unpack('<Q', header_size_bytes)[0]
                header_json_bytes = f.read(header_size)
                header_data = json.loads(header_json_bytes.decode('utf-8'))
                with open(output_path, 'w', encoding='utf-8') as outfile:
                    json.dump(header_data, outfile, indent=2)
            progress_status = {"status": "Success: Header extracted", "percentage": 100}

        elif file_path.endswith('.csv'):
            progress_status = {"status": "Converting CSV to JSON...", "percentage": 0}
            with open(file_path, 'r', encoding='utf-8') as f_in, open(output_path, 'w', encoding='utf-8') as f_out:
                reader = csv.DictReader(f_in)
                f_out.write('[')
                first = True
                bytes_read = 0
                for row in reader:
                    if not first: f_out.write(',\n')
                    f_out.write(json.dumps(row))
                    first = False
                    bytes_read += sum(len(str(v)) for v in row.values())
                    if bytes_read % 10000 == 0:
                         perc = min(int((bytes_read / file_size) * 100), 99)
                         progress_status = {"status": "Converting rows...", "percentage": perc}
                f_out.write(']')
            progress_status = {"status": "Success: CSV Converted", "percentage": 100}
        else:
            progress_status = {"status": "Error: Unsupported format", "percentage": 0}
    except Exception as e:
        progress_status = {"status": f"Error: {str(e)}", "percentage": 0}

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/action', methods=['POST'])
def action():
    global progress_status
    data = request.json
    mode = data.get('mode')
    path = data.get('path')
    dest = data.get('dest_path')
    size = data.get('size', '1GB')

    progress_status = {"status": "Starting...", "percentage": 0}
    
    if mode == 'split':
        threading.Thread(target=split_logic, args=(path, size, dest)).start()
    elif mode == 'merge':
        threading.Thread(target=merge_logic, args=(path,)).start()
    elif mode == 'convert':
        threading.Thread(target=convert_to_json_logic, args=(path,)).start()
        
    return jsonify({"message": "Process started"})

@app.route('/progress')
def progress():
    return jsonify(progress_status)

@app.route('/browse', methods=['POST'])
def browse_files():
    try:
        data = request.json
        path = data.get('path')

        if path == '::DRIVES::':
            drives = []
            for letter in string.ascii_uppercase:
                drive_path = f"{letter}:\\"
                if os.path.exists(drive_path):
                    drives.append(drive_path)
            return jsonify({
                'current_path': 'My PC',
                'parent_path': '',
                'dirs': drives,
                'files': []
            })

        if not path:
            path = os.path.expanduser("~")
        
        path = os.path.abspath(path)
        
        if not os.path.exists(path) or not os.path.isdir(path):
            return jsonify({"error": f"Path not found: {path}"}), 404

        try:
            items = os.listdir(path)
        except PermissionError:
            return jsonify({"error": "Access Denied"}), 403

        dirs = sorted([d for d in items if os.path.isdir(os.path.join(path, d))])
        files = sorted([f for f in items if os.path.isfile(os.path.join(path, f))])
        
        parent_dir = os.path.dirname(path)
        if parent_dir == path: # Root
            parent_dir = '::DRIVES::'

        return jsonify({
            'current_path': path,
            'parent_path': parent_dir,
            'dirs': dirs,
            'files': files
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/pastebin')
def pastebin():
    return render_template('pastebin.html')

@app.route('/save_paste', methods=['POST'])
def save_paste():
    try:
        data = request.json
        if not data or 'content' not in data: return jsonify({"error": "No content"}), 400

        paste_dir = os.path.join(os.getcwd(), 'pastes')
        if not os.path.exists(paste_dir): os.makedirs(paste_dir)

        paste_id = str(uuid.uuid4())[:8]
        timestamp = int(time.time())
        filename = f"paste_{timestamp}_{paste_id}.json"
        
        with open(os.path.join(paste_dir, filename), 'w', encoding='utf-8') as f:
            json.dump({"id": paste_id, "created_at": timestamp, **data}, f, indent=4)

        return jsonify({"message": "Success", "id": paste_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/paste/<paste_id>')
def view_paste(paste_id):
    filepath = get_paste_filepath(paste_id)
    if not filepath: return "Paste not found", 404
    with open(filepath, 'r', encoding='utf-8') as f:
        return render_template('view_paste.html', paste=json.load(f))

@app.route('/download/<paste_id>')
def download_paste(paste_id):
    filepath = get_paste_filepath(paste_id)
    if not filepath: return "Paste not found", 404
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    filename = f"{re.sub(r'[^\w\s-]', '', data.get('title','untitled')).strip().replace(' ', '_')}.md"
    response = make_response(data.get('content', ''))
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    return response

@app.route('/hf_downloader')
def hf_downloader_page():
    return render_template('hf_downloader.html')

@app.route('/api/hf_scan', methods=['POST'])
def hf_scan():
    data = request.json
    repo_id = data.get('repo_id', '').strip()
    repo_type = data.get('repo_type', 'model')
    token = data.get('token', '').strip() or None

    if not repo_id: return jsonify({"error": "Repo ID is required"}), 400

    result = hf_handler.scan_repo(repo_id, token, repo_type)
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/hf_download_links', methods=['POST'])
def hf_download_links():
    data = request.json
    repo_id = data.get('repo_id')
    files = data.get('files', [])
    repo_type = data.get('repo_type', 'model')

    if not repo_id or not files:
        return jsonify({"error": "Missing parameters"}), 400

    links = hf_handler.generate_browser_links(repo_id, files, repo_type)
    return jsonify({"links": links})

@app.route('/api/hf_download_server', methods=['POST'])
def hf_download_server():
    data = request.json
    repo_id = data.get('repo_id')
    files = data.get('files', [])
    repo_type = data.get('repo_type', 'model')
    local_dir = data.get('local_dir')
    token = data.get('token')

    if not repo_id or not files or not local_dir:
        return jsonify({"error": "Missing parameters (Repo ID, Files, or Local Path)"}), 400

    return Response(stream_with_context(hf_handler.download_files_to_local(repo_id, files, local_dir, token, repo_type)), mimetype='application/json')

@app.route('/file_manager')
def file_manager_page():
    return render_template('file_manager.html')

@app.route('/fm/list', methods=['POST'])
def fm_list():
    return browse_files() # Reuse logic

@app.route('/fm/mkdir', methods=['POST'])
def fm_mkdir():
    try:
        data = request.json
        os.makedirs(os.path.join(data['path'], data['name']))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/converter')
def converter_page():
    return render_template('converter.html')

@app.route('/api/convert', methods=['POST'])
def convert_api():
    try:
        data = request.json
        mode = data.get('mode', 'url')
        category = data.get('category')
        target_format = data.get('target_format')
        
        content_bytes = None
        content_text = None
        input_filename = "unknown"

        if mode == 'url':
            url = data.get('url')
            input_filename = url.split('/')[-1]
            resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
            if resp.status_code != 200: return jsonify({"error": "Fetch failed"}), 400
            content_bytes = resp.content
            try: content_text = resp.text
            except: pass
            
        elif mode == 'local':
            file_path = data.get('file_path')
            if not os.path.exists(file_path): return jsonify({"error": "File not found"}), 404
            input_filename = os.path.basename(file_path)
            with open(file_path, 'rb') as f: content_bytes = f.read()
            try: 
                with open(file_path, 'r', encoding='utf-8') as f: content_text = f.read()
            except: pass
        
        output_io = BytesIO()
        filename = "converted"
        mimetype = "application/octet-stream"

        if category == 'image':
            image = Image.open(BytesIO(content_bytes))
            if target_format in ['jpeg', 'pdf'] and image.mode in ("RGBA", "P"):
                image = image.convert("RGB")
            
            save_fmt = 'JPEG' if target_format.upper() == 'JPG' else target_format.upper()
            image.save(output_io, format=save_fmt)
            mimetype = f"image/{target_format}" if target_format != 'pdf' else "application/pdf"
            filename = f"image.{target_format}"

        elif category == 'data':
            parsed = None
            ext = input_filename.split('.')[-1].lower() if '.' in input_filename else ''
            
            if ext in ['xlsx', 'xls']:
                parsed = pd.read_excel(BytesIO(content_bytes)).to_dict(orient='records')
            elif ext == 'csv':
                parsed = pd.read_csv(BytesIO(content_bytes)).to_dict(orient='records')
            elif content_text:
                try: parsed = json.loads(content_text)
                except: 
                    try: parsed = yaml.safe_load(content_text)
                    except: pass
            
            if parsed is None: return jsonify({"error": "Parse error"}), 400

            if target_format == 'json':
                output_io.write(json.dumps(parsed, indent=2).encode('utf-8'))
                mimetype = "application/json"
                filename = "data.json"
            elif target_format == 'yaml':
                output_io.write(yaml.dump(parsed).encode('utf-8'))
                mimetype = "application/x-yaml"
                filename = "data.yaml"
            elif target_format == 'excel':
                pd.DataFrame(parsed).to_excel(output_io, index=False)
                mimetype = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                filename = "data.xlsx"
            elif target_format == 'csv':
                output_io.write(pd.DataFrame(parsed).to_csv(index=False).encode('utf-8'))
                mimetype = "text/csv"
                filename = "data.csv"

        elif category == 'document':
            ext = input_filename.split('.')[-1].lower() if '.' in input_filename else ''
            if ext in ['xlsx', 'xls', 'csv']:
                df = pd.read_csv(BytesIO(content_bytes)) if ext == 'csv' else pd.read_excel(BytesIO(content_bytes))
                if target_format == 'markdown':
                    output_io.write(df.to_markdown(index=False).encode('utf-8'))
                    filename = "table.md"
                elif target_format == 'html':
                    html = f"<html><link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css' rel='stylesheet'><body class='p-4'>{df.to_html(classes='table table-bordered', index=False)}</body></html>"
                    output_io.write(html.encode('utf-8'))
                    filename = "table.html"
            elif content_text and target_format == 'html':
                html = markdown.markdown(content_text, extensions=['tables'])
                output_io.write(f"<html><body>{html}</body></html>".encode('utf-8'))
                filename = "doc.html"
            elif content_text and target_format == 'markdown':
                output_io.write(content_text.encode('utf-8'))
                filename = "doc.md"
            else: return jsonify({"error": "Unsupported doc conversion"}), 400

        output_io.seek(0)
        return send_file(output_io, mimetype=mimetype, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/intelligence/<mode>')
def intelligence_page(mode):
    if mode not in ['dataset', 'model']:
        return redirect('/intelligence/dataset')
    return render_template('intelligence.html', active_mode=mode)

@app.route('/api/intel/analyze_dataset', methods=['POST'])
def analyze_dataset():
    try:
        data = request.json
        file_path = data.get('path')
        if not os.path.exists(file_path): return jsonify({"error": "File not found"}), 404
        
        ext = file_path.split('.')[-1].lower()
        df = None
        if ext == 'csv':
            df = pd.read_csv(file_path)
        elif ext in ['xlsx', 'xls']:
            df = pd.read_excel(file_path)
        elif ext == 'json':
            df = pd.read_json(file_path)
        
        if df is None: return jsonify({"error": "Unsupported dataset format"}), 400

        analysis = {
            "total_rows": len(df),
            "columns": list(df.columns),
            "duplicates": int(df.duplicated().sum()),
            "null_values": int(df.isnull().sum().sum()),
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
            "sample": df.head(5).to_dict(orient='records')
        }
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/intel/clean_dataset', methods=['POST'])
def clean_dataset():
    try:
        data = request.json
        file_path = data.get('path')
        if not os.path.exists(file_path): return jsonify({"error": "File not found"}), 404
        
        ext = file_path.split('.')[-1].lower()
        if ext == 'csv': df = pd.read_csv(file_path)
        elif ext == 'json': df = pd.read_json(file_path)
        else: return jsonify({"error": "Only CSV/JSON supported for direct cleaning"}), 400

        initial_rows = len(df)
        df = df.drop_duplicates()
        cleaned_rows = len(df)
        
        output_path = file_path.replace(f".{ext}", f"_cleaned.{ext}")
        if ext == 'csv': df.to_csv(output_path, index=False)
        else: df.to_json(output_path, orient='records', indent=2)

        return jsonify({
            "success": True, 
            "initial_rows": initial_rows, 
            "cleaned_rows": cleaned_rows,
            "saved_to": output_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/intel/inspect_model', methods=['POST'])
def inspect_model():
    try:
        data = request.json
        file_path = data.get('path')
        if not os.path.exists(file_path): return jsonify({"error": "File not found"}), 404

        if not file_path.endswith('.safetensors'):
            return jsonify({"error": "Currently only .safetensors inspection is supported"}), 400

        with open(file_path, 'rb') as f:
            header_size_bytes = f.read(8)
            header_size = struct.unpack('<Q', header_size_bytes)[0]
            header_json_bytes = f.read(header_size)
            header_data = json.loads(header_json_bytes.decode('utf-8'))

        metadata = header_data.get('__metadata__', {})
        tensors = []
        for key, val in header_data.items():
            if key == '__metadata__': continue
            tensors.append({
                "name": key,
                "shape": val.get('shape', []),
                "dtype": val.get('dtype', 'unknown')
            })

        return jsonify({
            "metadata": metadata,
            "tensor_count": len(tensors),
            "tensors": tensors[:50], # Return first 50 for preview
            "total_tensors": len(tensors)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/compute/<mode>')
def compute_page(mode):
    if mode != 'vram':
        return redirect('/compute/vram')
    return render_template('compute.html', active_mode=mode)

@app.route('/api/compute/vram_calc', methods=['POST'])
def vram_calc():
    try:
        data = request.json
        params = float(data.get('params', 0)) # in Billions
        bits = float(data.get('bits', 16))
        context = float(data.get('context', 2048))
        batch_size = float(data.get('batch_size', 1))

        # Weights: (Params * 10^9) * (Bits / 8) / (1024^3) GB
        weight_vram = (params * 10**9) * (bits / 8) / (1024**3)
        
        # KV Cache: 2 * layers * hidden_size * context * batch_size * dtype_size
        # Simplification: context * params * 0.5 (rough estimate for cache)
        kv_cache = (context * params * 10**9 * (bits / 8) * 0.0000001) / (1024**3) # Placeholder for complex calc
        
        # System Overhead: ~10%
        total = (weight_vram + kv_cache) * 1.1

        return jsonify({
            "weight_vram": round(weight_vram, 2),
            "kv_cache": round(kv_cache, 2),
            "total_estimated": round(total, 2)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/intelligence/rag')
def rag_page():
    return render_template('rag.html')

@app.route('/api/intel/rag_chunk', methods=['POST'])
def rag_chunk_logic():
    try:
        data = request.json
        text = data.get('text', '')
        chunk_size = int(data.get('chunk_size', 500))
        overlap = int(data.get('overlap', 50))
        
        if not text: return jsonify({"error": "No text provided"}), 400

        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append({
                "index": len(chunks) + 1,
                "content": chunk,
                "length": len(chunk),
                "tokens_est": int(len(chunk) / 4) # Rough estimation
            })
            if end >= len(text): break
            start += (chunk_size - overlap)

        return jsonify({
            "success": True,
            "total_chunks": len(chunks),
            "chunks": chunks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
