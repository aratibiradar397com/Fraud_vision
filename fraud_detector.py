import numpy as np
from PIL import Image
import cv2
import os

from cnn_model import get_model

class ImageFraudDetector:
    def __init__(self):
        # Initialize CNN model
        self.cnn_model = get_model()
    
    def _preprocess_image(self, image_path):
        """Preprocess the image for analysis."""
        try:
            # Load and resize image
            img = cv2.imread(image_path)
            if img is None:
                raise Exception("Failed to load image")
            
            # Convert BGR to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize image
            img_resized = cv2.resize(img_rgb, (224, 224))
            
            # Perform various analyses
            ela_score = float(self._error_level_analysis(image_path))
            noise_score = float(self._noise_analysis(img_resized))
            metadata_score = float(self._metadata_analysis(image_path))
            compression_score = float(self._compression_analysis(img_resized))
            
            return img_resized, ela_score, noise_score, metadata_score, compression_score
        except Exception as e:
            raise Exception(f"Error preprocessing image: {str(e)}")

    def _error_level_analysis(self, image_path):
        """Perform Error Level Analysis to detect potential modifications."""
        try:
            # Read original image with OpenCV
            original = cv2.imread(image_path)
            if original is None:
                return 0
            
            # Save image with known quality
            temp_path = "temp_ela.jpg"
            cv2.imwrite(temp_path, original, [cv2.IMWRITE_JPEG_QUALITY, 90])
            
            # Read compressed image
            compressed = cv2.imread(temp_path)
            if compressed is None:
                os.remove(temp_path)
                return 0
            
            # Calculate ELA
            ela = cv2.absdiff(original, compressed)
            
            # Clean up
            os.remove(temp_path)
            
            # Calculate mean error and normalize
            mean_error = np.mean(ela)
            return mean_error
        except Exception as e:
            print(f"ELA Error: {str(e)}")
            return 0

    def _noise_analysis(self, img_array):
        """Analyze image noise patterns to detect inconsistencies."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Apply noise detection filter
            noise = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate local noise variance
            local_noise = []
            for i in range(0, gray.shape[0]-32, 32):
                for j in range(0, gray.shape[1]-32, 32):
                    patch = gray[i:i+32, j:j+32]
                    local_noise.append(np.std(patch))
            
            # Check for inconsistent noise patterns
            noise_std = np.std(local_noise)
            return noise_std
        except Exception as e:
            print(f"Noise Analysis Error: {str(e)}")
            return 0

    def _metadata_analysis(self, image_path):
        """Analyze image metadata for potential inconsistencies."""
        try:
            img = Image.open(image_path)
            metadata = img.info
            
            # Check for common metadata fields
            score = 100
            
            # Suspicious if no metadata
            if not metadata:
                score -= 30
            
            # Check for software tags that might indicate editing
            if 'Software' in metadata:
                if any(editor in metadata['Software'].lower() for editor in ['photoshop', 'gimp', 'lightroom']):
                    score -= 20
            
            return max(0, score)
        except Exception as e:
            print(f"Metadata Analysis Error: {str(e)}")
            return 50  # Neutral score on error

    def _compression_analysis(self, img_array):
        """Analyze compression artifacts and patterns."""
        try:
            # Convert to YCrCb color space
            ycrcb = cv2.cvtColor(img_array, cv2.COLOR_RGB2YCrCb)
            
            # Analyze each channel
            scores = []
            for channel in cv2.split(ycrcb):
                # Convert to float32 for DCT
                channel_float = np.float32(channel)
                # Apply DCT transform
                dct = cv2.dct(channel_float)
                
                # Analyze DCT coefficients
                dct_score = np.std(dct)
                scores.append(dct_score)
            
            # Normalize and combine scores
            return np.mean(scores)
        except Exception as e:
            print(f"Compression Analysis Error: {str(e)}")
            return 0

    def analyze(self, image_path):
        """Analyze an image for potential fraud."""
        try:
            if not os.path.exists(image_path):
                raise Exception("Image file not found")
                
            # Preprocess and analyze image
            img_array, ela_score, noise_score, metadata_score, compression_score = self._preprocess_image(image_path)
            
            # Normalize scores
            ela_score_norm = min(1.0, ela_score / 100)
            noise_score_norm = min(1.0, noise_score / 50)
            metadata_score_norm = metadata_score / 100
            compression_score_norm = min(1.0, compression_score / 1000)
            
            # Get CNN prediction
            cnn_score = self.cnn_model.predict(img_array)
            
            # Use original image for traditional analysis
            ela_score = float(self._error_level_analysis(image_path))
            noise_score = float(self._noise_analysis(img_array))
            metadata_score = float(self._metadata_analysis(image_path))
            compression_score = float(self._compression_analysis(img_array))
            
            # Weight the different analysis components
            weights = {
                'cnn': 0.4,        # CNN has highest weight
                'ela': 0.2,
                'noise': 0.2,
                'metadata': 0.1,
                'compression': 0.1
            }
            
            # Calculate final authenticity score
            authenticity_score = float(
                cnn_score * weights['cnn'] +
                (1 - ela_score_norm) * weights['ela'] +
                (1 - noise_score_norm) * weights['noise'] +
                metadata_score_norm * weights['metadata'] +
                (1 - compression_score_norm) * weights['compression']
            )
            
            # Calculate confidence based on the consistency of different measures
            scores = [float(cnn_score), float(1 - ela_score_norm), float(1 - noise_score_norm), 
                     float(metadata_score_norm), float(1 - compression_score_norm)]
            confidence = float(1 - np.std(scores))
            
            # Convert all NumPy types to Python native types
            ela_score = float(1 - ela_score_norm)
            noise_score = float(1 - noise_score_norm)
            metadata_score = float(metadata_score_norm)
            compression_score = float(1 - compression_score_norm)
            
            # Prepare detailed analysis results
            result = {
                'authenticity_score': round(authenticity_score * 100, 2),
                'confidence': round(confidence * 100, 2),
                'analysis': {
                    'error_level_analysis': round(ela_score * 100, 2),
                    'noise_analysis': round(noise_score * 100, 2),
                    'metadata_analysis': round(metadata_score * 100, 2),
                    'compression_analysis': round(compression_score * 100, 2)
                },
                'verdict': 'authentic' if authenticity_score > 0.5 else 'potentially fraudulent'
            }
            
            return result
            
        except Exception as e:
            print(f"Analysis Error: {str(e)}")
            raise Exception(f"Error analyzing image: {str(e)}")
