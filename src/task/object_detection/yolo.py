import sys
from pathlib import Path
from typing import List

sys.path.append("app/core/validator")
from src.utils import yolo_stat
from src.task.validate import validate_image_files_exist, validate_second_dir, validate_sub_dir_exsists
from src.task.object_detection.abs import ObjectDetectionDatasetFormat


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


class YOLO(ObjectDetectionDatasetFormat):
    def set_common_attrs(self, yaml_path:str, root_path:str, output_dir:str, split_name):
        # split_name:Literal["train", "val", "test"]
        if yaml_path is None:
            raise Exception("yaml_path should be defined for yolo format")
        self.yaml_path = yaml_path
        self.root_path = Path(root_path)
        self.output_dir = output_dir
        self.split_name = split_name

    def get_stat(self):
        tmp_path = str(self.root_path)
        names, obj_stat, num_images = yolo_stat(tmp_path, self.yaml_path)        
        return tmp_path, names, obj_stat, num_images
        
    def remove_trees(self, tmp_path):
        """
        Just being for inheritance.
        """
        pass

    def specific_validation_for_each_dataset(self, **kwargs):
        errors = kwargs["errors"]
        img_list = kwargs["img_list"]
        label_list = kwargs["label_list"]
        num_classes = kwargs["num_classes"]
        
        errors = validate_second_dir(self.root_path, errors, ["images", "labels"])
        validate_sub_dir_exsists(self.root_path/"images")
        validate_sub_dir_exsists(self.root_path/"labels")
        errors = validate_image_files_exist(img_list, label_list, errors)
        errors = validate_label_files(label_list, num_classes, errors, fix=False)
        return errors