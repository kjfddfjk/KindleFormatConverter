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

from KindleFormatConverter import RecordList

# GLOBAL VARIBALES
# expect size
scale = 1
iconW = 24 * scale
iconH = 24 * scale
canX = 300
canY = 400
runningPath = os.path.split(os.path.realpath(__file__))[0]
textPath = ''
imagesDir = ''
tkImg = ''
imagesList = []
listRecord = RecordList.RecordList()
recordNumber = 0
messages = ''

# Window of application


class App:
    def __init__(self, master):
        self.master = master
        self.InitWidgets()

    def InitWidgets(self):
        # Initial icons
        self.InitIcons()

        self.tabControl = ttk.Notebook(
            self.master)          # Create Tab Control
        self.messageLabel = tk.Label(
            self.master, text="App Status Messages...")
        self.tabControl.pack(side=tk.TOP, fill="both", expand=tk.YES,
                             padx=5, pady=5, ipady=5)  # Pack to make visible
        self.messageLabel.pack(side=tk.RIGHT, fill=tk.X, expand=tk.NO)
        self.InitTextTab(self.tabControl)
        self.InitImageTab(self.tabControl)
        self.InitSettingTab(self.tabControl)

    def InitTextTab(self, tabControl):
        textTab = ttk.Frame(tabControl)
        textTab.pack(fill=tk.BOTH, ipadx=5, ipady=5)
        tabControl.add(textTab, text='Text',
                       image=self.master.icons["novel_icon"], compound=tk.LEFT)

        chooseFileButton = tk.Button(textTab, text='Choose text')
        chooseFileButton.pack(side=tk.LEFT)

        textVar = tk.StringVar(value='Please choose file')
        textPathEntry = tk.Entry(textTab, textvar=textVar)
        chooseFileButton.bind("<1>", lambda event, entry=textPathEntry,
                              textVar=textVar: ChooseFile(entry, textVar))
        textPathEntry.pack(side=tk.LEFT, ipadx=80)

        confirmConvertButton = tk.Button(textTab, text="Confirm Convert")
        confirmConvertButton.bind(
            "<1>", lambda event, textEntry=textPathEntry: self.ConvertText(textEntry))
        confirmConvertButton.pack(side=tk.LEFT)

    def InitImageTab(self, tabControl):
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
        imageCanvas = tk.Canvas(rightFrame, bg="white",
                                height=canY, width=canX)
        imageCanvas.pack(side=tk.TOP, expand=True)
        global tkImg
        tkImg = ImgTkResize('', (canX, canY))
        imageCanvas.create_text(canX/2, canY/2, text="Image Preview")
        imageCanvas.create_image(canX/2, canY/2, image=tkImg)
        imageListbox.bind("<Button-1>", lambda event, lb=imageListbox,
                          cn=imageCanvas: self.ShowImageFromList(lb, cn))

        bottomFrame = tk.Frame(rightFrame)
        bottomFrame.pack(side=tk.BOTTOM, fill="both", expand=tk.NO)

        deleteButton = tk.Button(rightFrame, text='Delete')
        deleteButton.bind("<Button-1>", lambda event,
                          lb=imageListbox, lv=listVar: self.ImageDelete(lb, lv))
        deleteButton.pack(side=tk.LEFT)

        convertButton = tk.Button(rightFrame, text='Convert')
        convertButton.bind('<ButtonPress-1>', lambda event, listvar=listVar,
                           canvas=imageCanvas: self.ImagesConvert(listvar, canvas))
        convertButton.pack(side=tk.LEFT)

    # Clear images tab
    def ClearList(self, listvariable, canvas):
        global imagesList
        imagesList = []
        listvariable.set(imagesList)
        canvas.create_image(0, 0, image='')

    def InitSettingTab(self, tabControl):
        setTab = ttk.Frame(tabControl)
        tabControl.add(setTab, text='Settings',
                       image=self.master.icons["setting_icon"], compound=tk.LEFT)

    # # 生成所有需要的图标
    def InitIcons(self):
        self.master.icons = {}
        self.master.icons["novel_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images/novel.png'))
        self.master.icons["image_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images/image.png'))
        self.master.icons["setting_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images/globe.png'))
    # 生成工具条

    def ListImages(self, listVar):
        global imagesDir, imagesList
        imagesDir = filedialog.askdirectory()
        if(imagesDir == ''):
            return None
        _path = tk.StringVar(value=imagesDir)
        listFiles = os.listdir(imagesDir)
        if listFiles == "":
            return None
        imagesList = []
        imgFormat = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico']
        for name in listFiles:
            extend = os.path.splitext(name)[1].lower()
            if extend in imgFormat:
                imagesList.append(name)
        listVar.set(imagesList)

    def ImageDelete(self, listbox, listvariable):
        select = listbox.curselection()
        if(select == ()):
            return None
        global imagesList
        # imagesList.remove(imagesList[select])
        for element in select:
            imagesList.pop(element)
            temp = listbox.get(select)
            print(temp + " has been removed.")
        listvariable.set(imagesList)

    def ShowImageFromList(self, listbox, canvas):
        index = listbox.curselection()
        if(index == ()):
            return
        global tkImg, imagesList, imagesDir
        directory = imagesDir + '/' + imagesList[index[0]]
        tkImg = ImgTkResize(directory, (canX, canY))
        canvas.create_image(canX/2, canY/2, image=tkImg)

    def ImagesConvert(self, listVar, canvas):
        ImagesConvertToMobi()
        self.ClearList(listVar, canvas)

    def ConvertText(self, entry):
        if(entry.get() == ''):
            print("No file can be convert")
            return None
        filePath = entry.get()
        basename = os.path.basename(os.path.splitext(filePath)[0])
        if(not os.access(textPath, mode=os.R_OK)):
            # TODO maybe need to
            print("Unable to read: %s" % textPath)
            return None
        saveName = filedialog.asksaveasfilename(
            initialfile=basename, filetypes=[("MOBI", ".mobi")])
        if(saveName):
            os.system('ebook-convert.exe' + ' "' +
                      textPath + '"  "' + saveName + '.mobi"')


def ChooseFile(entry, filevariable):
    global textPath
    textPath = filedialog.askopenfilename(filetypes=[(
        "Supported format", ".pdf .epub .txt .doc .docx"), ("All Types", ".*")])
    if(textPath):
        filevariable.set(textPath)


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


def ImagesConvertToMobi():
    global imagesList, imagesDir
    if(imagesList == []):
        return None
    imageOpenList = []
    firstImage = Image.open(imagesDir + '/' + imagesList[0])
    firstImage.load()
    firstImage = firstImage.convert('RGB')
    imagesList.pop(0)
    for image in imagesList:
        try:
            imageOpen = Image.open(imagesDir + '/' + image)
            imageOpen.load()
        except IOError:
            # TODO back to previous step 
            raise
        if imageOpen.mode == "RGBA":
            imageOpen = imageOpen.convert('RGB')
        imageOpenList.append(imageOpen)
    fileName = filedialog.asksaveasfilename(
        initialdir=imagesDir, defaultextension=[("MOBI", ".mobi")])
    # fileName = filedialog.asksaveasfilename(initialdir=path, filetypes=[("MOBI", ".mobi")])
    if(fileName):
        # TODO need to restore list
        raise ValueError("Missing given name")
    fileName = fileName + '.mobi'
    fileDir = os.path.dirname(fileName)
    tempFile = '%s.pdf' % os.path.join(tempfile.gettempdir(), str(os.getpid()))
    firstImage.save(tempFile, "PDF", resolution=100.0,
                    save_all=True, append_images=imageOpenList)
    os.system('ebook-convert.exe' + ' "' + tempFile + '"  "' + fileName + '"')
    os.remove(tempFile)


def PrintStatus(string):
    fonts = ['', 'red']
    if(string.startswith("ERROR:")):
        None  # TODO red font
    elif(string.startswith("NOTE:")):
        None  # TODO orange font
    elif(string.startwith("DONE")):
        None  # TODO green font
    else:
        None  # TODO black font


root = tk.Tk()
root.title("Kinapp Testing")
root.geometry('650x600')
# 可否改变窗口大小
root.resizable(width=True, height=True)
App(root)
root.mainloop()
