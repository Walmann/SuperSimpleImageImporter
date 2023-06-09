# Download

Check the Releases page: 

# Todo list: 

## For This Branch
- Toolbar for Settings and About section.
- "About" section that contains version information for the program.

### Settings
- Reset Settings
- Configure defaults
- Export settings, as in automatically sort folders into years, months etc.

## First Priority
-  Reset settings

## Second Priority

- Make the program prettier
- Error handling inside the program
- Give items background colors. # item.setBackground("black")
- Make it possible to translate the program to english and other languages.

## Third Priority

- Make sure Tab Order is correct in QtDesigner. As in the order of items to cycle thrugh when pressing TAB


# Building information:
(This is mostly for me)

pyinstaller 
--noconfirm 
--onefile 
--console 
--icon "C:/WORKFOLDER/Super_Simple_Image_Importer/Assets/icon.ico" 
--add-data "C:/WORKFOLDER/Super_Simple_Image_Importer/Assets;app/Assets/" 
--add-data "C:/WORKFOLDER/Super_Simple_Image_Importer/bin/importer.py;app/" 
--add-data "C:/WORKFOLDER/Super_Simple_Image_Importer/ui/mainwindow.ui;app/"  "C:/WORKFOLDER/Super_Simple_Image_Importer/setup.py"
