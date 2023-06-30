#-*- coding:utf-8 -*-
import sys
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List
from functools import reduce
import zipfile
import os
import glob
import yaml
import hashlib
import datetime

from loguru import logger

sys.path.append("app/core/validator")
from src.config import img_file_types
from src.exceptions import LabelException


global LOCAL
LOCAL=False


def get_target_suffix_file_list(dir_path: str, suffixes:List[str]):
    """
    Return image and label file list in form List[str], List[str]
    """
    file_list=[]
    for types in suffixes:
        files = Path(dir_path).glob(f"**/{types}")
        for f in files:
            if f.is_file():
                file_list.append(str(f))
    return sorted(file_list)


def yaml_safe_load(yaml_path: str) -> Dict[str, any]:
    with open(yaml_path, "r") as f:
        data_dict = yaml.safe_load(f)
    return data_dict


def delete_dirs(dir_path: str):
    shutil.rmtree(dir_path)


def json_load(json_path: str) -> Dict[str, any]:
    with open(json_path, "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict


def get_label2id(label_list: List[str], num_classes: int) -> Dict[str, int]:
    label2id = {}
    class_num = 1
    for l in label_list:
        try:
            xml_obj = xml_load(l)
        except:
            raise LabelException(f"{l} file is broken.")
        for obj in xml_obj.findall("object"):
            class_name = obj.findtext("name")
            # read class_name
            if class_name not in label2id.keys():
                label2id.update({f"{class_name}": class_num})
                class_num += 1
    return label2id


def get_bbox_from_xml_obj(
    obj, label2id: Dict[str, str], anno: str, errors: List[str]):
    xml_file_name = Path(anno).parts[-1]
    try:
        label = obj.findtext("name")
        if not (label in label2id):
            errors.append(f"{label} is not in 'yaml file', but in {anno} file.")
    except:
        errors.append(f"Can not find <name> in {anno}.")
    bndbox = obj.find("bndbox")
    if not bndbox:
        errors.append(f"Can not find <bndbox> in {anno}.")
        return 0, 0, 0, 0, errors

    def try_convert_bbox2number(
        bndbox, coord_name: str, anno: str, errors: List[str]
    ) -> int:
        try:
            ret = int(float(bndbox.findtext(coord_name)))
        except:
            errors.append(
                f"{bndbox.findtext(coord_name)} is not a number in {anno} file."
            )
            ret = 0
        return ret, errors

    xmin, errors = try_convert_bbox2number(bndbox, "xmin", anno, errors)
    xmax, errors = try_convert_bbox2number(bndbox, "xmax", anno, errors)
    ymin, errors = try_convert_bbox2number(bndbox, "ymin", anno, errors)
    ymax, errors = try_convert_bbox2number(bndbox, "ymax", anno, errors)
    return xmin, ymin, xmax, ymax, errors


def get_image_info_xml(annotation_root, extract_num_from_imgid=True) -> Dict[str, any]:
    path = annotation_root.findtext("path")
    if path is None:
        filename = annotation_root.findtext("filename")
    else:
        filename = str(Path(path).parts[-1])
    img_name = str(Path(filename).parts[-1])
    img_id = str(Path(img_name).stem)

    if extract_num_from_imgid and isinstance(img_id, str):
        img_id = int(re.findall(r"\d+", img_id)[0])

    size = annotation_root.find("size")
    width = int(size.findtext("width"))
    height = int(size.findtext("height"))

    image_info = {"file_name": filename, "height": height, "width": width, "id": img_id}
    return image_info


def xml_load(xml_path: str):
    with open(xml_path, 'r') as xml_file:
        tree = ET.parse(xml_path)
        annotation_root = tree.getroot()
    return annotation_root


def replace_images2labels(path: str) -> str:
    # for case of linux and mac user
    key = os.path.splitext(os.path.basename(path))[0]

    return key


def get_filename_wo_suffix(file_path: str):
    file_path = file_path.split(".")
    file_path = ".".join(file_path[:-1])
    return file_path


def get_dir_list(path: Path) -> List[str]:
    """
    Return directory list
    """
    dir_list = []
    paths = Path(path).glob("**/*")
    for p in paths:
        if p.is_dir():
            dir_list.append(str(p))
    return dir_list


def does_it_have(paths: str, file_type_list: List[str]) -> bool:
    flag = False
    for types in file_type_list:
        files = Path(paths).glob(f"{types}")
        num_files = sum(1 for _ in files)
        if num_files > 0:
            flag = True
            return flag
    return flag


def get_target_dirs(dir_paths: List[str], file_types: List[str]) -> List[str]:
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


def get_annotation_file_types():
    annotation_file_types =[
      "*.xml",
      "*.txt",
      "*.json"
    ]
    return annotation_file_types


def write_error_txt(errors: List[str], output_dir):
    f = open(os.path.join(output_dir,"validation_result.txt"), "a")
    for e in errors:
        f.write(e + "\n")
    f.close()


def log_n_print(message:str):
    if not LOCAL:
        logger.info(message)
    else:
        print(message)


def get_class_info_coco(annotation_file):
    with open(annotation_file, 'r', encoding='utf-8') as anno_file:
        anno = anno_file.read()
    anno_dict = json.loads(anno)
    categories = anno_dict["categories"]
    names = [cat["name"] for cat in categories]
    return names


def get_class_info_voc(annotation_file):
    xml_root = xml_load(annotation_file)
    object_eles = xml_root.findall("object")
    name_eles = []
    for obj in object_eles:
        name_eles += obj.findall("name")
    names = [n.text for n in name_eles]

    return names


def get_object_stat(annotation_file, format):
    if format == "coco":
        return get_object_stat_coco(annotation_file)
    if format == "voc":
        return get_object_stat_voc(annotation_file)
    

def get_object_stat_coco(annotation_file):
    with open(annotation_file, 'r') as anno_file:
        anno = anno_file.read()
    anno_dict = json.loads(anno)
    categories = anno_dict["categories"]
    categories_dict = {ele["id"]: ele["name"] for ele in categories}
    annotations = anno_dict["annotations"]
    stat_dict = {}
    for ele in categories_dict:
        stat_dict[ele] = 0

    for anno in annotations:
        stat_dict[anno["category_id"]] += 1
    
    ret = {}
    for ele in stat_dict:
        ret[categories_dict[ele]] = stat_dict[ele]
    return ret


def get_object_stat_voc(annotation_file):
    xml_root = xml_load(annotation_file)
    object_eles = xml_root.findall("object")
    obj_stat = {}
    for obj in object_eles:
        for obj_name in obj.findall("name"):
            obj_name_text = obj_name.text
            if obj_name_text in obj_stat:
                obj_stat[obj_name_text] += 1
            else:
                obj_stat[obj_name_text] = 1
    return obj_stat


def get_object_stat_yolo(annotation_file, names):
    with open(annotation_file, 'r') as anno_file:
        anno = anno_file.readlines()
    ret = {}
    for row in anno:
        class_name = names[int(row.split(' ')[0])]
        if class_name in ret:
            ret[class_name] += 1
        else:
            ret[class_name] = 1
    
    return ret
    

def yolo_stat(data_path, yaml_path):
    with open(yaml_path, 'r') as data_yaml:
        data_dict = yaml.load(data_yaml.read(), Loader=yaml.FullLoader)
    image_files = []
    for img_ext in img_file_types:
        image_files += glob.glob(f"{data_path}/images/{img_ext}")
    image_files = list(set(image_files))
    num_images = len(image_files)
    names = data_dict["names"]

    annotation_file_types = get_annotation_file_types()
    annotation_files = []
    for anno_ext in annotation_file_types:
        annotation_files += glob.glob(f"{data_path}/labels/{anno_ext}")
    annotation_files = list(set(annotation_files))
    obj_stat = []
    for anno in annotation_files:
        obj_stat.append(get_object_stat_yolo(anno, names))
    obj_stat_ret = reduce(sum_stat_dict, obj_stat)

    return names, obj_stat_ret, num_images
        

def sum_stat_dict(dict_a, dict_b):
    ret = {}
    for ele in set(dict_a.keys()).union(set(dict_b.keys())):
        ret[ele] = \
            int(0 if dict_a.get(ele) is None else dict_a.get(ele)) + \
            int(0 if dict_b.get(ele) is None else dict_b.get(ele))
    
    return ret


def structure_convert(data_dir:str, format:str):
    tmp_dir = os.path.join(data_dir, f'tmp_{datetime.datetime.now().strftime("%Y-%m-%dT%H%M%S")}')
    os.mkdir(tmp_dir)
    images_dir = os.path.join(tmp_dir, 'images')
    os.mkdir(images_dir)
    labels_dir = os.path.join(tmp_dir, 'labels')
    os.mkdir(labels_dir)
    image_files = []
    for img_ext in img_file_types:
        image_files += glob.glob(f"{data_dir}/{img_ext}")
    image_files = list(set(image_files))
    num_images = len(image_files)
    for img in image_files:
        shutil.copy(img, os.path.join(images_dir,os.path.basename(img)))
    
    annotation_file_types = get_annotation_file_types()
    annotation_files = []
    for anno_ext in annotation_file_types:
        annotation_files += glob.glob(f"{data_dir}/{anno_ext}")
    annotation_files = list(set(annotation_files))
    names = []
    obj_stat = []
    for anno in annotation_files:
        if format == "coco":
            names += get_class_info_coco(anno)
            obj_stat.append(get_object_stat_coco(anno))
        elif format == "voc":
            names += get_class_info_voc(anno)
            obj_stat.append(get_object_stat_voc(anno))
        shutil.copy(anno, os.path.join(labels_dir, os.path.basename(anno)))
    names = set(names)
    obj_stat_ret = reduce(sum_stat_dict, obj_stat)

    return tmp_dir, names, obj_stat_ret, num_images

    
def zip_packing(root_path, filename):
    zip_file = zipfile.ZipFile(f"{filename}", "w")
    for (path, dir, files) in os.walk(root_path):
        for file in files:
            file_path = os.path.join(path, file)
            rel_path = os.path.relpath(file_path, root_path)
            zip_file.write(file_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)
    zip_file.close()


def make_yaml_file(output_path, content):
    with open(output_path, 'w', encoding='utf-8') as f:
        yaml.dump(content, f, allow_unicode=True)


def make_yaml_content(names, num_images, obj_stat):
    nc = len(names)
    names = list(names)
    return {'nc': nc, 'names': names, 'num_images': num_images, 'obj_stat': obj_stat}


def calc_file_hash(path):
    f = open(path, 'rb')
    data = f.read()
    hash = hashlib.md5(data).hexdigest()   
    return hash


def zip_files(zip_file_name_on_path:str, target_dir:str):
    zip_file_path = f"{zip_file_name_on_path}.zip"
    zip_packing(target_dir, zip_file_path)
    return zip_file_path