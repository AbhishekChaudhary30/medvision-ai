import torchvision.transforms as T
from .transforms import get_base_preprocessing

def get_training_augmentation(image_size: int = 224):
    """
    Returns medically appropriate augmentation for training.
    Avoids extreme transformations that destroy pathology.
    """
    return T.Compose([
        T.RandomHorizontalFlip(p=0.5), # Appropriate for X-Rays usually, but check if heart position is a feature. For pneumonia, it's generally safe.
        T.RandomRotation(degrees=10),
        T.ColorJitter(brightness=0.2, contrast=0.2),
        T.Resize((image_size, image_size)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
