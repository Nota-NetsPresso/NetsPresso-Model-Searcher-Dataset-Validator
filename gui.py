#Import the Tkinter library
from run import execute 
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


#Create an instance of Tkinter frame
win= Tk()
win.title("NetsPresso Dataset Validator")
win.geometry()
win.resizable(0,0)
#Define the geometry


def select_train_dir():    
    input_dir = filedialog.askdirectory()
    train_dir.set(input_dir)

def select_test_dir():    
    input_dir = filedialog.askdirectory()
    test_dir.set(input_dir)

def select_valid_dir():    
    input_dir = filedialog.askdirectory()
    valid_dir.set(input_dir)

def select_output_dir():
    input_dir = filedialog.askdirectory()
    output_dir.set(input_dir)

def select_yaml():
    input_path = filedialog.askopenfilename()
    yaml_path.set(input_path)

def run():
    # execute(format, task, train_dir, test_dir, valid_dir, output_dir, yaml_path)
    input_dir = filedialog.askdirectory()
    output_dir.set(input_dir)
    progress.set("in progress")

    if test_dir.get() == '':
        test_dir_get = None
    else:
        test_dir_get = test_dir.get()
    if valid_dir.get() == '':
        valid_dir_get = None
    else:
        valid_dir_get = valid_dir.get()
    if output_dir.get() == '':
        output_dir_get = None
    else:
        output_dir_get = output_dir.get()
    if yaml_path.get() == '':
        yaml_path_get = None
    else:
        yaml_path_get = yaml_path.get()
    
    print(train_dir.get())
    execute(data_format.get(), "object_detection", train_dir.get(), test_dir_get, valid_dir_get, output_dir_get, yaml_path_get)
    progress.set("Done")


def yaml_switch():
    if data_format.get() == "yolo":
        yaml_button["state"] = "normal"
    else:
        yaml_button["state"] = "disabled"
        yaml_path.set(None)


def close():
    win.destroy()


train_dir = StringVar()
test_dir = StringVar()
valid_dir = StringVar()
output_dir = StringVar()
progress = StringVar()

frame_data_path = Frame(win, relief='ridge', bd=2, height=200, width=480)
frame_data_path.grid()
frame_data_path.grid_rowconfigure(4)

ttk.Label(frame_data_path, text="Dataset Path", font=("Arial", 10)).grid(column=0, row=0, sticky='w')
ttk.Label(frame_data_path, text="Train Dataset Path").grid(column=0, row=1, sticky='w')
train_dir_label = ttk.Entry(frame_data_path, textvariable=train_dir)
train_dir_label.grid(column=1, row=1)

train_data_button = ttk.Button(frame_data_path, text="Select", command=select_train_dir)
train_data_button.grid(column=2, row=1)


ttk.Label(frame_data_path, text="Test Dataset Path").grid(column=0, row=2, sticky='w')
test_dir_label = ttk.Entry(frame_data_path, textvariable=test_dir)
test_dir_label.grid(column=1, row=2)
test_data_button = ttk.Button(frame_data_path, text="Select", command=select_test_dir)
test_data_button.grid(column=2, row=2)


ttk.Label(frame_data_path, text="Validation Dataset Path").grid(column=0, row=3, sticky='w')
valid_dir_label = ttk.Entry(frame_data_path, textvariable=valid_dir)
valid_dir_label.grid(column=1, row=3)
valid_data_button = ttk.Button(frame_data_path, text="Select", command=select_valid_dir)
valid_data_button.grid(column=2, row=3)
ttk.Separator(frame_data_path, orient="horizontal").grid(column=0, row=4, columnspan=3, sticky='nesw')

ttk.Label(frame_data_path, text="Dataset Format", font=("Arial", 10)).grid(column=0, row=5, sticky='w')
data_format = StringVar(None, "yolo")
dataset_r1 = ttk.Radiobutton(frame_data_path, text="yolo", variable=data_format, value="yolo", command=yaml_switch)
dataset_r1.grid(column=0, row=6, sticky='w')
dataset_r2 = ttk.Radiobutton(frame_data_path, text="coco", variable=data_format, value="coco", command=yaml_switch)
dataset_r2.grid(column=0, row=7, sticky='w')
dataset_r3 = ttk.Radiobutton(frame_data_path, text="voc", variable=data_format, value="voc", command=yaml_switch)
dataset_r3.grid(column=0, row=8, sticky='w')

yaml_path = StringVar()
ttk.Label(frame_data_path, text="Data Yaml Path").grid(column=0, row=9, sticky='w')
yaml_label = ttk.Entry(frame_data_path, textvariable=yaml_path)
yaml_label.grid(column=1, row=9)
yaml_button = ttk.Button(frame_data_path, text="Select", command=select_yaml)
yaml_button.grid(column=2, row=9)

ttk.Separator(frame_data_path, orient="horizontal").grid(column=0, row=14, columnspan=3, sticky='nesw')
#ttk.Label(frame_data_path, text="Output Path").grid(column=0, row=15, sticky='w')
#output_dir_label = ttk.Entry(frame_data_path, textvariable=output_dir)
#output_dir_label.grid(column=1, row=15,sticky='w')
#output_path_button = ttk.Button(frame_data_path, text="Select", command=select_output_dir)
#output_path_button.grid(column=2, row=15, sticky='w')


ttk.Label(frame_data_path, textvariable=progress).grid(column=0, row=16, sticky='w')
run_button = ttk.Button(frame_data_path, text="run", command=run)
run_button.grid(column=1, row=16)
close_button = ttk.Button(frame_data_path, text="cancel", command=close)
close_button.grid(column=2, row=16, sticky='nesw')
win.mainloop()
