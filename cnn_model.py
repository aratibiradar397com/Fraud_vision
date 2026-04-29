import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.transforms as transforms
from torchvision.models import resnet18, ResNet18_Weights
import numpy as np

class ImageFraudCNN(nn.Module):
    def __init__(self):
        super(ImageFraudCNN, self).__init__()
        # Load pre-trained ResNet18 model
        self.resnet = resnet18(weights=ResNet18_Weights.DEFAULT)
        
        # Modify the last layer for binary classification
        num_features = self.resnet.fc.in_features
        self.resnet.fc = nn.Sequential(
            nn.Linear(num_features, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, 1),
            nn.Sigmoid()
        )
        
        # Define image transformations
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225])
        ])
    
    def forward(self, x):
        return self.resnet(x)
    
    def preprocess_image(self, img_array):
        """
        Preprocess image for the model
        Args:
            img_array: numpy array of shape (H, W, C) in RGB format
        Returns:
            torch.Tensor of shape (1, C, H, W)
        """
        # Convert numpy array to PIL Image
        img_tensor = torch.from_numpy(img_array).permute(2, 0, 1).float() / 255.0
        img_tensor = self.transform(img_tensor).unsqueeze(0)
        return img_tensor
    
    def predict(self, img_array):
        """
        Make prediction on a single image
        Args:
            img_array: numpy array of shape (H, W, C) in RGB format
        Returns:
            float: probability of being authentic (0-1)
        """
        self.eval()
        with torch.no_grad():
            img_tensor = self.preprocess_image(img_array)
            output = self(img_tensor)
            return float(output[0][0])

# Initialize model
def get_model():
    model = ImageFraudCNN()
    model.eval()  # Set to evaluation mode
    return model
