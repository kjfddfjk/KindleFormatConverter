import pyautogui


def testText_1():
    confirmBtnRg = pyautogui.locateOnScreen('test\\images\\confirmBtn.png')
    while(confirmBtnRg is None):
        confirmBtnRg = pyautogui.locateOnScreen("test\\images\\confirmBtn.png")
    x, y = pyautogui.center(confirmBtnRg)
    pyautogui.click(x, y, clicks=3, interval=0.5)


def testText_2():
    # pyautogui.moveTo(100,100); pyautogui.click()
    textBtnRg = pyautogui.locateOnScreen('test\\images\\selectTextBtn.png')
    x, y = pyautogui.center(textBtnRg)
    pyautogui.click(x, y)
    testPathRg = pyautogui.locateOnScreen('test\\images\\testPath.png')
    while(testPathRg is None):
        testPathRg = pyautogui.locateOnScreen("test\\images\\testPath.png")
    x, y = pyautogui.center(testPathRg)
    pyautogui.click(x, y)
    normalTextRg = pyautogui.locateOnScreen('test\\images\\normalText.png')
    x, y = pyautogui.center(normalTextRg)
    pyautogui.click(x, y)
    openDirBtnRg = pyautogui.locateOnScreen('test\\images\\openDirBtn.png')
    x, y = pyautogui.center(openDirBtnRg)
    pyautogui.click(x, y)

    confirmBtnRg = pyautogui.locateOnScreen('test\\images\\confirmBtn.png')
    while(confirmBtnRg is None):
        confirmBtnRg = pyautogui.locateOnScreen("test\\images\\confirmBtn.png")
    x, y = pyautogui.center(confirmBtnRg)
    pyautogui.click(x, y)
    saveBtnRg = pyautogui.locateOnScreen('test\\images\\saveBtn.png')
    while(saveBtnRg is None):
        saveBtnRg = pyautogui.locateOnScreen("test\\images\\saveBtn.png")
    x, y = pyautogui.center(saveBtnRg)
    pyautogui.click(x, y, clicks=2, interval=0.4)


def imageTab():
    comicTabRg = pyautogui.locateOnScreen("test\\images\\comicTab.png")
    x, y = pyautogui.center(comicTabRg)
    pyautogui.click(x, y)


def testImage_1():
    convertBtnRg = pyautogui.locateOnScreen('test\\images\\convertBtn.png')
    while(convertBtnRg is None):
        convertBtnRg = pyautogui.locateOnScreen("test\\images\\convertBtn.png")
    x, y = pyautogui.center(convertBtnRg)
    pyautogui.click(x, y, clicks=2, interval=0.5)


def testImage_2():
    importImageBtnRg = pyautogui.locateOnScreen('test\\images\\importImageBtn.png')
    x, y = pyautogui.center(importImageBtnRg)
    pyautogui.click(x, y)
    testPathRg = pyautogui.locateOnScreen('test\\images\\testPath.png')
    while(testPathRg is None):
        testPathRg = pyautogui.locateOnScreen("test\\images\\testPath.png")
    x, y = pyautogui.center(testPathRg)
    pyautogui.click(x, y)
    batmanFolderRg = pyautogui.locateOnScreen('test\\images\\batmanFolder.png')
    x, y = pyautogui.center(batmanFolderRg)
    pyautogui.click(x, y)
    selectDirBtnRg = pyautogui.locateOnScreen('test\\images\\selectDirBtn.png')
    x, y = pyautogui.center(selectDirBtnRg)
    pyautogui.click(x, y)
    imageInListRg = pyautogui.locateOnScreen("test\\images\\imageInList.png")
    while(imageInListRg is None):
        imageInListRg = pyautogui.locateOnScreen("test\\images\\imageInList.png")
    x, y = pyautogui.center(imageInListRg)
    pyautogui.click(x, y)

    deleteBtnRg = pyautogui.locateOnScreen("test\\images\\deleteBtn.png")
    x, y = pyautogui.center(deleteBtnRg)
    pyautogui.click(x, y)

    convertBtnRg = pyautogui.locateOnScreen('test\\images\\convertBtn.png')
    x, y = pyautogui.center(convertBtnRg)
    pyautogui.click(x, y)
    testPathRg = pyautogui.locateOnScreen('test\\images\\testPath.png')
    while(testPathRg is None):
        testPathRg = pyautogui.locateOnScreen("test\\images\\testPath.png")
    x, y = pyautogui.center(testPathRg)
    saveBtnRg = pyautogui.locateOnScreen("test\\images\\saveBtn.png")
    pyautogui.click(x, y)
    pyautogui.typewrite('Batman.mobi', 0.1)
    x, y = pyautogui.center(saveBtnRg)
    pyautogui.click(x, y, clicks=2, interval=0.4)


if __name__ == "__main__":
    pyautogui.PAUSE = 0.3
    testText_1()
    testText_2()
    imageTab()
    testImage_1()
    testImage_2()
