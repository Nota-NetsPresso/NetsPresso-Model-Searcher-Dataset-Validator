from typing import Dict, List
import sys
import os

sys.path.append("app/core/validator")
from src.utils import (get_bbox_from_xml_obj, get_image_info_xml, 
                       get_label2id, validate_image_files_exist,
                       xml_load, log_n_print)


def validate_label_files(
    img_list: List[str],
    label_list: List[str],
    num_classes: int,
    label2id: Dict[str, int],
    errors: List[str]
):
    for anno in label_list:
        display_anno = os.path.basename(anno)
        try:
            xml_obj = xml_load(anno)
            image_info = get_image_info_xml(xml_obj)
        except:
            errors.append(f"{display_anno} is broken file.")
            return errors
        for obj in xml_obj.findall("object"):
            if not obj:
                errors.append(f"There is not object tag in {display_anno}.")
                continue
            xmin, ymin, xmax, ymax, errors = get_bbox_from_xml_obj(obj, label2id, anno, errors)
            if not image_info["width"]:
                errors.append(
                    f"There is not width in {display_anno}."
                )
                continue
            if not image_info["height"]:
                errors.append(
                    f"There is not height in {display_anno}."
                )
                continue
            if type(image_info["width"]) not in [int, float]:
                errors.append(
                    f"'width' is not a number in {display_anno}."
                )
                continue
            if type(image_info["height"]) not in [int, float]:
                errors.append(
                    f"'height' is not a number in {display_anno}."
                )
                continue
            if (xmax <= xmin) or (ymax <= ymin):
                errors.append(
                    f"Box size error in {display_anno}: (xmin, ymin, xmax, ymax): {xmin, ymin, xmax, ymax}."
                )
            if image_info["width"] < xmax:
                errors.append(
                    f"Box size error in {display_anno}: xmax: {xmax} is greater than 'width'."
                )
            if image_info["height"] < ymax:
                errors.append(
                    f"Box size error in {display_anno}: ymax: {ymax} is greater than 'height'."
                )
            if xmin < 0:
                errors.append(
                    f"Box size error in {display_anno}: xmin: {xmin} is negative value."
                )
            if ymin < 0:
                errors.append(
                    f"Box size error in {display_anno}: ymin: {ymin} is negative value."
                )
            if xmax < 0:
                errors.append(
                    f"Box size error in {display_anno}: xmax: {xmax} is negative value."
                )
            if ymax < 0:
                errors.append(
                    f"Box size error in {display_anno}: ymax: {ymax} is negative value."
                )
            if xmax == 0:
                errors.append(
                    f"Box size error in {display_anno}: xmax can not be 0."
                )
            if ymax == 0:
                errors.append(
                    f"Box size error in {display_anno}: ymax can not be 0."
                )                
    return errors


def validate_yaml_names(yaml_label:List[str], label2id:Dict[str, int], num_classes:int, errors:List[str]):
    for y in label2id.keys():
        if y not in yaml_label:
            errors.append(
                f"{y} is not in xml files. Class names in 'yaml file' have to match with xml files. Please check 'yaml file' and xml files. Class names in xml files are {list(label2id.keys())}.")

    if len(label2id) != num_classes:
        errors.append(
            f"'nc' is not matched with the number of classes in your datasets. The number of classes in dataset is {len(label2id)}. Class names in xml files are {list(label2id.keys())}."
        )
    return errors


def validate_label2id(label2id:Dict[str, int], errors:List[str]):
    if "None" in label2id.keys():
        errors.append("There is xml file without <name> in it. Please read following error messages to fix it. In the message with 'None is not in 'yaml file'', there is broken file name.")
    if label2id == {}:
        errors.append("Can not find any class name information in any xml files.")
        return False, errors
    else:
        return True, errors


def validate(
    dir_path: str, 
    num_classes: int, 
    label_list:List[str], 
    img_list:List[str], 
    yaml_label:List[str],
    errors:List[str],
    fix:bool=False # not used but be here for other dataset type
    ):
    label2id = get_label2id(label_list, num_classes)
    flag, errors = validate_label2id(label2id, errors)
    if not flag:
        return errors
    errors = validate_yaml_names(yaml_label, label2id, num_classes, errors)
    errors = validate_image_files_exist(img_list, label_list, "xml", errors)
    log_n_print("[Validate: 4/5]: Validation finished for existing image files in the correct position.")
    errors = validate_label_files(img_list, label_list, num_classes, label2id, errors)
    log_n_print("[Validate: 5/5]: Validation finished for label files.")
    return errors


