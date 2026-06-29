import React, { useRef, useState } from "react";
import { Upload, X, FileImage } from "lucide-react";

export default function ImageUploader({ masterImage, isUploading, onUpload, onClear }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };

  return (
    <div className="glass-panel upload-container">
      <h3 className="section-title">
        <FileImage size={18} />
        Master Image
      </h3>
      
      {!masterImage ? (
        <div
          className={`upload-zone ${isDragging ? "dragging" : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="image/*"
            style={{ display: "none" }}
          />
          {isUploading ? (
            <>
              <div className="spinner" style={{ width: 28, height: 28, marginBottom: 12 }}></div>
              <p className="upload-text">Uploading Master Image...</p>
            </>
          ) : (
            <>
              <Upload className="upload-icon" size={32} />
              <p className="upload-text">Drag & drop your master image</p>
              <p className="upload-subtext">or click to browse from files</p>
            </>
          )}
        </div>
      ) : (
        <div>
          <div className="master-preview">
            <img
              src={`http://localhost:8001${masterImage.url}`}
              alt="Master Preview"
            />
            <button className="clear-btn" onClick={onClear} title="Clear Image">
              <X size={16} />
            </button>
          </div>
          <div style={{ marginTop: '0.75rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
            <strong>Dimension:</strong> {masterImage.width} x {masterImage.height}px &nbsp;|&nbsp;
            <strong>Format:</strong> {masterImage.format}
          </div>
        </div>
      )}
    </div>
  );
}
