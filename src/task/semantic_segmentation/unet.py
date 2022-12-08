from typing import Dict, Literal, List

import cv2

from src.config import img_file_types
from src.exceptions import Id2LabelJsonException
from src.utils import json_load, get_target_suffix_file_list
from src.task.validate import validate_second_dir, validate_image_mask_1_on_1_match
from src.task.semantic_segmentation.abs import SemanticSegmentationDatasetFormat


def validate_id2label_json_file(json_file_path:str):
    # From id2label.json file, all key must be str which that can be type change to int.
    json_obj = json_load(json_file_path)
    succeed_list = []
    for k, v in json_obj.items():
        try:
            int(k)
            succeed_list.append(True)
        except:
            raise Id2LabelJsonException("Key in id2label must be integer string.")
    

def count_class_appeared(image_file_list:List[str], id_count:Dict[str, int]):
    for img_file_path in image_file_list:
        img = cv2.imread(img_file_path)
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        for id in id_count:
            if int(id) in img:
                id_count[id] += 1
    return id_count


def get_id_count_dict(json_file_path:str):
    json_obj = json_load(json_file_path)
    ret_dict = {}
    for k, v in json_obj.items():
        ret_dict[k]=0
    return ret_dict


def get_class_names(json_file_path:str):
    json_obj = json_load(json_file_path)
    names = []
    for k, v in json_obj.items():
        names.append(v)
    return names


def get_obj_stat(id2label_dict, id_count_dict):
    obj_stat={}
    for k, v in id2label_dict.items():
        obj_stat[id2label_dict[k]]=id_count_dict[k]
    return obj_stat


class UNET(SemanticSegmentationDatasetFormat):
    def get_stat(self, id2label_path):
        img_list = get_target_suffix_file_list(self.root_path/"image", img_file_types)
        label_list = get_target_suffix_file_list(self.root_path/"mask", img_file_types)
        num_images = len(img_list)
        default_id_count_dict = get_id_count_dict(id2label_path)
        id_count_dict = count_class_appeared(label_list, default_id_count_dict)
        id2label_dict = json_load(id2label_path)
        obj_stat = get_obj_stat(id2label_dict, id_count_dict)
        names = get_class_names(id2label_path)
        tmp_path = str(self.root_path)
        return tmp_path, names, obj_stat, num_images

    def specific_validation_for_each_dataset(self, **kwargs):
        errors = kwargs["errors"]
        img_list = kwargs["img_list"]
        label_list = kwargs["label_list"]
        id2label_path = kwargs["id2label_path"]
        validate_id2label_json_file(id2label_path)
        errors = validate_second_dir(self.root_path, errors, ["image", "mask"])
        errors = validate_image_mask_1_on_1_match(img_list, label_list, errors)
        # errors = validate_label_files(label_list, num_classes, errors, fix=False) # TODO: Do it need to validte mask file?
        return errors