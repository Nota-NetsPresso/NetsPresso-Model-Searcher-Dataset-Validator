import os
from typing import List, Dict, Any
from pathlib import Path
import shutil

from src.exceptions import LabelException
from src.config import label_suffix_mapping, version
from src.utils import make_yaml_file, calc_file_hash, log_n_print, make_yaml_content, write_error_txt, zip_files


class AbstractTask():
    def __init__(self,):
        pass
    
    def preprocess(self, output_dir:str, valid_dir:str, test_dir:str):
        if output_dir is None:
            raise Exception("output_dir must be defined.")
        os.makedirs(output_dir, exist_ok=True)
        if test_dir is None and valid_dir is None:
            raise Exception("At least one of test_dir or valid_dir should be specified.")

    def postprocess(
        self,
        format:str,
        train_yaml:Dict[str, Any],
        valid_yaml:Dict[str, Any],
        test_yaml:Dict[str, Any],
        valid_dir:str,
        test_dir:str,
        train_md5:str,
        test_md5:str,
        valid_md5:str,
        output_dir:str, 
        succeed_list:List[bool],
        task:str
        ):
        yaml_all = {}
        yaml_all["task"] = task
        yaml_all["nc"] = train_yaml["nc"]
        yaml_all["format"] = format
        yaml_all["names"] = train_yaml["names"]
        yaml_all["train"] = {"num_images": train_yaml["num_images"], "obj_stat": train_yaml["obj_stat"]}
        if test_dir :
            yaml_all["test"] = {"num_images": test_yaml["num_images"], "obj_stat": test_yaml["obj_stat"]}
        if valid_dir :
            yaml_all["val"] = {"num_images": valid_yaml["num_images"], "obj_stat": valid_yaml["obj_stat"]}

        md5_all = {}
        md5_all["train"] = train_md5
        if test_dir :
            md5_all["test"] = test_md5
        if valid_dir :
            md5_all["val"] = valid_md5

        make_yaml_file(f'{output_dir}/data.yaml', yaml_all)
        md5_all["data"] = calc_file_hash(f'{output_dir}/data.yaml')
        md5_all["version"] = version
        make_yaml_file(f'{output_dir}/certification.np', md5_all)

        if all(succeed_list):
            log_n_print("Validation completed! Now try your dataset on NetsPresso!")
        else:
            log_n_print("Validation error, please check 'validation_result.txt'.")


class AbstractDatasetFormat():
    def __init__(self, dataset_format:str):
        self.dataset_format = dataset_format
        self.label_file_suffix = label_suffix_mapping[dataset_format]
        self.dir_path = None

    def set_common_attrs(self, yaml_path:str, root_path:str, output_dir:str, split_name):
        # split_name:Literal["train", "val", "test"]
        self.yaml_path = yaml_path
        self.root_path = Path(root_path)
        self.output_dir = output_dir
        self.split_name = split_name

    def prepare_yaml(self, names:set, num_images:int, obj_stat:Dict[str, int], tmp_path:str):
        yaml_content = make_yaml_content(names, num_images, obj_stat)
        temp_yaml_path = os.path.join(tmp_path, "temp_yaml.yaml")
        make_yaml_file(temp_yaml_path, yaml_content)
        return temp_yaml_path, yaml_content

    def write_error_or_not(self, errors:List[str], output_dir:str):
        if len(errors) == 0:
            succeed = True
        else:
            write_error_txt(errors, output_dir)
            succeed = False
        return succeed

    def get_file_hash(zip_file_path:str):
        md5_hash = calc_file_hash(zip_file_path)
        return md5_hash

    def remove_file(self, file_path:str):
        # Used for remove tmp yaml file
        os.remove(file_path)

    def remove_trees(self, dir_path:str):
        # Used for remove tmp dir
        shutil.rmtree(dir_path)

    def postprocess(self, errors:List[str], output_dir:str, temp_yaml_path:str, split_name:str, tmp_path:str):
        succeed = self.write_error_or_not(errors, output_dir)
        self.remove_file(temp_yaml_path)
        if succeed:
            zip_file_path = zip_files(os.path.join(output_dir, split_name), tmp_path)
            md5_hash = calc_file_hash(zip_file_path)
        else:
            # zip_file_path, md5_hash = None, None
            raise LabelException("Validation fail, please read validation_result.txt")
        return zip_file_path, md5_hash, succeed