import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { previewFileRoute } from '../utils/APIRoutes';

const ImagePreview = ({ fileId, filename, onImageClick }) => {
  const [imageData, setImageData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchImage = async () => {
      try {
        const response = await axios.get(`${previewFileRoute}/${fileId}`);
        if (response.data.status) {
          setImageData(response.data.file_data);
        }
      } catch (error) {
        console.error('Error fetching image:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchImage();
  }, [fileId]);

  if (loading) {
    return <div>Loading image...</div>;
  }

  if (!imageData) {
    return <div>Failed to load image</div>;
  }

  return (
    <img 
      src={imageData}
      alt={filename}
      onClick={onImageClick}
      style={{
        maxWidth: '200px',
        maxHeight: '150px',
        borderRadius: '8px',
        cursor: 'pointer',
        transition: 'transform 0.2s ease'
      }}
      onMouseOver={(e) => e.target.style.transform = 'scale(1.05)'}
      onMouseOut={(e) => e.target.style.transform = 'scale(1)'}
    />
  );
};

export default ImagePreview;