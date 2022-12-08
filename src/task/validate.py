import importlib
from typing import List, Literal
from pathlib import Path

from src.utils import log_n_print, yaml_safe_load, get_filename_wo_suffix, replace_images2labels
from src.exceptions import YamlException, DatatypeException, DirectoryException


def validate_image_files_exist(
    img_list: List[str], label_list: List[str], errors: List[str]
):
    img_name, label_name = [], []
    for i in img_list:
        path_wo_suffix = get_filename_wo_suffix(i)
        path_wo_suffix = replace_images2labels(path_wo_suffix)
        img_name += [path_wo_suffix]
    for l in label_list:
        label_name = replace_images2labels(get_filename_wo_suffix(l))
        if not label_name in img_name:
            errors.append(f"There is no image file for annotation file '{l}'")
    return errors


def validate_image_mask_1_on_1_match(
    img_list: List[str], label_list: List[str], errors: List[str]
):
    img_name, label_name = [], []
    for i in img_list:
        path_wo_suffix = get_filename_wo_suffix(i)
        path_wo_suffix = replace_images2labels(path_wo_suffix)
        img_name += [path_wo_suffix]
    for l in label_list:
        label_file_name = replace_images2labels(get_filename_wo_suffix(l))
        label_name.append(label_file_name)
        if not label_file_name in img_name:
            errors.append(f"There is no image file for annotation file '{l}'")
    for i in img_list:
        path_wo_suffix = get_filename_wo_suffix(i)
        path_wo_suffix = replace_images2labels(path_wo_suffix)
        if not path_wo_suffix in label_name:
            errors.append(f"There is no mask file for image file '{i}'")
    return errors


def validate_object_detection_dataset_type(root_path: str, user_data_type:Literal["coco", "voc", "yolo"]):
    data_type = None
    paths = Path(root_path).glob("**/*")
    for p in paths:
        suffix = str(p.suffix)
        if suffix == ".xml":
            data_type = "voc"
        if suffix == ".txt":
            data_type = "yolo"
            break
        if suffix == ".json":
            data_type = "coco"
            break
    if not data_type:
        raise DatatypeException(f"There are not any annotation files in {root_path} for {user_data_type} format.")
    elif user_data_type != data_type:
        raise DatatypeException(
            f"Check correct data type, your dataset type looks like '{data_type}', or unnecessary extra files exist in label directory."
        )


def validate_data_yaml(yaml_path: str, errors: List[str]):
    yaml_path = Path(yaml_path)
    if not yaml_path.is_file():
        raise YamlException(f"There is not {str(yaml_path)}")
    try:
        data_dict = yaml_safe_load(str(yaml_path))
    except:
        raise YamlException(f"{str(yaml_path)} file is broken.")
    if not data_dict.get("names"):
        raise YamlException(f"There is no 'names' in {str(yaml_path)}.")
    if not data_dict.get("nc"):
        raise YamlException(f"There is no 'nc' in {str(yaml_path)}.")
    if len(data_dict["names"]) != data_dict["nc"]:
        errors.append(
            f"Length of 'names' and value of 'nc' in {str(yaml_path)} must be same."
        )
    num_classes = max([len(data_dict["names"]), data_dict["nc"]])
    return data_dict["names"], errors, num_classes


def validate_second_dir(dir_path: Path, errors: List[str], targets:List[str]) -> List[str]:
    """
    In yolo case, Validate dir_path has 'images' and 'labels' dir or not.
    In unet case, Validate dir_path has 'image' and 'mask' dir or not.
    """
    paths = Path(dir_path).glob("*")
    check_dir_paths = []
    for p in paths:
        if p.is_dir():
            check_dir_paths.append(str(p.name))
    for target in targets:
        if not (f"{target}" in check_dir_paths):
            errors.append(f"Dataset dosen't have '{target}' dir under {dir_path}.")
    return errors


def validate_image_classification_task(
    root_path: str,
    data_format: str,
    yaml_path: str,
    ):
    errors = []
    dir_path = Path(root_path)
    #dir_paths, errors = validate_first_dirs(dir_path, errors)
    #log_n_print("[Validate: 1/4]: Done validation dir structure ['train', 'val', 'test'].")
    yaml_label, errors, _ = validate_data_yaml(yaml_path, errors)
    log_n_print(f"[Validate: 1/3]: Done validation for {yaml_path} file.")
    _validate = getattr(
        importlib.import_module(f"src.task.image_classification.{data_format.lower()}"),
        "validate",
        )
    errors = _validate(
        yaml_label, dir_path, errors
        )
    return errors


def validate_sub_dir_exsists(dir_path):
    paths = Path(dir_path).glob("*")
    for p in paths:
        if p.is_dir():
            raise DirectoryException(f"Sub dir {str(p)} is not allowed.")
    