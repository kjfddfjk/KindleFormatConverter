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
import pprint
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
recordNumber = 0
messages = ''
language2Long = {'en': 'English', 'chs': '简体中文', 'jp': '日本語'}
language2Short = {v: k for k, v in language2Long.items()}
app=None
# Window of application

coverPath = None
bgTkTest = None
singleHide = False


def DisplayWidget(event):
    widget = event.widget
    global singleHide
    if singleHide:
        widget.grid()
    else:
        widget.grid_remove()

        tempCanX = widget.winfo_width()
        tempCanY = widget.winfo_height()
    singleHide = not singleHide



class App:
    def __init__(self, master):
        global app
        app=self
        self.master = master
        self.InitConfigure()
        self.InitIcons()
        self.InitFrames()

    def InitFrames(self):
        self.master.title(self.language["APP"])
        self.tabControl = ttk.Notebook(
            self.master)          # Create Tab Control
        self.messageLabel = tk.Label(
            self.master, text=self.language["STATUS_MESSAGE"], bg="#ebfaff", font=("Sarasa UI CL", 10 if self.configure["FontSize"] - 2 < 10 else self.configure["FontSize"] - 2))
        self.tabControl.pack(side=tk.TOP, fill="both", expand=tk.YES,
                             padx=5, pady=5, ipady=5)  # Pack to make visible
        self.messageLabel.pack(side=tk.RIGHT, fill=tk.X, expand=tk.NO)
        self.InitTextTab(self.tabControl)
        self.InitImageTab(self.tabControl)
        self.InitSettingTab(self.tabControl)
        # 可否改变窗口大小
        self.master.resizable(width=False, height=False)

    def InitIcons(self):
        self.master.icons = {}
        self.master.icons["novel_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images', 'novel.png'), fill=True)
        self.master.icons["image_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images', 'image.png'), fill=True)
        self.master.icons["setting_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images', 'settings.png'), fill=True)
        self.master.icons["redo_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images', 'redo.png'))
        self.master.icons["undo_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images', 'undo.png'))
        self.master.icons["error_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images', 'error.png'))
        self.master.icons["warn_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images', 'warn.png'))
        self.master.icons["done_icon"] = ImgTkResize(
            os.path.join(runningPath, 'images', 'done.png'))
        self.master.icons["bg_image"] = ImgTkResize(
            self.configure["BgImagePath"], size=(winX, winY), fill=True)

    def InitTextTab(self, tabControl):
        global bgTkTest
        textTab = ttk.Frame(tabControl)
        textTab.pack(fill=tk.BOTH)
        tabControl.add(textTab, text=self.language["TEXT"],
                       image=self.master.icons["novel_icon"], compound=tk.LEFT)

        textBgLabel = tk.Label(textTab)
        textBgLabel.configure(image=self.master.icons["bg_image"])
        textBgLabel.pack(fill=tk.BOTH, expand=tk.YES)

        chooseFileButton = ttk.Button(
            textBgLabel, text=self.language["CHOOSE_TEXT"], style="ME.TButton")

        textVar = tk.StringVar(value=self.language["PLEASE_CHOOSE_FILE"])
        textPathEntry = tk.Entry(textBgLabel, textvar=textVar, state="readonly", font=("Sarasa UI CL Light",12))
        chooseFileButton.bind("<1>", lambda event: self.SetTextFile(event, textVar))
        confirmConvertButton = ttk.Button(
            textBgLabel, text=self.language["CONFIRM_CONVERT"], style="ME.TButton")
        confirmConvertButton.bind(
            "<1>", lambda event, textEntry=textPathEntry: self.TextConvert(textEntry))
        coverCanvas = tk.Canvas(textBgLabel, bg="#ebfaff",
                                height=canY, width=canX)
        coverCanvas.create_text(
            canX/2, canY/2, text=self.language["ORIGINAL_COVER"])
        coverCanvas.bind(
            "<1>", lambda event: self.SetCover(event))
        textPathEntry.grid(row=0, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=5)
        chooseFileButton.grid(row=0, column=3, padx=5, pady=5)
        confirmConvertButton.grid(row=9, column=9, sticky=tk.E, padx=5, pady=5)
        coverCanvas.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

    def InitImageTab(self, tabControl):
        global imagesList
        imgTab = ttk.Frame(tabControl)
        tabControl.add(imgTab, text=self.language["COMIC"],
                       image=self.master.icons["image_icon"], compound=tk.LEFT)

        # create frame for two sides
        leftBgLabel = ttk.Label(imgTab, width=80)
        leftBgLabel.configure(image=self.master.icons["bg_image"])
        rightBgLabel = ttk.Label(imgTab)
        rightBgLabel.configure(image=self.master.icons["bg_image"])
        leftBgLabel.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        rightBgLabel.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        # 左边的Frame
        directoryButton = ttk.Button(
            leftBgLabel, text=self.language["IMPORT_IMAGES"], style="ME.TButton")
        redoButton = ttk.Button(
            leftBgLabel, image=self.master.icons["redo_icon"], style="ME.TButton")
        undoButton = ttk.Button(
            leftBgLabel, image=self.master.icons["undo_icon"], style="ME.TButton")
        listVar = tk.StringVar()
        imageListbox = DragDrop.DragDropList(leftBgLabel, height=18, font=(
            'Courier New', 14), bg="#ebfaff", listvariable=listVar)
        scroll = ttk.Scrollbar(leftBgLabel)
        directoryButton.bind('<1>', lambda event,
                             listVar=listVar: self.ListImages(listVar))
        redoButton.bind('<1>', lambda event,
                        listVar=listVar: self.Redo(listVar))
        undoButton.bind('<1>', lambda event,
                        listVar=listVar: self.Undo(listVar))
        directoryButton.grid(row=0, sticky=tk.W, padx=5, pady=5)
        undoButton.grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)
        redoButton.grid(row=0, column=3, sticky=tk.E, padx=5, pady=5)
        imageListbox.grid(row=1, column=0, columnspan=4, sticky=tk.N+tk.S, padx=(5,0), pady=5)
        scroll.grid(row=1, column=4, sticky=tk.N+tk.S, padx=(0, 5), pady=5)
        # 设置滚动条与label组件关联
        scroll['command'] = imageListbox.yview
        imageListbox.configure(yscrollcommand=scroll.set)

        deleteButton = ttk.Button(leftBgLabel, text=self.language["DELETE"], style="ME.TButton")
        deleteButton.bind("<Button-1>", lambda event,
                          lb=imageListbox, lv=listVar: self.DeleteSelectImage(lb, lv))
        deleteButton.grid(row=2, sticky=tk.E, padx=5, pady=5)

        # 右边的Frame
        imageCanvas = tk.Canvas(rightBgLabel, bg="#ebfaff",
                                height=canY, width=canX)
        imageCanvas.grid(row=0, column=0, columnspan=4, sticky=tk.E+tk.W+tk.S+tk.N, padx=5, pady=5)
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

        convertButton = ttk.Button(
            rightBgLabel, text=self.language["CONVERT"], style="ME.TButton")
        convertButton.bind('<ButtonPress-1>', lambda event, listvar=listVar,
                           canvas=imageCanvas: self.ImagesConvert(listvar, canvas))
        convertButton.grid(row=9, column=3, sticky=tk.E, padx=5, pady=5)


    def InitSettingTab(self, tabControl):
        setTab = ttk.Frame(tabControl)
        tabControl.add(setTab, text=self.language["SETTINGS"],
                       image=self.master.icons["setting_icon"], compound=tk.LEFT)
        bgLabel = tk.Label(setTab)
        bgLabel.configure(image=self.master.icons["bg_image"])
        bgLabel.pack(fill=tk.BOTH, expand=tk.YES)
        languagePromptLabel=ttk.Label(bgLabel, text=self.language["LANGUAGE"], style="ME.TLabel")
        self.languageVar = tk.StringVar()  # 自带的文本
        self.languageCombobox = ttk.Combobox(
            bgLabel, textvariable=self.languageVar, state="readonly", font=("Sarasa UI CL", self.configure["FontSize"]))  # 初始化
        self.languageCombobox["values"] = list(language2Long.values())
        nowLanguage = self.language["LANGUAGES"]
        languagesList = list(language2Long.values())
        languageIndex = languagesList.index(nowLanguage)  # 找到当前语言在combox里的位置
        self.languageCombobox.current(languageIndex)  # 显示当前语言
        bgPathPromptLabel = ttk.Label(bgLabel, text=self.language["BG_LOCATION"], style="ME.TLabel")
        bgTextVar=tk.StringVar(value=self.language["PLEASE_CHOOSE_FILE"])
        bgPathEntry = ttk.Entry(bgLabel, textvar=bgTextVar, state="readonly", font=("Sarasa UI CL Light",12)) # TODO style not show correctly
        selectBgButton = ttk.Button(bgLabel, text=self.language["BROWSE"], style="ME.TButton")
        selectBgButton.bind("<1>", lambda event : self.SetBgImagePath(event, bgTextVar))
        configButton = ttk.Button(bgLabel, text=self.language["OK"], style="ME.TButton")
        configButton.bind("<1>", lambda event: self.WriteConfig(event))
        languagePromptLabel.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        self.languageCombobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        bgPathPromptLabel.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        bgPathEntry.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        selectBgButton.grid(row=2, column=3, padx=5, pady=5, sticky=tk.W)
        configButton.grid(row=9, column=9, sticky=tk.S, padx=5, pady=5)



    def ClearList(self, listvariable, canvas):
        global imagesList
        imagesList = []
        listvariable.set(imagesList)
        canvas.delete("all")

    def ListImages(self, listVar):
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
            print("WARN: '{}' {}".format(temp, self.language["IMAGE_REMOVE"]))
            self.ShowMessage("WARN: '{}' {}".format(temp, self.language["IMAGE_REMOVE"]))
        listRecord.insert(imagesList)
        listvariable.set(imagesList)

    def ShowImage(self, filePath, canvas):
        global tkImg
        tempCanX = canvas.winfo_width()
        tempCanY = canvas.winfo_height()
        tkImg = ImgTkResize(filePath, (canX, canY))
        if(tkImg == None):
            self.ShowMessage("ERROR: '{}' {}".format(filePath, self.language["UNABLE_OPEN"]))
            raise IOError("Cannot Open image {}".format(filePath))
        canvas.create_image(canX/2, canY/2, image=tkImg)

    def ShowImageFromList(self, listbox, canvas):
        global imagesList, imagesDir
        index = listbox.curselection()
        if(index == ()):
            return
        directory = imagesDir + '/' + imagesList[index[0]]
        self.ShowImage(directory, canvas)

    def ShowMessage(self, string):
        global messages
        if(string == ""):
            return
        messages = string
        information = tk.StringVar()
        self.messageLabel.configure(textvariable=information)
        status = MessageStatus(string)
        if(status[0] == 'ERROR'):
            messages = messages[6:]
            self.messageLabel.configure(fg="red", image=self.master.icons["error_icon"], compound=tk.LEFT)
        elif(status[0] == 'WARN'):
            messages = messages[5:]
            self.messageLabel.configure(fg="#ea9518", image=self.master.icons["warn_icon"], compound=tk.LEFT)
        elif(status[0] == 'DONE'):
            messages = messages[5:]
            self.messageLabel.configure(fg="green", image=self.master.icons["done_icon"], compound=tk.LEFT)
        else:
            self.messageLabel.configure(image="", fg="black")
        information.set(messages)

    def ImagesConvert(self, listVar, canvas):
        global imagesList
        status = ImagesConvertToMobi()
        self.ClearList(listVar, canvas)
        if(status != True):
            currentRecord = listRecord.getRecord()
            if(currentRecord != False):
                imagesList = currentRecord
                listVar.set(imagesList)

    def TextConvert(self, entry):
        if(entry.get() == self.language["PLEASE_CHOOSE_FILE"]):
            self.ShowMessage("ERROR: {}".format(self.language["NO_FILE_CONVERT"]))
            return
        status = ConvertToMobi(entry.get(), coverPath)
        if(status == "NO_FILE_CONVERT"):
            self.ShowMessage("ERROR: {}".format(self.language["NO_FILE_CONVERT"]))
        elif(status == "UNABLE_OPEN"):
            self.ShowMessage(("ERROR: '{}' {}".format(entry.get(), self.language["UNABLE_OPEN"])))
        elif(status == "NO_NAME_GIVEN"):
            self.ShowMessage(self.language["NO_NAME_GIVEN"])
        else:
            self.ShowMessage("DONE: {} '{}'".format(self.language["CONVERT_SUCCESS"], status))

    def Redo(self, listvariable):
        global imagesList
        temp = listRecord.redo()
        if(temp[0] != False):
            imagesList = temp[0]
            listvariable.set(imagesList)
        self.ShowMessage(temp[1])

    def Undo(self, listvariable):
        global imagesList
        temp = listRecord.undo()
        if(temp[0] != False):
            imagesList = temp[0]
            listvariable.set(imagesList)
        self.ShowMessage(temp[1])

    def InitConfigure(self):
        self.configure = {"Language":"en", "BgImagePath":os.path.join(runningPath, "images", "bgWater.jpg"), "FontSize":12}
        isWrite = False
        config = ConfigParser()
        if(os.path.exists('config.ini')):
            config.read('config.ini')
        else:
            isWrite = True

        try:
            temp = config.get('settings', 'Language')
            lan = language2Long[temp]
            self.configure["Language"] = temp
            self.language = SelectLanguage(lan)
        except Exception as e:
            self.language = SelectLanguage("English")
            isWrite = True
            print(repr(e))

        try:
            temp = config.get('settings', 'BgImagePath')
            if(not os.path.exists(temp)):
                raise FileNotFoundError("Not found '{}'".format(temp))
            test = Image.open(temp)
            self.configure["BgImagePath"] = temp
        except Exception as e:
            if(not os.path.exists(self.configure["BgImagePath"])):
                print("Not found default background image ''{}'".format(self.configure["BgImagePath"]))
            isWrite = True
            print(repr(e))

        
        try:
            temp = config.get('settings', 'FontSize')
            self.configure["FontSize"] = int(temp)
            if(self.configure["FontSize"] < 10):
                raise Exception("font size %d is too small", self.configure["FontSize"])
        except Exception as e:
            self.configure["FontSize"] = 12
            isWrite = True
            print(repr(e))
        
        if(isWrite):
            self.WriteConfig(initial=True)

        style = ttk.Style()
        # TODO may have to change bg or fg from backgroung page color for fit theme 
        style.configure('ME.TButton', relief="flat", font=("Sarasa UI CL Light", 12))
        # style.configure('ME.TEntry', font=("Sarasa UI CL Light", 12))
        style.configure('ME.TLabel', font=("Sarasa UI CL Light", self.configure["FontSize"]))
        style.configure("TNotebook.Tab", font=('Sarasa UI CL', self.configure["FontSize"]))

    def WriteConfig(self, event=None, initial=False):
        config = ConfigParser()
        if(initial == False):
            temp = self.languageCombobox.get()
            self.configure["Language"] = language2Short[temp]
        config['settings'] = self.configure
        config.write(open('config.ini', 'w'))
        if(initial == False):
            self.ShowMessage("DONE: "+self.language["RESTART_AFTER_CHANGE_CONFIG"])
        # print("地"+sys.executable+ "地"+os.path.abspath(__file__)+"地；")
        # Below is restart app
        # os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
    
    def SetTextFile(self, event, filevariable):
        ChooseFile(filevariable, [("Supported format", ".pdf .epub .txt .doc .docx")])
        
    def SetCover(self, event):
        global coverPath
        imagePath = ChooseFile(None, [("Image Format",'.png .jpg .jpeg .gif .bmp .ico')])
        if(imagePath != ''):
            try:
                canvas = event.widget
                self.ShowImage(imagePath, canvas)
                coverPath = imagePath
            except Exception as e:
                pass
                

    def SetBgImagePath(self, event, filevariable):
        temp = ChooseFile(filevariable, [("Image Format",'.png .jpg .jpeg .gif .bmp .ico')])
        if(temp != ''):
            self.configure["BgImagePath"] = temp
    

def ChooseFile(filevariable, types=None):
    if(types):
        temp = filedialog.askopenfilename(filetypes=types)
        if(filevariable and temp):
            filevariable.set(temp)
    return temp

def ImageRotate(filepath, degree, canvas):
    try:
        image = Image.open(filepath)
        image.rotate(degree)
        image.save(filepath)
    except:
        pass
    canvas.create_image()


def ImgTkResize(filepath, size=(iconW, iconH), fill=False):
    if(not os.path.exists(filepath)):
        return None
    # check if open success, cause by file missing, data crash, permission denied etc.
    try:
        pilImg = Image.open(filepath)
    except Exception as e:
        return None
    baseSize = pilImg.size
    if(baseSize[0] > size[0] or baseSize[1] > size[1]):
        if(fill == False):
            ratio = max(baseSize[0]/size[0], baseSize[1]/size[1])
        elif(baseSize[0] > size[0] and baseSize[1] > size[1]):
            ratio = min(baseSize[0]/size[0], baseSize[1]/size[1])
        else:
            return ImageTk.PhotoImage(pilImg)
        pilImgResized = pilImg.resize(
            (int(baseSize[0]/ratio), int(baseSize[1]/ratio)), Image.ANTIALIAS)
    else:
        return ImageTk.PhotoImage(pilImg)
    # convert PIL image object to Tkinter PhotoImage object
    return ImageTk.PhotoImage(pilImgResized)


def ConvertToMobi(filePath, cover=None):
    if(filePath == ''):
        return("NO_FILE_CONVERT")
    baseName = os.path.basename(os.path.splitext(filePath)[0])
    if(not os.access(filePath, mode=os.R_OK)):
        return("UNABLE_OPEN")
    saveName = filedialog.asksaveasfilename(
        initialfile=baseName, filetypes=[("MOBI", ".mobi")])
    if(saveName):
        saveName = saveName + ".mobi"
        if(cover == None):
            os.system('Calibre\\ebook-convert.exe' + ' "' +
                    filePath + '"  "' + saveName + '"')
        else:
            os.system('Calibre\\ebook-convert.exe' + ' "' +
                    filePath + '"  "' + saveName + '" --cover "' + cover + '"')
        return saveName
    else:
        return "NO_NAME_GIVEN"
                          
def ImagesConvertToMobi():
    global imagesList, imagesDir
    if(imagesList == []):
        return False
    imageOpenList = []
    firstImage = Image.open(os.path.join(imagesDir, imagesList[0]))
    firstImage.load()
    firstImage = firstImage.convert('RGB')
    imagesList.pop(0)
    for image in imagesList:
        try:
            imageOpen = Image.open(os.path.join(imagesDir,image))
            imageOpen.load()
        except IOError:
            # TODO back to previous step
            app.ShowMessage("ERROR: " + app.language["UNABLE_OPEN"])
            return False
        if imageOpen.mode == "RGBA":
            imageOpen = imageOpen.convert('RGB')
        imageOpenList.append(imageOpen)
    fileName = filedialog.asksaveasfilename(filetypes=[("MOBI", ".mobi")])
    if(fileName == ''):
        # TODO need to restore list
        app.ShowMessage("WARN: " + app.language["NO_NAME_GIVEN"])
        return False
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
                             ["LANGUAGE", "Language:", "语言：", "言語："],
                             ["COMIC", "Comic", "图片", "写真"],
                             ["TEXT", "Text", "文档", "ファイル"],
                             ["SETTINGS", "Settings", "设定", "設定"],
                             ["IMPORT_IMAGES", "Import Images", "汇入图片", "写真輸入"],
                             ["IMAGE_PREVIEW", "Image Preview", "图片预览", "写真プレビュー"],
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
                             ["BROWSE", "Browse..", "浏览...", "参照..."],
                             ["BG_LOCATION", "Background Image:", "背景图位置：", "背景画像の場所："],
                             ["IMAGE_REMOVE", "Image Remove", "图片移除", "画像削除"],
                             ["NO_FILE_CONVERT", "No File Can be Convert", "没有文件可以转换", "ファイルを変換できません"],
                             ["UNABLE_OPEN", "Unable to Open", "文件打开失败", "ファイルを開けません"],
                             ["NO_NAME_GIVEN", "Missing given Name", "没有给与文件名", "与えられた名前がありません"],
                             ["CONVERT_SUCCESS", "File Converted", "文件成功转换", "文の正常な変換"],
                             [1, 2, 3, 4]])
    if(not lan):
        return dict(zip(languages[:, 0], languages[:, 1]))
    see = languages[0, 1:]
    results = numpy.where(languages[0, 1:] == lan)
    if(not results):
        return dict(zip(languages[:, 0], languages[:, 1]))
    rs = results[0][0] + 1
    return dict(zip(languages[:, 0], languages[:, rs]))


def MessageStatus(string):
    fontSize = 12
    status = {'ERROR': ('ERROR', 'red', fontSize), 'WARN': ('WARN', 'yellow', fontSize), 'DONE': ('DONE', 
        'green', fontSize), 'INFO': ('INFO', "black", fontSize)}
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
