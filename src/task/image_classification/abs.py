from typing import Dict

from src.task.validate import validate_data_yaml
from src.task.abs import AbstractTask, AbstractDatasetFormat


class ImageClassificationTask(AbstractTask):
    def __init__(self):
        pass


class ImageClassificationDatasetFormat(AbstractDatasetFormat):
    def get_stat(self):
        raise NotImplementedError

    def specific_validation_for_each_dataset(self):
        raise NotImplementedError
    
    def common_validation(self, names:set, num_images:int, obj_stat:Dict[str, int], tmp_path:str):
        errors = []
        # Common validation of object detection
        temp_yaml_path, yaml_content = self.prepare_yaml(names, num_images, obj_stat, tmp_path)
        yaml_label, errors, num_classes = validate_data_yaml(temp_yaml_path, errors)
        return errors, num_classes, temp_yaml_path, yaml_content, yaml_label

    def validate(self, **kwargs):
        yaml_path = kwargs["yaml_path"]
        root_path = kwargs["root_path"]
        output_dir = kwargs["output_dir"]
        split_name = kwargs["split_name"]

        self.set_common_attrs(yaml_path, root_path, output_dir, split_name)
        tmp_path, names, obj_stat, num_images = self.get_stat()
        errors, num_classes, temp_yaml_path, yaml_content, yaml_label = self.common_validation(names, num_images, obj_stat, tmp_path)

        # validation for each dataset
        errors = self.specific_validation_for_each_dataset(
            errors=errors,
            names=names, 
            )

        zip_file_path, md5_hash, succeed = self.postprocess(errors, output_dir, temp_yaml_path, split_name, tmp_path)
        return zip_file_path, yaml_content, md5_hash, succeed