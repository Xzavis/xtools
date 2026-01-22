from huggingface_hub import HfApi
import json
import os
from urllib.parse import quote
from huggingface_hub import HfApi, hf_hub_download

class HFHandler:
    def __init__(self):
        self.api = HfApi()

    def scan_repo(self, repo_id, token=None, repo_type="model"):
        """
        Scans a repository and returns a list of files with metadata,
        grouped by extension.
        """
        try:
            # Attempt to list repo tree (most efficient)
            # Passing token explicitly to the method
            tree_iter = self.api.list_repo_tree(
                repo_id=repo_id, 
                repo_type=repo_type, 
                recursive=True, 
                token=token
            )
            
            all_files = []
            extensions = {}

            for item in tree_iter:
                if hasattr(item, 'size') and item.size is not None:
                    # It's a file
                    ext = item.path.split('.')[-1].lower() if '.' in item.path else 'unknown'
                    file_info = {
                        "path": item.path,
                        "size": item.size,
                        "extension": ext
                    }
                    all_files.append(file_info)

                    # Group stats
                    if ext not in extensions:
                        extensions[ext] = {"count": 0, "total_size": 0}
                    extensions[ext]["count"] += 1
                    extensions[ext]["total_size"] += item.size

            return {
                "success": True,
                "files": all_files,
                "extensions": extensions,
                "total_files": len(all_files)
            }

        except Exception as e:
            return {
                "success": False, 
                "error": str(e)
            }

    def generate_browser_links(self, repo_id, file_paths, repo_type="model"):
        """
        Generates direct download URLs for the browser.
        """
        links = []
        prefix = "datasets/" if repo_type == "dataset" else ""
        base_url = f"https://huggingface.co/{prefix}{repo_id}/resolve/main"
        
        for path in file_paths:
            # Properly quote the path for URLs and add download param
            safe_path = quote(path)
            links.append(f"{base_url}/{safe_path}?download=true")
            
        return links

    def download_files_to_local(self, repo_id, files, local_dir, token=None, repo_type="model"):
        """
        Generator function to download files sequentially to a local directory.
        Yields progress messages.
        """
        try:
            if not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)
            
            total_files = len(files)
            yield json.dumps({"type": "info", "message": f"Starting local download of {total_files} files to {local_dir}..."}) + "\n"

            for index, filename in enumerate(files):
                try:
                    yield json.dumps({"type": "progress", "message": f"[{index+1}/{total_files}] Downloading {filename}...", "file": filename}) + "\n"
                    
                    hf_hub_download(
                        repo_id=repo_id,
                        filename=filename,
                        local_dir=local_dir,
                        repo_type=repo_type,
                        token=token
                    )
                    
                    yield json.dumps({"type": "success", "message": f"Completed: {filename}"}) + "\n"
                except Exception as e:
                    yield json.dumps({"type": "error", "message": f"Failed {filename}: {str(e)}"}) + "\n"
            
            yield json.dumps({"type": "done", "message": "All downloads finished."}) + "\n"

        except Exception as e:
            yield json.dumps({"type": "error", "message": f"Critical Error: {str(e)}"}) + "\n"
