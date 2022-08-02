from typing import Dict, List
from pathlib import Path
import sys
import json

from loguru import logger
sys.path.append("app/core/validator")
from src.utils import (json_load, get_dir_list,
                       get_img_file_types, get_target_dirs, log_n_print)


def validate_coco_bbox(
    bbox: List[float], 
    image_width: float, 
    image_height: float, 
    label_file: str,
    annotation_id: int,
    errors:List[str]
):
    x, y, w, h = bbox[0], bbox[1], bbox[2], bbox[3]
    if not image_width >= x + w:
        errors.append(
            f"'x'+'width' in bbox cannot be greater than image file's width, please check annotations['id'] = {annotation_id} in {label_file}."
        )
    if not image_height >= y + h:
        errors.append(
            f"'y'+'height' in bbox cannot be greater than image file's width, please check annotations['id'] = {annotation_id} in {label_file}."
        )
    if not x >= 0:
        errors.append(
            f"'x' in bbox cannot be a negative value, please check annotations['id'] = {annotation_id} in {label_file}."
        )
    if not y >= 0:
        errors.append(
            f"'y' in bbox cannot be a negative value, please check annotations['id'] = {annotation_id} in {label_file}."
        )
    if not w > 0:
        errors.append(
            f"'width' in bbox cannot be a negative value, please check annotations['id'] = {annotation_id} in {label_file}."
        )
    if not h > 0:
        errors.append(
            f"'height' in bbox cannot be a negative value, please check annotations['id'] = {annotation_id} in {label_file}."
        )
    if not image_width >= x:
        errors.append(
            f"There can't be a bbox with width greater than the width of image, please check annotations['id'] = {annotation_id} in {label_file}."
        )
    if not image_height >= y:
        errors.append(
            f"There can't be a bbox with height greater than the height of image, please check annotations['id'] = {annotation_id} in {label_file}."
        )
    return errors


def validate_coco_label(
    images: List[Dict], 
    annotations: List[Dict], 
    json_file_name: str, 
    num_classes: int,
    errors: List[str]
):
    class_ids = []
    image_flag = True
    for img in images:
        if img.get("id") is None:
            errors.append(
                f"There is an image information without 'id' in 'images' in file {json_file_name}."
            )
            image_flag = False
        elif type(img.get("id")) != int:
            errors.append(
                f"There is an image information which 'id' is not a number in 'images' in file {json_file_name}."
            )
            image_flag = False
        elif img.get("id") < 0:
            errors.append(
                f"There is an image information which 'id' is a negative in 'images' in file {json_file_name}."
            )
            image_flag = False
        if img.get("file_name") is None:
            errors.append(
                f"There is an image information without 'file_name' in 'images' where images['id'] is {img.get('id')} in file {json_file_name}."
            )
            image_flag = False
        if img.get("height") is None:
            errors.append(
                f"There is an image information without 'height' in 'images' where images['id'] is {img.get('id')} in file {json_file_name}."
            )

            image_flag = False
        elif type(img.get("height")) not in [int, float]:
            errors.append(
                f"There is an image information with 'height' is not a number where images['id'] is {img.get('id')} in file {json_file_name}."
            )
            image_flag = False
        elif img.get("height") <= 0:
            errors.append(
                f"There is an image information with wrong 'height' value in 'images' where images['id'] is {img.get('id')} in file {json_file_name}."
            )
            image_flag = False

        if img.get("width") is None:
            errors.append(
                f"There is an image information without 'width' in 'images' where images['id'] is {img.get('id')} in file {json_file_name}."
            )
            image_flag = False
        elif type(img.get("width")) not in [int, float]:
            errors.append(
                f"There is an image information with 'width' is not a number where images['id'] is {img.get('id')} in file {json_file_name}."
            )
            image_flag = False
        elif img.get("width") <= 0:
            errors.append(
                f"There is an image information with wrong 'width' value in 'images' where images['id'] is {img.get('id')} in file {json_file_name}."
            )
            image_flag = False
    if not image_flag:
        return errors
    
    anno_flag = True
    for anno in annotations:
        if anno.get("id") is None:
            errors.append(
                f"There is an annotation information without 'id' in 'annotations' in file {json_file_name}."
            )
        elif type(anno.get("id")) != int:
            errors.append(
                f"There is an annotation information with 'id' which is not a number in file {json_file_name}."
            )
        elif anno.get("id") < 0:
            errors.append(
                f"There is an annotation information which 'id' is a negative in 'images' in file {json_file_name}."
            )
        if anno.get("image_id") is None:
            errors.append(
                f"There is an annotation information without 'image_id' in 'annotations' where annotations['id'] is {anno.get('id')} in file {json_file_name}."
            )
        elif type(anno.get("image_id")) != int:
            errors.append(
                f"There is an annotation information with 'image_id' which is not a number in file {json_file_name}."
            )
        elif anno.get("image_id") < 0:
            errors.append(
                f"There is an annotation information which 'image_id' is a negative in 'images' in file {json_file_name}."
            )
        if anno.get("bbox") is None:
            errors.append(
                f"There is an annotation information without 'bbox' in 'annotations'  where annotations['id'] is {anno.get('id')} in file {json_file_name}."
            )

        if anno.get("category_id") is None:
            errors.append(
                f"There is an annotation information without 'category_id' in 'annotations'  where annotations['id'] is {anno.get('id')} in file {json_file_name}."
            )
        elif type(anno.get("category_id")) != int:
            errors.append(
                f"There is an annotation information with 'category_id' is not a number in 'annotations' where annotations['id'] is {anno.get('id')} in file {json_file_name}."
            )
            anno_flag = False
        elif anno.get("category_id") < 0:
            errors.append(
                f"There is an annotation information with 'category_id':{anno.get('category_id')} is negative in {json_file_name}."
            )
        else:
            class_ids.append(anno.get("category_id"))
        for img in images:
            if (img.get("id") == anno.get("image_id")) and anno.get("bbox") and img.get("width") and img.get("height"):
                errors = validate_coco_bbox(
                    anno.get("bbox"), 
                    img.get("width"), 
                    img.get("height"), 
                    json_file_name, 
                    anno.get("id"), 
                    errors)
    if anno_flag and (max(class_ids) > num_classes-1):
        errors.append(
            f"'category_id' value {max(class_ids)} is greater than expected. Check 'annotations' in {json_file_name}.'category_id' have to be equal or less than {num_classes-1}."
        )
    return errors


def validate_category_id(categories: Dict[List, Dict[str, int]], json_path:str, errors:List[str], num_classes:int):
    nc = []
    for c in categories:
        if c.get("id") is None:
            errors.append(
                f"There is a category information without 'id' in 'categories' in {json_path}."
            )
        elif type(c["id"]) != int or c["id"] <= -1:
            errors.append(
                f"There is an inappropriate 'id' value '{c['id']}'' in 'categories' in {json_path}."
            )
        elif c.get("id") is not None:
            nc.append(c["id"])
    if max(nc) >= num_classes:
        errors.append(
                f"There is a category information with greater 'id' than expected in 'categories' in {json_path}."
            )
    if len(nc) != num_classes:
        errors.append(
                f"Number of category information in {json_path} is not matched with 'nc'."
            )
    return errors


def validate_label_files(label_list: List[str], num_classes: int, errors:List[str]):
    for ll in label_list:
        try:
            json_dict = json_load(ll)
        except:
            errors.append(f"'{ll}' file is broken or has an SyntaxError.")
            return errors
        if not json_dict.get("categories"):
            errors.append(f"'categories' key does not exist in the file {ll}.")
        else:
            categories = json_dict.get("categories")
            errors = validate_category_id(categories, ll, errors, num_classes)            
        if not json_dict.get("images"):
            errors.append(f"'images' key does not exist in the file {ll}.")
        if not json_dict.get("annotations"):
            errors.append(f"'annotations' key does not exist in the file {ll}.")
        if json_dict.get("images") and json_dict.get("annotations"):
            images = json_dict["images"]
            annotations = json_dict["annotations"]
            errors = validate_coco_label(images, annotations, ll, num_classes, errors)
    return errors


def validate_json_exist(dir_path: Path, errors:List[str]):
    dirs = get_dir_list(dir_path)
    img_file_types = get_img_file_types()
    image_dir_paths = get_target_dirs(dirs, img_file_types)
    json_dir_paths = get_target_dirs(dirs, ["*.json"])
    if len(image_dir_paths) != len(json_dir_paths):
        errors.append("'json' annotation file must exist in the corresponding directory. Please read 'https://github.com/Nota-NetsPresso/NetsPresso-ModelSearch-Dataset-Validator#coco-dataset-structure-example'")
    return errors


def validate(
    dir_path: str, 
    num_classes: int, 
    label_list:List[str], 
    img_list:None,
    yaml_label:None,
    errors:List[str],
    fix:bool=False, # not used but be here for other dataset type
):
    """
    'img_list' and 'yaml_label' are not used in this function, but written for dynamic importing in src.utils.py
    """
    errors = validate_json_exist(dir_path, errors)
    log_n_print("[Validate: 4/5]:  Validation finished for existing json files in the correct position.")
    errors = validate_label_files(label_list, num_classes, errors)
    log_n_print("[Validate: 5/5]: Validation finished for label files.")
    return errors



