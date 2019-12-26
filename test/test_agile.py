import os
import tkinter
import unittest
import sys
import pyautogui
import time

sys.path.append("..")
sys.path.extend([os.path.join(root, name) for root, dirs, _ in os.walk("../") for name in dirs])
import Converter

path = "test\\images"
interval = 0.3
activeTab = 1
runningPath = os.path.split(os.path.realpath(__file__))[0]


def initialWindow():
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = interval
    window = pyautogui.getWindowsWithTitle("KinApp")
    if window:
        window[0].moveTo(155, 54)
    window = pyautogui.getWindowsWithTitle("ScreenToGif")
    if window:
        window[0].moveTo(156, 23)


def startTk():
    temp = tkinter.Tk()
    return temp


def PathConvert(fileName):
    if(not os.access(fileName, mode=os.R_OK)):
        if(os.access(os.path.join(path, fileName), mode=os.R_OK)):
            return os.path.join(path, fileName)
        else:
            raise IOError("Cannot find {}".format(fileName))
    return fileName


def WindowMessageChanged(info=1, retry=20, showLater=True):
    window = pyautogui.getWindowsWithTitle("KinApp")[0]
    xl, yb = window.bottomleft
    xr, yb = window.bottomright
    xr = xr - xl
    # TODO get messagebar picture before convert and wait for change
    # but someother operation will show directly becall this function is called, which 'showLater'=False
    # if(showLater):
    #   pyautogui.screenshot('test\\compareOnly.png', region=(xl, yb - 40, xr, 40))
    for times in range(0, retry):
        if(info == 1):
            find = pyautogui.locateOnScreen(PathConvert('success.png'), region=(xl, yb - 40, xr, 40))
        elif(info == 2):
            find = pyautogui.locateOnScreen(PathConvert('warn.png'), region=(xl, yb - 40, xr, 40))
        elif(info == 3):
            find = pyautogui.locateOnScreen(PathConvert("error.png"), region=(xl, yb - 40, xr, 40))
        else:
            return False
        if(find is None):
            time.sleep(0.4)
        else:
            return True
    return False


def Click(picture, confidence=0.97, grayscale=False, clicks=1, interval=interval):
    try:
        file = PathConvert(picture)
    except Exception as e:
        raise repr(e)
    region = pyautogui.locateOnScreen(file, confidence=confidence, grayscale=grayscale)
    if(region):
        x, y = pyautogui.center(region)
        pyautogui.click(x, y, clicks, interval)
        return True
    return False


def ClickWait(picture, confidence=0.97, grayscale=False, clicks=1, interval=interval):
    try:
        file = PathConvert(picture)
        region = pyautogui.locateOnScreen(file, confidence=confidence, grayscale=grayscale)
        while(region is None):
            region = pyautogui.locateOnScreen(file)
        x, y = pyautogui.center(region)
        pyautogui.click(x, y, clicks, interval)
    except Exception as e:
        raise repr(e)


def Wait(picture, confidence=0.97, grayscale=False, clicks=1, interval=interval):
    try:
        file = PathConvert(picture)
    except Exception as e:
        raise e
    region = pyautogui.locateOnScreen(file, confidence=confidence, grayscale=grayscale)
    while(region is None):
        region = pyautogui.locateOnScreen(file)
    x, y = pyautogui.center(region)
    return x, y


def textTab():
    global activeTab
    if(activeTab != 1):
        click = Click("textTab.png")
        pyautogui.moveTo(200, 200)
        if(click):
            activeTab = 1
            Wait("activeText.png")
        else:
            activeTab = 1
            Wait("activeText.png")
    else:
        pyautogui.moveTo(200, 200)
        Wait("activeText.png")


def imageTab():
    global activeTab
    if(activeTab != 2):
        click = Click("comicTab.png")
        pyautogui.moveTo(200, 200)
        if(click):
            activeTab = 2
            Wait("activeComic.png")
        else:
            activeTab = 2
            Wait("activeComic.png")
    else:
        pyautogui.moveTo(200, 200)
        Wait("activeComic.png")


def settingTab():
    global activeTab
    if(activeTab != 3):
        click = Click("settingTab.png")
        pyautogui.moveTo(200, 200)
        if(click):
            activeTab = 3
            Wait("activeSetting.png")
        else:
            activeTab = 3
            Wait("activeSetting.png")
    else:
        pyautogui.moveTo(200, 200)
        Wait("activeSetting.png")


runningPath = os.path.split(os.path.realpath(__file__))[0]


class UnitImageResize(unittest.TestCase):
    def test_1(self):
        # for funtion return of ImageResize need initialize of Tk()
        startTk()
        image = Converter.TkImgResize(os.path.join(runningPath, "logo.ico"), (64, 128), True)
        height = image.height()
        width = image.width()
        self.assertTupleEqual((width, height), (128, 128))

    def test_2(self):
        startTk()
        image = Converter.TkImgResize(os.path.join(runningPath, "logo.ico"), (64, 300), True)
        height = image.height()
        width = image.width()
        self.assertTupleEqual((width, height), (256, 256))

    def test_3(self):
        startTk()
        image = Converter.TkImgResize(os.path.join(runningPath, "logo.ico"), (64, 300))
        height = image.height()
        width = image.width()
        self.assertTupleEqual((width, height), (64, 64))

    def test_4(self):
        startTk()
        image = Converter.TkImgResize(os.path.join(runningPath, "logo.ico"), (300, 300))
        height = image.height()
        width = image.width()
        self.assertTupleEqual((width, height), (256, 256))

    def test_5(self):
        startTk()
        result = Converter.TkImgResize(os.path.join(runningPath, "failImage.jpg"))
        self.assertEqual(result, None)

    def test_6(self):
        startTk()
        result = Converter.TkImgResize(os.path.join(runningPath, "none.jpg"))
        self.assertEqual(result, None)


class UnitImageRotate(unittest.TestCase):
    def test1_NoFile(self):
        canvas = tkinter.Canvas()
        try:
            Converter.ImageRotate("", 90, None)
            canvas.pack()
        except Exception as e:
            self.assertTrue(isinstance(e, IOError))
            print(repr(e))

    def test2_NotImage(self):
        canvas = tkinter.Canvas()
        try:
            Converter.ImageRotate(os.path.join(runningPath, "failImage.jpg"), 90, canvas)
            canvas.pack()
        except Exception as e:
            self.assertTrue(isinstance(e, IOError))
            print(repr(e))

    def test3_T(self):
        canvas = tkinter.Canvas()
        try:
            result = Converter.ImageRotate(os.path.join(runningPath, "Batman", "RCO013_1549447449.jpg"), 90, canvas)
            canvas.pack()
        except Exception as e:
            print(repr(e))
        canvas.pack()
        self.assertTrue(result)


'''
Gui test need to start main program (Converter.py) first before getting test
Use for test main function of our gui is works well

Since it located buttons completely depends by image in folder 'test/images/'
    and difference appearance may have in different computers
    thus maybe have to change icons if before using it
    otherwise may fail of testing
'''


class GuiTest(unittest.TestCase):
    def test1Text_F(self):
        initialWindow()
        textTab()
        ClickWait("confirmBtn.png", confidence=0.95, grayscale=True)
        self.assertTrue(WindowMessageChanged(3))

    def test2Text_T(self):
        textTab()
        Click("selectTextBtn.png", confidence=0.95, grayscale=True)
        ClickWait("testPath.png")
        Click("normalText.png", confidence=0.95, grayscale=True)
        pyautogui.keyDown('altleft')
        pyautogui.press('o')
        pyautogui.keyUp('altleft')
        ClickWait("confirmBtn.png", confidence=0.95, grayscale=True)
        ClickWait("saveBtn.png")
        i = 0
        createName = os.path.join("test", "Reference.mobi")
        while(not os.access(createName, mode=os.R_OK)):
            i = i + 1
            time.sleep(1)
            if(i == 20):
                return False
        return True
        self.assertTrue(WindowMessageChanged(1))

    def test3Image_F(self):
        imageTab()
        Click("convertBtn.png")
        self.assertTrue(WindowMessageChanged(3))

    def test4Image_T(self):
        imageTab()
        Click("importImageBtn.png")
        ClickWait('testPath.png')
        Click("batmanFolder.png")
        Click("selectDirBtn.png")
        ClickWait("imageInList.png")
        Click("deleteBtn.png")
        Click("imageInList.png", clicks=2)
        Click("rotateL.png")
        pyautogui.moveTo(300, 300)
        Click("rotateR.png")
        ClickWait("convertBtn.png")
        ClickWait("testPath.png")
        x, y = Wait("saveBtn.png")
        pyautogui.typewrite('Batman.mobi', 0.1)
        pyautogui.click(x, y)
        self.assertTrue(WindowMessageChanged(1))

    def test5Setting_chs(self):
        settingTab()
        Click("languageBar.png")
        Click("simpleChinese.png")
        Click("browseBtn.png")
        ClickWait('testPath.png')
        Click("fileName.png")
        pyautogui.typewrite('Batman\n', 0.1)
        pyautogui.typewrite("RCO014_1549447449.jpg\n", 0.15)
        ClickWait("okBtn.png")
        time.sleep(5)
        initialWindow()
        ans = Wait("defaultChs.png")
        Click("comicIcon.png")
        time.sleep(3)
        Click("setIcon.png")
        time.sleep(3)
        self.assertTrue(isinstance(ans, tuple))

    def test6Setting_jp(self):
        pyautogui.move(100, 100)
        Wait("setIcon.png")
        ClickWait("languageBar.png")
        pyautogui.move(0, 60)
        pyautogui.click()
        pyautogui.move(120, 70)
        pyautogui.click()
        time.sleep(5)
        initialWindow()
        ans = Wait("defaultJp.png")
        Click("comicIcon.png")
        time.sleep(3)
        Click("setIcon.png")
        time.sleep(3)
        self.assertTrue(isinstance(ans, tuple))

    def test7Setting_en(self):
        pyautogui.move(100, 100)
        ClickWait("languageBar.png")
        pyautogui.move(0, 30)
        pyautogui.click()
        pyautogui.move(120, 100)
        pyautogui.click()
        time.sleep(5)
        initialWindow()
        ans = Wait("defaultEng.png")
        self.assertTrue(isinstance(ans, tuple))


if __name__ == "__main__":
    unittest.main()
