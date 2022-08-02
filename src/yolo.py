from typing import Dict, List
import sys
import json

sys.path.append("app/core/validator")
from src.utils import validate_image_files_exist, log_n_print, get_annotation_file_types

def validate_label_files(
    label_list: List[str], num_classes: int, errors: List[str], fix: bool = False
):
    for ll in label_list:
        with open(ll, "r") as f:
            line = f.readlines()

        if fix:
            f = open(ll, "w")

        # ret_file_name = "/".join(ll.split("/")[4:])
        line_number = 0
        for l in line:
            line_number += 1
            label = l.split("\n")
            values = label[0].split(" ")

            if len(values) != 5:  # Tag 1 -> prevent IndexError
                errors.append(f"{ll} need 5 values in line {line_number}.")
                continue  # prevent for index error below with not matched error message.
            try:  # prevent TypeError
                values[0] = int(values[0])
            except:
                errors.append(f"{ll} has non-acceptable class value in {line_number}.")
                continue
            if (values[0] >= num_classes) or (values[0] < 0):
                errors.append(
                    f"{ll} has wrong class number {values[0]} in line {line_number}."
                )
            else:
                for i in range(len(values)):
                    try:  # Tag 2 -> prevent TypeError
                        values[i] = float(values[i])
                    except:
                        errors.append(
                            f"{ll} has non-acceptable coordinate value in {line_number}."
                        )
                try:  # do try for in case of TypeError
                    if values[1] <= 0 or values[1] >= 1:  # center_x
                        errors.append(
                            f"{ll} has wrong coordinate 'center_x' {values[1]} in line {line_number}."
                        )
                        # fix
                        values[1] = 0 if values[1] <= 0 else 1
                except:
                    pass  # Error message for TypeError and IndexError added already in Tag 1&2
                try:  # do try for in case of TypeError
                    if values[2] <= 0 or values[2] >= 1:  # center_y
                        errors.append(
                            f"{ll} has wrong coordinate 'center_y' {values[2]} in line {line_number}."
                        )
                        # fix
                        values[2] = 0 if values[2] <= 0 else 1
                except:
                    pass  # Error message for TypeError and IndexError added already in Tag 1&2
                try:  # do try for in case of TypeError
                    if values[3] <= 0 or values[3] > 1:  # width
                        errors.append(
                            f"{ll} has wrong coordinate 'width' {values[3]} in line {line_number}."
                        )
                        # fix
                        values[3] = 0 if values[3] <= 0 else 1
                except:
                    pass  # Error message for TypeError and IndexError added already in Tag 1&2
                try:  # do try for in case of TypeError
                    if values[4] <= 0 or values[4] > 1:  # height
                        errors.append(
                            f"{ll} has wrong coordinate 'height' {values[4]} in line {line_number}."
                        )
                        # fix
                        values[4] = 0 if values[4] <= 0 else 1
                except:
                    pass  # Error message for TypeError and IndexError added already in Tag 1&2

            if fix:
                if 0.0 not in values[1:]:
                    f.write(
                        f"{int(values[0])} {values[1]:.3f} {values[2]:.3f} {values[3]:.3f} {values[4]:.3f}\n"
                    )

        f.close()

    return errors


def validate(
    dir_path: str,
    num_classes: int,
    label_list: List[str],
    img_list: List[str],
    yaml_path: None,
    errors: List[str],
    fix: bool=False,
):
    errors = validate_image_files_exist(img_list, label_list, "txt", errors)
    log_n_print("[Validate: 4/5]: Validation finished for existing image files in the correct position.")
    errors = validate_label_files(label_list, num_classes, errors, fix)
    log_n_print("[Validate: 5/5]: Validation finished for label files.")
    return errors

