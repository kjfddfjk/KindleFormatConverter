import pyautogui
import os
import time
import unittest

path = "test\\images"
interval = 0.3
activeTab = 1
runningPath = os.path.split(os.path.realpath(__file__))[0]


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
        if(find is not None):
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
        if(click):
            activeTab = 1
            Wait("activeText.png")
        else:
            activeTab = 1
            Wait("activeText.png")
    else:
        Wait("activeText.png")


def imageTab():
    global activeTab
    if(activeTab != 2):
        click = Click("comicTab.png")
        if(click):
            activeTab = 2
            Wait("activeComic.png")
        else:
            activeTab = 2
            Wait("activeComic.png")
    else:
        Wait("activeComic.png")


def settingTab():
    global activeTab
    if(activeTab != 3):
        click = Click("settingTab.png")
        if(click):
            activeTab = 3
            Wait("activeSetting.png")
        else:
            activeTab = 3
            Wait("activeSetting.png")
    else:
        Wait("activeSetting.png")


class testCases(unittest.TestCase):
    def testText_1(self):
        textTab()
        ClickWait("confirmBtn.png", confidence=0.95, grayscale=True)
        self.assertTrue(WindowMessageChanged(3))

    def testText_2(self):
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

    def testImage_1(self):
        imageTab()
        Click("convertBtn.png")
        self.assertTrue(WindowMessageChanged(3))

    def testImage_2(self):
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


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = interval
    unittest.main()
