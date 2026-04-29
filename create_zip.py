import os
import zipfile
from pathlib import Path

def create_project_zip():
    # Project root directory
    root_dir = Path(__file__).parent

    # Files and directories to exclude
    exclude = {
        '__pycache__',
        'venv',
        'env',
        '.env',
        '.git',
        '.gitignore',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.Python',
        'build',
        'dist',
        '*.egg-info',
        '.DS_Store',
        'Thumbs.db',
        '*.db',
        '*.sqlite3',
        'create_zip.py',  # Exclude this script itself
    }

    # Create a zip file
    zip_path = root_dir / 'fraudvision_project.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(root_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude]
            
            for file in files:
                # Skip excluded files
                if any(file.endswith(ext) for ext in exclude if '*' in ext):
                    continue
                if file in exclude:
                    continue
                
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, root_dir)
                zipf.write(file_path, arc_path)

    print(f"\nProject has been zipped to: {zip_path}")
    print("\nTo run this project on another system:")
    print("1. Extract the zip file")
    print("2. Create a virtual environment:")
    print("   python -m venv venv")
    print("3. Activate the virtual environment:")
    print("   - Windows: .\\venv\\Scripts\\activate")
    print("   - macOS/Linux: source venv/bin/activate")
    print("4. Install dependencies:")
    print("   pip install -r requirements.txt")
    print("5. Create a .env file with your SECRET_KEY")
    print("6. Run the application:")
    print("   python app.py")
    print("\nThe application will be available at: http://localhost:5000")

if __name__ == '__main__':
    create_project_zip()
