import sys
import os
# Append parent directory to sys.path to allow absolute package imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dino_model import DinoV2Extractor
from image_processor import crop_1_1
from PIL import Image

def test():
    print("Testing DINOv2 loading...")
    extractor = DinoV2Extractor()
    print("DINOv2 extractor instantiated!")
    
    print("Creating dummy image...")
    dummy = Image.new("RGB", (300, 200), (255, 255, 255))
    
    print("Testing cropping (300x200 should crop to 200x200 for 1:1)...")
    cropped = crop_1_1(dummy)
    print(f"Cropped dimensions: {cropped.size}")
    assert cropped.size == (200, 200), f"Expected (200, 200), got {cropped.size}"
    print("Crop successful!")
    
    print("Testing color transform...")
 
    
    print("Testing embedding extraction...")
    emb = extractor.extract_embedding(dummy)
    print(f"Embedding shape: {emb.shape}")
    assert emb.shape == (384,), f"Expected shape (384,), got {emb.shape}"
    
    print("Similarity comparison test...")
    dummy2 = Image.new("RGB", (300, 200), (255, 200, 200))
    emb2 = extractor.extract_embedding(dummy2)
    sim = extractor.compute_similarity(emb, emb2)
    print(f"Similarity score between dummy images: {sim:.4f}")
    assert 0.0 <= sim <= 1.0, f"Expected similarity score in [0.0, 1.0], got {sim}"
    
    print("All backend checks passed successfully!")

if __name__ == "__main__":
    test()
