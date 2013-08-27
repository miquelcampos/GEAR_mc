'''

    This file is part of GEAR_mc.
    GEAR_mc is a fork of Jeremie Passerin's GEAR project.

    GEAR is free software: you can redistribute it and/or modify
    it under the terms of the GNU Lesser General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/lgpl.html>.

    Author:     Jeremie Passerin    geerem@hotmail.com  www.jeremiepasserin.com
    Fork Author:  Miquel Campos       hello@miqueltd.com  www.miqueltd.com
    Date:       2013 / 08 / 16

'''

## @package gear.xsi.uitoolkit
# @author Jeremie Passerin
#

##########################################################
# GLOBAL
##########################################################
import datetime

from gear.xsi import xsi, c, XSIUIToolkit, XSIMath

import gear.screen as scr
import gear.xsi.primitive as pri

##########################################################
# FILE FOLDER BROWSER
##########################################################
# ========================================================
## Call a file browser UI.
# @param title String - Name of the UI.
# @param initialDirectory String - Initial path of the file browser.
# @param fileName String - Initial name of the file.
# @param filters List of String - List of extension to filter.
# @param save Boolean - True to make it a saving UI. (Will ask confirmation of the file already exists)
# @return String - The path of the file. False if command was aborded.
def fileBrowser(title, initialDirectory=xsi.ActiveProject2.OriginPath, fileName="", filters=[], save=False):

    fileFilter = ""
    for s in filters:
        fileFilter += s+" Files (*."+s+")|*."+s+"|"
    fileFilter += "All Files (*.*)|*.*||"

    fileBrowser = XSIUIToolkit.FileBrowser
    fileBrowser.DialogTitle = title
    fileBrowser.InitialDirectory = initialDirectory
    fileBrowser.FileBaseName = fileName
    fileBrowser.Filter = fileFilter

    if save:
        fileBrowser.ShowSave()
    else:
        fileBrowser.ShowOpen()

    path = fileBrowser.FilePathName

    if not path:
        return False

    return path

# ========================================================
## Call a folder browser UI.
# @param title String - Name of the UI.
# @param initialDirectory String - Initial path of the file browser.
# @return String - The path of the folder. False if command was aborded.
def folderBrowser(title, initialDirectory):

    path = XSIUIToolkit.PickFolder(initialDirectory, title)

    if not path:
        return False

    return path

##########################################################
# PICK SESSION
##########################################################
# ========================================================
## Launch a pickSession for a unique object.
# @param objectFilter String - Object filter.
# @param message String - Help message for picking session.
# @param logWarning Boolean - True to log a warning if pick session is aborded.
# @return X3DObject - The picked object. False if PickSession is aborded.
def pickSession(objectFilter=c.siGenericObjectFilter, message="Pick Object", logWarning=True):

    rtn  = xsi.PickElement(objectFilter, message, message)

    if not rtn.Value("ButtonPressed"):
        if logWarning:
            xsi.LogMessage("Pick Session Aborded", c.siWarning)
        return False

    return rtn.Value("PickedElement")

# ========================================================
## Launch a pickSession for multiple objects.
# @param objectFilter String - Object filter.
# @param message String - Help message for picking session.
# @param logWarning Boolean - True to log a warning if pick session is aborded.
# @param minimum Integer - Minimum number position picked.
# @param maximum Integer - Maximum number of position picked. (set to -1 for infinite)
# @return List of X3DObject - The picked objects. False if PickSession is aborded.
def pickSessionMulti(objectFilter=c.siGenericObjectFilter, message="Pick Object", logWarning=True, minimum=1, maximum=-1):

    pickedObjects = []

    while True:
        rtn  = xsi.PickElement(objectFilter, message, message)
        if not rtn.Value("ButtonPressed"):
            break
        pickedObjects.append(rtn.Value("PickedElement"))
        if maximum > 0 and len(pickedObjects) >= maximum:
            break

    if len(pickedObjects) < minimum:
        if logWarning:
            xsi.LogMessage("Pick Session Aborded", c.siWarning)
        return False

    return pickedObjects

# ========================================================
## Launch a pick position session for a unique position.
# @param message String - Help message for picking session.
# @param logWarning Boolean - True to log a warning if pick session is aborded.
# @return SIVector3 - The picked position. False if PickSession is aborded.
def pickPosition(message="Pick position", logWarning=True):

    rtn = xsi.PickPosition(message, message)

    if rtn("ButtonPressed") == 0:
        if logWarning:
            xsi.LogMessage("Pick Session Aborded", c.siWarning)
        return False

    position = XSIMath.CreateVector3(rtn("PosX"), rtn("PosY"), rtn("PosZ"))
    return position

# ========================================================
## Launch a pick position session for multiple positions.
# @param message String - Help message for picking session.
# @param logWarning Boolean - True to log a warning if pick session is aborded.
# @param minimum Integer - Minimum number position picked.
# @param maximum Integer - Maximum number of position picked. (set to -1 for infinite)
# @return List of SIVector3 - The picked positions. False if PickSession is aborded.
def pickPositionMulti(message="Pick position", logWarning=True, minimum=1, maximum=-1):

    pickedPositions = []

    while True:
        rtn = xsi.PickPosition(message, message)
        if not rtn.Value("ButtonPressed"):
            break
        v = XSIMath.CreateVector3(rtn("PosX"), rtn("PosY"), rtn("PosZ"))
        pickedPositions.append(v)
        if addHelpers:
            null = pri.addNullFromPos(xsi.ActiveSceneRoot, "temp_0", v)
            pri.setNullDisplay(null, 1, .5, 2, 0, 0, 0, .5, .5, .5, [0, 1 ,0])
            helpers.Add(null)
        if maximum > 0 and len(pickedPositions) >= maximum:
            break

    if len(pickedPositions) < minimum:
        if logWarning:
            xsi.LogMessage("Pick Session Aborded", c.siWarning)
        return False

    return pickedPositions

##########################################################
# MESSAGE BOX
##########################################################
# ========================================================
## Open a message box ui.
# @param message String - Text to display.
# @param flag String - Flags to control the appearance of the dialog.
# @param caption String - Text to show in the title of the Message Box.
# @return Integer - Return values from XSIUIToolkit.MsgBox  that indicates which button was pressed by the user.
def msgBox(message, flag=c.siMsgExclamation, caption=""):
    return XSIUIToolkit.MsgBox(message, flag, caption)

##########################################################
# POP WINDOW
##########################################################
# ========================================================
## Open property.
# @param prop Property - The property to open.
# @param width Integer - Width of the window.
# @param height Integer - Height of the window.
# @param posX Integer - X position of the window.
# @param posY Integer - Y position of the window.
# @return
def popWindow(prop, width=100, height=100, posX=None, posY=None):

  if not prop:
     xsi.LogMessage("Can't find property", c.siError)
     return False

  resolution = scr.getResolution()

  if not posX:
     posX = int((resolution[0] / 2.0) - (width / 2.0))
  elif posX < 0:
     posX = int(resolution[0] + posX)

  if not posY:
     posY = int((resolution[1] / 2.0) - (height / 2.0))
  elif posY<0:
     posX = int(resolution[1] + posY)


  view = xsi.Desktop.ActiveLayout.CreateView("Property Panel", "MyProperty")

  view.BeginEdit()

  view.Move(posX, posY)
  view.Resize(width, height)
  view.SetAttributeValue("targetcontent", prop.FullName)

  view.EndEdit()

##########################################################
# PROGRESS BAR
##########################################################
# ========================================================
## Create a ProgressBar (XSI Object).
# @param maximum Double - Maximum length of the progressbar.
# @param step Double - step of progression.
# @param caption String - Main caption text.
# @param statutText String - secondary caption text.
# @param cancel Boolean - Display a cancel button on the progress bar.
# @return ProgressBar.
def progressBar(maximum, step, caption, statusText, cancel):

    progressBar = XSIUIToolkit.ProgressBar

    progressBar.Maximum = maximum
    progressBar.Step = step
    progressBar.Caption = caption
    progressBar.StatusText = statusText
    progressBar.CancelEnabled = cancel
    progressBar.Visible = True

    return progressBar

# ========================================================
## Reset a ProgressBar (XSI Object).
# @param progressBar ProgressBar.
# @param maximum Double - Maximum length of the progressbar.
# @param step Double - step of progression.
# @param caption String - Main caption text.
# @param statutText String - secondary caption text.
# @return ProgressBar.
def resetProgressBar(progressBar, maximum=None, step=None, caption=None, statusText=None):

    progressBar.Value = 0

    if maximum:
        progressBar.Maximum = maximum
    if step:
        progressBar.Step = step
    if caption:
        progressBar.Caption = caption
    if statusText:
        progressBar.StatusText = statusText

    progressBar.Visible = True

    return progressBar

##########################################################
# PROGRESS LOGGER
##########################################################
## Log progress step in the script editor and/or in a progress bar
class ProgressLog(object):

    ## Init method
    # @param self
    # @param showLog Boolean - True to log messages.
    # @param showBar Boolean - True to display a progress bar.
    # @param caption String - Caption Name.
    # @param statusText String - Status text.
    # @param maximum Double - Maximum limit of the progress bar.
    # @param step Double - Step incrementation of the progress bar.
    # @param cancel Boolean - Cancel button on the progress bar.
    def __init__(self, showLog=False, showBar=False, caption="", statusText="", maximum=100, step=1, cancel=False):

        self.showLog = showLog
        self.showBar = showBar

        self.startTime = datetime.datetime.now()

        self.bar = XSIUIToolkit.ProgressBar
        self.bar.Caption = caption
        self.bar.StatusText = statusText
        self.bar.Maximum = maximum
        self.bar.Step = step
        self.bar.CancelEnabled = cancel
        self.bar.Visible = False

    ## Return the time ellapsed since the creation of the object.
    # @param self
    # @return String - The time ellapsed.
    def getTime(self):
        return str(datetime.datetime.now() - self.startTime)

    ## Log the time ellapsed since the creation of the object.
    # @param self
    def logTime(self, message=""):
        xsi.LogMessage(message + " : " + self.getTime(), c.siComment)

    ## Reset the time counter.
    # @param self
    def resetTime(self):
        self.startTime = datetime.datetime.now()

    ## Log a message and change progress bar caption and status text.
    # @param self
    # @param caption String - New caption name.
    # @param statusText String - New status text.
    # @param increment Boolean - True to increment the progress bar.
    def log(self, caption=None, statusText=None, increment=False):

        self.bar.Visible = self.showBar

        if caption:
            self.bar.Caption = caption
        if statusText:
            self.bar.StatusText = statusText

        if self.showLog:
            s = " - ".join([s for s in [caption, statusText] if s is not None])
            xsi.LogMessage(s, c.siComment)

        if increment:
            self.increment()

    # ====================================================
    # PROGRESS BAR METHOD

    ## Show the progress bar.
    # @param self
    def showBar(self):
        self.bar.Visible = True

    ## Hide the progress bar.
    # @param self
    def hideBar(self):
        self.bar.Visible = False

    ## Increment the progress bar.
    # @param self
    def increment(self):
        if self.showBar:
            self.bar.Increment()

    ## Check if the progress bar Cancel button has been pressed.
    # @param self
    # @return Boolean - True if the button has been pressed
    def canceled(self):
        return self.bar.CancelPressed

    def start(self, caption=None, statusText=None, maximum=None, step=None):
        self.resetTime()
        if caption:
            self.bar.Caption = caption
        if statusText:
            self.bar.StatusText = statusText
        if maximum:
            self.bar.Maximum = maximum
        if step:
            self.bar.Step = step

    ## Reset the progress bar.
    # @param self
    # @param caption String - New caption name.
    # @param statusText String - New status text.
    # @param maximum Double - Maximum limit of the progress bar.
    # @param step Double - Step incrementation of the progress bar.
    def reset(self, caption=None, statusText=None, maximum=None, step=None):

        self.bar.Value = 0

        if caption:
            self.bar.Caption = caption
        if statusText:
            self.bar.StatusText = statusText
        if maximum:
            self.bar.Maximum = maximum
        if step:
            self.bar.Step = step
