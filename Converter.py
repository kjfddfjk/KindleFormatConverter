# -*- coding: UTF-8 -*-
import os
import subprocess
import sys
import tempfile
import numpy
# from functools import reduce
from configparser import ConfigParser
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
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
imagesDir = ''
tkImg = ''
listRecord = RecordList.RecordList()
imagesList = []
tempList = []
messages = ''
language2Long = {'en': 'English', 'chs': '简体中文', 'jp': '日本語'}
language2Short = {v: k for k, v in language2Long.items()}
app = None
# Window of application

singleHide = False


# def DisplayWidget(event):
#     widget = event.widget
#     global singleHide
#     if singleHide:
#         widget.grid()
#     else:
#         widget.grid_remove()

#         tempCanX = widget.winfo_width()
#         tempCanY = widget.winfo_height()
#     singleHide = not singleHide

class App:
    def __init__(self, master):
        global app
        app = self
        self.master = master
        self.InitConfigure()
        self.InitIcons()
        self.InitTheme()
        self.InitFrames()

    def InitFrames(self):
        self.master.wm_iconbitmap("logo.ico")
        self.master.title(self.language["APP"])
        self.tabControl = ttk.Notebook(
            self.master)          # Create Tab Control
        self.messageLabel = tk.Label(
            self.master, text=self.language["STATUS_MESSAGE"], bg=self.cfg["Bg1"])
        self.messageLabel.config(font=(self.cfg["TitleFont"], self.cfg["FontSize"] - 2))
        self.tabControl.pack(side=tk.TOP, fill="both", expand=tk.YES,
                             padx=5, pady=5, ipady=5)  # Pack to make visible
        self.messageLabel.pack(side=tk.RIGHT, fill=tk.X, expand=tk.NO)
        self.InitTextTab()
        self.InitImageTab()
        self.InitSettingTab()
        # 可否改变窗口大小
        self.master.resizable(width=False, height=False)

    def InitIcons(self):
        self.icons = {}
        self.icons["novel_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'novel.png'), fill=True)
        self.icons["image_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'image.png'), fill=True)
        self.icons["setting_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'settings.png'), fill=True)
        self.icons["lanugage_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'language.png'))
        self.icons["redo_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'redo.png'))
        self.icons["undo_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'undo.png'))
        self.icons["rotateL_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'rotateL.png'))
        self.icons["rotateR_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'rotateR.png'))
        self.icons["error_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'error.png'))
        self.icons["warn_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'warn.png'))
        self.icons["done_icon"] = TkImgResize(
            os.path.join(runningPath, 'images', 'done.png'))
        self.icons["bg_image"] = TkImgResize(
            self.cfg["BgImagePath"], size=(int(winX*1.2), winY))

    def InitTheme(self):
        pass
        # TODO

    def InitTextTab(self):
        textTab = ttk.Frame(self.tabControl)
        textTab.pack(fill=tk.BOTH)
        self.tabControl.add(textTab, text=self.language["TEXT"],
                            image=self.icons["novel_icon"], compound=tk.LEFT)

        textBgLabel = ttk.Label(textTab, image=self.icons["bg_image"])
        textBgLabel.pack(fill=tk.BOTH, expand=tk.YES)

        chooseFileButton = ttk.Button(
            textBgLabel, text=self.language["CHOOSE_TEXT"], style="ME.TButton")

        textVar = tk.StringVar(value=self.language["PLEASE_CHOOSE_FILE"])
        textPathEntry = tk.Entry(textBgLabel, textvar=textVar, state="readonly", font=(self.cfg["BodyFont"], 12))
        chooseFileButton.bind("<1>", lambda event: self.SetTextFile(event, textVar))
        confirmConvertButton = ttk.Button(
            textBgLabel, text=self.language["CONFIRM_CONVERT"], style="ME.TButton")
        confirmConvertButton.bind(
            "<1>", lambda event, textEntry=textPathEntry: self.TextConvert(textEntry))
        coverCanvas = tk.Canvas(textBgLabel, bg=self.cfg["Bg1"], width=canX,
                                height=canY//3)
        coverCanvas.create_text(
            canX//2, canY//6, text=self.language["ORIGINAL_COVER"])
        coverCanvas.bind(
            "<1>", lambda event: self.SetCover(event))
        textPathEntry.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        chooseFileButton.grid(row=0, column=3, padx=5, pady=5)
        confirmConvertButton.grid(row=9, column=3, sticky=tk.E, padx=5, pady=5)
        coverCanvas.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    def InitImageTab(self):
        global imagesList, tkImg
        imgTab = ttk.Frame(self.tabControl)
        self.tabControl.add(imgTab, text=self.language["COMIC"],
                            image=self.icons["image_icon"], compound=tk.LEFT)
        imageBgLabel = ttk.Label(imgTab, image=self.icons["bg_image"])
        imageBgLabel.pack(fill=tk.BOTH, expand=tk.YES)
        # 左边的Frame
        directoryButton = ttk.Button(
            imageBgLabel, text=self.language["IMPORT_IMAGES"], style="ME.TButton")
        redoButton = ttk.Button(
            imageBgLabel, image=self.icons["redo_icon"], style="ME.TButton")
        undoButton = ttk.Button(
            imageBgLabel, image=self.icons["undo_icon"], style="ME.TButton")
        listVar = tk.StringVar()
        imageListbox = DragDrop.DragDropList(imageBgLabel, height=18, font=(
            'Courier New', 14), bg=self.cfg["Bg1"], listvariable=listVar)
        scroll = ttk.Scrollbar(imageBgLabel)
        directoryButton.bind('<1>', lambda event: self.ListImages(listVar, imageCanvas))
        redoButton.bind('<1>', lambda event,
                        listVar=listVar: self.Redo(listVar))
        undoButton.bind('<1>', lambda event,
                        listVar=listVar: self.Undo(listVar))
        directoryButton.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        undoButton.grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)
        redoButton.grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)
        imageListbox.grid(row=1, column=0, columnspan=4, sticky=tk.N+tk.S+tk.W+tk.E, padx=(5, 0), pady=5)
        scroll.grid(row=1, column=4, sticky=tk.N+tk.S+tk.W, padx=(0, 5), pady=5)
        # 设置滚动条与label组件关联
        scroll['command'] = imageListbox.yview
        imageListbox.configure(yscrollcommand=scroll.set)

        deleteButton = ttk.Button(imageBgLabel, text=self.language["DELETE"], style="ME.TButton")
        deleteButton.bind("<Button-1>", lambda event,
                          lb=imageListbox, lv=listVar: self.DeleteSelectImage(lb, lv))
        deleteButton.grid(row=2, column=1, columnspan=2, sticky=tk.E, padx=5, pady=5)

        # 右边的Frame
        imageCanvas = tk.Canvas(imageBgLabel, bg=self.cfg["Bg1"],
                                height=canY, width=canX)
        imageCanvas.grid(row=1, column=5, columnspan=4, padx=5, pady=5)
        tkImg = TkImgResize('', (canX, canY))
        imageCanvas.create_text(
            canX//2, canY//2, text=self.language["IMAGE_PREVIEW"])
        imageCanvas.create_image(canX//2, canY//2, image=tkImg)
        imageListbox.bind("<Double-Button-1>", lambda event, lb=imageListbox,
                          cn=imageCanvas: self.ShowImageFromList(lb, cn))
        imageListbox.bind('<B1-Motion>', lambda event, lb=imageListbox,
                          lv=listVar: self.ShiftSelection(event, lb, lv))
        imageListbox.bind('<ButtonRelease-1>', lambda event,
                          lv=listVar: self.ListCompare(lv))
        rotateLeftButton = ttk.Button(imageBgLabel, image=self.icons["rotateL_icon"], style="ME.TButton")
        rotateLeftButton.bind('<1>', lambda event: ImageRotate(
            self.temp["IMAGE_PREVIEW"] if ("IMAGE_PREVIEW" in self.temp) else None, 90, imageCanvas))
        rotateRightButton = ttk.Button(imageBgLabel, image=self.icons["rotateR_icon"], style="ME.TButton")
        rotateRightButton.bind('<1>', lambda event: ImageRotate(
            self.temp["IMAGE_PREVIEW"] if ("IMAGE_PREVIEW" in self.temp) else None, -90, imageCanvas))
        convertButton = ttk.Button(
            imageBgLabel, text=self.language["CONVERT"], style="ME.TButton")
        convertButton.bind('<1>', lambda event, listvar=listVar,
                           canvas=imageCanvas: self.ImagesConvert(listvar, canvas))
        rotateLeftButton.grid(row=2, column=5, sticky=tk.E, padx=10, pady=5)
        rotateRightButton.grid(row=2, column=6, sticky=tk.W, padx=10, pady=5)
        convertButton.grid(row=2, column=7, columnspan=2, sticky=tk.E, padx=5, pady=5)

    def InitSettingTab(self):
        setTab = ttk.Frame(self.tabControl)
        self.tabControl.add(setTab, text=self.language["SETTINGS"],
                            image=self.icons["setting_icon"], compound=tk.LEFT)
        settingBgLabel = ttk.Label(setTab, image=self.icons["bg_image"])
        settingBgLabel.pack(fill=tk.BOTH, expand=tk.YES)
        languagePromptLabel = ttk.Label(settingBgLabel, text=self.language["LANGUAGE"])
        languagePromptLabel.config(image=self.icons["lanugage_icon"], compound=tk.LEFT, style="ME.TLabel")
        self.languageVar = tk.StringVar()
        self.languageCombobox = ttk.Combobox(settingBgLabel, textvariable=self.languageVar,
                                             state="readonly", font=(self.cfg["TitleFont"], self.cfg["FontSize"]))
        self.languageCombobox["values"] = list(language2Long.values())
        nowLanguage = self.language["LANGUAGES"]
        languagesList = list(language2Long.values())
        languageIndex = languagesList.index(nowLanguage)  # 找到当前语言在combox里的位置
        self.languageCombobox.current(languageIndex)  # 显示当前语言
        bgPathPromptLabel = ttk.Label(settingBgLabel, text=self.language["BG_IMAGE"], style="ME.TLabel")
        bgTextVar = tk.StringVar(value=self.language["PLEASE_CHOOSE_FILE"])
        bgPathEntry = ttk.Entry(settingBgLabel, textvar=bgTextVar, state="readonly",
                                font=(self.cfg["BodyFont"], 12))  # TODO style not show correctly
        selectBgButton = ttk.Button(settingBgLabel, text=self.language["BROWSE"], style="ME.TButton")
        selectBgButton.bind("<1>", lambda event: self.SetBgImagePath(event, bgTextVar))
        configButton = ttk.Button(settingBgLabel, text=self.language["OK"], style="ME.TButton")
        configButton.bind("<1>", lambda event: self.WriteConfig(event))
        languagePromptLabel.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.languageCombobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        bgPathPromptLabel.grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        bgPathEntry.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        selectBgButton.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
        configButton.grid(row=9, column=3, sticky=tk.S, padx=5, pady=5)

    def ClearList(self, listvariable, canvas):
        global imagesList
        imagesList = []
        listvariable.set(imagesList)
        canvas.delete("all")

    def ListImages(self, listVar, canvas):
        global imagesDir, imagesList, listRecord
        imagesDir = filedialog.askdirectory()
        if(imagesDir == ''):
            return None
        self.ClearList(listVar, canvas)
        listFiles = os.listdir(imagesDir)
        if listFiles == "":
            return None
        imagesList = []
        self.temp["IMAGE_PREVIEW"] = None
        imgFormat = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico']
        for name in listFiles:
            extend = os.path.splitext(name)[1].lower()
            if extend in imgFormat:
                imagesList.append(name)
        listRecord.insert(imagesList)
        listVar.set(imagesList)
        self.ShowMessage("DONE: {} {}".format(len(imagesList), self.language["IMAGES_IMPORT_SUCCESS"]))

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
            self.ShowMessage(self.language["NO_IMAGE_SELECT"])
            return None
        global imagesList
        # imagesList.remove(imagesList[select])
        for element in select:
            temp = listbox.get(select)
            imagesList.pop(element)
            print("WARN: '{}' {}".format(temp, self.language["IMAGE_REMOVE"]))
            self.ShowMessage("WARN: '{}' {}".format(temp, self.language["IMAGE_REMOVE"]))
        listRecord.insert(imagesList)
        listvariable.set(imagesList)

    def ShowImage(self, filePath, canvas):
        global tkImg
        tkImg = TkImgResize(filePath, (canX, canY))
        if(tkImg is None):
            self.ShowMessage("ERROR: '{}' {}".format(filePath, self.language["UNABLE_OPEN"]))
            raise IOError("Cannot Open image {}".format(filePath))
        tempX = tkImg.width()
        tempY = tkImg.height()
        canvas.config(width=tempX, height=tempY)
        canvas.create_image(tempX//2, tempY//2, image=tkImg)

    def ShowImageFromList(self, listbox, canvas):
        global imagesList, imagesDir
        index = listbox.curselection()
        if(index == ()):
            return
        directory = os.path.join(imagesDir, imagesList[index[0]])
        self.ShowImage(directory, canvas)
        self.temp["IMAGE_PREVIEW"] = directory

    def ShowMessage(self, string):
        global messages
        if(not string):
            return
        messages = string
        information = tk.StringVar()
        self.messageLabel.configure(textvariable=information)
        status = MessageStatus(string)
        if(status[0] == 'ERROR'):
            messages = messages[6:]
            self.messageLabel.configure(fg="red", image=self.icons["error_icon"], compound=tk.LEFT)
        elif(status[0] == 'WARN'):
            messages = messages[5:]
            self.messageLabel.configure(fg="#ea9518", image=self.icons["warn_icon"], compound=tk.LEFT)
        elif(status[0] == 'DONE'):
            messages = messages[5:]
            self.messageLabel.configure(fg="green", image=self.icons["done_icon"], compound=tk.LEFT)
        else:
            self.messageLabel.configure(image="", fg="black")
        information.set(messages)

    def ImagesConvert(self, listVar, canvas):
        global imagesList
        status = ImagesConvertToMobi()
        if(status[1] == "CONVERT_SUCCESS"):
            self.ShowMessage("DONE: '{}' {}".format(status[0], self.language[status[1]]))
        elif(status[1] == "NO_FILE_CONVERT"):
            self.ShowMessage("ERROR: {}".format(self.language[status[1]]))
        elif(status[1] == "UNABLE_OPEN"):
            self.ShowMessage("ERROR: '{}' {}".format(status[0], self.language[status[1]]))
        elif(status[1] == "NO_NAME_GIVEN"):
            self.ShowMessage("WARN: '{}' {}".format(status[0], self.language[status[1]]))
        else:
            self.ShowMessage("ERROR: '{}' {}".format(status[0], self.language[status[1]]))
            raise Exception('Unexpect return!')

    def TextConvert(self, entry):
        if(entry.get() == self.language["PLEASE_CHOOSE_FILE"]):
            self.ShowMessage("ERROR: {}".format(self.language["NO_FILE_CONVERT"]))
            return None
        try:
            Image.open(self.temp["COVER"])
            status = ConvertToMobi(entry.get(), self.temp["COVER"])
        except Exception as e:
            if("COVER" in self.temp):
                self.ShowMessage('ERROR: "{}" {}'.format(self.temp["COVER"], self.language["UNABLE_OPEN"]))
                print(repr(e))
            status = ConvertToMobi(entry.get(), None)
        if(len(status) != 2):
            print("ERROR"+status)
        elif(status[0] is True):
            self.ShowMessage("DONE: {} '{}'".format(self.language["CONVERT_SUCCESS"], status[1]))
        elif(status[0] is False and status[1] in self.language):
            self.ShowMessage("ERROR: {}".format(self.language[status[1]]))
        elif(status[1] in self.language):
            self.ShowMessage("ERROR: {} '{}'".format(self.language[status[1]], status[0]))
        else:
            print("ERROR"+status)

    def Redo(self, listvariable):
        global imagesList
        temp = listRecord.redo()
        if(temp[0] is not False):
            imagesList = temp[0]
            listvariable.set(imagesList)
        self.ShowMessage(temp[1])

    def Undo(self, listvariable):
        global imagesList
        temp = listRecord.undo()
        if(temp[0] is not False):
            imagesList = temp[0]
            listvariable.set(imagesList)
        self.ShowMessage(temp[1])

    def InitConfigure(self):
        self.temp = {}
        self.cfg = {"Language": "en", "BgImagePath": os.path.join(runningPath, "images", "bgWater.jpg"),
                    "FontSize": 12}
        isWrite = False
        config = ConfigParser()
        if(os.path.exists('config.ini')):
            config.read('config.ini')
        else:
            isWrite = True

        try:
            temp = config.get('settings', 'Language')
            lan = language2Long[temp]
            self.cfg["Language"] = temp
            self.language = SelectLanguage(lan)
        except Exception as e:
            self.language = SelectLanguage("English")
            isWrite = True
            print(repr(e))

        try:
            temp = config.get('settings', 'BgImagePath')
            if(not os.path.exists(temp)):
                raise FileNotFoundError("Not found '{}'".format(temp))
            self.cfg["BgImagePath"] = temp
        except Exception as e:
            if(not os.path.exists(self.cfg["BgImagePath"])):
                print("Not found default background image ''{}'".format(self.cfg["BgImagePath"]))
            isWrite = True
            print(repr(e))

        try:
            temp = config.get('settings', 'FontSize')
            self.cfg["FontSize"] = int(temp)
            if(self.cfg["FontSize"] < 10):
                raise Exception("Font size %d is too small", self.cfg["FontSize"])
        except Exception as e:
            self.cfg["FontSize"] = 10
            isWrite = True
            print(repr(e))

        if(isWrite):
            self.WriteConfig(initial=True)
        self.cfg["BodyFont"] = "Sarasa UI CL Light"
        self.cfg["TitleFont"] = "Sarasa UI CL"
        self.cfg["Bg1"] = "#ebfaff"
        style = ttk.Style()
        # TODO may have to change bg or fg from backgroung page color for fit theme
        style.configure('ME.TButton', relief="flat", font=(self.cfg["BodyFont"], 12))
        # style.configure('ME.TEntry', font=("Sarasa UI CL Light", 12))
        # style.configure('MSG.TLabel', bg=self.cfg["Bg1"], font=(self.cfg["TitleFont"],
        # 10 if self.cfg["FontSize"] - 2 < 10 else self.cfg["FontSize"] - 2))
        style.configure('ME.TLabel', font=(self.cfg["BodyFont"], self.cfg["FontSize"]))
        style.configure("TNotebook.Tab", font=(self.cfg["TitleFont"], self.cfg["FontSize"]))

    def WriteConfig(self, event=None, initial=False):
        config = ConfigParser()
        if(initial is False):
            temp = self.languageCombobox.get()
            self.cfg["Language"] = language2Short[temp]
        config['settings'] = self.cfg
        config.write(open('config.ini', 'w'))
        if(initial is False):
            self.ShowMessage("DONE: "+self.language["RESTART_AFTER_CHANGE_CONFIG"])
        # print("地"+sys.executable+ "地"+os.path.abspath(__file__)+"地；")
        # Below is restart app
        gettrace = getattr(sys, 'gettrace', None)
        if gettrace is None:
            pass
        elif gettrace():
            print('Big Debugger is watching')
        else:
            x = sys.executable
            p = '"{}"'.format(os.path.abspath(__file__))
            os.execl(x, x, p)

    def SetTextFile(self, event, filevariable):
        ChooseFile(filevariable, [("Supported format", ".pdf .epub .txt .doc .docx")])

    def SetCover(self, event):
        imagePath = ChooseFile(None, [("Image Format", '.png .jpg .jpeg .gif .bmp .ico')])
        if(imagePath != ''):
            try:

                canvas = event.widget
                canvas.delete("all")
                self.ShowImage(imagePath, canvas)
                self.temp["COVER"] = imagePath
            except Exception as e:
                self.temp["COVER"] = None
                raise e

    def SetBgImagePath(self, event, filevariable):
        temp = ChooseFile(filevariable, [("Image Format", '.png .jpg .jpeg .gif .bmp .ico')])
        if(temp != ''):
            self.cfg["BgImagePath"] = temp


def ChooseFile(filevariable, types=None):
    if(types):
        temp = filedialog.askopenfilename(filetypes=types)
        if(filevariable and temp):
            filevariable.set(temp)
    return temp


def ImageRotate(filePath, degree, canvas):
    if(not filePath):
        raise IOError("No image been passed")
    try:
        image = Image.open(filePath)
        rotated = image.rotate(degree, expand=True)
        rotated.save(filePath)
        app.ShowImage(filePath, canvas)
    except Exception as e:
        print(repr(e))
        raise IOError("Unable to open {}".format(filePath))


def TkImgResize(filepath, size=(iconW, iconH), fill=False):
    if(not os.path.exists(filepath)):
        return None
    # check if open success, cause by file missing, data crash, permission denied etc.
    try:
        pilImg = Image.open(filepath)
    except Exception as e:
        print(repr(e))
        return None
    baseSize = pilImg.size
    if(baseSize[0] > size[0] or baseSize[1] > size[1]):
        if(fill is False):
            ratio = max(baseSize[0]//size[0], baseSize[1]//size[1])
        elif(baseSize[0] > size[0] and baseSize[1] > size[1]):
            ratio = min(baseSize[0]//size[0], baseSize[1]//size[1])
        else:
            return ImageTk.PhotoImage(pilImg)
        pilImgResized = pilImg.resize(
            (baseSize[0]//ratio, baseSize[1]//ratio), Image.ANTIALIAS)
    else:
        return ImageTk.PhotoImage(pilImg)
    # convert PIL image object to Tkinter PhotoImage object
    return ImageTk.PhotoImage(pilImgResized)


def ConvertToMobi(filePath, cover):
    if(filePath == ''):
        return [False, "NO_FILE_CONVERT"]
    baseName = os.path.basename(os.path.splitext(filePath)[0])
    if(not os.access(filePath, mode=os.R_OK)):
        return [False, "UNABLE_OPEN"]
    saveName = filedialog.asksaveasfilename(
        initialfile=baseName, filetypes=[("MOBI", ".mobi")])
    if(saveName):
        if(not saveName.endswith(".mobi")):
            saveName = saveName + ".mobi"
        saveName = '"{}"'.format(saveName)
        filePath = '"{}"'.format(filePath)
        call = '"{}"'.format(os.path.join(runningPath, "Calibre", "ebook-convert.exe"))
        if(cover is None):
            subProcess = subprocess.Popen(call + ' ' +
                                          filePath + ' ' + saveName)
        else:
            try:
                cover = '"{}"'.format(cover)
                Image.open(cover)
                subProcess = subprocess.Popen(call + ' ' +
                                              filePath + ' ' + saveName + ' --cover ' + cover)
            except Exception as e:
                print(repr(e))
                subProcess = subprocess.Popen(call + ' ' +
                                              filePath + ' ' + saveName)
        subProcess.wait()
        if (subProcess.returncode == 0):
            return [True, saveName]
        if (subProcess.returncode != 0):
            return [saveName, "UNABLE_CONVERT"]
    else:
        return [False, "NO_NAME_GIVEN"]


def ImagesConvertToMobi():
    global imagesList, imagesDir
    if(imagesList == []):
        return [None, "NO_FILE_CONVERT"]
    imageOpenList = []
    try:
        firstImage = Image.open(os.path.join(imagesDir, imagesList[0]))
        firstImage.load()
    except Exception as e:
        print(repr(e))
        return [imagesList[0], "UNABLE_OPEN"]

    firstImage = firstImage.convert('RGB')
    for image in imagesList[1:]:
        try:
            imageOpen = Image.open(os.path.join(imagesDir, image))
            imageOpen.load()
        except Exception as e:
            print(repr(e))
            return [image, "UNABLE_OPEN"]
        if imageOpen.mode == "RGBA":
            imageOpen = imageOpen.convert('RGB')
        imageOpenList.append(imageOpen)
    fileName = filedialog.asksaveasfilename(filetypes=[("MOBI", ".mobi")])
    if(fileName == ''):
        return [None, "NO_NAME_GIVEN"]
    if(not fileName.endswith(".mobi")):
        fileName = fileName + '.mobi'
    tempFile = '%s.pdf' % os.path.join(tempfile.gettempdir(), str(os.getpid()))
    firstImage.save(tempFile, "PDF", resolution=100.0,
                    save_all=True, append_images=imageOpenList)

    # call = 'ebook-convert.exe'
    # print('{} "{}" "{}"'.format(call, tempFile, fileName))
    # os.system('"{}" "{}" "{}"'.format(call, tempFile, fileName))
    # os.system(call + ' "' + tempFile + '"  "' + fileName + '"')
    os.system('ebook-convert.exe' + ' "' + tempFile + '"  "' + fileName + '"')
    os.remove(tempFile)
    return [fileName, "CONVERT_SUCCESS"]


def SelectLanguage(lan):
    languages = numpy.array([["LANGUAGES", "English", "简体中文", "日本語"],
                             ["APP", "KinApp", "KinApp", "KinApp"],
                             ["LANGUAGE", "Language:", "语言：", "言語："],
                             ["COMIC", "Comic", "图片", "写真"],
                             ["TEXT", "Text", "文档", "ファイル"],
                             ["SETTINGS", "Settings", "设定", "設定"],
                             ["IMPORT_IMAGES", "Import Images", "汇入图片", "写真輸入"],
                             ["IMAGE_PREVIEW", "Image Preview", "图片预览", "写真プレビュー"],
                             ["BROWSE", "Browse..", "浏览...", "参照..."],
                             ["DELETE", "Delete", "删除", "削除"],
                             ["CONVERT", "Convert", "转换", "変換"],
                             ["CHOOSE_TEXT", "Choose Text", "选择文档", "ファイル選択"],
                             ["PLEASE_CHOOSE_FILE", "Please Choose File",
                                 "请选择文件", "ファイルを選択してください"],
                             ["CONFIRM_CONVERT", "Confirm Convert", "确认转换", "変換を確認"],
                             ["OK", "Ok", "确定", "決定する"],
                             ["STATUS_MESSAGE", "App Status Messege",
                                 "状态输出", "ステータス出力"],
                             ["ORIGINAL_COVER", "Use Original Cover",
                                 "使用原有封面", "元のカバーを使用"],
                             ["RESTART_AFTER_CHANGE_CONFIG",
                                 "Restart after Change Config", "请重启以改变显示", "再起動して表示を変更してください"],
                             ["BG_IMAGE", "Background Image:", "背景图：", "背景画像："],
                             ["IMAGE_REMOVE", "Image Remove", "图片移除", "画像削除"],
                             ["NO_FILE_CONVERT", "No File Can be Convert", "没有文件可以转换", "ファイルを変換できません"],
                             ["UNABLE_OPEN", "Unable to Open", "文件打开失败", "ファイルを開けません"],
                             ["UNABLE_CONVERT", "Unable to Convert", "文件转换失败", "ファイル変換に失敗しました"],
                             ["NO_NAME_GIVEN", "Missing given Name", "没有给与文件名", "与えられた名前がありません"],
                             ["CONVERT_SUCCESS", "File Converted", "文件成功转换", "文の正常な変換"],
                             ["IMAGES_IMPORT_SUCCESS", "Images successfully imported", "张图片成功汇入", "枚の画像が正常にインポート"],
                             ["NO_IMAGE", "no image", "没有图片", "写真なし"],
                             ["PLEASE_WAIT", "Please wait", "请等待", "お待ちください"],
                             ["NO_IMAGE_SELECT", "No image selected", "没有选择图片", "画像が選択されていません"],
                             [1, 2, 3, 4]])
    if(not lan):
        return dict(zip(languages[:, 0], languages[:, 1]))
    results = numpy.where(languages[0, 1:] == lan)
    if(not results):
        return dict(zip(languages[:, 0], languages[:, 1]))
    rs = results[0][0] + 1
    return dict(zip(languages[:, 0], languages[:, rs]))


def MessageStatus(string):
    fontSize = 12
    status = {'ERROR': ('ERROR', 'red', fontSize), 'WARN': ('WARN', 'yellow', fontSize),
              'DONE': ('DONE', 'green', fontSize), 'INFO': ('INFO', "black", fontSize)}
    if(string.startswith("ERROR: ")):
        return status["ERROR"]
    elif(string.startswith("WARN: ")):
        return status["WARN"]
    elif(string.startswith("DONE: ")):
        return status["DONE"]
    else:
        return status["INFO"]


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    # root.attributes("-alpha", 0.5)
    root.mainloop()
