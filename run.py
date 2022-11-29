import argparse
import shutil
import os
import yaml
from typing import Literal

from src.task.wrapper import BaseWrapper
from src.config import DatasetType, TaskType


def execute(
        format:str, 
        task:str, 
        train_dir:str, 
        test_dir:str=None, 
        valid_dir:str=None,
        output_dir:str=None, 
        yaml_path:str=None,
        id2label_path:str=None,
        ):
    succeed_list = []
    base_wrapper = BaseWrapper(format, task)
    base_wrapper.task_wrapper.task_class.preprocess(output_dir, valid_dir, test_dir)

    train_zip_path, train_yaml, train_md5, succeed = base_wrapper.dataset_format_wrapper.format_module.validate(
        yaml_path=yaml_path, 
        root_path=train_dir, 
        output_dir=output_dir, 
        split_name="train",
        id2label_path=id2label_path
        )
    succeed_list.append(succeed)
    if valid_dir :
        valid_zip_path, valid_yaml, valid_md5, succeed = base_wrapper.dataset_format_wrapper.format_module.validate(
            yaml_path=yaml_path, 
            root_path=valid_dir, 
            output_dir=output_dir, 
            split_name="val",
            id2label_path=id2label_path
            )
        succeed_list.append(succeed)
    if test_dir :
        test_zip_path, test_yaml, test_md5, succeed = base_wrapper.dataset_format_wrapper.format_module.validate(
            yaml_path=yaml_path, 
            root_path=test_dir, 
            output_dir=output_dir, 
            split_name="test",
            id2label_path=id2label_path
        )
        succeed_list.append(succeed)
    
    base_wrapper.task_wrapper.task_class.postprocess(format, train_yaml, valid_yaml, test_yaml, valid_dir, test_dir, train_md5, test_md5, valid_md5, output_dir, succeed_list)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset validator.")
    parser.add_argument("--format", type=DatasetType, choices=list(DatasetType), required=True, help="dataset format")
    parser.add_argument("--task", type=TaskType, choices=list(TaskType), default="object_detection", help="task")
    parser.add_argument("--yaml_path", type=str, required=False, help="yaml file path")
    parser.add_argument("--id2label_path", type=str, required=False, help="id2label file path")
    parser.add_argument("--train_dir", type=str, required=True, help="train dataset path.")
    parser.add_argument("--test_dir", type=str, required=False, help="test dataset path.")
    parser.add_argument("--valid_dir", type=str, required=False, help="validation dataset path.")
    parser.add_argument("--output_dir", type=str, required=False, help="output directory")
    args = parser.parse_args()

    format, task, yaml_path, train_dir, test_dir, valid_dir, output_dir, id2label_path=(
        str(args.format),
        str(args.task),
        args.yaml_path,
        args.train_dir,
        args.test_dir,
        args.valid_dir,
        args.output_dir.rstrip('/'),
        args.id2label_path
    )
    
    execute(format, task, train_dir, test_dir, valid_dir, output_dir, yaml_path, id2label_path)