import argparse
from src.utils import validate, structure_convert, zip_packing, make_yaml_file, calc_file_hash,  make_yaml_content, yolo_stat, log_n_print
import shutil
import os
import yaml


def main(dir_path, format, task, data_type, yaml_path=None, output_dir=None):
    if format == "yolo" and yaml_path is None:
        raise Exception("yaml_path should be defined for yolo format ")

    if format in ["coco", "voc"]:
        tmp_path, names, obj_stat, num_images = structure_convert(dir_path, format)
    else:
        tmp_path = dir_path
        names, obj_stat, num_images = yolo_stat(tmp_path, yaml_path)
        
    yaml_content = make_yaml_content(names, num_images, obj_stat)
    temp_yaml_path = os.path.join(tmp_path, "temp_yaml.yaml")
    make_yaml_file(temp_yaml_path, yaml_content)
    succeed = validate(tmp_path, format, temp_yaml_path, output_dir, task)
    zip_file_path = f"{output_dir}/{data_type}.zip"
    
    if succeed:
        zip_packing(tmp_path, zip_file_path)
        md5_hash = calc_file_hash(zip_file_path)
        if format in ["coco", "voc"]:
          shutil.rmtree(tmp_path)
        return zip_file_path, yaml_content, md5_hash, succeed
    else:
        if format in ["coco", "voc"]:
          shutil.rmtree(tmp_path)
        return zip_file_path, yaml_content, None, succeed
    
    
def execute(format, task, train_dir, test_dir=None, valid_dir=None, output_dir=None, yaml_path=None):
    if output_dir is None:
        return 
    os.makedirs(output_dir, exist_ok=True)
    if test_dir is None and valid_dir is None:
        raise Exception("At least one of test_dir or valid_dir should be specified")

    succeed_list = []
    train_zip_path, train_yaml, train_md5, succeed = main(train_dir, format, task, "train", yaml_path, output_dir) # train
    succeed_list.append(succeed)
    if test_dir :
        test_zip_path, test_yaml, test_md5, succeed = main(test_dir, format, task, "test", yaml_path, output_dir) # test
        succeed_list.append(succeed)
    if valid_dir :
        valid_zip_path, valid_yaml, valid_md5, succeed = main(valid_dir, format, task, "valid", yaml_path, output_dir) # valid
        succeed_list.append(succeed)

    yaml_all = {}
    yaml_all["nc"] = train_yaml["nc"]
    yaml_all["names"] = train_yaml["names"]
    yaml_all["train"] = {"num_images": train_yaml["num_images"], "obj_stat": train_yaml["obj_stat"]}
    if test_dir :
        yaml_all["test"] = {"num_images": test_yaml["num_images"], "obj_stat": test_yaml["obj_stat"]}
    if valid_dir :
        yaml_all["valid"] = {"num_images": valid_yaml["num_images"], "obj_stat": valid_yaml["obj_stat"]}

    md5_all = {}
    md5_all["train"] = train_md5
    if test_dir :
        md5_all["test"] = test_md5
    if valid_dir :
        md5_all["valid"] = valid_md5
    if format == "yolo":
        md5_all["data"] = calc_file_hash(yaml_path)
    
    make_yaml_file(f'{output_dir}/data.yaml', yaml_all)
    make_yaml_file(f'{output_dir}/validation_key.np', md5_all)

    if all(succeed_list):
        log_n_print("Validation completed! Now try your dataset on NetsPresso!")
    else:
        log_n_print("Validation error, please check 'validation_result.txt'.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dataset validator.")
    parser.add_argument("--format", type=str, required=True, help="dataset format")
    parser.add_argument("--task", type=str, default="detection", help="task")
    parser.add_argument("--yaml_path", type=str, required=False, help="yaml file path")
    parser.add_argument("--train_dir", type=str, required=True, help="train dataset path.")
    parser.add_argument("--test_dir", type=str, required=False, help="test dataset path.")
    parser.add_argument("--valid_dir", type=str, required=False, help="validation dataset path.")
    parser.add_argument("--output_dir", type=str, required=False, help="output directory")
    args = parser.parse_args()

    format, task, yaml_path, train_dir, test_dir, valid_dir, output_dir= (
        args.format.lower(),
        args.task.lower(),
        args.yaml_path,
        args.train_dir,
        args.test_dir,
        args.valid_dir,
        args.output_dir.rstrip('/')
    )
    
    execute(format, task, train_dir, test_dir, valid_dir, output_dir, yaml_path)
    