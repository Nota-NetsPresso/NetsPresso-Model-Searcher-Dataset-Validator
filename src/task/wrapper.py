import types

from src.task import image_classification, object_detection, semantic_segmentation
from src.task.image_classification.abs import ImageClassificationTask
from src.task.object_detection.abs import ObjectDetectionTask
from src.task.semantic_segmentation.abs import SemanticSegmentationTask


task_module_mapping = {
    "image_classification":image_classification,
    "object_detection":object_detection,
    "semantic_segmentation":semantic_segmentation

}

task_class_mapping = {
        "image_classification":ImageClassificationTask,
    "object_detection":ObjectDetectionTask,
    "semantic_segmentation":SemanticSegmentationTask
}


class TaskWrapper():
    def __init__(self, task:str):
        self.task_module = task_module_mapping[task]
        # Call __init__ of task class
        self.task_class = task_class_mapping[task]()


class DatasetFormatWrapper():
    def __init__(self, dataset_format:str, task_module:types.ModuleType):
        # Call __init__ of dataset format class
        self.format_module = getattr(task_module, dataset_format)(dataset_format)


class BaseWrapper():
    def __init__(self, dataset_format:str, task:str):
        self.task_wrapper = TaskWrapper(task)
        self.dataset_format_wrapper = DatasetFormatWrapper(dataset_format, task_module_mapping[task])