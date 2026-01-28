from huggingface_hub import HfApi, hf_hub_download, list_models, list_datasets
import json
import os
import time
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
import queue

class HFHandler:
    def __init__(self):
        self.api = HfApi()
        self.cache_file = os.path.join(os.getcwd(), ".xtools_cache.json")
        # ensure cache file exists with initial structure
        if not os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump({"cache": {}}, f)
            except Exception:
                pass
        self._cache = {}

    def _load_cache_from_disk(self, key, ttl):
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            cache = content.get("cache", {})
            entry = cache.get(key)
            if not entry:
                return None
            if ttl is not None and (time.time() - entry.get('ts', 0) > ttl):
                return None
            return entry.get('value')
        except Exception:
            return None

    def _save_cache_to_disk(self, key, value):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.cache_file)), exist_ok=True)
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    content = json.load(f)
            else:
                content = {"cache": {}}
        except Exception:
            content = {"cache": {}}
        
        if "cache" not in content:
            content["cache"] = {}
            
        content["cache"][key] = {"ts": time.time(), "value": value}
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=4)
        except Exception as e:
            print(f"Error saving cache to disk: {e}")
    def clear_cache(self):
        """
        Clear both in-memory and on-disk caches.
        """
        self._cache = {}
        try:
            if os.path.exists(self.cache_file):
                os.remove(self.cache_file)
        except Exception:
            pass
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({"cache": {}}, f)
        except Exception:
            pass
        return {"success": True, "message": "Cache cleared"}

    def cache_status(self):
        """
        Return basic cache status (disk + memory).
        """
        disk_entries = 0
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            cache = content.get("cache", {})
            disk_entries = len(cache)
        except Exception:
            disk_entries = 0
        memory_entries = len(self._cache)
        return {"success": True, "disk_entries": disk_entries, "memory_entries": memory_entries}

    def search_repositories(self, query, limit=20, sort="downloads", direction=-1, repo_type="model"):
        """
        Search HuggingFace for models or datasets.
        """
        try:
            if repo_type == "model":
                results = list_models(
                    search=query,
                    sort=sort,
                    direction=direction,
                    limit=limit,
                    full=False
                )
            else:
                # FIX: Use self.api.list_datasets explicitly and ensure sort/direction logic is compatible.
                # list_datasets uses 'direction' for ascending/descending, but 'sort' might need mapping.
                # Default sort for datasets is often 'lastModified' or 'downloads'.
                
                # The direction parameter in list_models/list_datasets seems to be 1 for ascending, -1 for descending.
                # For datasets, we use the API directly to ensure consistency.
                
                sort_by = sort
                if sort == "downloads":
                    sort_by = "downloads"
                elif sort == "lastModified":
                    sort_by = "lastModified"

                results = self.api.list_datasets(
                    search=query,
                    sort=sort_by,
                    direction=direction,
                    limit=limit
                )
            
            data = []
            for r in results:
                # Handle different object structures
                item = {
                    "id": r.id,
                    "tags": getattr(r, 'tags', []),
                    "author": r.id.split('/')[0] if '/' in r.id else r.id,
                    "downloads": r.cardData.get('downloads', 0) if hasattr(r, 'cardData') and r.cardData else 0,
                    "lastModified": r.lastModified.isoformat() if hasattr(r, 'lastModified') and r.lastModified else None
                }
                data.append(item)
            return {"success": True, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def scan_repo(self, repo_id, token=None, repo_type="model", options=None):
        """
        Scans a repository and returns a list of files with metadata.
        Supports caching and optional filtering by extension.
        """
        opts = options or {}
        ttl = int(opts.get('cache_ttl', 300))
        use_cache = bool(opts.get('cache', False))
        refresh = bool(opts.get('refresh', False))
        filter_exts = opts.get('filter_exts')
        filter_exts = set([e.lower() for e in filter_exts]) if filter_exts else None

        actual_token = token if token and str(token).strip() else None
        cache_key = f"{repo_id}:{actual_token}:{repo_type}"

        # Return cached result if requested
        if use_cache and not refresh:
            cached = self._load_cache_from_disk(cache_key, ttl)
            if cached:
                data = cached
                # Apply filtering on cached data if needed
                if filter_exts:
                    filtered_files = [f for f in data['files'] if f['extension'] in filter_exts]
                    # Recompute extensions summary for filtered set
                    extensions_filtered = {}
                    for f in filtered_files:
                        ext = f['extension']
                        if ext not in extensions_filtered:
                            extensions_filtered[ext] = {"count": 0, "total_size": 0}
                        extensions_filtered[ext]["count"] += 1
                        extensions_filtered[ext]["total_size"] += int(f['size'])
                    data = {
                        "success": True,
                        "files": filtered_files,
                        "extensions": extensions_filtered,
                        "total_files": len(filtered_files),
                        "from_cache": True
                    }
                else:
                    data = {**data, "from_cache": True}
                return data

        # No usable cache, perform real scan
        try:
            tree_iter = self.api.list_repo_tree(
                recursive=True,
                repo_id=repo_id,
                repo_type=repo_type,
                token=actual_token
            )
            all_files = []
            extensions = {}

            for item in tree_iter:
                # Support both dict-like and object-like items
                if isinstance(item, dict):
                    path = item.get('path')
                    size = item.get('size')
                else:
                    path = getattr(item, 'path', None)
                    size = getattr(item, 'size', None)

                if not path:
                    continue
                # Skip directories or unknown sizes
                if size is None:
                    continue

                ext = path.split('.')[-1].lower() if '.' in path else 'unknown'
                if path.lower().endswith('.jsonl.gz'):
                    ext = 'jsonl.gz'
                elif path.lower().endswith('.tar.gz'):
                    ext = 'tar.gz'

                file_info = {"path": path, "size": int(size), "extension": ext}
                all_files.append(file_info)

                if ext not in extensions:
                    extensions[ext] = {"count": 0, "total_size": 0}
                extensions[ext]["count"] += 1
                extensions[ext]["total_size"] += int(size)

            all_files.sort(key=lambda x: x['path'])
            data = {"success": True, "files": all_files, "extensions": extensions, "total_files": len(all_files)}

            if use_cache:
                self._save_cache_to_disk(cache_key, data)

            if filter_exts:
                filtered_files = [f for f in all_files if f['extension'] in filter_exts]
                extensions_filtered = {}
                for f in filtered_files:
                    ext = f['extension']
                    if ext not in extensions_filtered:
                        extensions_filtered[ext] = {"count": 0, "total_size": 0}
                    extensions_filtered[ext]["count"] += 1
                    extensions_filtered[ext]["total_size"] += int(f['size'])
                data = {
                    "success": True,
                    "files": filtered_files,
                    "extensions": extensions_filtered,
                    "total_files": len(filtered_files),
                    "from_cache": False
                }

            return data

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_browser_links(self, repo_id, file_paths, repo_type="model"):
        """
        Generates direct download URLs for the browser.
        """
        links = []
        prefix = "datasets/" if repo_type == "dataset" else ""
        base_url = f"https://huggingface.co/{prefix}{repo_id}/resolve/main"
        
        for path in file_paths:
            safe_path = quote(path)
            links.append(f"{base_url}/{safe_path}?download=true")
            
        return links

    def estimate_total_size(self, repo_id, files, repo_type="model", token=None):
        """Estimate total size for a given list of file names by inspecting repo tree."""
        actual_token = token if token and token.strip() else None
        try:
            tree_iter = self.api.list_repo_tree(
                recursive=True,
                repo_id=repo_id,
                repo_type=repo_type,
                token=actual_token
            )
            requested = set([f if isinstance(f, str) else str(f) for f in files])
            total = 0
            found = False
            for item in tree_iter:
                if isinstance(item, dict):
                    path = item.get('path')
                    size = item.get('size')
                else:
                    path = getattr(item, 'path', None)
                    size = getattr(item, 'size', None)
                if not path or size is None:
                    continue
                name_only = os.path.basename(path)
                if path in requested or name_only in requested:
                    total += int(size)
                    found = True
            return total if found else None
        except Exception:
            return None

    def download_files_to_local(self, repo_id, files, local_dir, token=None, repo_type="model", max_workers=5):
        """
        Generator function to download files concurrently with robust retry logic.
        """
        try:
            actual_token = token if token and token.strip() else None
            local_dir = os.path.abspath(local_dir)
            # Create full path and ensure we have write permissions
            if not os.path.exists(local_dir):
                try:
                    os.makedirs(local_dir, exist_ok=True)
                except Exception as e:
                    yield json.dumps({"type": "error", "message": f"Failed to create directory {local_dir}: {str(e)}"}) + "\n"
                    return
            
            total_files = len(files)
            
            # Estimate total size for start event if possible
            estimated_size = None
            if files:
                estimated_size = self.estimate_total_size(repo_id, files, repo_type, actual_token)

            # Emit start event
            yield json.dumps({
                "type": "start", 
                "total_files": total_files, 
                "total_size": estimated_size, 
                "message": f"Starting parallel transfer of {total_files} objects using {max_workers} threads..."
            }) + "\n"

            # Thread-safe queue for status updates
            status_queue = queue.Queue()

            def _download_worker(filename):
                attempts = 0
                max_retries = 3
                success = False
                
                while not success and attempts < max_retries:
                    attempts += 1
                    try:
                        status_queue.put({"type": "progress", "file": filename, "status": "Downloading..."})
                        
                        hf_hub_download(
                            repo_id=repo_id,
                            filename=filename,
                            repo_type=repo_type,
                            local_dir=local_dir,
                            token=actual_token,
                            local_dir_use_symlinks=False
                        )
                        success = True
                        status_queue.put({"type": "success", "file": filename})
                    except Exception as e:
                        if attempts < max_retries:
                            wait_time = 2 ** attempts
                            status_queue.put({"type": "warning", "file": filename, "message": f"Retry {attempts}/{max_retries}: {str(e)}"})
                            time.sleep(wait_time)
                        else:
                            status_queue.put({"type": "error", "file": filename, "error": str(e)})

            # Start ThreadPool
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                futures = {executor.submit(_download_worker, f): f for f in files}
                
                # Monitor queue until all tasks are done
                completed_count = 0
                while completed_count < total_files:
                    try:
                        # Non-blocking get with timeout to keep yielding alive
                        msg = status_queue.get(timeout=0.1)
                        
                        if msg['type'] == 'success':
                            completed_count += 1
                            yield json.dumps({"type": "success", "message": f"Completed: {msg['file']}"}) + "\n"
                        elif msg['type'] == 'error':
                            completed_count += 1
                            yield json.dumps({"type": "error", "message": f"FAILED: {msg['file']} - {msg['error']}"}) + "\n"
                        elif msg['type'] == 'progress':
                             yield json.dumps({
                                "type": "progress", 
                                "message": f"Downloading: {msg['file']}",
                                "file": msg['file']
                            }) + "\n"
                        elif msg['type'] == 'warning':
                            yield json.dumps({
                                "type": "warning",
                                "message": f"Warning [{msg['file']}]: {msg['message']}"
                            }) + "\n"
                            
                    except queue.Empty:
                        # Check if all futures are done (just in case)
                        if all(f.done() for f in futures):
                             if status_queue.empty():
                                 break
                        continue

            yield json.dumps({"type": "done", "total_files": total_files, "message": "ALL_TRANSFERS_COMPLETED"}) + "\n"

        except Exception as e:
            yield json.dumps({"type": "error", "message": f"FATAL_SYSTEM_ERROR: {str(e)}"}) + "\n"