import glob
import os
import shutil
import sys
import zipfile
from pathlib import Path, PurePath, PurePosixPath
from typing import Dict, List

import yaml

from src.utils import (get_file_lists, replace_images2labels,
                       validate_data_yaml, validate_dataset_type,
                       validate_first_dirs, validate_image_files_exist,
                       validate_second_dirs, yaml_safe_load)


def validate_label_files(label_list: List[str], num_classes: int, errors:List[str]):
    for ll in label_list:
        with open(ll, "r") as f:
            line = f.readlines()
            ret_file_name = "/".join(ll.split("/")[4:])
            line_number = 0
            for l in line:
                line_number += 1
                label = l.split("\n")
                values = label[0].split(" ")
                if type(int(values[0])) != int:
                    errors.append(
                        f"{ll} has wrong class number in line {line_number}."
                        )
                if len(values) != 5:
                    errors.append(
                        f"{ll} need more coordinat value in line {line_number}."
                        )
                if (int(values[0]) >= num_classes) or (int(values[0]) < 0):
                    errors.append(
                        f"{ll} has wrong class number {values[0]} in line {line_number}."
                        )
                if len(values) != 5:
                    errors.append(
                        f"{ll} need more coordinat value in line {line_number}."
                        )
                else:
                    for i in range(len(values)):
                        values[i] = float(values[i])
                    if values[1] <= 0 or values[1] > 1: # center_x
                        errors.append(
                            f"{ll} has wrong coordinate 'center_x' {values[1]} in line {line_number}."
                            )
                    if values[2] <= 0 or values[2] > 1: # center_y
                        errors.append(
                            f"{ll} has wrong coordinate 'center_y' {values[2]} in line {line_number}."
                            )
                    if values[3] <= 0 or values[3] > 1: # width
                        errors.append(
                            f"{ll} has wrong coordinate 'width' {values[3]} in line {line_number}."
                            )
                    if values[4] <= 0 or values[4] > 1: # height
                        errors.append(
                            f"{ll} has wrong coordinate 'height' {values[4]} in line {line_number}."
                            )
    return errors


def validate(
    dir_path: str, 
    num_classes: int, 
    label_list:List[str], 
    img_list:List[str],
    yaml_path:None,
    errors:List[str]
):
    errors = validate_image_files_exist(img_list, label_list, "txt", errors)
    print("[Validate: 5/6]: Validation finished for existing image files in the correct position.")
    errors = validate_label_files(label_list, num_classes, errors)
    print("[Validate: 6/6]: Validation finished for label files.")
    return errors