import torchvision.transforms as T

def get_base_preprocessing(image_size: int = 224):
    """
    Returns the authoritative base preprocessing pipeline used for BOTH training and inference.
    """
    return T.Compose([
        T.Resize((image_size, image_size)),
        T.ToTensor(),
        # ImageNet normalization as a standard baseline, 
        # for real production a dataset-specific normalization might be computed.
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
