import os
# Enable hf_transfer for maximum bandwidth utilization
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"

from flask import Flask, render_template, request, jsonify, send_file, make_response, Response, stream_with_context, redirect, session
from functools import wraps
import re
import threading
import struct
import json
import csv
import time
import uuid
import shutil
import string
import gzip
import random
from io import BytesIO
from PIL import Image
import pandas as pd
import requests
import yaml
import markdown
from huggingface_hub import snapshot_download, hf_hub_download, list_repo_files
from hf_handler import HFHandler

# Import security utilities
try:
    from security_utils import token_security
    SECURITY_ENABLED = True
except ImportError:
    SECURITY_ENABLED = False
    print("Warning: security_utils not found, running without advanced security")

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(32)
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
            match = re.search(r'(.+?)\.[0-9]{3}$', file_name_with_part)
            if not match:
                progress_status = {"status": "Error: Invalid part format", "percentage": 0}
                return
            base_output_name = match.group(1)
        else:
            base_output_name = match.group(1) + match.group(2)

        prefix = match.group(1)
        suffix = match.group(2) if len(match.groups()) > 1 else ""
        
        parts = sorted([os.path.join(dir_name, f) for f in os.listdir(dir_name) 
                       if f.startswith(prefix) and (suffix in f) and (("-part" in f) or re.search(r'\.[0-9]{3}$', f))])
        
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

@app.route('/preview_jsonl')
def preview_jsonl_page():
    return render_template('preview_jsonl.html')

@app.route('/api/hf_scan', methods=['POST'])
def hf_scan():
    data = request.json
    repo_id = data.get('repo_id', '').strip()
    repo_type = data.get('repo_type', 'model')
    token = data.get('token', '').strip() or None

    if not repo_id: return jsonify({"error": "Repo ID is required"}), 400

    result = hf_handler.scan_repo(repo_id, token, repo_type, options=data.get('options'))
    if result.get('success'):
        return jsonify(result)
    else:
        return jsonify(result), 400

@app.route('/api/hf_search', methods=['POST'])
def hf_search():
    data = request.json
    query = data.get('query', '')
    limit = int(data.get('limit', 20))
    sort = data.get('sort', 'downloads')
    direction = int(data.get('direction', -1))
    repo_type = data.get('repo_type', 'model')
    
    result = hf_handler.search_repositories(query, limit, sort, direction, repo_type)
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

@app.route('/converter')
def converter_page():
    return render_template('converter.html')

@app.route('/api/file_info', methods=['POST'])
def get_file_info():
    """Get file information for local disk selection"""
    try:
        data = request.json
        file_path = data.get('path')
        
        if not file_path or not os.path.exists(file_path):
            return jsonify({"error": "File not found"}), 404
        
        if not os.path.isfile(file_path):
            return jsonify({"error": "Path is not a file"}), 400
        
        # Get basic file stats
        stat = os.stat(file_path)
        file_size = stat.st_size
        file_name = os.path.basename(file_path)
        
        # Get extension
        _, ext = os.path.splitext(file_name)
        extension = ext.lstrip('.').lower() if ext else ''
        
        # Estimate rows for certain file types
        estimated_rows = None
        try:
            if extension == 'parquet':
                # Read parquet metadata without loading full data
                import pyarrow.parquet as pq
                parquet_file = pq.ParquetFile(file_path)
                estimated_rows = parquet_file.metadata.num_rows
            elif extension in ['csv']:
                # Rough estimate for CSV
                with open(file_path, 'rb') as f:
                    # Read first 1MB to estimate
                    sample = f.read(1024 * 1024)
                    avg_line_length = len(sample) / sample.count(b'\n') if sample.count(b'\n') > 0 else 100
                    estimated_rows = int(file_size / avg_line_length)
            elif extension in ['jsonl']:
                # Count lines (limit to first 10000 for speed)
                with open(file_path, 'rb') as f:
                    estimated_rows = sum(1 for _ in f)
            elif extension in ['json']:
                # Try to count array items
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1024 * 1024)  # Read first 1MB
                    estimated_rows = content.count('{')  # Rough estimate
        except Exception:
            pass
        
        return jsonify({
            "name": file_name,
            "path": file_path,
            "size": file_size,
            "extension": extension,
            "estimated_rows": _formatNumber(estimated_rows) if estimated_rows else '-',
            "modified_time": stat.st_mtime
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def _formatNumber(num):
    """Format number to human readable"""
    if num is None:
        return '-'
    if num >= 1000000:
        return f"{num/1000000:.1f}M"
    if num >= 1000:
        return f"{num/1000:.1f}K"
    return str(num)

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

        elif category == 'parquet':
            ext = input_filename.split('.')[-1].lower() if '.' in input_filename else ''
            if ext != 'parquet':
                return jsonify({"error": "Invalid file format. Expected .parquet file"}), 400
            
            try:
                # Read parquet file using pandas
                df = pd.read_parquet(BytesIO(content_bytes))
                
                if target_format == 'jsonl':
                    # Convert DataFrame to JSON Lines format
                    jsonl_lines = []
                    for _, row in df.iterrows():
                        # Convert row to dict and handle non-serializable types
                        row_dict = row.to_dict()
                        # Convert numpy types to python native types
                        for key, value in row_dict.items():
                            if hasattr(value, 'item'):  # numpy scalar
                                row_dict[key] = value.item()
                            elif isinstance(value, (pd.Timestamp, pd.NaT)):
                                row_dict[key] = str(value) if pd.notna(value) else None
                            elif pd.isna(value):
                                row_dict[key] = None
                        jsonl_lines.append(json.dumps(row_dict, ensure_ascii=False))
                    
                    output_io.write('\n'.join(jsonl_lines).encode('utf-8'))
                    mimetype = "application/jsonlines"
                    filename = "data.jsonl"
                else:
                    return jsonify({"error": "Unsupported parquet conversion format"}), 400
            except Exception as e:
                return jsonify({"error": f"Parquet processing failed: {str(e)}"}), 500

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
        if not file_path or not os.path.exists(file_path): 
            return jsonify({"error": "File not found"}), 404
        
        file_path_lower = file_path.lower()
        is_gz = file_path_lower.endswith('.gz')
        df = None
        total_rows = 0

        # Format detection
        if file_path_lower.endswith('.csv'):
            df = pd.read_csv(file_path)
            total_rows = len(df)
        elif file_path_lower.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
            total_rows = len(df)
        elif file_path_lower.endswith('.json') and not file_path_lower.endswith('.jsonl'):
            df = pd.read_json(file_path)
            total_rows = len(df)
        elif file_path_lower.endswith('.jsonl') or file_path_lower.endswith('.jsonl.gz'):
            import gzip
            open_func = gzip.open if is_gz else open
            mode = 'rt' if is_gz else 'r'
            
            records = []
            with open_func(file_path, mode, encoding='utf-8', errors='replace') as f:
                for i, line in enumerate(f):
                    if i < 1000:
                        try:
                            line_data = json.loads(line)
                            if line_data: records.append(line_data)
                        except: pass
                    else: break
            
            if records:
                df = pd.DataFrame(records)
                # Count total lines efficiently
                with open_func(file_path, mode, encoding='utf-8', errors='replace') as f:
                    total_rows = sum(1 for _ in f)
            else:
                return jsonify({"error": "Could not parse any valid JSON objects from file"}), 400
        
        if df is None:
            return jsonify({"error": "Unsupported or unrecognized dataset format"}), 400

        # Safe duplicate detection (JSONL often has dicts/lists which are unhashable)
        duplicates = 0
        try:
            duplicates = int(df.duplicated().sum())
        except TypeError:
            try:
                duplicates = int(df.astype(str).duplicated().sum())
            except:
                duplicates = "Unsupported (Nested Data)"

        analysis = {
            "total_rows": total_rows,
            "columns": list(df.columns),
            "duplicates": duplicates,
            "null_values": int(df.isnull().sum().sum()),
            "memory_usage": f"{os.path.getsize(file_path) / 1024**2:.2f} MB",
            "sample": df.head(5).to_dict(orient='records')
        }
        return jsonify(analysis)
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

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
        # Ensure target directory exists for the cleaned file
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        try:
            if ext == 'csv': df.to_csv(output_path, index=False)
            else: df.to_json(output_path, orient='records', indent=2)
        except Exception as save_err:
            return jsonify({"error": f"Failed to write cleaned file to disk: {str(save_err)}"}), 500

        return jsonify({
            "success": True, 
            "initial_rows": initial_rows, 
            "cleaned_rows": cleaned_rows,
            "saved_to": output_path
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/compute/vram_calc', methods=['POST'])
def vram_calc():
    try:
        data = request.json
        params = float(data.get('params', 0)) # in Billions
        bits = float(data.get('bits', 16))
        context = float(data.get('context', 2048))
        batch_size = float(data.get('batch_size', 1))

        # Weights: (Params * 10^9) * (Bits / 8) / (1024**3) GB
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

@app.route('/compute/vram')
def compute_vram_page():
    return render_template('compute.html')

@app.route('/data_preparation')
def data_preparation_page():
    return render_template('data_preparation.html')

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

@app.route('/api/intel/preview_jsonl', methods=['POST'])
def preview_jsonl():
    try:
        data = request.json
        file_path = data.get('path')
        lines_to_read = int(data.get('limit', 20))
        max_line_length = 50000 # Safeguard against massive lines
        
        if not file_path:
             return jsonify({"error": "Path is required"}), 400

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return jsonify({"error": "File not found or is not a valid file"}), 404
            
        preview_data = []
        is_gz = file_path.lower().endswith('.gz')
        
        try:
            import gzip
            # Open with gzip if .gz, otherwise normal open
            open_func = gzip.open if is_gz else open
            mode = 'rt' if is_gz else 'r' # 'rt' for text mode in gzip
            
            with open_func(file_path, mode, encoding='utf-8', errors='replace') as f:
                for i, line in enumerate(f):
                    if i >= lines_to_read:
                        break
                    
                    # Safeguard: skip or truncate extremely long lines
                    if len(line) > max_line_length:
                        preview_data.append({
                            "_error": "Line too large to preview", 
                            "length": len(line),
                            "preview": line[:1000] + "..."
                        })
                        continue

                    clean_line = line.strip()
                    if not clean_line: continue

                    try:
                        preview_data.append(json.loads(clean_line))
                    except json.JSONDecodeError:
                        preview_data.append({"_error": "Invalid JSON on this line", "raw": clean_line[:200] + "..."})
        except Exception as e:
            return jsonify({"error": f"Failed to read file: {str(e)}"}), 500
        
        return jsonify({
            "success": True,
            "filename": os.path.basename(file_path),
            "preview": preview_data,
            "total_previewed": len(preview_data),
            "file_size": os.path.getsize(file_path),
            "is_compressed": is_gz
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Data Preparation API Endpoints

@app.route('/api/prep/clean', methods=['POST'])
def prep_clean():
    """Data Cleaning: membersihkan data dari noise dan inkonsistensi"""
    try:
        data = request.json
        input_path = data.get('input_path')
        output_path = data.get('output_path')
        options = data.get('options', {})
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({"error": "Input file not found"}), 404
        
        is_gz = input_path.lower().endswith('.gz')
        open_func = gzip.open if is_gz else open
        mode = 'rt' if is_gz else 'r'
        
        records = []
        errors = []
        
        # Read all records
        with open_func(input_path, mode, encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                try:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    records.append(record)
                except json.JSONDecodeError as e:
                    errors.append({"line": i + 1, "error": str(e)})
        
        initial_count = len(records)
        
        # Apply cleaning operations
        cleaned_records = records.copy()
        
        # 1. Remove duplicates (convert to string for comparison)
        if options.get('remove_duplicates', True):
            seen = set()
            unique_records = []
            for record in cleaned_records:
                record_str = json.dumps(record, sort_keys=True)
                if record_str not in seen:
                    seen.add(record_str)
                    unique_records.append(record)
            cleaned_records = unique_records
        
        # 2. Handle nulls - filter out records with all null values
        if options.get('handle_nulls', True):
            def has_valid_data(record):
                if not record:
                    return False
                for v in record.values():
                    if v is not None and v != '' and v != [] and v != {}:
                        return True
                return False
            cleaned_records = [r for r in cleaned_records if has_valid_data(r)]
        
        # 3. Normalize text fields
        if options.get('normalize_text', True):
            for record in cleaned_records:
                for key, value in record.items():
                    if isinstance(value, str):
                        record[key] = value.strip()
        
        # 4. Remove special characters
        if options.get('remove_special_chars', False):
            import re
            for record in cleaned_records:
                for key, value in record.items():
                    if isinstance(value, str):
                        record[key] = re.sub(r'[^\w\s-]', '', value)
        
        # 5. Filter by minimum length
        if options.get('filter_min_length', False):
            min_length = options.get('min_length', 10)
            cleaned_records = [
                r for r in cleaned_records 
                if any(len(str(v)) >= min_length for v in r.values() if isinstance(v, str))
            ]
        
        final_count = len(cleaned_records)
        removed_count = initial_count - final_count
        reduction_percent = round((removed_count / initial_count * 100), 2) if initial_count > 0 else 0
        
        # Determine output path
        if not output_path:
            base, ext = os.path.splitext(input_path)
            if is_gz:
                base = base.replace('.jsonl', '')
                output_path = f"{base}_cleaned.jsonl.gz"
            else:
                output_path = f"{base}_cleaned.jsonl"
        
        # Write cleaned data
        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or '.', exist_ok=True)
        
        if output_path.lower().endswith('.gz'):
            with gzip.open(output_path, 'wt', encoding='utf-8') as f:
                for record in cleaned_records:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
        else:
            with open(output_path, 'w', encoding='utf-8') as f:
                for record in cleaned_records:
                    f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        return jsonify({
            "success": True,
            "initial_count": initial_count,
            "final_count": final_count,
            "removed_count": removed_count,
            "reduction_percent": reduction_percent,
            "output_path": output_path,
            "parse_errors": len(errors)
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/api/prep/split', methods=['POST'])
def prep_split():
    """Data Splitting: membagi data menjadi training dan validation set"""
    try:
        data = request.json
        input_path = data.get('input_path')
        output_dir = data.get('output_dir')
        train_ratio = data.get('train_ratio', 0.8)
        random_seed = data.get('random_seed', 42)
        shuffle = data.get('shuffle', True)
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({"error": "Input file not found"}), 404
        
        is_gz = input_path.lower().endswith('.gz')
        open_func = gzip.open if is_gz else open
        mode = 'rt' if is_gz else 'r'
        
        # Read all records
        records = []
        with open_func(input_path, mode, encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except:
                    pass
        
        total_count = len(records)
        if total_count == 0:
            return jsonify({"error": "No valid records found in file"}), 400
        
        # Shuffle if requested
        if shuffle:
            import random
            random.seed(random_seed)
            random.shuffle(records)
        
        # Calculate split
        train_count = int(total_count * train_ratio)
        val_count = total_count - train_count
        
        train_records = records[:train_count]
        val_records = records[train_count:]
        
        # Determine output directory and filenames
        if not output_dir:
            output_dir = os.path.dirname(os.path.abspath(input_path)) or '.'
        
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        if is_gz:
            base_name = base_name.replace('.jsonl', '')
        
        train_file = os.path.join(output_dir, f"{base_name}_train.jsonl")
        val_file = os.path.join(output_dir, f"{base_name}_validation.jsonl")
        
        # Write train file
        with open(train_file, 'w', encoding='utf-8') as f:
            for record in train_records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        # Write validation file
        with open(val_file, 'w', encoding='utf-8') as f:
            for record in val_records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        return jsonify({
            "success": True,
            "total_count": total_count,
            "train_count": train_count,
            "val_count": val_count,
            "train_percent": round(train_count / total_count * 100, 1),
            "val_percent": round(val_count / total_count * 100, 1),
            "train_file": train_file,
            "val_file": val_file
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/api/prep/tokenize', methods=['POST'])
def prep_tokenize():
    """Tokenization: mengkonversikan teks ke token menggunakan tokenizer dari model base"""
    try:
        data = request.json
        input_path = data.get('input_path')
        model_base = data.get('model_base', 'Qwen/Qwen2-7B-Instruct')
        text_field = data.get('text_field', 'text')
        calc_max_length = data.get('calc_max_length', True)
        calc_avg_length = data.get('calc_avg_length', True)
        preview_tokens = data.get('preview_tokens', False)
        max_records = data.get('max_records', 1000)
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({"error": "Input file not found"}), 404
        
        # Try to import transformers
        try:
            from transformers import AutoTokenizer
        except ImportError:
            return jsonify({"error": "transformers library not installed. Run: pip install transformers"}), 500
        
        # Load tokenizer
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_base, trust_remote_code=True)
        except Exception as e:
            return jsonify({"error": f"Failed to load tokenizer: {str(e)}"}), 500
        
        is_gz = input_path.lower().endswith('.gz')
        open_func = gzip.open if is_gz else open
        mode = 'rt' if is_gz else 'r'
        
        # Read and tokenize records
        records = []
        with open_func(input_path, mode, encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if max_records > 0 and i >= max_records:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                    records.append(record)
                except:
                    pass
        
        token_counts = []
        preview_data = []
        
        for record in records:
            text = ''
            if isinstance(text_field, str) and text_field in record:
                text = str(record[text_field])
            else:
                # If text_field not found, try common fields
                for field in ['text', 'content', 'instruction', 'input', 'output']:
                    if field in record:
                        text = str(record[field])
                        break
            
            if text:
                tokens = tokenizer.encode(text, add_special_tokens=False)
                token_counts.append(len(tokens))
                
                if preview_tokens and len(preview_data) < 5:
                    # Decode tokens back to strings for preview
                    decoded = tokenizer.convert_ids_to_tokens(tokens[:20])  # First 20 tokens
                    preview_data.append(decoded)
        
        result = {
            "success": True,
            "tokenizer": model_base,
            "record_count": len(records),
            "text_field": text_field
        }
        
        if token_counts:
            if calc_max_length:
                result["max_tokens"] = max(token_counts)
            if calc_avg_length:
                result["avg_tokens"] = round(sum(token_counts) / len(token_counts), 2)
            result["total_tokens"] = sum(token_counts)
        else:
            result["max_tokens"] = 0
            result["avg_tokens"] = 0
            result["total_tokens"] = 0
        
        if preview_tokens and preview_data:
            result["preview"] = preview_data
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


@app.route('/api/prep/validate', methods=['POST'])
def prep_validate():
    """Data Validation: memastikan format JSONL valid dan konsisten"""
    try:
        data = request.json
        input_path = data.get('input_path')
        validate_json = data.get('validate_json', True)
        validate_fields = data.get('validate_fields', True)
        validate_types = data.get('validate_types', False)
        validate_encoding = data.get('validate_encoding', True)
        required_fields = data.get('required_fields', [])
        max_records = data.get('max_records', 0)
        
        if not input_path or not os.path.exists(input_path):
            return jsonify({"error": "Input file not found"}), 404
        
        is_gz = input_path.lower().endswith('.gz')
        open_func = gzip.open if is_gz else open
        mode = 'rt' if is_gz else 'r'
        
        total_count = 0
        valid_count = 0
        invalid_count = 0
        errors = []
        
        # Detect encoding if needed
        if validate_encoding and not is_gz:
            try:
                with open(input_path, 'rb') as f:
                    raw_data = f.read()
                    try:
                        raw_data.decode('utf-8')
                    except UnicodeDecodeError:
                        return jsonify({"error": "File is not valid UTF-8 encoded"}), 400
            except Exception as e:
                return jsonify({"error": f"Encoding validation failed: {str(e)}"}), 500
        
        with open_func(input_path, mode, encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if max_records > 0 and i >= max_records:
                    break
                
                total_count += 1
                line_num = i + 1
                line_errors = []
                
                # Check if line is empty
                if not line.strip():
                    invalid_count += 1
                    errors.append({"line": line_num, "message": "Empty line"})
                    continue
                
                # Validate JSON syntax
                if validate_json:
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError as e:
                        invalid_count += 1
                        errors.append({"line": line_num, "message": f"Invalid JSON: {str(e)}"})
                        continue
                else:
                    try:
                        record = json.loads(line)
                    except:
                        invalid_count += 1
                        continue
                
                # Validate required fields
                if validate_fields and required_fields:
                    missing_fields = [f for f in required_fields if f not in record]
                    if missing_fields:
                        line_errors.append(f"Missing fields: {', '.join(missing_fields)}")
                
                # Validate data types (basic check)
                if validate_types and record:
                    for key, value in record.items():
                        if value is not None and not isinstance(value, (str, int, float, bool, list, dict)):
                            line_errors.append(f"Field '{key}' has unsupported type: {type(value).__name__}")
                
                if line_errors:
                    invalid_count += 1
                    for err in line_errors[:3]:  # Limit errors per line
                        errors.append({"line": line_num, "message": err})
                else:
                    valid_count += 1
        
        success_rate = round(valid_count / total_count * 100, 2) if total_count > 0 else 0
        
        # Limit error display
        display_errors = errors[:50]  # Show max 50 errors
        
        return jsonify({
            "success": True,
            "total_count": total_count,
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "success_rate": success_rate,
            "errors": display_errors,
            "total_errors": len(errors)
        })
        
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# Settings management endpoints
SETTINGS_FILE = os.path.join(os.getcwd(), '.xtools_settings.json')

def load_settings():
    """Load settings from JSON file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_settings(settings):
    """Save settings to JSON file"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if SECURITY_ENABLED:
            # Check for lockout
            is_locked, remaining = token_security.check_lockout()
            if is_locked:
                return jsonify({
                    "success": False, 
                    "error": f"Too many failed attempts. Try again in {remaining} seconds."
                }), 429
        return f(*args, **kwargs)
    return decorated_function

@app.route('/settings')
@require_auth
def settings_page():
    return render_template('settings.html', active_page='settings')

@app.route('/api/settings', methods=['GET'])
@require_auth
def get_settings():
    """Get all settings"""
    try:
        settings = load_settings()
        # Mask sensitive data for display
        display_settings = settings.copy()
        if 'hf_token' in display_settings and display_settings['hf_token']:
            # Show only first 4 and last 4 characters
            display_settings['hf_token'] = 'hf_****...****'
        
        # Add security info
        display_settings['security_enabled'] = SECURITY_ENABLED
        display_settings['lockout_status'] = 'locked' if (SECURITY_ENABLED and token_security.check_lockout()[0]) else 'ok'
        
        return jsonify({"success": True, "settings": display_settings})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings', methods=['POST'])
@require_auth
def save_settings_api():
    """Save settings"""
    try:
        data = request.json
        current_settings = load_settings()
        
        # Update settings
        if 'hf_token' in data:
            token = data['hf_token']
            # Only update if not masked (user entered new token)
            if not token.startswith('*'):
                # Validate token format
                if SECURITY_ENABLED:
                    is_valid, error_msg = token_security.validate_token_format(token)
                    if not is_valid:
                        token_security.record_failed_attempt()
                        token_security.audit_log('token_validation_failed', {'error': error_msg})
                        return jsonify({"success": False, "error": error_msg}), 400
                
                # Encrypt token if security is enabled
                if SECURITY_ENABLED:
                    encrypted = token_security.encrypt_token(token)
                    if encrypted:
                        current_settings['hf_token'] = encrypted
                        current_settings['token_hash'] = token_security.hash_token(token)
                        current_settings['token_saved_at'] = time.time()
                        token_security.audit_log('token_saved', {'hash_prefix': token[:8]})
                    else:
                        return jsonify({"success": False, "error": "Failed to encrypt token"}), 500
                else:
                    # Fallback: store plain (not recommended)
                    current_settings['hf_token'] = token
                    current_settings['token_hash'] = hashlib.sha256(token.encode()).hexdigest()[:16]
        
        # Save other settings
        for key, value in data.items():
            if key not in ['hf_token', 'token_hash']:
                current_settings[key] = value
        
        if save_settings(current_settings):
            return jsonify({"success": True, "message": "Settings saved successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to save settings"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/settings/token', methods=['GET'])
def get_token():
    """Get HF token (for internal use) - checks env var first, then encrypted storage"""
    try:
        # Priority 1: Environment variable (most secure for production)
        if SECURITY_ENABLED:
            env_token = token_security.get_token_from_env()
            if env_token:
                token_security.audit_log('token_retrieved_from_env')
                return jsonify({"success": True, "token": env_token, "source": "environment"})
        else:
            env_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGINGFACE_TOKEN')
            if env_token:
                return jsonify({"success": True, "token": env_token, "source": "environment"})
        
        # Priority 2: Encrypted storage
        settings = load_settings()
        encrypted_token = settings.get('hf_token', '')
        
        if encrypted_token:
            # Decrypt if security is enabled
            if SECURITY_ENABLED:
                decrypted = token_security.decrypt_token(encrypted_token)
                if decrypted:
                    token_security.audit_log('token_retrieved_from_storage')
                    return jsonify({"success": True, "token": decrypted, "source": "encrypted_storage"})
                else:
                    token_security.audit_log('token_decryption_failed')
                    return jsonify({"success": False, "error": "Failed to decrypt token"}), 500
            else:
                # Fallback: assume plaintext
                return jsonify({"success": True, "token": encrypted_token, "source": "storage"})
        
        return jsonify({"success": True, "token": "", "source": "none"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/security/status', methods=['GET'])
def security_status():
    """Get security status"""
    try:
        status = {
            "security_enabled": SECURITY_ENABLED,
            "encryption_available": SECURITY_ENABLED,
            "environment_token_available": bool(os.environ.get('HF_TOKEN') or os.environ.get('HUGGINGFACE_TOKEN')),
        }
        
        if SECURITY_ENABLED:
            is_locked, remaining = token_security.check_lockout()
            status['lockout_active'] = is_locked
            status['lockout_remaining'] = remaining if is_locked else 0
            status['max_attempts'] = token_security.max_attempts
            status['lockout_duration'] = token_security.lockout_duration
        
        return jsonify({"success": True, "security": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/security/audit-log', methods=['GET'])
def get_audit_log():
    """Get recent audit log entries"""
    try:
        if not SECURITY_ENABLED:
            return jsonify({"success": False, "error": "Security features not enabled"}), 400
        
        log_file = token_security.audit_log_file
        if not os.path.exists(log_file):
            return jsonify({"success": True, "logs": []})
        
        # Read last 100 entries
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        logs = []
        for line in lines[-100:]:
            try:
                logs.append(json.loads(line.strip()))
            except:
                pass
        
        return jsonify({"success": True, "logs": logs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/security/clear-lockout', methods=['POST'])
def clear_lockout():
    """Clear lockout status (for admin use)"""
    try:
        if SECURITY_ENABLED:
            token_security._reset_lockout()
            token_security.audit_log('lockout_cleared')
        return jsonify({"success": True, "message": "Lockout cleared"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# Cache management endpoints
@app.route('/api/cache/clear', methods=['POST'])
def cache_clear():
    try:
        res = hf_handler.clear_cache()
        status = 200 if res.get('success') else 500
        return jsonify(res), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cache/status', methods=['GET'])
def cache_status():
    try:
        return jsonify(hf_handler.cache_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Running on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
