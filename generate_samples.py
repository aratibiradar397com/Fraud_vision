import cv2
import numpy as np
import os

def create_real_image():
    """Create a simple real image"""
    # Create a gradient background
    img = np.zeros((512, 512, 3), dtype=np.uint8)
    for i in range(512):
        for j in range(512):
            img[i, j] = [(i + j) // 4, 100, (i + j) // 4]
    
    # Add some shapes
    cv2.circle(img, (256, 256), 100, (255, 0, 0), -1)
    cv2.rectangle(img, (100, 100), (400, 150), (0, 255, 0), -1)
    
    return img

def create_manipulated_image(real_img):
    """Create a manipulated version of the real image"""
    img = real_img.copy()
    
    # Add a spliced region
    splice = np.zeros((100, 100, 3), dtype=np.uint8)
    splice[:, :] = [0, 0, 255]
    img[300:400, 300:400] = splice
    
    # Apply different compression to the spliced region
    cv2.imwrite('temp.jpg', img[300:400, 300:400], [cv2.IMWRITE_JPEG_QUALITY, 50])
    spliced_compressed = cv2.imread('temp.jpg')
    img[300:400, 300:400] = spliced_compressed
    
    # Clean up
    if os.path.exists('temp.jpg'):
        os.remove('temp.jpg')
    
    return img

# Create and save sample images
if __name__ == '__main__':
    # Create output directory
    os.makedirs('sample_images', exist_ok=True)
    
    # Generate real image
    real_img = create_real_image()
    cv2.imwrite('sample_images/real_image.jpg', real_img)
    
    # Generate manipulated image
    fake_img = create_manipulated_image(real_img)
    cv2.imwrite('sample_images/manipulated_image.jpg', fake_img)
    
    print("Sample images generated in 'sample_images' directory")
