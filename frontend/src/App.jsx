import React, { useState } from "react";
import axios from "axios";
import ImageUploader from "./components/ImageUploader";
import OptionsPanel from "./components/OptionsPanel";
import VariantGallery from "./components/VariantGallery";
import LoadingIndicator from "./components/LoadingIndicator";
import "./App.css";

const API_BASE_URL = "http://localhost:8001";

function App() {
  const [masterImage, setMasterImage] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [variants, setVariants] = useState([]);
  const [error, setError] = useState(null);

  // Option selections
  const [aspectRatios, setAspectRatios] = useState({
    "1:1": true,
    "4:3": false,
    "16:9": false,
  });
  const [colors, setColors] = useState({
    warm: false,
    cool: false,
    dark: false,
    brand: false,
  });
  const [brandColor, setBrandColor] = useState("#6366f1");
  const [backgrounds, setBackgrounds] = useState({
    white: false,
    black: false,
    gradient: false,
    custom: false,
  });
  const [customBgColor, setCustomBgColor] = useState("#38bdf8");
  
  // Style and evaluation options
  const [brightness, setBrightness] = useState(1.0);
  const [contrast, setContrast] = useState(1.0);
  const [saturation, setSaturation] = useState(1.0);
  const [numVariants, setNumVariants] = useState(5);
  const [threshold, setThreshold] = useState(0.90);

  const handleUpload = async (file) => {
    setIsUploading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      setMasterImage(response.data);
      // Clear variants from any previous master image
      setVariants([]);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "Failed to upload master image. Ensure the backend server is running on port 8000.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleClearMaster = () => {
    setMasterImage(null);
    setVariants([]);
    setError(null);
  };

  const handleGenerate = async () => {
    if (!masterImage) return;
    setIsGenerating(true);
    setError(null);

    const payload = {
      master_id: masterImage.id,
      aspect_ratios: Object.keys(aspectRatios).filter(k => aspectRatios[k]),
      colors: Object.keys(colors).filter(k => colors[k]),
      brand_color: brandColor,
      backgrounds: Object.keys(backgrounds).filter(k => backgrounds[k]),
      custom_bg_color: customBgColor,
      brightness_factor: brightness,
      contrast_factor: contrast,
      saturation_factor: saturation,
      num_variants: numVariants,
      similarity_threshold: threshold,
    };

    try {
      const response = await axios.post(`${API_BASE_URL}/generate`, payload);
      setVariants(response.data.variants);
      if (response.data.variants.length === 0) {
        setError(`All generated variants scored below the similarity threshold of ${threshold}. Try reducing the threshold slider or choosing lighter modifications.`);
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || "An error occurred while generating image variants.");
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadAllZip = () => {
    if (!masterImage || variants.length === 0) return;
    // Trigger direct browser download of generated ZIP archive
    window.location.href = `${API_BASE_URL}/download-zip/${masterImage.id}`;
  };

  return (
    <div className="app-container">
      <header>
        <h1 className="brand-title">Automated Image Variant Generator</h1>
        <p className="brand-subtitle">
          Synthesize crop, color, and background variants validated against Meta DINOv2 embeddings
        </p>
      </header>

      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '12px',
          color: '#fca5a5',
          padding: '1rem 1.25rem',
          marginBottom: '2rem',
          fontSize: '0.875rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <span><strong>Error:</strong> {error}</span>
          <button
            onClick={() => setError(null)}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#fca5a5',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '1rem'
            }}
          >
            ✕
          </button>
        </div>
      )}

      <div className="main-layout">
        <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
          <ImageUploader
            masterImage={masterImage}
            isUploading={isUploading}
            onUpload={handleUpload}
            onClear={handleClearMaster}
          />
          <OptionsPanel
            aspectRatios={aspectRatios}
            setAspectRatios={setAspectRatios}
            colors={colors}
            setColors={setColors}
            brandColor={brandColor}
            setBrandColor={setBrandColor}
            backgrounds={backgrounds}
            setBackgrounds={setBackgrounds}
            customBgColor={customBgColor}
            setCustomBgColor={setCustomBgColor}
            brightness={brightness}
            setBrightness={setBrightness}
            contrast={contrast}
            setContrast={setContrast}
            saturation={saturation}
            setSaturation={setSaturation}
            numVariants={numVariants}
            setNumVariants={setNumVariants}
            threshold={threshold}
            setThreshold={setThreshold}
            onGenerate={handleGenerate}
            disabled={!masterImage || isGenerating || isUploading}
          />
        </div>

        <div className="glass-panel" style={{ padding: "1.5rem", minHeight: "500px" }}>
          {isGenerating ? (
            <LoadingIndicator progressText="Synthesizing and evaluating image variants..." />
          ) : (
            <VariantGallery
              variants={variants}
              onDownloadAllZip={handleDownloadAllZip}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
