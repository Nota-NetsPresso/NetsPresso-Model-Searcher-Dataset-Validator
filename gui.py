import tkinter
import tkinter.ttk
from tkinter import filedialog
from pathlib import Path

from gui_util import Validator
from src.exceptions import JsonException, YamlException, DirectoryException


task_option_list=[
    "Object Detection",
    "Image Classification",
    "Semantic Segmentation"
] 

image_classification_dataset=[
    "ImageNet"
]
object_detection_dataset=[
    "YOLO (Recommended)",
    "COCO",
    "VOC",
]
semantic_segmentation_dataset=[
    "UNet(like YOLO)",
]

task_map={
    "Object Detection":"object_detection",
    "Image Classification":"image_classification",
    "Semantic Segmentation":"semantic_segmentation"
}

dataset_map={
    "COCO":"coco",
    "VOC":"voc",
    "YOLO (Recommended)":"yolo",
    "ImageNet":"imagenet",
    "UNet(like YOLO)":"unet",
}

row_order={
    "task_title":0,
    "task_combobox":1,
    "dataset_title":2,
    "dataset_combobox":3,
    "first_separator":4,
    # "dataset_dir":5,
    "train":5,
    "valid":6,
    "test":7,
    "extra":8,
    "second_separator":9,
    "output":10,
    "run_button":11,
    "close_button":11,
}

title_column = 0
button_column = 1
label_column = 2

window = tkinter.Tk()
window.title("NetsPresso Dataset Validator")
window.eval('tk::PlaceWindow . center')
window.geometry()
window.resizable(0,0)

frame=tkinter.Frame(window, relief='ridge', bd=2, height=1000, width=1000)
frame.grid()
frame.grid_rowconfigure(0, minsize=20)


def get_task(eventObject):
    if task_combobox.get()=="Object Detection":
        dataset_combobox.config(value=object_detection_dataset)
        dataset_combobox.set("")
    elif task_combobox.get()=="Image Classification":
        dataset_combobox.config(value=image_classification_dataset)
        dataset_combobox.set("")
    elif task_combobox.get()=="Semantic Segmentation":
        dataset_combobox.config(value=semantic_segmentation_dataset)
        dataset_combobox.set("")


def select_train_dir():
    input_dir = filedialog.askdirectory()
    train_dir.set(input_dir)


def select_valid_dir():
    input_dir = filedialog.askdirectory()
    valid_dir.set(input_dir)


def select_test_dir():    
    input_dir = filedialog.askdirectory()
    test_dir.set(input_dir)


def select_output_dir():
    input_dir = filedialog.askdirectory()
    output_dir.set(input_dir)


def select_yaml():
    input_path = filedialog.askopenfilename()
    yaml_path.set(input_path)


def select_id2label():
    input_path = filedialog.askopenfilename()
    id2label_path.set(input_path)


def close():
    window.destroy()


def combine_switch(eventObject):
    yaml_switch(eventObject)
    id2label_switch(eventObject)


def yaml_switch(eventObject):
    if dataset_map[dataset_combobox.get()] == "yolo":
        yaml_button["state"] = "normal"
        yaml_path.set("")
        yaml_title.grid(column=title_column, row=row_order["extra"], sticky='w')
        yaml_label.grid(column=label_column, row=row_order["extra"])
        yaml_button.grid(column=button_column, row=row_order["extra"])
    else:
        yaml_button["state"] = "disabled"
        yaml_path.set(None)
        yaml_title.grid_remove()
        yaml_label.grid_remove()
        yaml_button.grid_remove()


def id2label_switch(eventObject):
    if dataset_map[dataset_combobox.get()] == "unet":
        id2label_button["state"] = "normal"
        id2label_path.set("")
        id2label_title.grid(column=title_column, row=row_order["extra"], sticky='w')
        id2label_label.grid(column=label_column, row=row_order["extra"])
        id2label_button.grid(column=button_column, row=row_order["extra"])
    else:
        id2label_button["state"] = "disabled"
        id2label_path.set(None)
        id2label_title.grid_remove()
        id2label_label.grid_remove()
        id2label_button.grid_remove()        


def on_click_proceed():
    ok_cancel_messagebox=tkinter.messagebox.askokcancel("Proceed", "Do you want to proceed?")
    if ok_cancel_messagebox:
        try:
            dataset_type, task_type, train_dir_get, test_dir_get, valid_dir_get, output_dir_get, yaml_path_get, id2label_path_get = get_validator_input()
            input_validation(yaml_path_get, id2label_path_get, train_dir_get, test_dir_get, valid_dir_get, output_dir_get)
            x = window.winfo_x()
            y = window.winfo_y()
            validator = Validator(dataset_type, task_type, train_dir_get, test_dir_get, valid_dir_get, output_dir_get, yaml_path_get, id2label_path_get, x, y)
            validator.start()
        except Exception as e:
            tkinter.messagebox.showerror("Error", e)
    else:
        pass


def get_validator_input():
    output_dir.get()
    
    if test_dir.get() == '':
        test_dir_get = None
    else:
        test_dir_get = test_dir.get()

    if valid_dir.get() == '':
        valid_dir_get = None
    else:
        valid_dir_get = valid_dir.get()
    
    if yaml_path.get() == '':
        yaml_path_get = None
    else:
        yaml_path_get = yaml_path.get()
    if id2label_path.get() == '':
        id2label_path_get = None
    else:
        id2label_path_get = id2label_path.get()
           # dataset_type                       # task_type                    # train_dir      # test_dir    # valid_dir    # output_dir      # yaml_path    # id2label_path
    return dataset_map[dataset_combobox.get()], task_map[task_combobox.get()], train_dir.get(), test_dir_get, valid_dir_get, output_dir.get(), yaml_path_get, id2label_path_get


def input_validation(yaml_path_get, id2label_path_get, train_dir_get:str, test_dir_get:str, valid_dir_get:str, output_dir_get:str):
    if train_dir_get == "":
        raise DirectoryException("Select 'Training Dataset'.")
    if test_dir_get is None and valid_dir_get is None:
        raise DirectoryException("Select at least one 'Valid Dataset' or 'Testing Dataset'.")
    if output_dir_get == "":
        raise DirectoryException("Select 'Output Directory'.")
    if yaml_path_get is None:
        raise YamlException("Select yaml file for 'Data yaml Path'.")
    else:
        if Path(yaml_path_get).suffix != ".yaml" and yaml_path_get != "None":
            raise YamlException("Select yaml file for 'Data yaml Path'.")
    if id2label_path_get is None:
        raise JsonException("Select json file for 'id2label Path(json)'.")
    else:
        if Path(id2label_path_get).suffix != ".json" and id2label_path_get != "None":
            raise JsonException("Select json file for 'id2label Path(json)'.")


task_title=tkinter.Label(frame, text="Task", font=("Arial", 10, "bold"))
task_title.grid(column=title_column, row=row_order["task_title"], sticky='w') # grid return None always
task_combobox=tkinter.ttk.Combobox(frame, height=len(task_option_list), value=task_option_list)
task_combobox.set("Select task type") 
task_combobox.grid(column=title_column, row=row_order["task_combobox"], sticky='w')
task_combobox.bind("<<ComboboxSelected>>", get_task) # event, triggerd function

dataset_title=tkinter.Label(frame, text="Dataset format", font=("Arial", 10, "bold"))
dataset_title.grid(column=title_column, row=row_order["dataset_title"], sticky='w')
dataset_combobox=tkinter.ttk.Combobox(frame, value=[""])
dataset_combobox.set("")
dataset_combobox.grid(column=title_column, row=row_order["dataset_combobox"], sticky='w')
dataset_combobox.bind("<<ComboboxSelected>>", combine_switch) # event, triggerd function+

first_separator=tkinter.ttk.Separator(frame, orient="horizontal")
first_separator.grid(column=0, row=row_order["first_separator"], columnspan=3, sticky='ew')

# dataset_dir_title=tkinter.Label(frame, text="Dataset Directory", font=("Arial", 10, "bold"))
# dataset_dir_title.grid(column=title_column, row=row_order["dataset_dir"], sticky='w')

train_dir = tkinter.StringVar()
tkinter.ttk.Label(frame, text="Training Dataset(max 5GB)").grid(column=title_column, row=row_order["train"], sticky='w')
train_dir_label=tkinter.ttk.Entry(frame, textvariable=train_dir)
train_dir_label.grid(column=label_column, row=row_order["train"])

train_data_button = tkinter.ttk.Button(frame, text="Browse", command=select_train_dir)
train_data_button.grid(column=button_column, row=row_order["train"])

valid_dir = tkinter.StringVar()
tkinter.ttk.Label(frame, text="Validation Dataset(max 1GB)").grid(column=title_column, row=row_order["valid"], sticky='w')
valid_dir_label = tkinter.ttk.Entry(frame, textvariable=valid_dir)
valid_dir_label.grid(column=label_column, row=row_order["valid"])

valid_data_button = tkinter.ttk.Button(frame, text="Browse", command=select_valid_dir)
valid_data_button.grid(column=button_column, row=row_order["valid"])

test_dir = tkinter.StringVar()
tkinter.ttk.Label(frame, text="Testing Dataset(max 1GB)").grid(column=title_column, row=row_order["test"], sticky='w')
test_dir_label=tkinter.ttk.Entry(frame, textvariable=test_dir)
test_dir_label.grid(column=label_column, row=row_order["test"])

test_data_button = tkinter.ttk.Button(frame, text="Browse", command=select_test_dir)
test_data_button.grid(column=button_column, row=row_order["test"])

yaml_path = tkinter.StringVar()
yaml_title = tkinter.ttk.Label(frame, text="Yaml file")
yaml_title.grid_remove()
yaml_label = tkinter.ttk.Entry(frame, textvariable=yaml_path)
yaml_label.grid_remove()

yaml_button = tkinter.ttk.Button(frame, text="Browse", command=select_yaml)
yaml_button.grid_remove()

id2label_path = tkinter.StringVar()
id2label_title = tkinter.ttk.Label(frame, text="id2label Path(json)")
id2label_title.grid_remove()
id2label_label = tkinter.ttk.Entry(frame, textvariable=id2label_path)
id2label_label.grid_remove()

id2label_button = tkinter.ttk.Button(frame, text="Browse", command=select_id2label)
id2label_button.grid_remove()

second_separator= tkinter.ttk.Separator(frame, orient="horizontal")
second_separator.grid(column=0, row=row_order["second_separator"], columnspan=3, sticky='nesw')

output_dir = tkinter.StringVar()
output_title = tkinter.ttk.Label(frame, text="Output Directory", font=("Arial", 10, "bold"))
output_title.grid(column=title_column, row=row_order["output"], sticky='w')
output_dir_label = tkinter.ttk.Entry(frame, textvariable=output_dir)
output_dir_label.grid(column=label_column, row=row_order["output"])

output_dir_button = tkinter.ttk.Button(frame, text="Browse", command=select_output_dir)
output_dir_button.grid(column=button_column, row=row_order["output"])

third_seperator = tkinter.ttk.Separator(frame, orient="horizontal")
third_seperator.grid(column=title_column, row=11, columnspan=3, sticky='nesw')
run_button = tkinter.ttk.Button(frame, text="Run", command=on_click_proceed)
run_button.grid(column=button_column, row=row_order["run_button"])
close_button = tkinter.ttk.Button(frame, text="Cancel", command=close)
close_button.grid(column=title_column, row=row_order["close_button"], sticky='w')

window.mainloop()