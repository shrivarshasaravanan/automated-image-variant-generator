import requests
import os
from PIL import Image

API_URL = "http://127.0.0.1:8001"

def run_e2e_test():
    print("--- Starting End-to-End API & AI Model Test ---")
    
    # 1. Create a dummy test image (simulate high-quality product photo with clear central subject)
    # We will create an image with a central red box on a white background
    img_path = "temp_test_image.jpg"
    img = Image.new("RGB", (400, 400), (255, 255, 255))
    pixels = img.load()
    # Draw a colored square in the center
    for x in range(100, 300):
        for y in range(100, 300):
            pixels[x, y] = (79, 70, 229) # Indigo color
    img.save(img_path, "JPEG")
    print(f"Created temporary local test image: {img_path}")
    
    try:
        # 2. Upload the master image
        print("\n1. Uploading master image to POST /upload...")
        with open(img_path, "rb") as f:
            files = {"file": (img_path, f, "image/jpeg")}
            resp = requests.post(f"{API_URL}/upload", files=files)
            
        assert resp.status_code == 200, f"Upload failed: {resp.text}"
        master_data = resp.json()
        master_id = master_data["id"]
        print(f"Upload successful! Master ID: {master_id}")
        print(f"Image Metadata: {master_data}")
        
        # 3. Generate image variants
        print("\n2. Launching variant generation on POST /generate...")
        payload = {
            "master_id": master_id,
            "aspect_ratios": ["1:1", "16:9"],
            "colors": ["warm", "cool", "brand"],
            "brand_color": "#ec4899",
            "backgrounds": ["gradient"],
            "brightness_factor": 1.1,
            "contrast_factor: ": 1.0,
            "saturation_factor": 1.0,
            "num_variants": 6,
            "similarity_threshold": 0.85 # Using 0.85 for testing to ensure items pass
        }
        
        resp = requests.post(f"{API_URL}/generate", json=payload)
        assert resp.status_code == 200, f"Generation failed: {resp.text}"
        gen_data = resp.json()
        print(f"Generation successful! Generated {gen_data['total_generated']} variants out of {gen_data['total_requested']} requested.")
        
        for idx, variant in enumerate(gen_data["variants"]):
            print(f"  - Variant {idx+1}: {variant['variant_type']} | Similarity: {variant['similarity_score']:.4f} | URL: {variant['url']}")
            
        # 4. Fetch results from DB
        print(f"\n3. Fetching logged results from GET /results/{master_id}...")
        resp = requests.get(f"{API_URL}/results/{master_id}")
        assert resp.status_code == 200, f"Fetch failed: {resp.text}"
        db_results = resp.json()
        print(f"Found {len(db_results)} records in database for Master ID {master_id}.")
        assert len(db_results) == gen_data["total_generated"], "Database variant count mismatch!"
        
        # 5. Download the ZIP file
        print(f"\n4. Downloading ZIP archive from GET /download-zip/{master_id}...")
        resp = requests.get(f"{API_URL}/download-zip/{master_id}")
        assert resp.status_code == 200, f"ZIP download failed: {resp.text}"
        zip_len = len(resp.content)
        print(f"ZIP file downloaded successfully! Size: {zip_len} bytes.")
        assert zip_len > 1000, "ZIP archive seems empty or corrupted."
        
        print("\n--- E2E API and Model Verification PASSED ---")
        
    finally:
        # Clean up temporary test file
        if os.path.exists(img_path):
            os.remove(img_path)
            print(f"Removed temporary local test image: {img_path}")

if __name__ == "__main__":
    run_e2e_test()
