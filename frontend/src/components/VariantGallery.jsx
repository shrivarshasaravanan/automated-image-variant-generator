import React from "react";
import { Download, FolderArchive, Image as ImageIcon, CheckCircle } from "lucide-react";

export default function VariantGallery({ variants, onDownloadAllZip }) {
  
  const getSimilarityClass = (score) => {
    if (score >= 0.95) return "high";
    if (score >= 0.90) return "medium";
    return "low";
  };

  const handleDownloadFile = (url, filename) => {
    const link = document.createElement("a");
    link.href = `http://localhost:8001${url}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="results-column">
      <div className="gallery-header">
        <h2 className="gallery-title">Generated Variants</h2>
        {variants.length > 0 && (
          <button className="zip-download-btn" onClick={onDownloadAllZip}>
            <FolderArchive size={16} />
            Download ZIP
          </button>
        )}
      </div>

      {variants.length === 0 ? (
        <div className="empty-gallery">
          <ImageIcon className="empty-icon" size={48} />
          <p style={{ fontWeight: 600, fontSize: '1.05rem', marginBottom: '0.25rem' }}>No Variants Generated Yet</p>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', maxWidth: '300px' }}>
            Upload a master image, configure your options, and click Generate to see similarity-verified AI variants.
          </p>
        </div>
      ) : (
        <div className="gallery-grid">
          {variants.map((v) => {
            const similarityPercent = (v.similarity_score * 100).toFixed(1);
            return (
              <div key={v.id} className="variant-card">
                <div className="variant-image-wrapper">
                  <img
                    src={`http://localhost:8001${v.url}`}
                    alt={v.variant_type}
                    loading="lazy"
                  />
                  <div className={`similarity-badge ${getSimilarityClass(v.similarity_score)}`}>
                    <CheckCircle size={12} /> {similarityPercent}%
                  </div>
                </div>
                <div className="variant-info">
                  <div className="variant-type-label">{v.variant_type}</div>
                  <div className="variant-meta">
                    <span className="meta-pill">Ratio: {v.aspect_ratio}</span>
                    {v.palette && <span className="meta-pill">Theme: {v.palette}</span>}
                  </div>
                  <div className="card-actions">
                    <button
                      className="card-btn primary"
                      onClick={() => handleDownloadFile(v.url, v.filename)}
                    >
                      <Download size={14} />
                      Download
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
