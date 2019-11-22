# -*- coding: UTF-8 -*-
import os
import sys
import tempfile
import numpy
# from functools import reduce
from configparser import ConfigParser
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

from modules import DragDrop
from modules import RecordList

# GLOBAL VARIBALES
# expect size
scale = 1
winX = 620
winY = 600
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
language2Long = {'en': 'English', 'chs': '简体中文', 'jp': '日本語'}
language2Short = {v: k for k, v in language2Long.items()}
# Window of application

coverPath = ''


class App:
    def __init__(self, master):
        self.master = master
        self.InitConfigure()
        self.InitIcons()
        self.InitFrames()

    def InitFrames(self):
        self.master.title(self.language["APP"])
        # 可否改变窗口大小
        self.master.resizable(width=True, height=True)
        self.tabControl = ttk.Notebook(
            self.master)          # Create Tab Control
        self.messageLabel = ttk.Label(
            self.master, text=self.language["STATUS_MESSAGE"])
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

    def InitImageTab(self, tabControl):
        global imagesList
        imgTab = ttk.Frame(tabControl)
        tabControl.add(imgTab, text=self.language["COMIC"],
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
        leftDownFrame.pack(expand=tk.YES, fill=tk.BOTH, ipadx=5, ipady=5)
        rightUpFrame = ttk.Frame(rightFrame)
        rightUpFrame.pack(expand=tk.YES, fill=tk.BOTH, ipadx=5, ipady=5)
        rightDownFrame = ttk.Frame(rightFrame)
        rightDownFrame.pack(fill=tk.BOTH, ipadx=5, ipady=5)

        # 左边的Frame
        directoryButton = tk.Button(
            leftUpFrame, text=self.language["IMPORT_IMAGES"])
        redoButton = tk.Button(
            leftUpFrame, image=self.master.icons["redo_icon"])
        undoButton = tk.Button(
            leftUpFrame, image=self.master.icons["undo_icon"])
        listVar = tk.StringVar()
        imageListbox = DragDrop.DragDropList(leftDownFrame, font=(
            'Courier New', 16), listvariable=listVar)
        scroll = ttk.Scrollbar(leftDownFrame)
        directoryButton.pack(side=tk.LEFT, anchor=tk.N, padx=5, pady=5)
        directoryButton.bind('<1>', lambda event,
                             listVar=listVar, but=directoryButton: self.ListImages(listVar, but))
        redoButton.bind('<1>', lambda event,
                        listVar=listVar: self.Redo(listVar))
        undoButton.bind('<1>', lambda event,
                        listVar=listVar: self.Undo(listVar))
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
        imageCanvas.create_text(
            canX/2, canY/2, text=self.language["IMAGE_PREVIEW"])
        imageCanvas.create_image(canX/2, canY/2, image=tkImg)
        imageListbox.bind("<Double-Button-1>", lambda event, lb=imageListbox,
                          cn=imageCanvas: self.ShowImageFromList(lb, cn))
        imageListbox.bind('<B1-Motion>', lambda event, lb=imageListbox,
                          lv=listVar: self.ShiftSelection(event, lb, lv))
        imageListbox.bind('<ButtonRelease-1>', lambda event,
                          lv=listVar: self.ListCompare(lv))
        bottomFrame = tk.Frame(rightDownFrame)
        bottomFrame.pack(side=tk.BOTTOM, fill="both", expand=tk.NO)

        deleteButton = tk.Button(rightDownFrame, text=self.language["DELETE"])
        deleteButton.bind("<Button-1>", lambda event,
                          lb=imageListbox, lv=listVar: self.DeleteSelectImage(lb, lv))
        deleteButton.pack(side=tk.LEFT)

        convertButton = tk.Button(
            rightDownFrame, text=self.language["CONVERT"])
        convertButton.bind('<ButtonPress-1>', lambda event, listvar=listVar,
                           canvas=imageCanvas: self.ImagesConvert(listvar, canvas))
        convertButton.pack(side=tk.LEFT)

    def InitTextTab(self, tabControl):
        textTab = ttk.Frame(tabControl)
        textTab.pack(fill=tk.BOTH, ipadx=5, ipady=5)
        tabControl.add(textTab, text='Text',
                       image=self.master.icons["novel_icon"], compound=tk.LEFT)

        chooseFileButton = tk.Button(
            textTab, text=self.language["CHOOSE_TEXT"])
        chooseFileButton.pack(side=tk.LEFT)

        textVar = tk.StringVar(value=self.language["PLEASE_CHOOSE_FILE"])
        textPathEntry = tk.Entry(textTab, textvar=textVar)
        chooseFileButton.bind("<1>", lambda event, entry=textPathEntry,
                              textVar=textVar: ChooseFile(entry, textVar))
        textPathEntry.pack(side=tk.LEFT, ipadx=80)

        confirmConvertButton = tk.Button(
            textTab, text=self.language["CONFIRM_CONVERT"])
        confirmConvertButton.bind(
            "<1>", lambda event, textEntry=textPathEntry: self.ConvertText(textEntry))
        confirmConvertButton.pack(side=tk.LEFT)
        coverCanvas = tk.Canvas(textTab, bg="white", height=canY, width=canX)
        coverCanvas.create_text(
            canX/2, canY/2, text=self.language["ORIGINAL_COVER"])
        coverCanvas.bind("<1>", lambda event,
                         canvas=coverCanvas: ChooseImage(canvas))

    def InitSettingTab(self, tabControl):
        setTab = ttk.Frame(tabControl)
        tabControl.add(setTab, text=self.language["SETTINGS"],
                       image=self.master.icons["setting_icon"], compound=tk.LEFT)
        '''
        '''
        languageVar = tk.StringVar()  # 自带的文本
        languageCombobox = ttk.Combobox(
            setTab, textvariable=languageVar)  # 初始化
        languageCombobox["values"] = list(language2Long.values())
        # print(languageCombobox["values"])
        nowLanguage = self.language["LANGUAGES"]
        languagesList = list(language2Long.values())
        languageIndex = languagesList.index(nowLanguage)  # 找到当前语言在combox里的位置
        languageCombobox.current(languageIndex)  # 显示当前语言
        languageCombobox.bind("<<ComboboxSelected>>", lambda event, combobox=languageCombobox: self.ChangeConfig(
            settings={"Language": languageCombobox.get()}))
        languageCombobox.pack()

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

    def ConvertText(self, entry, cover=""):
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
            if(cover == ''):
                os.system('ebook-convert.exe' + ' "' +
                          textPath + '"  "' + saveName + '.mobi"')
            else:
                os.system('ebook-convert.exe' + ' "' +
                          textPath + '"  "' + saveName + '.mobi" --cover "' + cover + '"')

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

    def InitConfigure(self):
        if not os.path.exists('config.ini'):
            self.ChangeConfig()

        config = ConfigParser()
        config.read('config.ini')
        language = config.get('settings', 'Language')

        try:
            lan = language2Long[language]
            self.language = SelectLanguage(lan)
        except Exception as e:
            self.language = SelectLanguage('English')
            self.ChangeConfig()
            print(repr(e))

    def ChangeConfig(self, settings={'Language': 'English'}):
        tempSettings = dict()
        tempSettings['Language'] = language2Short[settings['Language']]
        config = ConfigParser()
        if not os.path.exists('config.ini'):
            config['settings'] = tempSettings
            config.write(open('config.ini', 'w'))
        config.read('config.ini')
        if(isinstance(tempSettings, dict)):
            config['settings'] = tempSettings
            config.write(open('config.ini', 'w'))
        else:
            raise TypeError(
                "Require dict type of 'settings' send to ChangeConfig")
        print("Restart app after change language")


def ChooseImage(widget):
    pass
# TODO by open select a image file explore, and put tkimage to canvas widget. create_image which use for text cover


def ChooseFile(entry, filevariable):
    global textPath
    textPath = filedialog.askopenfilename(filetypes=[(
        "Supported format", ".pdf .epub .txt .doc .docx"), ("All Types", ".*")])
    if(textPath):
        filevariable.set(textPath)


def ImgTkResize(filepath, size=(iconW, iconH), fill=False):
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
    # fileTypes=[("MOBI", ".mobi")]
    # fileName = filedialog.asksaveasfilename(initialdir=imagesDir)
    fileName = filedialog.asksaveasfilename(filetypes=[("MOBI", ".mobi")])
    if(not fileName):
        # TODO need to restore list
        raise ValueError("Missing given name")
    fileName = fileName + '.mobi'
    fileDir = os.path.dirname(fileName)
    tempFile = '%s.pdf' % os.path.join(tempfile.gettempdir(), str(os.getpid()))
    firstImage.save(tempFile, "PDF", resolution=100.0,
                    save_all=True, append_images=imageOpenList)

    # call = 'ebook-convert.exe'
    # print('{} "{}" "{}"'.format(call, tempFile, fileName))
    # os.system('"{}" "{}" "{}"'.format(call, tempFile, fileName))
    # os.system(call + ' "' + tempFile + '"  "' + fileName + '"')
    os.system('ebook-convert.exe' + ' "' + tempFile + '"  "' + fileName + '"')
    os.remove(tempFile)
    return True


def SelectLanguage(lan):
    languages = numpy.array([["LANGUAGES", "English", "简体中文", "日本語"],
                             ["APP", "KinApp", "KinApp", "KinApp"],
                             ["COMIC", "Comic", "图片", "写真"],
                             ["TEXT", "Text", "文档", "ファイル"],
                             ["SETTINGS", "Settings", "设定", "設定"],
                             ["IMPORT_IMAGES", "import images", "汇入图片", "写真輸入"],
                             ["IMAGE_PREVIEW", "image preview", "图片预览", "写真プレビュー"],
                             ["DELETE", "delete", "删除", "削除"],
                             ["CONVERT", "convert", "转换", "変換"],
                             ["CHOOSE_TEXT", "choose text", "选择文档", "ファイル選択"],
                             ["PLEASE_CHOOSE_FILE", "please choose file", "请选择文件", "ファイルを選択してください"],
                             ["CONFIRM_CONVERT", "confirm convert", "确认转换", "変換を確認"],
                             ["STATUS_MESSAGE", "App status messege", "状态输出", "ステータス出力"],
                             ["ORIGINAL_COVER", "Use Original Cover", "使用原有封面", "元のカバーを使用"],
                             ["RESTART_AFTER_CHANGE_CONFIG",
                                 "Restart after change config", "请重启以改变显示", "再起動して表示を変更してください"],
                             [1, 2, 3, 4]])
    if(not lan):
        return dict(zip(languages[:, 0], languages[:, 1]))
    see = languages[0, 1:]
    results = numpy.where(languages[0, 1:] == lan)
    if(not results):
        return dict(zip(languages[:, 0], languages[:, 1]))
    rs = results[0][0] + 1
    return dict(zip(languages[:, 0], languages[:, rs]))


def PrintStatus(string):
    fonts = ['', 'red']
    if(string.startswith("ERROR:")):
        pass  # TODO red font
    elif(string.startswith("NOTE:")):
        pass  # TODO orange font
    elif(string.startwith("DONE")):
        pass  # TODO green font
    else:
        pass  # TODO black font


if __name__ == "__main__":
    root = tk.Tk()
    # TODO 多次删除和undo redo 后显示有误
    App(root)
    root.mainloop()
