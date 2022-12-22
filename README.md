# Validate your dataset structure to use NetsPresso

## How to use

### Install requirements
```
pip3 install -r requirements.txt
```
### Run
Run the command below to validate when the data is ready-to-use. If you do not get any error message, you are all set! If error occurs, please refer to the error message to resolve the issue.
* task: object_detection, image_classification, semantic_segmentation
```
python3 run.py --format {dataset_format} --task {task type} --yaml_path {data.yaml file path(only required in yolo format)} --id2label {id2label.json file path(only required in unet format)}--train_dir {train foler path} --valid_dir {validation folder path} --test_dir {test folder path} --output_dir {output path}
```

### Validation success case

Five(or Four) files will be created at the selected output path.
```
train.zip, val.zip, test.zip, certification.np, data.yaml
```
**certification.np** contains certification and file information which created together.
Make sure that the files are not changed. If any file changes, the certification will not work and may not enable you to upload dataset to NetsPresso.

```
netspresso@netspresso:~/NetsPresso-ModelSearch-Dataset-Validator$ python3 run.py --format yolo --yaml_path ./data.yaml --train_dir ./dataset/train --valid_dir ./dataset/val --test_dir ./dataset/test --output_dir ./output
Start dataset validation.
Validation completed! Now try your dataset on NetsPresso!
```
### Validation fail case

For more detail, please see [Validation check list][validationchecklist]

In case of validation fail with traceback, please read exception error message.
```
netspresso@netspresso:~/NetsPresso-ModelSearch-Dataset-Validator$ python3 run.py --format yolo --task object_detection --yaml_path ./data.yaml --train_dir ./dataset/train --valid_dir ./dataset/val --test_dir ./dataset/test --output_dir ./output
Start dataset validation.
Traceback (most recent call last):
  File "run.py", line 13, in <module>
    validate(dir_path, num_classes, dataset_type)
  File "/hdd1/home/NetsPresso-ModelSearch-Dataset-Validator/src/utils.py", line 307, in validate
    yaml_label, errors = validate_data_yaml(dir_path, num_classes, errors)
  File "/hdd1/home/NetsPresso-ModelSearch-Dataset-Validator/src/utils.py", line 199, in validate_data_yaml
    raise YamlException("There is no 'names' in data.yaml.")
src.exceptions.YamlException: There is no 'names' in data.yaml.
```
In case of validation fail with Validation error, please check 'validation_result.txt'., please check validation_result.txt file to resolve failure.
```
netspresso@netspresso:~/NetsPresso-ModelSearch-Dataset-Validator$ python3 run.py --format yolo --task object_detection --yaml_path ./data.yaml --train_dir ./dataset/train --valid_dir ./dataset/val --test_dir ./dataset/test --output_dir ./output
Start dataset validation.
Validation error, please check 'validation_result.txt'.
```
And contents of 'validation_result.txt are like below.
```
There is no image file for annotation file 'yolo/train/labels/000000000025.txt'
There is no image file for annotation file 'yolo/test/labels/000000000337.txt'
```

## Dataset Structure

Please read this link: [Dataset Structure](https://docs.netspresso.ai/docs/ms-step1-prepare-dataset)
