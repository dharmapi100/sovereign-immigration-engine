"""
Document Classifier
===================
Classifies a scanned document as passport / visa / contract. Torch +
torchvision are imported lazily so the compliance core runs without the
ML stack installed.
"""


class DocumentClassifier:
    CLASSES = ["passport", "visa", "contract"]

    def __init__(self):
        self._model = None
        self._transform = None

    def _ensure_model(self):
        if self._model is None:
            import torchvision  # lazy: heavy dep
            from torchvision import models, transforms

            _ = torchvision
            self._model = models.resnet18(pretrained=True)
            self._model.eval()
            self._transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize([0.485, 0.456, 0.406],
                                     [0.229, 0.224, 0.225]),
            ])
        return self._model

    def predict(self, image_path):
        import torch  # lazy
        from PIL import Image  # lazy: heavy dep

        model = self._ensure_model()
        img = Image.open(image_path).convert("RGB")
        batch_t = self._transform(img).unsqueeze(0)
        with torch.no_grad():
            output = model(batch_t)
        return self.CLASSES[output.argmax()]


if __name__ == "__main__":
    pass