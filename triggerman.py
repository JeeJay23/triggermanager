import tkinter as tk
from tkinter import ttk, filedialog, IntVar
from triggers import *
from os import path

root = tk.Tk ()
root.title ("triggerman")
root.geometry ("650x600")

# gui globals
FLASH_LENGTH = 200

# globals
selected_item = IntVar()
trigger_item_list = []

def open_file ():
    _path = filedialog.askopenfilename (
        filetypes=[
            ("all files", "*.*"),
            ("Mp3 Files", "*.mp3"),
            ("WAV files", "*.wav")
        ]
    )
    return _path

def update_element (_item, **kwargs):
    for key in kwargs:
        _item[key] = kwargs[key]

def update_trigger_wrapper (_item, _id, **kwargs):

    orig_color = _item.cget ("background")

    if 'path' in kwargs:
        _path = open_file ()
        if not (len (_path) == 0):
            kwargs['path'] = _path
            _item['text'] = path.basename (_path)

    if 'activation_frame' in kwargs:
        try:
            kwargs['activation_frame'] = int (kwargs['activation_frame'])
        except ValueError:
            _item['bg'] = "red"
            _item.delete (0, tk.END)
        else:
            _item['bg'] = "green"
            update_trigger (id=_id, **kwargs)
        finally:
            _item.after (FLASH_LENGTH, lambda: update_element (_item, bg=orig_color))
    else:
        _item['bg'] = "green"
        update_trigger (id=_id, **kwargs)
        _item.after (FLASH_LENGTH, lambda: update_element (_item, bg=orig_color))


def add_list_item (trigger):
    global selected_item

    # root of item
    lst_item        = tk.Frame          (frame_trigger_list)

    btn_selected    = tk.Radiobutton    (lst_item, variable=selected_item, value=trigger.id)
    lbl_id          = tk.Label          (lst_item, text="%02i" % trigger.id)
    entry_name      = tk.Entry          (lst_item)
    btn_filepath    = tk.Button         (
        lst_item,
        text="select file",
        command=lambda: update_trigger_wrapper (
            btn_filepath,
            trigger.id,
            path=1
        )
    )
    lbl_enabled     = tk.Label          (lst_item, text="enabled:")
    btn_enabled     = tk.Checkbutton    (lst_item, variable=trigger.enabled)
    entry_tframe    = tk.Entry          (lst_item)

    entry_name.insert   (0, trigger.name)
    entry_name.bind     (
        "<Return>",
        lambda a: update_trigger_wrapper (
            _item=entry_name,
            _id=trigger.id,
            name=entry_name.get ()
            )
        )

    entry_tframe.insert (0, str (trigger.activation_frame))
    entry_tframe.bind   (
        "<Return>",
        lambda a: update_trigger_wrapper (
            _item=entry_tframe,
            _id=trigger.id,
            activation_frame=entry_tframe.get ()
            )
    )

    lst_item.pack       (fill=tk.X, expand=1, anchor=tk.NW)
    btn_selected.pack   (side=tk.LEFT, padx=2, pady=1)
    lbl_id.pack         (side=tk.LEFT, padx=2, pady=1)
    entry_name.pack     (side=tk.LEFT, padx=2, pady=1)
    btn_filepath.pack   (side=tk.LEFT, padx=2, pady=1)
    lbl_enabled.pack    (side=tk.LEFT, padx=2, pady=1)
    btn_enabled.pack    (side=tk.LEFT)
    entry_tframe.pack   (side=tk.LEFT, padx=2, pady=1)

    trigger_item_list.append (lst_item)

def remove_item ():
    remove_trigger (selected_item.get ())
    trigger_item_list[selected_item.get ()].pack_forget ()

def add_item ():
    add_trigger ()
    add_list_item (trigger_list[-1])

# Setup scroll frame

container           = ttk.Frame (root)
canvas              = tk.Canvas (container)
scrollbar           = ttk.Scrollbar (container, orient="vertical", command=canvas.yview)
frame_trigger_list  = ttk.Frame (canvas)

frame_trigger_list.bind (
    "<Configure>",
    lambda e: canvas.configure (
        scrollregion = canvas.bbox ("all")
    )
)

canvas.create_window ((0,0), window=frame_trigger_list, anchor="nw")
canvas.configure (yscrollcommand=scrollbar.set)

btn_add         = tk.Button (root, text="add", command=add_item)
btn_remove      = tk.Button (root, text="remove", bg="red", command=remove_item)
btn_copy        = tk.Button (root, text="copy")

# packing

container.pack  (fill=tk.BOTH, expand=1, anchor=tk.N)
canvas.pack     (side=tk.LEFT, fill=tk.BOTH, expand=1)
scrollbar.pack  (side=tk.RIGHT, fill=tk.Y)
btn_add.pack    (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_remove.pack (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)
btn_copy.pack   (anchor=tk.NW, side=tk.LEFT, fill=tk.X, pady=2, padx=2)

root.mainloop ()
