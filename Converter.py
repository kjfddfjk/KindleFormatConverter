#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import os
import sys
import tempfile
# from functools import reduce
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
# from tkinter import dialog
from tkinter import messagebox
from PIL import Image, ImageTk

from modules import DragDrop
from modules import RecordList

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
listRecord = RecordList.RecordList()
imagesList = []
tempList = []
recordNumber = 0
messages = ''
# Window of application


class App:
    def __init__(self, master):
        self.master = master
        self.StyleSetting()

        self.InitFrames()

    def InitFrames(self):
        # Initial icons
        self.InitIcons()

        self.tabControl = ttk.Notebook(
            self.master)          # Create Tab Control
        self.messageLabel = ttk.Label(
            self.master, text="App Status Messages...")
        self.tabControl.pack(side=tk.TOP, fill="both", expand=tk.YES,
                             padx=5, pady=5, ipady=5)  # Pack to make visible
        self.messageLabel.pack(side=tk.RIGHT, fill=tk.X, expand=tk.NO)
        self.InitTextTab(self.tabControl)
        self.InitImageTab(self.tabControl)
        self.InitSettingTab(self.tabControl)

    def InitIcons(self):
        self.master.icons = {}
        self.master.icons["novel_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images/novel.png'))
        self.master.icons["image_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images/image.png'))
        self.master.icons["setting_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images/globe.png'))
        self.master.icons["redo_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images/redo.png'))
        self.master.icons["undo_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images/undo.png'))

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

        # create frame for two sides
        leftFrame = ttk.Frame(imgTab, width=80)
        leftFrame.pack(side=tk.LEFT, fill=tk.BOTH)
        rightFrame = ttk.Frame(imgTab)
        rightFrame.pack(side=tk.LEFT, fill=tk.BOTH)

        # Devide to 4 parts of frames
        leftUpFrame = ttk.Frame(leftFrame)
        leftUpFrame.pack(fill=tk.BOTH, ipadx=5, ipady=5)
        leftDownFrame = ttk.Frame(leftFrame)
        leftDownFrame.pack(expand=tk.YES ,fill=tk.BOTH, ipadx=5, ipady=5)
        rightUpFrame = ttk.Frame(rightFrame)
        rightUpFrame.pack(expand=tk.YES, fill=tk.BOTH, ipadx=5, ipady=5)
        rightDownFrame = ttk.Frame(rightFrame)
        rightDownFrame.pack(fill=tk.BOTH, ipadx=5, ipady=5)

        # 左边的Frame
        directoryButton = tk.Button(leftUpFrame, text='Import Images')
        redoButton = tk.Button(leftUpFrame, image=self.master.icons["redo_icon"])
        undoButton = tk.Button(leftUpFrame, image=self.master.icons["undo_icon"])
        listVar = tk.StringVar()
        imageListbox = DragDrop.DragDropList(leftDownFrame, font=(
            'Courier New', 16), listvariable=listVar)
        scroll = ttk.Scrollbar(leftDownFrame)
        directoryButton.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        directoryButton.bind('<1>', lambda event,
                             listVar=listVar, but=directoryButton: self.ListImages(listVar, but))
        redoButton.bind('<1>', lambda event, listVar=listVar: self.Redo(listVar))
        undoButton.bind('<1>', lambda event, listVar=listVar: self.Undo(listVar))
        redoButton.pack(side=tk.RIGHT, anchor=tk.N, padx=5, pady=5)
        undoButton.pack(side=tk.RIGHT, anchor=tk.N, padx=5, pady=5)
        imageListbox.pack(side=tk.LEFT, anchor=tk.SW, fill=tk.Y, expand=tk.YES)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        # 设置滚动条与label组件关联
        scroll['command'] = imageListbox.yview
        imageListbox.configure(yscrollcommand=scroll.set)

        # 右边的Frame,再分上下两个Frame
        imageCanvas = tk.Canvas(rightUpFrame, bg="white",
                                height=canY, width=canX)
        imageCanvas.pack(side=tk.BOTTOM, expand=tk.YES)
        global tkImg
        tkImg = ImgTkResize('', (canX, canY))
        imageCanvas.create_text(canX/2, canY/2, text="Image Preview")
        imageCanvas.create_image(canX/2, canY/2, image=tkImg)
        imageListbox.bind("<Double-Button-1>", lambda event, lb=imageListbox,
                          cn=imageCanvas: self.ShowImageFromList(lb, cn))
        imageListbox.bind('<B1-Motion>', lambda event, lb = imageListbox, lv = listVar:self.ShiftSelection(event, lb, lv))
        imageListbox.bind('<ButtonRelease-1>', lambda event, lv = listVar:self.ListCompare(lv))
        bottomFrame = tk.Frame(rightDownFrame)
        bottomFrame.pack(side=tk.BOTTOM, fill="both", expand=tk.NO)

        deleteButton = tk.Button(rightDownFrame, text='Delete')
        deleteButton.bind("<Button-1>", lambda event,
                          lb=imageListbox, lv=listVar: self.DeleteSelectImage(lb, lv))
        deleteButton.pack(side=tk.LEFT)

        convertButton = tk.Button(rightDownFrame, text='Convert')
        convertButton.bind('<ButtonPress-1>', lambda event, listvar=listVar,
                           canvas=imageCanvas: self.ImagesConvert(listvar, canvas))
        convertButton.pack(side=tk.LEFT)

    def InitSettingTab(self, tabControl):
        setTab = ttk.Frame(tabControl)
        tabControl.add(setTab, text='Settings',
                       image=self.master.icons["setting_icon"], compound=tk.LEFT)

    # Clear images tab
    def ClearList(self, listvariable, canvas):
        global listRecord, imagesList
        imagesList = []
        listvariable.set(imagesList)
        canvas.create_image(0, 0, image='')

    def ListImages(self, listVar, button):
        global imagesDir, imagesList, listRecord
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
        listRecord.insert(imagesList)
        listVar.set(imagesList)

    def ShiftSelection(self, event, listbox, listVar):
        global imagesList, listRecord, tempList
        tempList = listbox.shiftSelection(event)
        
        
    def ListCompare(self, listVar):
        global imagesList, listRecord, tempList
        if(tempList != [] and tempList != imagesList):
            imagesList = tempList
            tempList = []
            listRecord.insert(imagesList)
            listVar.set(imagesList)

    def DeleteSelectImage(self, listbox, listvariable):
        global imagesList, listRecord
        select = listbox.curselection()
        if(select == ()):
            return None
        global imagesList
        # imagesList.remove(imagesList[select])
        for element in select:
            temp = listbox.get(select)
            imagesList.pop(element)
            print(temp + " has been removed.")
        listRecord.insert(imagesList)
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
        status = ImagesConvertToMobi()
        if(status != True):
            imagesList = listRecord.getRecord()
            listVar.set(imagesList)
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

    def Redo(self, listvariable):
        global imagesList
        temp = listRecord.redo()
        if(temp != False):
            imagesList = temp
            listvariable.set(imagesList)

    def Undo(self, listvariable):
        global imagesList
        temp = listRecord.undo()
        if(temp != False):
            imagesList = temp
            listvariable.set(imagesList)

    def StyleSetting(self):
        pass
        # self.master.bind_class(tk.Button, "<Enter>", )
        # self.master.bind_class(tk.Button, "<Leave>",)

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
    return True


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

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Kinapp Testing")
    root.geometry('620x600')
    # 可否改变窗口大小
    # TODO 多次删除和undo redo 后显示有误
    root.resizable(width=True, height=True)
    App(root)
    root.mainloop()
