import torch
import torchvision.transforms as T
from PIL import Image
import numpy as np

class DinoV2Extractor:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading DINOv2 model on {self.device}...")
        # Use PyTorch Hub cache if available, download if not
        self.model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')
        self.model.to(self.device)
        self.model.eval()
        
        # Preprocessing transforms: DINOv2 requires image sizing to be divisible by 14.
        # Standard input size is 224x224.
        self.transforms = T.Compose([
            T.Resize((224, 224)),
            T.ToTensor(),
            T.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
        print("DINOv2 model loaded successfully!")

    def extract_embedding(self, image_or_path):
        """
        Extract normalized embedding vector for a given image or path.
        """
        try:
            if isinstance(image_or_path, str):
                image = Image.open(image_or_path).convert("RGB")
            elif isinstance(image_or_path, Image.Image):
                image = image_or_path.convert("RGB")
            else:
                raise ValueError("Input must be a file path or a PIL Image object")

            # Apply transforms and add batch dimension
            tensor = self.transforms(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                features = self.model(tensor)
                # DINOv2 returns a tensor of shape [1, 384] for dinov2_vits14
                embedding = features.squeeze(0).cpu().numpy()
                
                # Normalize embedding to unit length
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                return embedding
        except Exception as e:
            print(f"Error extracting embedding: {e}")
            raise e

    def compute_similarity(self, emb1, emb2):
        """
        Compute cosine similarity between two normalized embedding vectors.
        """
        # Cosine similarity is the dot product when vectors are normalized to unit length
        return float(np.dot(emb1, emb2))

# Instantiate a global extractor to avoid reloading the model on every API call
extractor = None

def get_extractor():
    global extractor
    if extractor is None:
        extractor = DinoV2Extractor()
    return extractor
