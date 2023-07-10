# Validate your dataset structure to use NetsPresso

## How to use
### 1. Create python virtual environment and activate it
```
python3 -m venv .venv && source .venv/bin/activate
```
### 2. Install requirements
```
pip3 install -r requirements.txt
```
### 3. Run CLI

Run the command below to validate when the data is ready-to-use. If you do not get any error message, you are all set! If error occurs, please refer to the error message to resolve the issue.

#### :small_blue_diamond:When uploading via Netspresso web page


```
python3 run.py --format {dataset_format} \
               --task {task type} \
               --storage_type {storage_type} \
               --yaml_path {data.yaml file path(only required in yolo format)} \
               --train_dir {train foler path} --valid_dir {validation folder path} \
               --test_dir {test folder path} \
               --output_dir {output path} \
               --id2label {id2label.json file path(only required in unet format)}

```
| Argument        	| Values                                                          	| Description                                           	| Required                     |
|-----------------	|-----------------------------------------------------------------	|-------------------------------------------------------	|:----------------------------:|
| --format        	| yolo / voc / coco / unet / imagenet                             	| format of the dataset                                 	|              O               |
| --task          	| image_classification / object_detection / semantic_segmentation 	| task of the dataset                                   	|              O               |
| --storage_type   	| s3 / local                                                      	| storage type of the dataset            			           	|              O               |
| --yaml_path     	| ex) ./coco_dataset/data.yaml                                    	| yaml file path for yolo format dataset                	| only when using yolo format  |
| --train_dir     	| ex) ./coco_dataset/train                                        	| train dataset folder path                             	|              O               |
| --test_dir      	| ex) ./coco_dataset/test                                         	| test dataset folder path                              	|           optional           |
| --valid_dir     	| ex) ./coco_dataset/val                                          	| valid dataset folder path                             	|           optional           |
| --output_dir    	| ex) ./validation_dataset                                        	| output folder where validation results will be stored 	|           optional           |
| --id2label_path 	| ex) ./unet_dataset/id2label.json                                	| id2label file path for unet format dataset            	| only when using unet format  |

#### :small_blue_diamond:When using dataset in personal server
```
python3 run.py --format {dataset_format} \
               --task {task type} \
               --storage_type {storage_type} \
               --dataset_root_path {dataset root folder path} \
               --yaml_path {data.yaml file path(only required in yolo format)} \
               --id2label {id2label.json file path(only required in unet format)} \
               --server_info_path {server_info_netspresso.json file path}

```

arguments: 

| Argument          	| Values                                                          | Description                                           | Required                    |
|-----------------  	|-----------------------------------------------------------------|------------------------------------------------------	|:-----------------------------:|
| --format     	      | yolo / voc / coco / unet / imagenet                             | format of the dataset                  	              |              O              	|
| --task      	      | image_classification / object_detection / semantic_segmentation | task of the dataset                        	          |              O              	|
| --storage_type     	| s3 / local                                                      | storage type of the dataset                           |              O              	|
| --dataset_root_path | ex) ./coco_dataset/                                             | dataset root path                                  	  |              O              	|
| --yaml_path         | ex) ./coco_dataset/data.yaml                                    | yaml file path for yolo format dataset                |only when using yolo format    |
| --id2label_path     | ex) ./unet_dataset/id2label.json                                | id2label file path for unet format dataset            | only when using unet format 	|
| --server_info_path  | ex) ./netspresso/server_info_netspresso.json                    | A server information file which is generated upon registering a personal training server|O|

### Validation success case

**certification.np** contains certification and file information which created together.
Make sure that the files are not changed. If any file changes, the certification will not work and may not enable you to upload dataset to NetsPresso.

```
netspresso@netspresso:~/NetsPresso-ModelSearch-Dataset-Validator$ python3 run.py --format yolo --yaml_path ./data.yaml --train_dir ./dataset/train --valid_dir ./dataset/val --test_dir ./dataset/test --output_dir ./output
Start dataset validation.
Validation completed! Now try your dataset on NetsPresso!
```

#### :small_blue_diamond:When using dataset in personal server


Five(or Four) files will be created at the selected output path.
```
train.zip
val.zip
test.zip
certification.np
data.yaml
```

#### :small_blue_diamond:When using dataset in personal server

Two files will be created as shown below at the dataset root path.
```
certification.np
data.yaml
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
