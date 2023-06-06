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

# TODO Replace this with just code
from PyQt5.uic import loadUiType
dialog_class = loadUiType("./ui/dialogRenameFile.ui")[0]  # Load the UI


class Dialog_Existing_File(QDialog, dialog_class):
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

form_class = loadUiType("./ui/mainwindow.ui")[0]  # Load the UI
class MainWindowUI(QMainWindow, form_class):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        # self.setWindowTitle("Super Simple Image Importer")
        # self.set

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

        # Setup progressbar
        pbar = self.ExportProgressBar
        pbar.show()
        pbar.setMinimum(0)
        pbar.setMaximum(len(imagesToImport))

        renameOrSkipALL = "Ask"  # "skipAll", "renameAll", "Ask"
        for index, images in enumerate(imagesToImport):
            try:
                imageFilename = images.stem
                ext = images.suffix
                newImagePath = folderPathExport + "\\" + imageFilename + ext

                if CheckFileExists(newImagePath):
                    if renameOrSkipALL == "Ask":
                        dialogBox = Dialog_Existing_File("fileExists")
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
            except PermissionError as Error:
                print(Error)
                writeLog(Error)

                continue
        pbar.setValue(len(imagesToImport))
