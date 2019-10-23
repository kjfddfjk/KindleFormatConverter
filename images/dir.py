import tkinter
from tkinter.filedialog import askdirectory

def selectPath():
    path_ = askdirectory()
    path.set(path_)

root = tkinter.Tk()
path = tkinter.StringVar()

tkinter.Label(root,text = "Folder:").grid(row = 0, column = 0)
tkinter.Entry(root, textvariable = path).grid(row = 0, column = 1)
tkinter.Button(root, text = "Choose folder", command = selectPath).grid(row = 0, column = 2)

root.mainloop()