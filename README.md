# epub-chapters

## About

Built on PySide2 for Python 3.7+.

This is an app for managing individual chapters of a work and for quickly building an EPUB from the chapters. Currently, there are two supported formats: comic and text. Comic chapters are stored as .cbz files and text chapters are stored as .html files.

Comic chapters can be imported as folders with images inside. Text chapters can be imported as .txt files which will be converted to .html.

Uses Calibre to convert and view EPUBs and a text editor of your choice to edit chapters.

## Setup

### Setup config.json

`config["root"]` is the path to the root directory of your library.

`config["output"]` is the path to the output directory of your library.

`config["CSS"]` is the path to the CSS stylesheet used in the conversions.

`config["covers"]` is a list of cover file names to search for (in order) in the directory of your chapter files used in the conversions.

Currently, there are two supported formats: Comic and Text. Under each, you can create individual groupings of your choosing, under which are the works. Under `config["Comic"]` and `config["Text"]` are name-value pairs where name is the name of the Python enum and the value is the folder title for the grouping.

`config["Calibre"]["convert"]` is a list for the command to convert to EPUB. Additional command line options for specific formats are placed separately under `config["Calibre"]["convert-comic-epub"]` and `config["Calibre"]["convert-html-epub"]`. Check the [full Calibre documentation](https://manual.calibre-ebook.com/generated/en/ebook-convert.html) for details.

https://manual.calibre-ebook.com/generated/en/ebook-meta.html

`config["Calibre"]["viewer"]` is a list for the command to open an EPUB for viewing. Check the [full Calibre documentation](https://manual.calibre-ebook.com/generated/en/ebook-viewer.html) for details.


### Setup library

Setup your library based on the config.json file you set. Create a root folder, with as many groupings as you listed in your config.json file. Make sure to place your cover file as well as any other required static files. An example would be
```
Library
    calibre.css
    FirstGroup
        SomeNovel
        cover.png
        Static-image.jpg
    SecondGroup
        SomeComic
            cover.jpg
```

After importing chapters, it might look something like

```
Library
    calibre.css
    FirstGroup
        SomeNovel
        Chapter1.html
        Chapter2.html
        cover.png
        Static-image.jpg
    SecondGroup
        SomeComic
        Chapter1.cbz
        Chapter2.cbz
        Cover.jpg
```

