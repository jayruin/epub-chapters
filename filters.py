from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import os.path

class EmptyFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super(EmptyFilterProxyModel, self).__init__(*args, **kwargs)

    def filterAcceptsRow(self, source_row, source_parent):
        return False

class WorkFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super(WorkFilterProxyModel, self).__init__(*args, **kwargs)

    def filterAcceptsRow(self, source_row, source_parent):
        idx = self.sourceModel().index(source_row, 0, source_parent)
        name = idx.data()

        if source_parent.parent() == self.sourceModel().index(self.sourceModel().rootPath()) or not self.sourceModel().isDir(self.sourceModel().index(source_row, 0, source_parent)):
            return False
        if idx.isValid():
            return True
        return False

class FileFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, extensions, dirs=True, *args, **kwargs):
        super(FileFilterProxyModel, self).__init__(*args, **kwargs)

        self.extensions = extensions
        self.dirs = dirs

    def filterAcceptsRow(self, source_row, source_parent):
        idx = self.sourceModel().index(source_row, 0, source_parent)
        name = idx.data()
        if not self.sourceModel().isDir(idx) and os.path.splitext(name)[1] not in self.extensions:
            return False
        if not self.dirs and self.sourceModel().isDir(idx) and source_parent == self.sourceModel().index(self.sourceModel().rootPath()):
            return False
        if idx.isValid():
            return True
