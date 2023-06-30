import os
from pathlib import Path
from typing import List, Dict
import shutil

from src.config import img_file_types
from src.exceptions import LabelException
from src.task.abs import AbstractTask, AbstractDatasetFormat
from src.utils import get_target_suffix_file_list, zip_files, calc_file_hash
from src.task.validate import validate_data_yaml


class SemanticSegmentationTask(AbstractTask):
    def __init__(self):
        super().__init__()


class SemanticSegmentationDatasetFormat(AbstractDatasetFormat):
    def __init__(self, dataset_format:str):
        super().__init__(dataset_format)

    def get_stat(self, id2label:str):
        raise NotImplementedError

    def specific_validation_for_each_dataset(self):
        raise NotImplementedError

    def remove_trees(self, tmp_path:str):
        pass

    def common_validation(self, names:set, num_images:int, obj_stat:Dict[str, int], tmp_path:str):
        errors = []
        # Common validation of object detection
        temp_yaml_path, yaml_content = self.prepare_yaml(names, num_images, obj_stat, tmp_path)
        # TODO someday, add Validate dataset type -> Is this Unet or not?
        img_list = get_target_suffix_file_list(self.root_path/"image", img_file_types)
        label_list = get_target_suffix_file_list(self.root_path/"mask", img_file_types) # unet label is arbitrary image format
        yaml_label, errors, num_classes = validate_data_yaml(temp_yaml_path, errors)
        return errors, img_list, label_list, num_classes, temp_yaml_path, yaml_content, yaml_label

    def postprocess(self, errors:List[str], output_dir:str, temp_yaml_path:str, split_name:str, tmp_path:str, id2label_path:str):
        succeed = self.write_error_or_not(errors, output_dir)
        self.remove_file(temp_yaml_path)
        if succeed:
            if storage_type=="s3":
                temp_id2label_path = Path(tmp_path)/Path(id2label_path).name
                # Copy id2label.json into zipped dir.
                shutil.copy(id2label_path, temp_id2label_path)
                zip_file_path = zip_files(os.path.join(output_dir, split_name), tmp_path)
                md5_hash = calc_file_hash(zip_file_path)
                self.remove_file(temp_id2label_path)
            else:
                zip_file_path, md5_hash = None, None
        else:
            raise LabelException("Validation fail, please read validation_result.txt")
        return zip_file_path, md5_hash, succeed

    def validate(self, **kwargs):
        yaml_path = kwargs["yaml_path"]
        root_path = kwargs["root_path"]
        output_dir = kwargs["output_dir"]
        split_name = kwargs["split_name"]
        id2label_path = kwargs["id2label_path"]

        self.set_common_attrs(yaml_path, root_path, output_dir, split_name)
        tmp_path, names, obj_stat, num_images = self.get_stat(id2label_path)
        errors, img_list, label_list, num_classes, temp_yaml_path, yaml_content, yaml_label = self.common_validation(names, num_images, obj_stat, tmp_path)
        
        # validation for each dataset
        errors = self.specific_validation_for_each_dataset(
            errors=errors, 
            img_list=img_list, 
            label_list=label_list, 
            num_classes=num_classes, 
            yaml_label=yaml_label,
            id2label_path=id2label_path
            )

        zip_file_path, md5_hash, succeed = self.postprocess(errors, output_dir, temp_yaml_path, split_name, tmp_path, id2label_path)
        self.remove_trees(tmp_path)
        return zip_file_path, yaml_content, md5_hash, succeed