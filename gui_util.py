import threading
from functools import partial
import webbrowser

import tkinter
import tkinter.ttk
import tkinter.messagebox
from tkinter import CURRENT, END, Text

from src.task.wrapper import BaseWrapper
from src.exceptions import ExceptionWithHyperlink
from src.config import dataset_docs_url


class HyperlinkManager:
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground="blue", underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        # add an action to the manager.  returns tags to use in
        # associated text widget
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.config(cursor="hand2")

    def _leave(self, event):
        self.text.config(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return


class Validator(threading.Thread):
    def __init__(self, dataset_type, task_type, train_dir_get, test_dir_get, valid_dir_get, output_dir_get, yaml_path_get, id2label_path_get, x, y):
        threading.Thread.__init__(self)
        self.daemon = True
        self.dataset_type=dataset_type
        self.task_type=task_type
        self.train_dir_get=train_dir_get
        self.test_dir_get=test_dir_get
        self.valid_dir_get=valid_dir_get
        self.output_dir_get=output_dir_get
        self.yaml_path_get=yaml_path_get
        self.id2label_path_get=id2label_path_get
        self.x=x
        self.y=y
        return

    def run(self):
        try:
            run(self.dataset_type, self.task_type, self.train_dir_get, self.test_dir_get, self.valid_dir_get, self.output_dir_get, self.yaml_path_get, self.id2label_path_get, self.x, self.y)
            return True
        except Exception as e:
            return e

def open_url(eventObject):
    webbrowser.open_new(eventObject.widget.cget("text"))


def run(
    dataset_type, 
    task_type, 
    train_dir_get, 
    test_dir_get, 
    valid_dir_get, 
    output_dir_get, 
    yaml_path_get, 
    id2label_path_get,
    x,
    y
    ):
    # 이 함수 안에서 storage_type 을 task, datasetformat class 의 post_process 에서 사용할 수 있도록 처리해아 합니다
    try:
        #start progress bar
        popup = tkinter.Toplevel()
        popup.geometry("+%d+%d" %(x+120,y+100))
        
        popup_label=tkinter.Label(popup, text="Start Validation", width=25)
        popup_label.grid(row=0,column=0)
        
        def progress_close():
            popup.destroy()

        progress = 0
        progress_var = tkinter.DoubleVar()
        progress_bar = tkinter.ttk.Progressbar(popup, variable=progress_var, maximum=100, mode="determinate", length=100, orient='horizontal') # mode can be indeterminate
        progress_bar.grid(row=1, column=0)
        progress_close_button = tkinter.ttk.Button(popup, text="cancel", command=progress_close)
        progress_close_button.grid(column=0, row=2, sticky='nesw')
        popup.pack_slaves()

        succeed_list = []
        base_wrapper = BaseWrapper(dataset_type, task_type)

        popup.update()
        popup_label.config(text="Doing validation preprocess.")
        base_wrapper.task_wrapper.task_class.preprocess(output_dir_get, valid_dir_get, test_dir_get)
        progress += 20
        progress_var.set(progress)

        popup.update()
        popup_label.config(text="Validate train dataset.")
        train_zip_path, train_yaml, train_md5, succeed = base_wrapper.dataset_format_wrapper.format_module.validate(
            yaml_path=yaml_path_get, 
            root_path=train_dir_get, 
            output_dir=output_dir_get, 
            split_name="train",
            id2label_path=id2label_path_get
            )    
        succeed_list.append(succeed)
        progress += 20
        progress_var.set(progress)

        popup.update()
        popup_label.config(text="Validate validation dataset.")
        if valid_dir_get:
            valid_zip_path, valid_yaml, valid_md5, succeed = base_wrapper.dataset_format_wrapper.format_module.validate(
                yaml_path=yaml_path_get, 
                root_path=valid_dir_get, 
                output_dir=output_dir_get, 
                split_name="val",
                id2label_path=id2label_path_get
                )
            succeed_list.append(succeed)
        else:
            valid_yaml=None
            valid_md5=None
        progress += 20
        progress_var.set(progress)

        popup.update()
        popup_label.config(text="Validate test dataset.")
        if test_dir_get :
            test_zip_path, test_yaml, test_md5, succeed = base_wrapper.dataset_format_wrapper.format_module.validate(
                yaml_path=yaml_path_get, 
                root_path=test_dir_get, 
                output_dir=output_dir_get, 
                split_name="test",
                id2label_path=id2label_path_get
            )
            succeed_list.append(succeed)
        else:
            test_yaml=None
            test_md5=None
        progress += 20
        progress_var.set(progress)

        popup.update()
        popup_label.config(text="Doing validate postprocess.")

        base_wrapper.task_wrapper.task_class.postprocess(
            dataset_type, 
            train_yaml, 
            valid_yaml, 
            test_yaml, 
            valid_dir_get, 
            test_dir_get, 
            train_md5, 
            test_md5, 
            valid_md5, 
            output_dir_get, 
            succeed_list,
            task_type
            )
        progress += 20
        progress_var.set(progress)

        if progress_var.get()==100:
            popup.destroy()

        if all(succeed_list): # success
            new_popup = tkinter.Toplevel()
            new_popup.geometry("+%d+%d" %(x+120,y+100))
            new_popup_label_first=tkinter.Label(new_popup, text="Validation Success!", width=25)
            new_popup_label_first.grid(row=0,column=0)
            new_popup_label_second=tkinter.Label(new_popup, text="Upload your dataset at ", width=25)
            new_popup_label_second.grid(row=1,column=0)
            new_popup_label_third = tkinter.Label(new_popup, text=r"https://netspresso.ai/", fg="blue", cursor="hand2")
            new_popup_label_third.grid(row=2,column=0)
            new_popup_label_third.bind("<Button-1>", open_url)
            
            def close():
                new_popup.destroy()

            close_button = tkinter.ttk.Button(new_popup, text="Ok", command=close)
            close_button.grid(column=0, row=3, sticky='nsew', pady=5, padx=5)
            new_popup.update()
        else:
            tkinter.messagebox.showinfo("Info", f"Validation Fail, Please read validation_result.txt file in {output_dir_get}")
    except ExceptionWithHyperlink as e:
        popup.destroy()
        error_message_popup = tkinter.Toplevel()
        error_message_popup.geometry("+%d+%d" %(x+120,y+100))
        error_message_popup_first=tkinter.Label(error_message_popup, text=str(e))
        error_message_popup_first.grid(row=0,column=0)
        error_message_popup_second = tkinter.Label(error_message_popup, text=f"{dataset_docs_url}", fg="blue", cursor="hand2")
        error_message_popup_second.grid(row=1,column=0)
        error_message_popup_second.bind("<Button-1>", open_url)

    except Exception as e:
        popup.destroy()
        tkinter.messagebox.showerror("Error", e)