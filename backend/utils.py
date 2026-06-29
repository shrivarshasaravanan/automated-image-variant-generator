import os
import zipfile
from io import BytesIO

def ensure_directories_exist():
    """Ensure that the backend uploads directory and global outputs directory exist."""
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(backend_dir)
    
    uploads_dir = os.path.join(backend_dir, "uploads")
    outputs_dir = os.path.join(project_root, "outputs")
    
    os.makedirs(uploads_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)
    
    return uploads_dir, outputs_dir

def create_zip_archive(variant_paths: list[str]) -> bytes:
    """Compress all provided variant files into a single ZIP archive in memory."""
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in variant_paths:
            if os.path.exists(file_path):
                arcname = os.path.basename(file_path)
                zip_file.write(file_path, arcname=arcname)
    return zip_buffer.getvalue()
