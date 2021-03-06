import json
from enum import Enum

import os
import os.path
import errno
import subprocess

from utility import *
from metadata import *

class Library:
    """
    A library for epub files.

    Attributes:
        _config_file: Path to the json configuration file.
        _grouping: An Enum representing the different work groupings.
        _comics: List of comic groupings as str.
        _texts: List of text groupings as str.
        _root_directory: Path to library root directory.
        _output_directory: Path to library output directory.
        _css_file: Path to the CSS file to use for conversions.
        _covers: List of paths to possible cover file names to use for conversions in search order.
        _calibre_settings: Settings for using Calibre.
    """
    def __init__(self, config_file):
        """
        Initialize Library class with given configuration file.

        Args:
            config_file: Path to the json configuration file.

        Returns:
            Nothing.
        """
        self._config_file = config_file

        with open(config_file, "r") as f:
            config = json.loads(f.read())
        
        self._grouping = Enum("Grouping", {**config["FORMATS"]["Comic"], **config["FORMATS"]["Text"]})
        self._comics = list(config["FORMATS"]["Comic"].values())
        self._texts = list(config["FORMATS"]["Text"].values())

        self._root_directory = config["root"]
        self._output_directory = config["output"]
        self._css_file = config["CSS"]
        self._covers = config["covers"]

        self._calibre_settings = config["Calibre"]
    
    @property
    def grouping(self):
        """An Enum representing the different work groupings."""
        return self._grouping
    
    @property
    def all_groupings(self):
        """List of all groupings as str."""
        return [*self._comics, *self._texts]
    
    @property
    def root_directory(self):
        """Path to library root directory."""
        return self._root_directory
    
    @property
    def output_directory(self):
        """Path to library output directory."""
        return self._output_directory
    
    @property
    def css_file(self):
        """Path to the CSS file to use for conversions."""
        return self._css_file

    @property
    def covers(self):
        """List of paths to possible cover file names to use for conversions in search order."""
        return self._covers

    def is_comic(self, grouping):
        """
        Checks whether grouping is a comic.

        Args:
            grouping: Grouping enum representing the grouping to check.

        Returns:
            Bool whether grouping is a comic.
        """
        if grouping.value in self._comics:
            return True
        return False

    def is_text(self, grouping):
        """
        Checks whether grouping is a text.

        Args:
            grouping: Grouping enum representing the grouping to check.

        Returns:
            Bool whether grouping is a text.
        """
        if grouping.value in self._texts:
            return True
        return False

    def get_comic_epub_command(self, source, destination, cover, metadata):
        """
        Get the command for converting a comic to EPUB.

        Args:
            source: Path to the file to convert from.
            destination: Path to the file to convert to.
            cover: Path to the cover file to use.
            metadata: Metadata object for the work.

        Returns:
            List[str]: Command list for converting comics to EPUB.
        """
        if cover is None:
            cover_option = []
        else:
            cover_option = ["--cover", cover]
        return [*self._calibre_settings["convert"], *[source, destination], *self._calibre_settings["convert-comic-epub"], *cover_option, *metadata.get_build_command_options()]

    def get_text_epub_command(self, source, destination, cover, metadata):
        """
        Get the command for converting a text to EPUB.

        Args:
            source: Path to the file to convert from.
            destination: Path to the file to convert to.
            cover: Path to the cover file to use.
            metadata: Metadata object for the work.

        Returns:
            List[str]: Command list for converting comics to EPUB.
        """
        if cover is None:
            cover_option = []
        else:
            cover_option = ["--cover", cover]
        return [*self._calibre_settings["convert"], *[source, destination], *self._calibre_settings["convert-html-epub"], *cover_option, *metadata.get_build_command_options()]

    def get_view_epub_command(self, epub):
        """
        Get the command for viewing an EPUB.

        Args:
            epub: Path to EPUB file to view.

        Returns:
            List[str]: Command list for viewing an EPUB.
        """
        return [*self._calibre_settings["viewer"], *[epub]]

    def build_comic_epub(self, source, destination, metadata):
        """
        Build a comic EPUB.

        Args:
            source: Path to the directory with individual chapters.
            destination: Path to the directory to place the EPUB.
            metadata: Metadata object for the work.

        Returns:
            Nothing.
        """
        title = os.path.basename(os.path.normpath(source))
        chapters = [os.path.join(source, chapter) for chapter in metadata.chapters]

        txt = generate_comic_table_of_contents(chapters, destination)
        cover = find_cover(source, self._covers)
        cbc = generate_cbc(chapters, destination, txt, title)
        command = self.get_comic_epub_command(cbc, "{0}.epub".format(os.path.splitext(cbc)[0]), cover, metadata)
        subprocess.run(command)
        os.remove(txt)
        os.remove(cbc)
    
    def build_text_epub(self, source, destination, metadata):
        """
        Build a text EPUB.

        Args:
            source: Path to the directory with individual chapters.
            destination: Path to the directory to place the EPUB.
            metadata: Metadata object for the work.

        Returns:
            Nothing.
        """
        title = os.path.basename(os.path.normpath(source))
        chapters = [os.path.join(source, chapter) for chapter in metadata.chapters]

        html = generate_text_table_of_contents(chapters, destination, title)
        cover = find_cover(source, self._covers)
        command = self.get_text_epub_command(html, "{0}.epub".format(os.path.splitext(html)[0]), cover, metadata)
        subprocess.run(command)
        
        os.remove(html)
    
    def build_epub(self, grouping, work):
        """
        Build the EPUB for a given grouping and work.

        Args:
            grouping: Grouping enum representing the grouping of the work.
            work: Name of the work as str.

        Returns:
            Nothing.
        """
        metadata = self.load_metadata(grouping, work)
        source = os.path.abspath(os.path.join(self._root_directory, grouping.value, work))
        destination = os.path.abspath(os.path.join(self._root_directory, grouping.value, work, self._output_directory))
        if self.is_comic(grouping):
            self.build_comic_epub(source, destination, metadata)
        elif self.is_text(grouping):
            self.build_text_epub(source, destination, metadata)
    
    def open_epub(self, grouping, work):
        """
        Open the EPUB for a given grouping and work.

        Args:
            grouping: Grouping enum representing the grouping of the new work.
            work: Name of the new work as str.

        Returns:
            Nothing.
        
        Raises:
            FileNotFoundError: If no EPUB file can be found.
        """
        folder = os.path.abspath(os.path.join(self._root_directory, grouping.value, work, self._output_directory))
        epub = os.path.join(folder, "{0}.epub".format(work))
        if os.path.isfile(epub):
            command = self.get_view_epub_command(epub)
            subprocess.run(command)
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), epub)
    
    def create_work(self, grouping, work):
        """
        Create a new work.

        Args:
            grouping: Grouping enum representing the grouping of the new work.
            work: Name of the new work as str.

        Returns:
            Nothing.
        """
        location = os.path.join(self._root_directory, grouping.value, work)
        if not os.path.exists(location):
            os.makedirs(location)
    
    def import_chapters(self, grouping, work, chapters):
        """
        Imports chapters for a given grouping and work.

        Args:
            grouping: Grouping enum representing the grouping of the work.
            work: Name of the work as str.
            chapters: List of paths to the individual chapters to import.

        Returns:
            Nothing.
        """
        destination = os.path.abspath(os.path.join(self._root_directory, grouping.value, work))
        if self.is_comic(grouping):
            import_comics(chapters, destination)
        elif self.is_text(grouping):
            import_texts(chapters, destination, self._css_file)
    
    def load_metadata(self, grouping, work):
        """
        Load metadata for a given grouping and work.

        Args:
            grouping: Grouping enum representing the grouping of the work.
            work: Name of the work as str.

        Returns:
            Metadata: The metadata.
        """
        work_directory = os.path.join(self._root_directory, grouping.value, work)
        metadata_json_file = os.path.abspath(os.path.join(work_directory, "metadata.json"))
        if os.path.isfile(metadata_json_file):
            with open(metadata_json_file, "r") as f:
                return Metadata(**json.load(f))
        else:
            chapters = []
            if self.is_comic(grouping):
                with os.scandir(work_directory) as it:
                    for entry in sorted(it, key=lambda e: e.name):
                        if entry.is_file() and entry.name.endswith(".cbz"):
                            chapters.append(entry.name)
            elif self.is_text(grouping):
                with os.scandir(work_directory) as it:
                    for entry in sorted(it, key=lambda e: e.name):
                        if entry.is_file() and entry.name.endswith(".html"):
                            chapters.append(entry.name)
            return Metadata(chapters=chapters)
    
    def save_metadata(self, grouping, work, metadata):
        """
        Save metadata for a given grouping and work.

        Args:
            grouping: Grouping enum representing the grouping of the work.
            work: Name of the work as str.
            metadata: Metadata object to save.

        Returns:
            Nothing.
        """
        metadata_json_file = os.path.abspath(os.path.join(self._root_directory, grouping.value, work, "metadata.json"))
        with open(metadata_json_file, "w") as f:
            f.write(metadata.to_json())
    
    def regenerate(self):
        """
        Regenerate library absolute paths.

        Args:
            None
        Returns:
            Nothing        
        """
        for text_grouping in self._texts:
            text_grouping_dir = os.path.join(self._root_directory, text_grouping)
            with os.scandir(text_grouping_dir) as it:
                for entry in it:
                    if entry.is_dir():
                        text_work_dir = os.path.join(text_grouping_dir, entry.name)
                        with os.scandir(text_work_dir) as it:
                            for entry in it:
                                if entry.name.endswith(".html"):
                                    fix_css(entry.path, self._css_file)