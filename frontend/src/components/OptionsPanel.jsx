import React from "react";
import { Sliders, Maximize, Palette, Layers, Sparkles } from "lucide-react";

export default function OptionsPanel({
  aspectRatios,
  setAspectRatios,
  colors,
  setColors,
  brandColor,
  setBrandColor,
  backgrounds,
  setBackgrounds,
  customBgColor,
  setCustomBgColor,
  brightness,
  setBrightness,
  contrast,
  setContrast,
  saturation,
  setSaturation,
  numVariants,
  setNumVariants,
  threshold,
  setThreshold,
  onGenerate,
  disabled
}) {

  const toggleAspectRatio = (ratio) => {
    setAspectRatios(prev => ({ ...prev, [ratio]: !prev[ratio] }));
  };

  const toggleColor = (color) => {
    setColors(prev => ({ ...prev, [color]: !prev[color] }));
  };

  const toggleBackground = (bg) => {
    setBackgrounds(prev => ({ ...prev, [bg]: !prev[bg] }));
  };

  return (
    <div className="glass-panel options-container">
      {/* Aspect Ratios Section */}
      <div>
        <h3 className="section-title">
          <Maximize size={16} />
          Aspect Ratios
        </h3>
        <div className="checkbox-grid">
          {["1:1", "4:3", "16:9"].map(ratio => (
            <label key={ratio} className="custom-checkbox">
              <input
                type="checkbox"
                checked={aspectRatios[ratio]}
                onChange={() => toggleAspectRatio(ratio)}
              />
              <span className="checkbox-tile">
                <span>{ratio}</span>
                <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4 }}>
                  {ratio === "1:1" ? "Square" : ratio === "4:3" ? "Landscape" : "Banner"}
                </span>
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Colors Section */}
      <div>
        <h3 className="section-title">
          <Palette size={16} />
          Color Transformations
        </h3>
        <div className="checkbox-grid">
          {[
            { key: "warm", label: "Warm Tone" },
            { key: "cool", label: "Cool Tone" },
            { key: "dark", label: "Dark Mode" },
            { key: "brand", label: "Brand Overlay" }
          ].map(c => (
            <label key={c.key} className="custom-checkbox">
              <input
                type="checkbox"
                checked={colors[c.key]}
                onChange={() => toggleColor(c.key)}
              />
              <span className="checkbox-tile">{c.label}</span>
            </label>
          ))}
        </div>
        
        {colors.brand && (
          <div className="color-picker-wrapper">
            <span className="color-picker-label">Brand Color:</span>
            <input
              type="color"
              className="color-input"
              value={brandColor}
              onChange={(e) => setBrandColor(e.target.value)}
            />
            <input
              type="text"
              className="text-input"
              value={brandColor}
              onChange={(e) => setBrandColor(e.target.value)}
              placeholder="#4f46e5"
            />
          </div>
        )}
      </div>

      {/* Background Section */}
      <div>
        <h3 className="section-title">
          <Layers size={16} />
          Background Replacement
        </h3>
        <div className="checkbox-grid">
          {[
            { key: "white", label: "White Studio" },
            { key: "black", label: "Black Studio" },
            { key: "gradient", label: "Gradient" },
            { key: "custom", label: "Custom Solid" }
          ].map(bg => (
            <label key={bg.key} className="custom-checkbox">
              <input
                type="checkbox"
                checked={backgrounds[bg.key]}
                onChange={() => toggleBackground(bg.key)}
              />
              <span className="checkbox-tile">{bg.label}</span>
            </label>
          ))}
        </div>

        {backgrounds.custom && (
          <div className="color-picker-wrapper">
            <span className="color-picker-label">Custom BG:</span>
            <input
              type="color"
              className="color-input"
              value={customBgColor}
              onChange={(e) => setCustomBgColor(e.target.value)}
            />
            <input
              type="text"
              className="text-input"
              value={customBgColor}
              onChange={(e) => setCustomBgColor(e.target.value)}
              placeholder="#f3f4f6"
            />
          </div>
        )}
      </div>

      {/* Style Sliders */}
      <div>
        <h3 className="section-title">
          <Sliders size={16} />
          Style & Similarity Options
        </h3>
        <div className="slider-container">
          <div className="slider-row">
            <div className="slider-header">
              <span>Brightness</span>
              <span className="slider-val">{brightness.toFixed(1)}x</span>
            </div>
            <input
              type="range"
              className="custom-slider"
              min="0.5"
              max="1.5"
              step="0.1"
              value={brightness}
              onChange={(e) => setBrightness(parseFloat(e.target.value))}
            />
          </div>

          <div className="slider-row">
            <div className="slider-header">
              <span>Contrast</span>
              <span className="slider-val">{contrast.toFixed(1)}x</span>
            </div>
            <input
              type="range"
              className="custom-slider"
              min="0.5"
              max="1.5"
              step="0.1"
              value={contrast}
              onChange={(e) => setContrast(parseFloat(e.target.value))}
            />
          </div>

          <div className="slider-row">
            <div className="slider-header">
              <span>Saturation</span>
              <span className="slider-val">{saturation.toFixed(1)}x</span>
            </div>
            <input
              type="range"
              className="custom-slider"
              min="0.5"
              max="1.5"
              step="0.1"
              value={saturation}
              onChange={(e) => setSaturation(parseFloat(e.target.value))}
            />
          </div>

          <div className="slider-row" style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
            <div className="slider-header">
              <span>Number of Variants</span>
              <span className="slider-val">{numVariants}</span>
            </div>
            <input
              type="range"
              className="custom-slider"
              min="1"
              max="15"
              step="1"
              value={numVariants}
              onChange={(e) => setNumVariants(parseInt(e.target.value))}
            />
          </div>

          <div className="slider-row">
            <div className="slider-header" title="Meta DINOv2 embedding cosine similarity minimum threshold. Keep variants higher than this.">
              <span>Similarity Threshold</span>
              <span className="slider-val">{threshold.toFixed(2)}</span>
            </div>
            <input
              type="range"
              className="custom-slider"
              min="0.80"
              max="0.99"
              step="0.01"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
            />
          </div>
        </div>
      </div>

      <button
        className="generate-btn"
        onClick={onGenerate}
        disabled={disabled}
      >
        <Sparkles size={18} />
        Generate Variants
      </button>
    </div>
  );
}
