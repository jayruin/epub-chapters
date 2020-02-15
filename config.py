import json
from enum import Enum

class Config:
    """
    A configuration file.

    Attributes:
        file: Path to the json configuration file.
        config: A dictionary representing the parsed json configuration file.
        grouping: An Enum representing the different work groupings.
    """
    def __init__(self, file):
        """
        Initialize Config class with given file.

        Args:
            file: Path to the json configuration file.

        Returns:
            Nothing.
        """
        self.file = file
        with open(file, "r") as f:
            self.config = json.loads(f.read())
        self.grouping = Enum("Grouping", {**self.config["FORMATS"]["Comic"], **self.config["FORMATS"]["Text"]})

    def get_groupings(self):
        """
        Get the work groupings.

        Args:
            No args.

        Returns:
            List of groupings as str.
        """
        return list({**self.config["FORMATS"]["Comic"], **self.config["FORMATS"]["Text"]}.values())

    def is_comic(self, grouping):
        """
        Checks whether grouping is a comic.

        Args:
            grouping: Str representing the grouping to check.

        Returns:
            Bool whether grouping is a comic.
        """
        if grouping.value in list(self.config["FORMATS"]["Comic"].values()):
            return True
        return False

    def is_text(self, grouping):
        """
        Checks whether grouping is a text.

        Args:
            grouping: Str representing the grouping to check.

        Returns:
            Bool whether grouping is a text.
        """
        if grouping.value in list(self.config["FORMATS"]["Text"].values()):
            return True
        return False

    def get_library_root(self):
        """
        Get library root.

        Args:
            No args.

        Returns:
            Path to library root directory.
        """
        return self.config["root"]

    def get_library_output(self):
        """
        Get library output directory.

        Args:
            No args.

        Returns:
            Path to library output directory.
        """
        return self.config["output"]

    def get_comic_epub_command(self, source, destination, cover):
        """
        Get the command for converting a comic to EPUB.

        Args:
            source: Path to the file to convert from.
            destination: Path to the file to convert to.
            cover: Path to the cover file to use.

        Returns:
            Command list for converting comics to EPUB.
        """
        if cover is None:
            cover_option = []
        else:
            cover_option = ["--cover", cover]
        return [*self.config["Calibre"]["convert"], *[source, destination], *self.config["Calibre"]["convert-comic-epub"], *cover_option]

    def get_text_epub_command(self, source, destination, cover):
        """
        Get the command for converting a text to EPUB.

        Args:
            source: Path to the file to convert from.
            destination: Path to the file to convert to.
            cover: Path to the cover file to use.

        Returns:
            Command list for converting comics to EPUB.
        """
        if cover is None:
            cover_option = []
        else:
            cover_option = ["--cover", cover]
        return [*self.config["Calibre"]["convert"], *[source, destination], *self.config["Calibre"]["convert-html-epub"], *cover_option]

    def get_view_epub_command(self, epub):
        """
        Get the command for viewing an EPUB.

        Args:
            epub: Path to EPUB file to view.

        Returns:
            Command list for viewing an EPUB.
        """
        return [*self.config["Calibre"]["viewer"], *[epub]]

    def get_css(self):
        """
        Get the CSS file to use for conversions.

        Args:
            No args.

        Returns:
            Path to the CSS file.
        """
        return self.config["CSS"]

    def get_covers(self):
        """
        Get the possible cover files to use for conversions in search order.

        Args:
            No args.

        Returns:
            List of paths to cover file names in search order.
        """
        return self.config["covers"]