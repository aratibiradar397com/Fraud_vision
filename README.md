# FraudVision

A deep learning-based image fraud detection system that combines CNN with traditional image analysis techniques to identify potentially manipulated images.

## Features

- Deep Learning-based image analysis using ResNet18
- Error Level Analysis (ELA)
- Noise Analysis
- Metadata Analysis
- Compression Pattern Analysis
- User Authentication
- Image Upload and Analysis Dashboard
- Detailed Analysis Reports

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/fraudvision.git
   cd fraudvision
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following content:
   ```env
   SECRET_KEY=your_secret_key_here
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

3. Create an account or log in

4. Upload an image to analyze

5. View the detailed analysis results

## Project Structure

```
fraudvision/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── cnn_model.py        # CNN model implementation
├── fraud_detector.py   # Image analysis implementation
├── models.py           # Database models
├── requirements.txt    # Project dependencies
├── static/             # Static files (CSS, JS)
├── templates/          # HTML templates
└── uploads/           # Temporary image storage
```

## Dependencies

- Python 3.8+
- Flask
- PyTorch
- OpenCV
- NumPy
- Pillow

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

MIT License
 - AI Image Authenticity Detector

FraudVision is an advanced AI-powered system that detects fraudulent, tampered, or AI-generated images. It combines multiple analysis techniques including deep learning, error level analysis, and noise pattern analysis to provide comprehensive image authenticity assessment.

## Features

- Deep learning-based image analysis using EfficientNetB0
- Error Level Analysis (ELA) for detecting image manipulation
- Noise pattern analysis for identifying AI-generated content
- Real-time image processing and results
- User-friendly web interface with drag-and-drop support
- Detailed analysis breakdown with confidence scores

## Installation

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Flask server:
   ```bash
   python app.py
   ```
2. Open your web browser and navigate to `http://localhost:5000`
3. Upload an image by dragging and dropping or clicking to select
4. View the detailed analysis results

## Analysis Components

- **Deep Learning Score**: Uses EfficientNetB0 to detect patterns common in manipulated or AI-generated images
- **Error Level Analysis**: Detects inconsistencies in JPEG compression that may indicate tampering
- **Noise Analysis**: Identifies unusual noise patterns that could suggest image manipulation

## Technical Details

- Backend: Python, Flask
- Deep Learning: TensorFlow, EfficientNet
- Image Processing: OpenCV, Pillow
- Frontend: HTML, JavaScript, TailwindCSS

## Note

The system provides a confidence score along with its verdict. However, as with any AI system, results should be interpreted as probabilistic rather than absolute. For critical applications, manual verification is recommended.
