import argparse
from pathlib import Path
from src.task.wrapper import BaseWrapper
from src.config import DatasetType, TaskType
from src.exceptions import DirectoryException


def execute(
    format: str,
    task: str,
    train_dir: str = None,
    test_dir: str = None,
    valid_dir: str = None,
    output_dir: str = None,
    yaml_path: str = None,
    id2label_path: str = None,
    dataset_root_path: str = None,
    storage_type: str = None,
    server_info_path: str = None,
):
    if storage_type == "local":
        for path in Path(dataset_root_path).iterdir():
            if path.is_dir():
                if path.parts[-1] == "train":
                    train_dir = Path(dataset_root_path) / "train"
                elif path.parts[-1] == "val":
                    valid_dir = Path(dataset_root_path) / "val"
                elif path.parts[-1] == "test":
                    test_dir = Path(dataset_root_path) / "test"
        
        # validate train/val/test dir
        if train_dir:
            if not (test_dir or valid_dir):
                raise DirectoryException(f"valid or test folder should exists.")
        else:
            raise DirectoryException(f"train folder should exists.")

    succeed_list = []
    base_wrapper = BaseWrapper(format, task)
    base_wrapper.task_wrapper.task_class.preprocess(
        output_dir, valid_dir, test_dir, storage_type
    )
    (
        train_zip_path,
        train_yaml,
        train_md5,
        succeed,
    ) = base_wrapper.dataset_format_wrapper.format_module.validate(
        yaml_path=yaml_path,
        root_path=train_dir,
        output_dir=output_dir,
        split_name="train",
        id2label_path=id2label_path,
        storage_type=storage_type,
    )
    succeed_list.append(succeed)
    if valid_dir:
        (
            valid_zip_path,
            valid_yaml,
            valid_md5,
            succeed,
        ) = base_wrapper.dataset_format_wrapper.format_module.validate(
            yaml_path=yaml_path,
            root_path=valid_dir,
            output_dir=output_dir,
            split_name="val",
            id2label_path=id2label_path,
            storage_type=storage_type,
        )
        succeed_list.append(succeed)
    else:
        valid_yaml = None
        valid_md5 = None
    if test_dir:
        (
            test_zip_path,
            test_yaml,
            test_md5,
            succeed,
        ) = base_wrapper.dataset_format_wrapper.format_module.validate(
            yaml_path=yaml_path,
            root_path=test_dir,
            output_dir=output_dir,
            split_name="test",
            id2label_path=id2label_path,
            storage_type=storage_type,
        )
        succeed_list.append(succeed)
    else:
        test_yaml = None
        test_md5 = None

    base_wrapper.task_wrapper.task_class.postprocess(
        format=format,
        train_yaml=train_yaml,
        valid_yaml=valid_yaml,
        test_yaml=test_yaml,
        valid_dir=valid_dir,
        test_dir=test_dir,
        train_md5=train_md5,
        test_md5=test_md5,
        valid_md5=valid_md5,
        output_dir=output_dir,
        succeed_list=succeed_list,
        task=task,
        dataset_root_path=dataset_root_path,
        storage_type=storage_type,
        server_info_path=server_info_path,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset validator.")

    parser.add_argument(
        "--format",
        type=DatasetType,
        choices=list(DatasetType),
        required=True,
        help="dataset format",
    )
    parser.add_argument(
        "--task",
        type=TaskType,
        choices=list(TaskType),
        default="object_detection",
        help="task",
    )
    ## s3 upload case
    parser.add_argument("--yaml_path", type=str, required=False, help="yaml file path")
    parser.add_argument(
        "--id2label_path", type=str, required=False, help="id2label file path"
    )
    parser.add_argument(
        "--train_dir", type=str, required=False, help="train dataset path."
    )
    parser.add_argument(
        "--test_dir", type=str, required=False, help="test dataset path."
    )
    parser.add_argument(
        "--valid_dir", type=str, required=False, help="validation dataset path."
    )
    parser.add_argument(
        "--output_dir", type=str, default="", required=False, help="output directory"
    )

    # local upload case
    parser.add_argument(
        "--dataset_root_path", type=str, required=False, help="Dataset root path."
    )
    parser.add_argument(
        "--storage_type",
        type=str,
        default="s3",
        required=False,
        help="storage type of dataset(s3 or local)",
    )
    parser.add_argument(
        "--server_info_path",
        type=str,
        required=False,
        help="server_info_netspresso.json file path",
    )

    args = parser.parse_args()

    (
        format,
        task,
        yaml_path,
        train_dir,
        test_dir,
        valid_dir,
        output_dir,
        id2label_path,
        dataset_root_path,
        storage_type,
        server_info_path,
    ) = (
        str(args.format),
        str(args.task),
        args.yaml_path,
        args.train_dir,
        args.test_dir,
        args.valid_dir,
        args.output_dir.rstrip("/"),
        args.id2label_path,
        args.dataset_root_path,
        args.storage_type,
        args.server_info_path,
    )

    if storage_type == "local":
        output_dir = dataset_root_path
    execute(
        format,
        task,
        train_dir,
        test_dir,
        valid_dir,
        output_dir,
        yaml_path,
        id2label_path,
        dataset_root_path,
        storage_type,
        server_info_path,
    )
