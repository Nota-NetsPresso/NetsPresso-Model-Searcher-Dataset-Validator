from enum import Enum


class DatasetType(Enum):
    # Object detection
    coco = "coco"
    voc = "voc"
    yolo = "yolo"
    # Semantic segmentation
    unet = "unet"
    # Image classification
    imagenet = "imagenet"

    def __str__(self):
        return self.value


class TaskType(Enum):
    image_classification = "image_classification"
    object_detection = "object_detection"
    semantic_segmentation = "semantic_segmentation"

    def __str__(self):
        return self.value


label_suffix_mapping = {
    "voc":"xml",
    "coco":"json",
    "yolo":"txt",
    "unet":None, # Any image type
    "imagenet":None # No label file
}

img_file_types = [
        "*.jpeg",
        "*.JPEG",
        "*.jpg",
        "*.JPG",
        "*.png",
        "*.PNG",
        "*.BMP",
        "*.bmp",
        "*.TIF",
        "*.tif",
        "*.TIFF",
        "*.tiff",
        "*.DNG",
        "*.dng",
        "*.WEBP",
        "*.webp",
        "*.mpo",
        "*.MPO",
    ]

version="v1"