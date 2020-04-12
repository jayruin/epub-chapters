from library import *
from utility import *
from filters import *

import os.path
from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from shiboken2 import *


class Builder(QMainWindow):
    def __init__(self, library, parent=None):
        super(Builder, self).__init__(parent)

        self.library = library
        self.grouping = None
        self.work = None

        QApplication.setStyle("Fusion")
        QApplication.setPalette(QApplication.style().standardPalette())
        self.setWindowTitle("Title")

        self.mainLayout = QGridLayout()
        self.mainWidget = QWidget()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget);

        self.createMenu()
        self.createHeader()
        self.createView()
        self.createFooter()

    def createMenu(self):
        mainMenu = self.menuBar()

        newMenu = mainMenu.addMenu('New')
        openMenu = mainMenu.addMenu('Open')

        for grouping in self.library.all_groupings:
            newAction = QAction("New " + grouping, self)
            newAction.triggered.connect(lambda f=self.newWork, arg=self.library.grouping(grouping): f(arg))
            newMenu.addAction(newAction)
            openAction = QAction("Open " + grouping, self)        
            openAction.triggered.connect(lambda f=self.openWork, arg=self.library.grouping(grouping): f(arg))
            openMenu.addAction(openAction)

        browseAction = QAction("Browse", self)
        browseAction.triggered.connect(self.browse)
        mainMenu.addAction(browseAction)

    def createHeader(self):
        layout = QHBoxLayout()

        self.label = QLabel(self)

        buildButton = QPushButton("Build EPUB")
        buildButton.clicked.connect(self.buildEPUB)

        openButton = QPushButton("Open EPUB")
        openButton.clicked.connect(self.openEPUB)

        layout.addWidget(self.label, 5)
        layout.addWidget(buildButton, 1)
        layout.addWidget(openButton, 1)

        self.mainLayout.addLayout(layout, 0, 0)

    def createView(self):
        layout = QVBoxLayout()

        self.model = QFileSystemModel(self)
        self.model.setReadOnly(True)
        self.proxyModel = EmptyFilterProxyModel(parent=self)
        self.proxyModel.setDynamicSortFilter(True)
        self.proxyModel.setSourceModel(self.model)

        self.view = QTreeView()
        self.view.setModel(self.proxyModel)
        self.view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.view.header().setStretchLastSection(False)

        layout.addWidget(self.view)

        self.mainLayout.addLayout(layout, 1, 0)

    def createFooter(self):
        layout = QHBoxLayout()

        importButton = QPushButton("Import Chapter")
        importButton.clicked.connect(self.importChapters)

        layout.addWidget(importButton)

        self.mainLayout.addLayout(layout, 2, 0)

    def newWork(self, grouping):
        text, ok = QInputDialog().getText(self, "New Work", "Title:", QLineEdit.Normal)
        if ok and text:
            self.library.create_work(grouping, text)

    def openWork(self, grouping):
        WorkSelector(self, grouping).show()

    def browse(self):
        if not self.label.text():
            url = QUrl.fromLocalFile(os.path.abspath(self.library.root_directory))
        else:
            url = QUrl.fromLocalFile(os.path.abspath(os.path.join(self.library.root_directory, self.label.text()))).url()
        QDesktopServices.openUrl(url)

    def buildEPUB(self):
        if not self.grouping:
            messageBox = QMessageBox(QMessageBox.Critical, "Error", "No work has been selected!")
            messageBox.exec()
        else:
            self.library.build_epub(self.grouping, self.work)

    def openEPUB(self):
        try:
            self.library.open_epub(self.grouping, self.work)
        except FileNotFoundError:
            messageBox = QMessageBox(QMessageBox.Critical, "Error", "No EPUB found!")
            messageBox.exec()

    def importChapters(self):
        if not self.grouping:
            messageBox = QMessageBox(QMessageBox.Critical, "Error", "No work has been selected!")
            messageBox.exec()
        elif self.library.is_comic(self.grouping):
            destination = os.path.abspath(os.path.join(self.library.root_directory, self.label.text()))
            dialog = QFileDialog(self, "Import Comic", directory=destination)
            dialog.setFileMode(QFileDialog.DirectoryOnly)
            dialog.setOption(QFileDialog.DontUseNativeDialog)
            dialog.setOption(QFileDialog.ShowDirsOnly, False)
            dialog.setProxyModel(FileFilterProxyModel([".cbz"], parent=dialog))
            for fileView in dialog.findChildren(QAbstractItemView):
                if isinstance(fileView.model(), QFileSystemModel) or isinstance(fileView.model(), FileFilterProxyModel):
                    fileView.setSelectionMode(QAbstractItemView.MultiSelection)
                    fileView.setSelectionMode(QAbstractItemView.ExtendedSelection)

            if dialog.exec() == QDialog.Accepted:
                sources = dialog.selectedFiles()
                import_comics(sources, destination)

        elif self.library.is_text(self.grouping):
            destination = os.path.abspath(os.path.join(self.library.root_directory, self.label.text()))
            dialog = QFileDialog(self, "Import Text", directory=destination)
            dialog.setOption(QFileDialog.DontUseNativeDialog)
            dialog.setProxyModel(FileFilterProxyModel([".txt", ".html"], parent=dialog))
            for fileView in dialog.findChildren(QAbstractItemView):
                if isinstance(fileView.model(), QFileSystemModel) or isinstance(fileView.model(), FileFilterProxyModel):
                    fileView.setSelectionMode(QAbstractItemView.MultiSelection)
                    fileView.setSelectionMode(QAbstractItemView.ExtendedSelection)

            if dialog.exec() == QDialog.Accepted:
                sources = dialog.selectedFiles()
                import_texts(sources, destination, self.library.css_file)

class WorkSelector(QDialog):
    def __init__(self, parent, grouping):
        super(WorkSelector, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setWindowTitle("Choose a work to open")
        self.grouping = grouping

        layout = QVBoxLayout()

        model = QFileSystemModel(self)
        model.setReadOnly(True)
        model.setRootPath(os.path.join(self.parentWidget().library.root_directory, grouping.value))
        proxyModel = WorkFilterProxyModel(parent=self)
        proxyModel.setDynamicSortFilter(True)
        proxyModel.setSourceModel(model)

        view = QTreeView()
        view.setModel(proxyModel)
        view.setRootIndex(proxyModel.mapFromSource(model.index(os.path.join(self.parentWidget().library.root_directory, grouping.value))))
        view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        view.header().setStretchLastSection(False)

        button = QPushButton("OK")
        button.clicked.connect(lambda: self.makeSelection(view))

        layout.addWidget(view)
        layout.addWidget(button)

        self.setLayout(layout)
        self.resize(self.parentWidget().size())

    def makeSelection(self, view):
        if len(view.selectedIndexes()) < 1:
            messageBox = QMessageBox(QMessageBox.Critical, "Error", "Nothing is selected!")
            messageBox.exec()
        elif not view.model().sourceModel().isDir(view.model().mapToSource(view.selectedIndexes()[0])):
            messageBox = QMessageBox(QMessageBox.Critical, "Error", "Invalid selection!")
            messageBox.exec()
        else:
            if self.parentWidget().library.is_comic(self.grouping):
                self.parentWidget().proxyModel = FileFilterProxyModel([".cbz"], dirs=False, parent=self.parentWidget())
            elif self.parentWidget().library.is_text(self.grouping):
                self.parentWidget().proxyModel = FileFilterProxyModel([".html"], dirs=False, parent=self.parentWidget())
            else:
                messageBox = QMessageBox(QMessageBox.Critical, "Error", "Invalid selection!")
                messageBox.exec()
            
            self.parentWidget().proxyModel.setDynamicSortFilter(True)
            self.parentWidget().proxyModel.setSourceModel(self.parentWidget().model)

            root = view.model().sourceModel().filePath(view.model().mapToSource(view.selectedIndexes()[0]))

            shiboken2.delete(self.parentWidget().view.model())
            self.parentWidget().model.setRootPath(root)
            self.parentWidget().view.setModel(self.parentWidget().proxyModel)
            self.parentWidget().view.setRootIndex(self.parentWidget().proxyModel.mapFromSource(self.parentWidget().model.index(root)))
            self.parentWidget().grouping = self.grouping
            self.parentWidget().work = view.model().sourceModel().fileName(view.model().mapToSource(view.selectedIndexes()[0]))
            self.parentWidget().label.setText(os.path.join(self.grouping.value, self.parentWidget().work))
            self.close()


