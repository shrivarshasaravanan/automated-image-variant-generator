# Automated Image Variant Generator

The **Automated Image Variant Generator** is a full-stack AI application that automatically produces multiple visual variations of a master image (such as aspect ratio crops, color overlays, background swaps, and style parameters) while ensuring strict design consistency using Meta AI's **DINOv2** visual embeddings.

Variants are screened using PyTorch cosine similarity check and filtered out if they fall below a user-defined threshold (default $\ge 0.90$).

---

## Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                                 REACT FRONTEND (Vite)                             |
|  - Custom CSS Glassmorphism UI                                                    |
|  - Image Upload Drag & Drop & Metadata Inspector                                  |
|  - Option Panel (Crops, Colors, Background replacements, Sliders)                 |
|  - Dynamic Variant Gallery & Score Badges (High, Med, Low)                        |
|  - Archive ZIP downloader                                                         |
+-------------------------------------------------+---------------------------------+
                                                  |
                                       HTTP / JSON / FormData
                                                  |
                                                  v
+-------------------------------------------------+---------------------------------+
|                                 FASTAPI BACKEND                                   |
|  - RESTful Endpoints (/upload, /generate, /results, /download-zip)                |
|  - SQLite Database logs (SQLAlchemy ORM logging master images and variant paths) |
|  - In-Memory ZIP compressor                                                       |
+-------------------+-----------------------------+--------------------+------------+
                    |                                                  |
                    v                                                  v
+-------------------+-------------------------+    +-------------------+------------+
|             IMAGE PROCESSING MODULE         |    |            DINOv2 MODEL            |
|  - OpenCV GrabCut subject segmentation      |    |  - PyTorch Hub dinov2_vits14   |
|  - PIL ImageEnhance parameters              |    |  - Normalize with ImageNet     |
|  - Center aspect ratio cropping             |    |  - Cosine Similarity Filter    |
|  - Color channels shift & gradient builders |    |    (Threshold >= 0.90)         |
+---------------------------------------------+    +--------------------------------+
```

---

## Project Structure

```
automated-image-variant-generator/
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ImageUploader.jsx
│   │   │   ├── OptionsPanel.jsx
│   │   │   ├── VariantGallery.jsx
│   │   │   └── LoadingIndicator.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── index.html
│   └── vite.config.js
│
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── image_processor.py
│   ├── dino_model.py
│   ├── utils.py
│   ├── requirements.txt
│   ├── verify_backend.py
│   └── uploads/
│
├── outputs/
└── README.md
```

---

## Setup & Running Instructions

### 1. Prerequisite Checks
Make sure you have **Python 3.8+** and **Node.js 18+** installed.

### 2. Backend Installation & Run
Navigate to the `backend` directory, create a virtual environment, install requirements, and launch:

```bash
# Go to backend folder
cd backend

# (Optional) Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Verify the backend environment components
python verify_backend.py

# Run backend server (will run on http://localhost:8000)
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

*Note: The first time uvicorn starts or when variant generation is requested, the application loads Meta's `dinov2_vits14` model. PyTorch will fetch it from PyTorch Hub and cache it locally.*

### 3. Frontend Installation & Run
Navigate to the `frontend` directory, install packages, and boot up:

```bash
# Open a new terminal in the frontend directory
cd frontend

# Install package dependencies
npm install

# Run the React dev server (will start on http://localhost:5173 or similar)
npm run dev
```

Open your browser and navigate to the address shown in the output (typically `http://localhost:5173`).

---

## Core Features & Usage Guide

1. **Master Image Upload**: Drag & drop any product or portrait image. The app uploads the asset, logs dimensions, and displays the master photo in the preview panel.
2. **Select Variants**: Check the specific crop aspect ratios (1:1, 4:3, 16:9), color shifts (warm, cool, dark, custom brand tint), or background swaps (white studio, black studio, diagonal gradient, custom solid color) you want to generate.
3. **Refine Styles**: Adjust sliders for Brightness, Contrast, Saturation, or tweak the minimum DINOv2 Cosine Similarity Threshold (default 0.90).
4. **Generate & Filter**: Hit **Generate Variants**. The backend processes the images, computes embeddings, compares them to the master image, and filters out any variants with similarity scores below the threshold.
5. **Inspect & Download**: View the verified results in the gallery grid with similarity badges. Download any variant individually, or compile all approved variations into a single ZIP archive.
