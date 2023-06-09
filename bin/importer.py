from os import walk
from os.path import exists as CheckFileExists
from os.path import join as PathJoin
from os.path import splitext as PathSplitText
from pathlib import Path as PathlibPath
from PIL import Image
from PyQt5.QtCore import Qt, QUrl, QStandardPaths, QSize
from PyQt5.QtGui import QImageReader, QPixmap, QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QListWidgetItem,
    QDialog,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QApplication,
)
from PyQt5.uic import loadUiType
import sys

from update_check import check_for_updates
from handle_settings import SettingsHandlerClass 

# import CheckUpdate


## This bit is for checking wich modules are actually used på the program.
# import builtins
# real_import = builtins.__import__
# def my_import(name, globals=None, locals=None, fromlist=(), level=0):
#     with open("Modules.txt", "a+") as file:
#         file.write(f'{name}\n')
#     # print(f'Importing: {name}')
#     return real_import(name, globals, locals, fromlist, level)
# builtins.__import__ = my_import

form_class = loadUiType("./ui/mainwindow.ui")[0]  # Load the UI
dialog_class = loadUiType("./ui/dialogRenameFile.ui")[0]  # Load the UI





class MyWindowClass(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        # self.setWindowTitle("Super Simple Image Importer")
        # self.set
        
        if settingsHandler.HasDefaultInputfolder() or settingsHandler.HasDefaultOutputfolder():
            print("Test!")
            global folderPathImport
            folderPathImport = settingsHandler.LoadSetting("DefaultInputfolder")
            self.OutputFolderField.setText(str(folderPathImport))
            
            
            global folderPathExport
            folderPathExport = settingsHandler.LoadSetting("DefaultOutputFolder")
            self.OutputFolderField.setText(str(folderPathExport))



        self.ExportProgressBar.hide()
        self.fileList = []
        self.searchingForFile = False

    def selectImportFolder(self):
        global folderPathImport
        folderPathImport = QFileDialog.getExistingDirectoryUrl(
            parent=self,
            caption="Velg mape for importering",
            directory=QUrl("clsid:0AC0837C-BBF8-452A-850D-79D08E667CA7"),
            # directory=QUrl("clsid:33E28130-4E1E-4676-835A-98395C3BC3BB"),
            # options=QFileDialog.Option.ShowDirsOnly
        )

        if folderPathImport.toString() != "":
            folderPathImport = folderPathImport.toString().replace("file:///", "")
            createImagePreviewGrid(self, folderPathImport)
            self.ImportFolderField.setText(folderPathImport)

            # if self.SetDefaultExportPath.isChecked():
            #     settingsHandler.SaveSetting("DefaultInputfolder", str(folderPathImport))
            #     print("HellO!!")

    def selectOutputFolder(self):
        global folderPathExport

        dialog = QFileDialog(
            self,
            "Velg mappe for importering",
            QStandardPaths.writableLocation(QStandardPaths.PicturesLocation),
        )
        dialog.setFileMode(QFileDialog.Directory)
        # dialog.setOption(QFileDialog.DontUseNativeDialog, False)
        # dialog.setOption(QFileDialog.ShowDirsOnly, False)
        if dialog.exec_():
            folderPathExport = dialog.selectedFiles()[0]
            try:
                self.OutputFolderField.setText(str(folderPathExport))




            except UnboundLocalError:
                pass

    def Button_setDefaultExportPath(self):
        settingsHandler.SaveSetting("DefaultOutputFolder", str(folderPathExport))
        print("HellO!!")

    def resetSettings(self):
        settingsHandler.resetSettings(self)

    def updateImportList(self):
        # TODO Add filepath to Hover Tooltip
        global imagesToImport
        imagesToImport = []
        for item in self.ImagePreviewListWidget.selectedItems():
            imagesToImport.append(item.data(Qt.UserRole + 1))

    def startImportJob(self):
        import shutil

        global folderPathExport
        global imagesToImport

        if len(imagesToImport) == 0:
            return False

        # if self.SetDefaultExportPath.isChecked():
        #     settingsHandler.SaveSetting("DefaultOutputFolder", str(folderPathExport))
        #     print("HellO!!")


        # Setup progressbar
        pbar = self.ExportProgressBar
        pbar.show()
        pbar.setMinimum(0)
        pbar.setMaximum(len(imagesToImport))

        renameOrSkipALL = "Ask"  # "skipAll", "renameAll", "Ask"
        for list_index, images in enumerate(imagesToImport):
            try:
                imageFilename = images.stem
                ext = images.suffix
                newImagePath = folderPathExport + "\\" + imageFilename + ext

                if CheckFileExists(newImagePath):
                    if renameOrSkipALL == "Ask":
                        dialogBox = Dialog("fileExists")
                        renameOrSkipALL = dialogBox.exec_()

                    if renameOrSkipALL == "skipAll":
                        continue
                    elif renameOrSkipALL == "skip":
                        renameOrSkipALL = "Ask"
                        continue

                    elif renameOrSkipALL == "rename" or renameOrSkipALL == "rename_all":
                        if renameOrSkipALL == "rename":
                            renameOrSkipALL = "Ask"
                        index = 1
                        while True:
                            newImagePath = (
                                folderPathExport
                                + "\\"
                                + f"{imageFilename} ({index}){ext}"
                            )
                            if CheckFileExists(newImagePath):
                                index += 1
                            else:
                                break

                shutil.copy2(images, newImagePath)

                if self.checkBoxResize.isChecked():
                    resizeImage(
                        image_path=newImagePath,
                        resolution=self.SelectNewSize.currentText()
                        .replace(")", "")
                        .split("(")[1],
                    )
                if self.checkBoxConvertFormat.isChecked(): #TODO NEXT Convert images if this checkbox is enabled :) 
                    newImagePath = convert_to_png(image_path=newImagePath)
                
                pbar.setValue(index + 1)
                # print(images)
                # print(f"Index: {list_index}")
                pbar.setValue(list_index + 1)
            except PermissionError as Error:
                print(Error)
                writeLog(Error)

                continue
        pbar.setValue(len(imagesToImport))

def convert_to_png(image_path):
    image = Image.open(image_path)
    new_image_path = PathSplitText(image_path)[0] + '.png'
    image.save(new_image_path)
    return new_image_path


def resizeImage(image_path, resolution):
    # Load the image
    image = Image.open(image_path)

    # Get the width and height of the image
    width, height = image.size

    # Determine the aspect ratio of the image
    aspect_ratio = width / height

    # Parse the size string into width and height integers
    size_parts = resolution.split("x")
    max_width = int(size_parts[0])
    max_height = int(size_parts[1])

    # Determine the maximum width and height based on the size parameters
    if aspect_ratio >= 1:
        # Landscape orientation
        new_width = min(width, max_width)
        new_height = int(new_width / aspect_ratio)
        if new_height > max_height:
            new_height = max_height
            new_width = int(new_height * aspect_ratio)
    else:
        # Portrait orientation
        new_height = min(height, max_height)
        new_width = int(new_height * aspect_ratio)
        if new_width > max_width:
            new_width = max_width
            new_height = int(new_width / aspect_ratio)

    # Resize the image using the calculated width and height
    resized_image = image.resize((new_width, new_height), Image.ANTIALIAS)
    resized_image.save(image_path)
    return resized_image


def writeLog(Error):
    with open("ImportLog.log", "+a") as file:
        file.write(str(Error) + "\n")


def createImagePreviewGrid(self, folderPath):
    self.ImagePreviewListWidget.clear()

    if type(folderPath) == str:
        fileListe = listAllImagePaths(self, folderPath)

    for x in fileListe:
        item = QListWidgetItem(str(x))

        itemSize = QSize(200, 200)

        imageReader = QImageReader()
        imageReader.setFileName(str(x))
        size = imageReader.size()
        size.scale(itemSize.width(), itemSize.height() - 50, Qt.KeepAspectRatio)
        imageReader.setScaledSize(size)
        image = imageReader.read()

        pix = QPixmap.fromImage(image)
        icon = QIcon(pix)
        item.setIcon(icon)
        item.setText(str(x).split("\\")[-1])
        item.setSizeHint(itemSize)
        item.setData(Qt.UserRole + 1, x)

        self.ImagePreviewListWidget.addItem(item)


def listAllImagePaths(self, FolderToImport):
    """List all images in folder, and subfolders

    Args:
        FolderToImport (str): Path for folder to search

    Returns:
        dict: dict of all images found.
    """
    extensions = (
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".tiff",
        ".webp",
        ".svg",
        ".raw",
        ".ico",
    )
    for filepath in PathlibPath(FolderToImport).glob("**/*"):
        if str(filepath).endswith(extensions):
            fileList.append(filepath)
    return fileList


class LoadingDialog(QDialog):
    def __init__(self, FolderToImport=None):
        super(LoadingDialog, self).__init__()
        self.setFixedSize(300, 100)
        self.setModal(True)
        self.label = QLabel("Laster inn bilder", self)
        font = self.label.font()
        font.setPointSize(20)
        self.label.setFont(font)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        extensions = (
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".tiff",
            ".webp",
            ".svg",
            ".raw",
            ".ico",
        )
        self.tempList = []
        for dirpath, dirnames, filenames in walk(FolderToImport):
            for filename in filenames:
                if filename.endswith(extensions):
                    self.tempList.append(PathJoin(dirpath, filename))


class Dialog(QDialog, dialog_class):
    def __init__(self, dialog_type=None):
        super().__init__()

        self.button_pressed = None

        if dialog_type == "fileExists":
            self.fileExists()
        else:
            return False

    def fileExists(self):
        vbox = QVBoxLayout()

        label = QLabel(
            "Det finnes allerede en fil med dette navnet. Venligst velg en handling:"
        )
        vbox.addWidget(label)

        # Rename files
        hboxRename = QVBoxLayout()

        btn_rename = QPushButton("Gi nytt navn til denne filen")
        btn_rename.clicked.connect(self.rename)
        hboxRename.addWidget(btn_rename)

        btn_rename_all = QPushButton("Gi nytt navn til ALLE filer")
        btn_rename_all.clicked.connect(self.rename_all)
        hboxRename.addWidget(btn_rename_all)

        vbox.addLayout(hboxRename)

        # Skip Files
        hboxSkip = QVBoxLayout()

        btn_skip_all = QPushButton("Hopp over ALLE filer")
        btn_skip_all.clicked.connect(self.skip_all)
        hboxSkip.addWidget(btn_skip_all)

        btn_skip = QPushButton("Hopp over fil")
        btn_skip.clicked.connect(self.skip)
        hboxSkip.addWidget(btn_skip)

        vbox.addLayout(hboxSkip)

        # Cancel
        btn_cancel = QPushButton("Avbryt")
        btn_cancel.clicked.connect(self.cancel)
        vbox.addWidget(btn_cancel)

        self.setLayout(vbox)

    def skip_all(self):
        self.button_pressed = "skip_all"
        self.accept()

    def skip(self):
        self.button_pressed = "skip"
        self.accept()

    def rename(self):
        self.button_pressed = "rename"
        self.accept()

    def rename_all(self):
        self.button_pressed = "rename_all"
        self.accept()

    def cancel(self):
        self.button_pressed = "cancel"
        self.reject()

    def exec_(self):
        super().exec_()
        return self.button_pressed



class AboutSection(QDialog):
    def __init__(self):
        super().__init__()

    # TODO NEXT Lag About vinduet. 


fileList = []
folderPathImport = ""
folderPathExport = ""
imagesToImport = []
settingsHandler = SettingsHandlerClass()

# if CheckUpdate.check_new_version():
#     print("New Verion Available")
#     CheckUpdate.install_update()

app = QApplication(sys.argv)
#Check for update: 
is_update_available = check_for_updates()
if is_update_available[0]:
    from fetch_and_install_update import download_and_install_latest_release
    download_and_install_latest_release(local_ver=is_update_available[1], remote_ver=is_update_available[2])


# Start main window:
myWindow = MyWindowClass(None)
myWindow.show()
sys.exit(app.exec_())
# else: 