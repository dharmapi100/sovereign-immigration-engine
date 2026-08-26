import os
from PIL import Image
import torch
from torchvision import models, transforms

class DocumentClassifier:
    def __init__(self):
        self.model = models.resnet18(pretrained=True)
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        self.classes = ['passport', 'visa', 'contract']

    def predict(self, image_path):
        img = Image.open(image_path).convert('RGB')
        img_t = self.transform(img)
        # ensure tensor
        batch_t = img_t.unsqueeze(0)
        
        with torch.no_grad():
            output = self.model(batch_t)
        
        return self.classes[output.argmax()]

if __name__ == "__main__":
    pass
