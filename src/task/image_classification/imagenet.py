from typing import List
from pathlib import Path

from src.config import img_file_types
from src.task.image_classification.abs import ImageClassificationDatasetFormat


def validate_img_file_type(
    path:Path,
    errors: List[str],
):
    files  = Path(path).glob("**/*")
    for f in files:
        if f.is_file() and ('*'+f.suffix) not in img_file_types:
            errors.append(f"{f} is not supported image file type")
    return errors


def get_classes(target_path: str):
    class_list = []
    for p in Path(target_path).glob("*"):
        if p.is_dir():
            class_list.append(str(p.name))
    return sorted(class_list)


def get_imagenet_obj_stat_num_images(target_path: str):
    class_list = []
    ret_dict = {}
    num_images = 0
    for p in Path(target_path).glob("*"):
        if p.is_dir():
            class_list.append(p)
    for cl in class_list:
        images = cl.glob("*")
        ret_dict[cl.name]=len(list(images))
        num_images+=ret_dict[cl.name]
    return ret_dict, num_images


class IMAGENET(ImageClassificationDatasetFormat):
    def get_stat(self):
        tmp_path = self.root_path
        names = get_classes(self.root_path)
        obj_stat, num_images = get_imagenet_obj_stat_num_images(self.root_path)
        return tmp_path, names, obj_stat, num_images

    def specific_validation_for_each_dataset(self, **kwargs):
        errors = kwargs["errors"]
        names = kwargs["names"]
        for name in names:
            errors = validate_img_file_type(self.root_path/name, errors)
        return errors