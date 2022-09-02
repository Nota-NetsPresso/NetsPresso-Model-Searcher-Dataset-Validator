# Validate your dataset structure to use NetsPresso

## How to use

### Install requirements
```
pip3 install -r requirements.txt
```
### Run
Run the command below to validate when the data is ready-to-use. If you do not get any error message, you are all set! If error occurs, please refer to the error message to resolve the issue.
```
python3 run.py --format {dataset_format} --yaml_path {data.yaml file path(only required in yolo format)} --train_dir {train foler path} --valid_dir {validation folder path} --test_dir {test folder path} --output_dir {output path}
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
[Validate: 1/5]: Done validation dir structure.
[Validate: 2/5]: Done validation, user select correct data type.
[Validate: 3/5]: Done validation for data.yaml file.
[Validate: 4/5]: Validation finished for existing image files in the correct position.
[Validate: 5/5]: Validation finished for label files.
Validation completed! Now try your dataset on NetsPresso!
```
### Validation fail case

For more detail, please see [Validation check list][validationchecklist]

In case of validation fail with traceback, please read exception error message.
```
netspresso@netspresso:~/NetsPresso-ModelSearch-Dataset-Validator$ python3 run.py --format yolo --yaml_path ./data.yaml --train_dir ./dataset/train --valid_dir ./dataset/val --test_dir ./dataset/test --output_dir ./output
Start dataset validation.
[Validate: 1/5]: Done validation dir structure.
[Validate: 2/5]: Done validation, user select correct data type.
[Validate: 3/5]: Done validation for data.yaml file.
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
netspresso@netspresso:~/NetsPresso-ModelSearch-Dataset-Validator$ python3 run.py --format yolo --yaml_path ./data.yaml --train_dir ./dataset/train --valid_dir ./dataset/val --test_dir ./dataset/test --output_dir ./output
Start dataset validation.
[Validate: 1/5]: Done validation dir structure.
[Validate: 2/5]: Done validation, user select correct data type.
[Validate: 3/5]: Done validation for data.yaml file.
[Validate: 4/5]: Validation finished for existing image files in the correct position.
[Validate: 5/5]: Validation finished for label files.
Validation error, please check 'validation_result.txt'.
```
And contents of 'validation_result.txt are like below.
```
There is no image file for annotation file 'yolo/train/labels/000000000025.txt'
There is no image file for annotation file 'yolo/test/labels/000000000337.txt'
```

## Dataset structure for NetsPresso
NetsPresso supports YOLO, COCO, and VOC formats for object detection tasks. (YOLO format is recommended.)
There are labeling tools, such as [CVAT][cvatlink] and [labelimg][labelimglink] support these annotation formats.

### Supported image file types
'bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo' are supported.

### [YOLO] Dataset structure example
YOLO format has a '.txt' file for each image with the same file name. However, if there is no object in the image file, no '.txt' file is required for that image. Make sure that every '.txt' file requires a corresponding image file.
To train a model, a "train" dataset and at least one of "val" and "test" dataset must exist.
### Prepare dataset yaml file
In yolo format, "data.yaml" file containing information about the class name and number of classes is needed.

- all elements of the names must be written in the same class number as the dataset.
- names: Names of classes
- nc: Number of classes

#### Yaml file example
```
names:
- aeroplane
- bicycle
- bird
- boat
- bottle
- bus
- car
- cat
- chair
- cow
- diningtable
- dog
- horse
- motorbike
- person
- pottedplant
- sheep
- sofa
- train
- tvmonitor
nc: 20
```
Dataset structure example
```
{train_folder}
   ├── images
   │   ├── example_1.jpg
   │   └── example_2.jpg
   └── labels
       ├── example_1.txt
       └── example_2.txt
{val_folder}
   ├── images
   │   ├── example_3.jpg
   │   └── example_4.jpg
   └── labels
       ├── example_3.txt
       └── example_4.txt
{test_folder}
   ├── images
   │   ├── example_5.jpg
   │   └── example_6.jpg
   └── labels
       ├── example_5.txt
       └── example_6.txt
```

### annotation file example for YOLO format
![sample](https://user-images.githubusercontent.com/45225793/141430419-9c94f0ba-d08f-4d73-83c1-78947cbdae84.png)
<p align="center"><img src="https://user-images.githubusercontent.com/45225793/128144814-3f613edf-3a31-4d88-878d-45ac01ca08a3.png"></p>

- One row per object
- Each row is ```{class number} {center_x} {center_y} {width} {height}```
- Box coordinates must be in normalized xywh format (from 0 - 1). If your boxes are in pixels, divide ```center_x``` and ```width``` by image width, and ```center_y``` and ```height``` by image height.
  - For example,  an image above has a size of ```width 623px, height 396px```. And the coordinate of first object in its label are ```center_x 259, center_y 196, width 246, height 328```. After normalization, the coordinates are ```center_x 0.415730, center_y 0.494949, width 0.394864, height 0.828283```.
- Class numbers are zero-indexed (starting from 0).

### [COCO] Dataset structure example
Please refer to the official [COCO Data format][cocoformat] for COCO label format.
To train a model, a "train" dataset and at least one of "val" and "test" dataset must exist.
```
{train_folder}
   ├── example_1.jpg
   ├── example_2.jpg
   └── annotations.json (contain annotaions of train dataset images)
{val_folder}
   ├── example_3.jpg
   ├── example_4.jpg
   └── annotations.json (contain annotaions of val dataset images)
{test_folder}
   ├── example_5.jpg
   ├── example_6.jpg
   └── annotations.json (contain annotaions of test dataset images)   
```

If supercategory exist in categories, supercategory class will be added to the output data.yaml file.

```
    "categories": [
        {
            "id": 0,
            "name": "animal",
            "supercategory": "none"
        },
        {                                        names:
            "id": 1,                             - animal
            "name": "cat",                =>     - cat
            "supercategory": "animal"            - dog
        },                                       nc: 3
        {
            "id": 2,
            "name": "doc",
            "supercategory": "animal"
        }
    ]
```

### [VOC] Dataset structure example
VOC format has one '.xml' file per image with the same file name. If there is no object in an image, no '.xml' file is required for the image. Make sure that every '.xml' file requires a corresponding image file.
Please refer to the official [VOC Data format][vocformat] for VOC label format.
To train a model, a "train" dataset and at least one of "val" and "test" dataset must exist.
```
{train_folder}
   ├── example_1.jpg
   ├── example_2.jpg
   ├── example_1.xml
   └── example_2.xml
{val_folder}
   ├── example_3.jpg
   ├── example_4.jpg
   ├── example_3.xml
   └── example_4.xml
{test_folder}
   ├── example_5.jpg
   ├── example_6.jpg
   ├── example_5.xml
   └── example_6.xml
```

[cocoformat]: https://cocodataset.org/#format-data
[labelimglink]: https://github.com/tzutalin/labelImg
[cvatlink]: https://github.com/openvinotoolkit/cvat
[convert2yololink]: https://github.com/ssaru/convert2Yolo
[vocformat]: http://host.robots.ox.ac.uk/pascal/VOC/voc2007/
[validationchecklist]: https://github.com/Nota-NetsPresso/NetsPresso-ModelSearch-Dataset-Validator/blob/main/validation_check_list.md
[yaml_file]:https://github.com/Nota-NetsPresso/NetsPresso-ModelSearch-Dataset-Validator/tree/main#yaml-file-example
