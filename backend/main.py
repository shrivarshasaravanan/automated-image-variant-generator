import os
import uuid
import shutil
from typing import List, Optional
from fastapi import FastAPI, Depends, UploadFile, File, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session
from PIL import Image

from database import engine, Base, get_db
from models import MasterImage, Variant
import image_processor
from dino_model import get_extractor
from utils import ensure_directories_exist, create_zip_archive

# Initialize DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Automated Image Variant Generator API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads and outputs folders exist
uploads_dir, outputs_dir = ensure_directories_exist()

# Mount uploads and outputs directories for static access
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")
app.mount("/outputs", StaticFiles(directory=outputs_dir), name="outputs")

# Request Pydantic Model for Variant Generation
class GenerateRequest(BaseModel):
    master_id: int
    aspect_ratios: List[str] = []       # "1:1", "4:3", "16:9"
    colors: List[str] = []              # "warm", "cool", "dark", "brand"
    brand_color: str = "#4f46e5"
    backgrounds: List[str] = []         # "white", "black", "gradient", "custom"
    custom_bg_color: str = "#f3f4f6"
    brightness_factor: float = 1.0
    contrast_factor: float = 1.0
    saturation_factor: float = 1.0
    num_variants: int = 5
    similarity_threshold: float = 0.90

@app.post("/upload")
async def upload_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image.")
    
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(uploads_dir, unique_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        with Image.open(file_path) as img:
            width, height = img.size
            img_format = img.format
            
        master_img = MasterImage(
            filename=file.filename,
            path=file_path,
            width=width,
            height=height,
            format=img_format
        )
        db.add(master_img)
        db.commit()
        db.refresh(master_img)
        
        return {
            "id": master_img.id,
            "filename": master_img.filename,
            "url": f"/uploads/{unique_filename}",
            "width": width,
            "height": height,
            "format": img_format,
            "uploaded_at": master_img.uploaded_at
        }
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/generate")
async def generate_variants(req: GenerateRequest, db: Session = Depends(get_db)):
    # 1. Fetch the master image
    master = db.query(MasterImage).filter(MasterImage.id == req.master_id).first()
    if not master:
        raise HTTPException(status_code=404, detail="Master image not found.")
        
    if not os.path.exists(master.path):
        raise HTTPException(status_code=404, detail="Master image file missing from server storage.")
        
    try:
        master_pil = Image.open(master.path).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open master image: {str(e)}")
        
    # 2. Get the DINOv2 extractor
    dino = get_extractor()
    master_embedding = dino.extract_embedding(master_pil)
    
    # 3. Define the recipe list
    recipes = []
    
    # -- Aspect Ratios --
    if "1:1" in req.aspect_ratios:
        recipes.append({
            "type": "crop_1_1", "ratio": "1:1", "palette": None,
            "name": "Square Crop (1:1)",
            "funcs": [image_processor.crop_1_1]
        })
    if "4:3" in req.aspect_ratios:
        recipes.append({
            "type": "crop_4_3", "ratio": "4:3", "palette": None,
            "name": "Landscape Crop (4:3)",
            "funcs": [image_processor.crop_4_3]
        })
    if "16:9" in req.aspect_ratios:
        recipes.append({
            "type": "crop_16_9", "ratio": "16:9", "palette": None,
            "name": "Banner Crop (16:9)",
            "funcs": [image_processor.crop_16_9]
        })
        
    # -- Colors --
    if "warm" in req.colors:
        recipes.append({
            "type": "color_warm", "ratio": "Original", "palette": "warm",
            "name": "Warm Tone Shift",
            "funcs": [image_processor.transform_warm_tone]
        })
    if "cool" in req.colors:
        recipes.append({
            "type": "color_cool", "ratio": "Original", "palette": "cool",
            "name": "Cool Tone Shift",
            "funcs": [image_processor.transform_cool_tone]
        })
    if "dark" in req.colors:
        recipes.append({
            "type": "color_dark", "ratio": "Original", "palette": "dark",
            "name": "Dark Mode Theme",
            "funcs": [image_processor.transform_dark_mode]
        })
    if "brand" in req.colors:
        recipes.append({
            "type": "color_brand", "ratio": "Original", "palette": "brand",
            "name": f"Brand Overlay ({req.brand_color})",
            "funcs": [lambda img: image_processor.transform_brand_palette(img, req.brand_color)]
        })
        
    # -- Backgrounds --
    if "white" in req.backgrounds:
        recipes.append({
            "type": "bg_white", "ratio": "Original", "palette": None,
            "name": "White Studio Background",
            "funcs": [image_processor.bg_replace_white]
        })
    if "black" in req.backgrounds:
        recipes.append({
            "type": "bg_black", "ratio": "Original", "palette": None,
            "name": "Black Studio Background",
            "funcs": [image_processor.bg_replace_black]
        })
    if "gradient" in req.backgrounds:
        recipes.append({
            "type": "bg_gradient", "ratio": "Original", "palette": None,
            "name": "Diagonal Gradient Background",
            "funcs": [image_processor.bg_replace_gradient]
        })
    if "custom" in req.backgrounds:
        recipes.append({
            "type": "bg_custom", "ratio": "Original", "palette": "custom",
            "name": f"Custom Background ({req.custom_bg_color})",
            "funcs": [lambda img: image_processor.bg_replace_custom(img, req.custom_bg_color)]
        })
        
    # -- Style Slider Adjustments (Only if sliders are set away from 1.0) --
    has_style_changes = (
        abs(req.brightness_factor - 1.0) > 0.01 or
        abs(req.contrast_factor - 1.0) > 0.01 or
        abs(req.saturation_factor - 1.0) > 0.01
    )
    if has_style_changes:
        recipes.append({
            "type": "style_adjust", "ratio": "Original", "palette": None,
            "name": "Brightness/Contrast/Saturation Adjust",
            "funcs": [
                lambda img: image_processor.adjust_brightness(img, req.brightness_factor),
                lambda img: image_processor.adjust_contrast(img, req.contrast_factor),
                lambda img: image_processor.adjust_saturation(img, req.saturation_factor)
            ]
        })

    # -- Combination Recipes (To hit num_variants if base recipes are fewer) --
    # Let's generate combinations: Crop + Color, Crop + Background, etc.
    active_crops = [r for r in recipes if r["type"].startswith("crop_")]
    active_colors = [r for r in recipes if r["type"].startswith("color_")]
    active_bgs = [r for r in recipes if r["type"].startswith("bg_")]
    
    # 1. Combine Crops with Colors
    for crop in active_crops:
        for color in active_colors:
            if len(recipes) >= req.num_variants:
                break
            recipes.append({
                "type": f"{crop['type']}_{color['type']}",
                "ratio": crop["ratio"],
                "palette": color["palette"],
                "name": f"{crop['name']} + {color['name']}",
                "funcs": crop["funcs"] + color["funcs"]
            })
            
    # 2. Combine Crops with Backgrounds
    for crop in active_crops:
        for bg in active_bgs:
            if len(recipes) >= req.num_variants:
                break
            recipes.append({
                "type": f"{crop['type']}_{bg['type']}",
                "ratio": crop["ratio"],
                "palette": bg["palette"],
                "name": f"{crop['name']} + {bg['name']}",
                "funcs": crop["funcs"] + bg["funcs"]
            })

    # 3. Combine Backgrounds with Colors
    for bg in active_bgs:
        for color in active_colors:
            if len(recipes) >= req.num_variants:
                break
            recipes.append({
                "type": f"{bg['type']}_{color['type']}",
                "ratio": "Original",
                "palette": color["palette"],
                "name": f"{bg['name']} + {color['name']}",
                "funcs": bg["funcs"] + color["funcs"]
            })

    # Cap recipes at the requested number of variants
    recipes = recipes[:req.num_variants]
    
    # If no options were selected and we have no recipes, add a default set to ensure we generate *something*
    if not recipes:
        recipes = [
            {
                "type": "crop_1_1", "ratio": "1:1", "palette": None,
                "name": "Square Crop (1:1) [Default]",
                "funcs": [image_processor.crop_1_1]
            },
            {
                "type": "color_warm", "ratio": "Original", "palette": "warm",
                "name": "Warm Tone Shift [Default]",
                "funcs": [image_processor.transform_warm_tone]
            },
            {
                "type": "bg_gradient", "ratio": "Original", "palette": None,
                "name": "Diagonal Gradient [Default]",
                "funcs": [image_processor.bg_replace_gradient]
            }
        ][:req.num_variants]

    # Delete any existing variants for this master image before regenerating
    old_variants = db.query(Variant).filter(Variant.master_id == master.id).all()
    for ov in old_variants:
        if os.path.exists(ov.path):
            try:
                os.remove(ov.path)
            except Exception:
                pass
        db.delete(ov)
    db.commit()

    generated_variants = []
    
    # 4. Generate variants, score them with DINOv2, filter and save
    for idx, recipe in enumerate(recipes):
        try:
            # Sequentially apply transformation functions
            temp_img = master_pil.copy()
            for fn in recipe["funcs"]:
                temp_img = fn(temp_img)
                
            # Create a unique filename for the variant
            unique_name = f"var_{master.id}_{idx}_{uuid.uuid4().hex[:8]}.jpg"
            save_path = os.path.join(outputs_dir, unique_name)
            
            # Save the processed image
            temp_img.save(save_path, format="JPEG", quality=95)
            
            # Calculate similarity score using DINOv2
            variant_embedding = dino.extract_embedding(temp_img)
            score = dino.compute_similarity(master_embedding, variant_embedding)
            
            # Filter based on similarity threshold
            if score >= req.similarity_threshold:
                # Add to DB
                var_record = Variant(
                    master_id=master.id,
                    filename=unique_name,
                    path=save_path,
                    variant_type=recipe["name"],
                    aspect_ratio=recipe["ratio"],
                    palette=recipe["palette"],
                    similarity_score=score
                )
                db.add(var_record)
                db.commit()
                db.refresh(var_record)
                
                generated_variants.append({
                    "id": var_record.id,
                    "filename": unique_name,
                    "url": f"/outputs/{unique_name}",
                    "variant_type": recipe["name"],
                    "aspect_ratio": recipe["ratio"],
                    "palette": recipe["palette"],
                    "similarity_score": score
                })
            else:
                # If similarity threshold is not met, delete the file and skip
                print(f"Rejected variant '{recipe['name']}' due to similarity score: {score:.4f} (threshold: {req.similarity_threshold})")
                if os.path.exists(save_path):
                    os.remove(save_path)
        except Exception as e:
            print(f"Failed to generate variant {recipe['name']}: {str(e)}")
            continue

    return {
        "master_id": master.id,
        "total_requested": len(recipes),
        "total_generated": len(generated_variants),
        "variants": generated_variants
    }

@app.get("/results/{master_id}")
async def get_results(master_id: int, db: Session = Depends(get_db)):
    variants = db.query(Variant).filter(Variant.master_id == master_id).all()
    results = []
    for var in variants:
        results.append({
            "id": var.id,
            "filename": var.filename,
            "url": f"/outputs/{var.filename}",
            "variant_type": var.variant_type,
            "aspect_ratio": var.aspect_ratio,
            "palette": var.palette,
            "similarity_score": var.similarity_score,
            "created_at": var.created_at
        })
    return results

@app.get("/download-zip/{master_id}")
async def download_zip(master_id: int, db: Session = Depends(get_db)):
    variants = db.query(Variant).filter(Variant.master_id == master_id).all()
    if not variants:
        raise HTTPException(status_code=404, detail="No variants found for this master image.")
        
    paths = [var.path for var in variants if os.path.exists(var.path)]
    if not paths:
        raise HTTPException(status_code=404, detail="No physical variant image files found.")
        
    zip_bytes = create_zip_archive(paths)
    
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=variants_master_{master_id}.zip"
        }
    )
