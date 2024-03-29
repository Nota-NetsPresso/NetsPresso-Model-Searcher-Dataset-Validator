from typing import Dict

from src.config import img_file_types
from src.task.validate import validate_object_detection_dataset_type, validate_data_yaml, validate_sub_dir_exsists
from src.task.abs import AbstractTask, AbstractDatasetFormat
from src.utils import get_target_suffix_file_list


class ObjectDetectionTask(AbstractTask):
    def __init__(self):
        pass


class ObjectDetectionDatasetFormat(AbstractDatasetFormat):
    def get_stat(self):
        raise NotImplementedError

    def specific_validation_for_each_dataset(self):
        raise NotImplementedError
    
    def validate(self, storage_type:str = "s3", **kwargs):
        yaml_path = kwargs["yaml_path"]
        root_path = kwargs["root_path"]
        output_dir = kwargs["output_dir"]
        split_name = kwargs["split_name"]

        self.set_common_attrs(yaml_path, root_path, output_dir, split_name)
        validate_object_detection_dataset_type(self.root_path, self.dataset_format)

        if self.dataset_format in ["coco", "voc"]:
            validate_sub_dir_exsists(self.root_path)
        tmp_path, names, obj_stat, num_images = self.get_stat()
        errors, img_list, label_list, num_classes, temp_yaml_path, yaml_content, yaml_label = self.common_validation(names, num_images, obj_stat, tmp_path)
        
        # validation for each dataset
        errors = self.specific_validation_for_each_dataset(
            errors=errors, 
            img_list=img_list, 
            label_list=label_list, 
            num_classes=num_classes, 
            yaml_label=yaml_label
            )
        zip_file_path, md5_hash, succeed = self.postprocess(errors, output_dir, temp_yaml_path, split_name, tmp_path, storage_type)
        self.remove_trees(tmp_path)
        return zip_file_path, yaml_content, md5_hash, succeed

    def common_validation(self, names:set, num_images:int, obj_stat:Dict[str, int], tmp_path:str):
        errors = []
        # Common validation of object detection
        temp_yaml_path, yaml_content = self.prepare_yaml(names, num_images, obj_stat, tmp_path)
        img_list = get_target_suffix_file_list(self.root_path, img_file_types)
        label_list = get_target_suffix_file_list(self.root_path, [f"*.{self.label_file_suffix}"])
        yaml_label, errors, num_classes = validate_data_yaml(temp_yaml_path, errors)
        return errors, img_list, label_list, num_classes, temp_yaml_path, yaml_content, yaml_label