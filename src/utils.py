import glob
import json
import os
import re
import shutil
import importlib
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePath, PurePosixPath
from typing import Dict, List

import yaml

from src.exceptions import DatatypeException, YamlException


def get_img_list(file_paths: str, img_list: List[str]) -> List[str]:
    img_file_types = get_img_file_types()
    for types in img_file_types:
        files = Path(file_paths).glob(f"**/{types}")
        for f in files:
            if f.is_file():
                img_list.append(str(f))
    return img_list


def get_label_list(file_paths: Path, label_list: List[str]) -> List[str]:
    files = Path(file_paths).glob("**/*.txt")
    for f in files:
        if f.is_file():
            label_list.append(str(f))
    files = Path(file_paths).glob("**/*.json")
    for f in files:
        if f.is_file():
            label_list.append(str(f))
    files = Path(file_paths).glob("**/*.xml")
    for f in files:
        if f.is_file():
            label_list.append(str(f))
    return label_list


def get_file_lists(dir_paths: str) -> (List[str], List[str]):
    file_count = 0
    img_list = []
    label_list = []
    for p in dir_paths:
        p = Path(p)
        label_list = get_label_list(p, label_list)
        img_list = get_img_list(p, img_list)
    return sorted(img_list), sorted(label_list)


def yaml_safe_load(yaml_path: str)->Dict[str, any]:
    with open(yaml_path, "r") as f:
        data_dict = yaml.safe_load(f)
    return data_dict


def delete_dirs(dir_path: str):
    shutil.rmtree(dir_path)


def json_load(json_path: str)->Dict[str, any]:
    with open(json_path, "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict


def get_label2id(label_list: List[str], num_classes: int)->Dict[str, int]:
    label2id = {}
    class_num = 1
    for l in label_list:
        xml_obj = xml_load(l)
        for obj in xml_obj.findall("object"):
            class_name = obj.findtext("name")
            # read class_name
            if class_name not in label2id.keys():
                label2id.update({f"{class_name}": class_num})
                class_num += 1
    return label2id


def get_bbox_from_xml_obj(obj, label2id: Dict[str, str], anno: str, errors:List[str])->(int, int, int, int, List[str]):
    xml_file_name = Path(anno).parts[-1]
    label = obj.findtext("name")
    if not (label in label2id):
        errors.append(
            f"{label} is not in data.yaml but in {anno} file."
        )
    bndbox = obj.find("bndbox")
    xmin = int(float(bndbox.findtext("xmin")))
    ymin = int(float(bndbox.findtext("ymin")))
    xmax = int(float(bndbox.findtext("xmax")))
    ymax = int(float(bndbox.findtext("ymax")))
    return xmin, ymin, xmax, ymax, errors


def get_image_info_xml(annotation_root, extract_num_from_imgid=True)->Dict[str, any]:
    path = annotation_root.findtext("path")
    if path is None:
        filename = annotation_root.findtext("filename")
    else:
        filename = os.path.basename(path)
    img_name = os.path.basename(filename)
    img_id = os.path.splitext(img_name)[0]

    if extract_num_from_imgid and isinstance(img_id, str):
        img_id = int(re.findall(r"\d+", img_id)[0])

    size = annotation_root.find("size")
    width = int(size.findtext("width"))
    height = int(size.findtext("height"))

    image_info = {"file_name": filename, "height": height, "width": width, "id": img_id}
    return image_info


def xml_load(xml_path: str):
    tree = ET.parse(xml_path)
    annotation_root = tree.getroot()
    return annotation_root


def validate_first_dirs(dir_path: str, errors:List[str])->List[str]:
    paths = Path(dir_path).glob("*")
    check_dir_paths = []
    ret_dir_paths = []
    for p in paths:
        if p.is_dir():
            check_dir_paths.append(str(p.name))
            ret_dir_paths.append(str(p))
    if not ("train" in check_dir_paths):
        errors.append("Dataset dosen't have 'train' dir.")
    correct_cases = [
        set(["train", "val", "test"]),
        set(["train", "val"]),
        set(["train", "test"])
    ]
    if set(check_dir_paths) not in correct_cases:
        errors.append(
            "Dataset has wrong directory structure. Any other directory than ['train', 'val', 'test'] is not accepted."
        )
    return ret_dir_paths, errors


def validate_second_dirs(dir_path: List[str], errors:List[str])->List[str]:
    ret_dir_paths = []
    for sub_dir in dir_path:
        paths = Path(sub_dir).glob("*")
        check_dir_paths = []
        for p in paths:
            if p.is_dir():
                check_dir_paths.append(str(p.name))
                ret_dir_paths.append(str(p))
        if not ("images" in check_dir_paths):
            errors.append(f"Dataset dosen't have 'images' dir under {sub_dir}.")
        if not ("labels" in check_dir_paths):
            errors.append(f"Dataset dosen't have 'labels' dir under {sub_dir}.")
    return ret_dir_paths, errors


def replace_images2labels(path: str)->str:
    path = path.replace("train/images/", "train/labels/", 1)
    path = path.replace("val/images/", "val/labels/", 1)
    path = path.replace("test/images/", "test/labels/", 1)
    return path


def get_filename_wo_suffix(file_path:str):
    file_path = file_path.split(".")
    file_path = ".".join(file_path[:-1])
    return file_path


def validate_image_files_exist(img_list: List[str], label_list: List[str], suffix: str, errors:List[str]):
    img_name, label_name = [], []
    for i in img_list:
        path_wo_suffix = get_filename_wo_suffix(i)
        path_wo_suffix = replace_images2labels(path_wo_suffix)
        img_name += [path_wo_suffix]
    for l in label_list:
        label_name = get_filename_wo_suffix(l)
        if not label_name in img_name:
            errors.append(
                f"There is no image file for annotation file '{l}'"
            )
    return errors


def validate_data_yaml(dir_path: str, num_classes: int, errors:List[str]):
    yaml_path = Path(dir_path) / Path("data.yaml")
    if not yaml_path.is_file():
        errors.append("There is no 'data.yaml' file.")
    data_dict = yaml_safe_load(str(yaml_path))
    if not data_dict.get("names"):
        raise YamlException("There is no 'names' in data.yaml.")
    if not data_dict.get("nc"):
        raise YamlException("There is no 'nc' in data.yaml.")
    if len(data_dict["names"]) != data_dict["nc"]:
        errors.append("Length of 'names' and value of 'nc' in data.yaml must be same.")
    if num_classes != data_dict["nc"]:
        errors.append("Value of 'nc' in data.yaml must be same with num_classes.")
    if num_classes != len(data_dict["names"]):
        errors.append("Length of 'names' in data.yaml must be same with num_classes.")
    return data_dict['names'], errors


def validate_dataset_type(root_path: str, user_data_type: str):
    """
    data_type in ["coco", "yolo", "voc"]
    """
    target_dirs = ["train/labels/", "val/labels/", "test/labels/"]
    data_type = None
    for td in target_dirs:
        paths = (Path(root_path) / td).glob("**/*")
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
        raise DatatypeException(
            f"There are not any annotation files in {td}."
        )
    elif user_data_type != data_type:
        raise DatatypeException(
            f"Check correct data type, your dataset type looks like '{data_type}'."
        )
        

def get_dir_list(path: Path)->List[str]:
    """
    Return directory list
    """
    dir_list = []
    paths = Path(path).glob("**/*")
    for p in paths:
        if p.is_dir():
            dir_list.append(str(p))
    return dir_list


def does_it_have(paths: str, file_type_list: List[str])->bool:
    flag = False
    for types in file_type_list:
        files = Path(paths).glob(f"{types}")
        num_files = sum(1 for _ in files)
        if num_files > 0:
            flag = True
            return flag
    return flag


def get_target_dirs(dir_paths: List[str], file_types: List[str])->List[str]:
    """
    Return directory list which have files in same file types in file_types.
    """
    ret_dir_paths = []
    for p in dir_paths:
        answer = does_it_have(p, file_types)
        if answer:
            ret_dir_paths.append(p)
            continue
    return ret_dir_paths


def get_img_file_types()->List[str]:
    img_file_types = [
        "*.jpeg",
        "*.JPEG",
        "*.jpg",
        "*.JPG",
        "*.png",
        "*.PNG",
        "*.BMP",
        "*.bmp",
    ]
    return img_file_types


def write_error_txt(errors:List[str]):
    f = open("validation_result.txt", 'w')
    for e in errors:
        f.write(e+"\n")
    f.close()


def validate(root_path: str, num_classes: int, data_format:str, delete=False):
    print("Start dataset validation.")
    errors = []
    dir_path = Path(root_path)
    dir_paths, errors = validate_first_dirs(dir_path, errors)
    print("[Validate: 1/6]: Done validation dir structure ['train', 'val', 'test'].")
    _, errors = validate_second_dirs(dir_paths, errors)
    print("[Validate: 2/6]: Done validation dir structure ['images', 'labels'].")
    validate_dataset_type(root_path, data_format)
    print("[Validate: 3/6]: Done validation, user select correct data type.")
    img_list, label_list = get_file_lists(dir_paths)
    yaml_label, errors = validate_data_yaml(dir_path, num_classes, errors)
    print("[Validate: 4/6]: Done validation for 'data.yaml' file.")
    _validate = getattr(
        importlib.import_module(f"src.{data_format.lower()}"),
        "validate",
    )
    errors = _validate(dir_path, num_classes, label_list, img_list, yaml_label, errors)
    if len(errors) == 0:
        print("Validation completed! Now try your dataset on NetsPresso!")
    else:
        write_error_txt(errors)
        print("Validation error, please check 'validation_result.txt'.")
    if delete:
        delete_dirs(dir_path)