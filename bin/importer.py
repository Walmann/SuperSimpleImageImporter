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
from ui.ui import Dialog_Existing_File, MainWindowUI


from PyQt5.uic import loadUiType
import sys

from update_check import check_for_updates

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

# form_class = loadUiType("./ui/mainwindow.ui")[0]  # Load the UI
# dialog_class = loadUiType("./ui/dialogRenameFile.ui")[0]  # Load the UI


print()
#################### First Priority ####################

# TODO "About" section that contains version information for the program.

# TODO HEIC and HEIV files should be converted to JPG or similar. Done via checkbox next to resize button.

# TODO Errors if Input, Output, or selected images is empty

#################### Second Priority ####################

# TODO Error handling inside the program


# TODO Give items background colors. # item.setBackground("black")

#################### Third Priority ####################

# TODO Make sure Tab Order is correct in QtDesigner. 
#      As in the order of items to cycle thrugh when pressing TAB



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


# class LoadingDialog(QDialog):
#     def __init__(self, FolderToImport=None):
#         super(LoadingDialog, self).__init__()
#         self.setFixedSize(300, 100)
#         self.setModal(True)
#         self.label = QLabel("Laster inn bilder", self)
#         font = self.label.font()
#         font.setPointSize(20)
#         self.label.setFont(font)
#         layout = QVBoxLayout(self)
#         layout.addWidget(self.label)

#         extensions = (
#             ".jpg",
#             ".jpeg",
#             ".png",
#             ".gif",
#             ".tiff",
#             ".webp",
#             ".svg",
#             ".raw",
#             ".ico",
#         )
#         self.tempList = []
#         for dirpath, dirnames, filenames in walk(FolderToImport):
#             for filename in filenames:
#                 if filename.endswith(extensions):
#                     self.tempList.append(PathJoin(dirpath, filename))




fileList = []
folderPathImport = ""
folderPathExport = ""
imagesToImport = []

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
myWindow = MainWindowUI(None)
myWindow.show()
sys.exit(app.exec_())
# else: 