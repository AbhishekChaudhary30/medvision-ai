from typing import Dict, Any, Tuple, Optional
import torch
import torchvision.models as models

class ModalityRegistry:
    """Registry mapping modalities to their architecture and class configurations."""
    
    _registry: Dict[str, Dict[str, Any]] = {
        # --- RADIOGRAPHY (X-RAY) ---
        "chest-xray": {
            "name": "Chest X-Ray Pneumonia",
            "category": "X-Ray",
            "classes": {0: "NORMAL", 1: "PNEUMONIA"},
            "num_classes": 2,
            "architecture": "CustomCNN",
            "is_dummy": False
        },
        "bone-xray": {
            "name": "Bone X-Ray Fracture",
            "category": "X-Ray",
            "classes": {0: "NORMAL", 1: "FRACTURE"},
            "num_classes": 2,
            "architecture": "densenet121",
            "is_dummy": True
        },
        "dental-xray": {
            "name": "Dental X-Ray Caries",
            "category": "X-Ray",
            "classes": {0: "HEALTHY", 1: "CARIES/DECAY"},
            "num_classes": 2,
            "architecture": "resnet18",
            "is_dummy": True
        },
        
        # --- COMPUTED TOMOGRAPHY (CT) ---
        "head-ct": {
            "name": "Head CT Hemorrhage",
            "category": "CT Scan",
            "classes": {0: "NORMAL", 1: "HEMORRHAGE"},
            "num_classes": 2,
            "architecture": "resnet50",
            "is_dummy": True
        },
        "chest-ct": {
            "name": "Chest CT Nodule/Cancer",
            "category": "CT Scan",
            "classes": {0: "BENIGN", 1: "MALIGNANT NODULE"},
            "num_classes": 2,
            "architecture": "resnet50",
            "is_dummy": True
        },
        "abdomen-ct": {
            "name": "Abdomen CT Appendicitis",
            "category": "CT Scan",
            "classes": {0: "NORMAL", 1: "APPENDICITIS"},
            "num_classes": 2,
            "architecture": "resnet34",
            "is_dummy": True
        },

        # --- MAGNETIC RESONANCE IMAGING (MRI) ---
        "brain-mri": {
            "name": "Brain MRI Tumor",
            "category": "MRI",
            "classes": {0: "NORMAL", 1: "TUMOR"},
            "num_classes": 2,
            "architecture": "resnet18",
            "is_dummy": True
        },
        "spine-mri": {
            "name": "Spine MRI Herniation",
            "category": "MRI",
            "classes": {0: "NORMAL", 1: "HERNIATED DISC"},
            "num_classes": 2,
            "architecture": "densenet121",
            "is_dummy": True
        },
        "knee-mri": {
            "name": "Knee MRI ACL Tear",
            "category": "MRI",
            "classes": {0: "INTACT", 1: "ACL TEAR"},
            "num_classes": 2,
            "architecture": "resnet34",
            "is_dummy": True
        },

        # --- ULTRASOUND ---
        "fetal-ultrasound": {
            "name": "Fetal Ultrasound Anomaly",
            "category": "Ultrasound",
            "classes": {0: "NORMAL GROWTH", 1: "STRUCTURAL ANOMALY"},
            "num_classes": 2,
            "architecture": "resnet18",
            "is_dummy": True
        },
        "echocardiogram": {
            "name": "Echocardiogram Function",
            "category": "Ultrasound",
            "classes": {0: "NORMAL EJECTION FRACTION", 1: "HEART FAILURE / REDUCED EF"},
            "num_classes": 2,
            "architecture": "resnet34",
            "is_dummy": True
        },
        "abdominal-ultrasound": {
            "name": "Abdominal US Gallstones",
            "category": "Ultrasound",
            "classes": {0: "NORMAL", 1: "CHOLELITHIASIS (GALLSTONES)"},
            "num_classes": 2,
            "architecture": "resnet18",
            "is_dummy": True
        },

        # --- PATHOLOGY & ENDOSCOPY ---
        "skin-lesion": {
            "name": "Dermatology Melanoma",
            "category": "Pathology/Derm",
            "classes": {0: "BENIGN NEVUS", 1: "MELANOMA"},
            "num_classes": 2,
            "architecture": "resnet50",
            "is_dummy": True
        },
        "retinal-fundus": {
            "name": "Retinal Fundus Diabetic Retinopathy",
            "category": "Ophthalmology",
            "classes": {0: "NORMAL", 1: "DIABETIC RETINOPATHY"},
            "num_classes": 2,
            "architecture": "densenet121",
            "is_dummy": True
        },
        "histopathology": {
            "name": "Histopathology Slide Cancer",
            "category": "Pathology/Derm",
            "classes": {0: "BENIGN TISSUE", 1: "INVASIVE CARCINOMA"},
            "num_classes": 2,
            "architecture": "resnet50",
            "is_dummy": True
        },
        "colonoscopy": {
            "name": "Colonoscopy Polyp Detection",
            "category": "Endoscopy",
            "classes": {0: "NORMAL MUCOSA", 1: "ADENOMATOUS POLYP"},
            "num_classes": 2,
            "architecture": "resnet34",
            "is_dummy": True
        },
        "mammography": {
            "name": "Mammography Breast Cancer",
            "category": "X-Ray",
            "classes": {0: "BIRADS-1 (NEGATIVE)", 1: "BIRADS-4/5 (SUSPICIOUS/MALIGNANT)"},
            "num_classes": 2,
            "architecture": "resnet50",
            "is_dummy": True
        }
    }

    @classmethod
    def get_config(cls, modality: str) -> Dict[str, Any]:
        if modality not in cls._registry:
            raise ValueError(f"Modality '{modality}' is not supported.")
        return cls._registry[modality]

    @classmethod
    def get_all_modalities(cls) -> Dict[str, Dict[str, Any]]:
        return cls._registry

    @classmethod
    def load_model(cls, modality: str, strict: bool = True) -> Tuple[Optional[torch.nn.Module], str, Dict[int, str]]:
        """
        Loads the PyTorch model for the given modality.
        If is_dummy is True, it simulates loading enterprise weights by instantiating a pre-trained model.
        Returns: (model, architecture_name, class_names)
        """
        config = cls.get_config(modality)
        
        if config["is_dummy"]:
            arch_name = config["architecture"]
            if arch_name.startswith("resnet18"):
                model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
                num_ftrs = model.fc.in_features
                model.fc = torch.nn.Linear(num_ftrs, config["num_classes"])
            elif arch_name.startswith("resnet34"):
                model = models.resnet34(weights=models.ResNet34_Weights.DEFAULT)
                num_ftrs = model.fc.in_features
                model.fc = torch.nn.Linear(num_ftrs, config["num_classes"])
            elif arch_name.startswith("resnet50"):
                model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
                num_ftrs = model.fc.in_features
                model.fc = torch.nn.Linear(num_ftrs, config["num_classes"])
            elif arch_name.startswith("densenet121"):
                model = models.densenet121(weights=models.DenseNet121_Weights.DEFAULT)
                num_ftrs = model.classifier.in_features
                model.classifier = torch.nn.Linear(num_ftrs, config["num_classes"])
            else:
                model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
                num_ftrs = model.fc.in_features
                model.fc = torch.nn.Linear(num_ftrs, config["num_classes"])

            model.eval()
            return model, config["architecture"], config["classes"]
        else:
            # For chest-xray, we use the actual ModelBundle
            return None, config["architecture"], config["classes"]

    @classmethod
    def is_valid(cls, modality: str) -> bool:
        return modality in cls._registry
