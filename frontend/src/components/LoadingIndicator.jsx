import React from "react";

export default function LoadingIndicator({ progressText }) {
  return (
    <div className="results-column">
      <div className="gallery-header">
        <h2 className="gallery-title">Generating...</h2>
      </div>
      <div className="loading-panel">
        <div className="spinner"></div>
        <p className="loading-text">{progressText || "Generating Variants..."}</p>
        <p className="loading-subtext">
          Applying image modifications and running Meta DINOv2 embedding checks to evaluate structural visual similarity.
        </p>
        <div className="progress-bar-container">
          <div className="progress-bar-fill"></div>
        </div>
      </div>
      <div className="gallery-grid" style={{ opacity: 0.5 }}>
        {Array.from({ length: 3 }).map((_, idx) => (
          <div key={idx} className="shimmer-card"></div>
        ))}
      </div>
    </div>
  );
}
