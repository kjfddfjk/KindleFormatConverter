#!/usr/bin/env python
import os
import sys
import tempfile
from functools import reduce
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import dialog
from tkinter import messagebox
from collections import OrderedDict
from PIL import Image, ImageTk

# GLOBAL VARIBALES
# expect size
scale = 1
iconW = 24 * scale
iconH = 24 * scale
canX = 300
canY = 400
path = ''
tkImg = ''
imagesList = []
messages = ''


class App:
    def __init__(self, master):
        self.master = master
        self.initWidgets()

    def initWidgets(self):
        # Initial icons
        self.init_icons()

        self.tabControl = ttk.Notebook(
            self.master)          # Create Tab Control
        self.messageLabel = tk.Label(
            self.master, text="App Status Messages...")
        self.tabControl.pack(side=tk.TOP, fill="both", expand=tk.YES,
                             padx=5, pady=5, ipady=5)  # Pack to make visible
        self.messageLabel.pack(side=tk.RIGHT, fill=tk.X, expand=tk.NO)
        self.initTextTab(self.tabControl)
        self.initImageTab(self.tabControl)
        self.initSettingTab(self.tabControl)

    def initTextTab(self, tabControl):
        textTab = ttk.Frame(tabControl)
        tabControl.add(textTab, text='Text',
                       image=self.master.icons["novel_icon"], compound=tk.LEFT)

    def initImageTab(self, tabControl):
        global imagesList
        imgTab = ttk.Frame(tabControl)
        tabControl.add(imgTab, text='Comic',
                       image=self.master.icons["image_icon"], compound=tk.LEFT)

        # 创建两边的Frame
        leftFrame = ttk.Frame(imgTab, width=80)
        leftFrame.pack(side=tk.LEFT, fill=tk.BOTH, ipadx=5, ipady=5)
        rightFrame = ttk.Frame(imgTab)
        rightFrame.pack(side=tk.TOP, fill=tk.BOTH, ipadx=5, ipady=5)

        # 左边的Frame
        directoryButton = tk.Button(leftFrame, text='Import Images')
        listVar = tk.StringVar()
        imageListbox = tk.Listbox(leftFrame, font=(
            'Courier New', 16), listvariable=listVar)
        scroll = ttk.Scrollbar(leftFrame)
        directoryButton.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        directoryButton.bind('<ButtonRelease-1>', lambda event,
                             listVar=listVar: self.ListImages(listVar))
        # lambda: self.ListImages(event, imageListbox))
        imageListbox.pack(side=tk.LEFT, fill=tk.Y, expand=tk.YES)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        # 设置滚动条与label组件关联
        scroll['command'] = imageListbox.yview
        imageListbox.configure(yscrollcommand=scroll.set)

        # 右边的Frame,再分上下两个Frame
        imageCanvas = tk.Canvas(rightFrame, bg="white", height=canY, width=canX)#
        imageCanvas.pack(side=tk.TOP, expand=True)
        global tkImg
        tkImg = ImgTkResize('', (canX, canY))
        imageCanvas.create_text(canX/2, canY/2, text="Image Preview")
        imageCanvas.create_image(canX/2, canY/2, image=tkImg)
        imageListbox.bind("<Button-1>", lambda event, lb=imageListbox, cn=imageCanvas: self.showImageFromList(lb, cn))

        bottomFrame = tk.Frame(rightFrame)
        bottomFrame.pack(side=tk.BOTTOM, fill="both", expand=tk.NO)

        deleteButton = tk.Button(rightFrame, text='Delete')
        deleteButton.bind("<Button-1>", lambda event, lb=imageListbox, lv=listVar: self.imageDelete(lb,lv))
        deleteButton.pack(side=tk.LEFT)
        
        convertButton = tk.Button(rightFrame, text='Convert', command=imageConvertToMobi)
        convertButton.pack(side=tk.LEFT)
    
    def ClearList(self, listvariable, canvas):
        global imagesList
        imagesList.pop[:]
        listvariable.set(imagesList)
        canvas.create_image(image='')

    def initSettingTab(self, tabControl):
        setTab = ttk.Frame(tabControl)
        tabControl.add(setTab, text='Settings',
                       image=self.master.icons["setting_icon"], compound=tk.LEFT)

    # # 生成所有需要的图标
    def init_icons(self):
        self.master.icons = {}
        self.master.icons["novel_icon"] = ImgTkResize('images/novel.png')
        self.master.icons["image_icon"] = ImgTkResize('images/image.png')
        self.master.icons["setting_icon"] = ImgTkResize('images/globe.png')
    # 生成工具条

    def ListImages(self, listVar):
        global path, imagesList
        path = filedialog.askdirectory()
        if(path == ''):
            return None
        _path = tk.StringVar(value=path)
        listFiles = os.listdir(path)
        if listFiles == "":
            return None
        imagesList = []
        imgFormat = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico']
        for name in listFiles:
            extend = os.path.splitext(name)[1].lower()
            if extend in imgFormat:
                imagesList.append(name)
        listVar.set(imagesList)

    def imageDelete(self, listbox, listvariable):
        select = listbox.curselection()
        if(select == ()):
            return None
        global imagesList
        # imagesList.remove(imagesList[select])
        for element in select:
            imagesList.pop(element)
            temp = listbox.get(select)
            print(temp + " has been deleted.")
        listvariable.set(imagesList)

    def showImageFromList(self, listbox, canvas):
        index = listbox.curselection()
        if(index == ()):
            return
        global tkImg, imagesList, path
        directory = path + '/' + imagesList[index[0]]
        tkImg = ImgTkResize(directory, (canX, canY))
        canvas.create_image(canX/2, canY/2, image=tkImg)
        


def ListSync(listbox, listVar, strList):
    listVar.set(strList)


def ImgTkResize(filepath, size=(iconW, iconH)):
    if(not os.path.exists(filepath)):
        return None
    # open as a PIL image object
    pilImg = Image.open(filepath)
    # check if open success, cause by file missing, data crash, permission denied etc.
    if(not isinstance(pilImg, Image.Image)):
        return None
    baseSize = pilImg.size
    if(baseSize[0] > size[0] or baseSize[1] > size[1]):
        ratio = max(baseSize[0]/size[0], baseSize[1]/size[1])
        pilImgResized = pilImg.resize(
            (int(baseSize[0]/ratio), int(baseSize[1]/ratio)), Image.ANTIALIAS)
    else:
        return ImageTk.PhotoImage(pilImg)
    # convert PIL image object to Tkinter PhotoImage object
    return ImageTk.PhotoImage(pilImgResized)

def imageConvertToMobi():
    global imagesList, path
    if(imagesList == []):
        return None
    imageOpenList = []
    firstImage = Image.open(path + '/' + imagesList[0])
    firstImage.load()
    firstImage = firstImage.convert('RGB')
    imagesList.pop(0)
    for image in imagesList:
        imageOpen = Image.open(path + '/' + image)
        imageOpen.load()
        if imageOpen.mode == "RGBA":
            imageOpen = imageOpen.convert('RGB')
        imageOpenList.append(imageOpen)
    fileName = filedialog.asksaveasfilename(initialdir=path, filetypes=[("MOBI", ".mobi")])
    fileDir = os.path.dirname(fileName)
    tempFile = '%s.pdf' % os.path.join(tempfile.gettempdir(), str(os.getpid()))
    firstImage.save(tempFile, "PDF", resolution=100.0, save_all=True, append_images=imageOpenList)
    os.system('ebook-convert.exe' + ' "' + tempFile + '"  "' + fileName + '.mobi"')
    os.remove(tempFile)
    # canvas.delete("all")

root = tk.Tk()
root.title("Kinapp Testing")
root.geometry('650x600')
# 可否改变窗口大小
root.resizable(width=True, height=True)
App(root)
root.mainloop()
