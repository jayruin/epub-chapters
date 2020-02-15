import os
import os.path
import math
import subprocess
import shutil
from zipfile import *
from html.entities import *

def txt_to_html(txt, entities, css):
	"""
	Converts plaintext txt to html and saves it with given css file.

    Args:
        txt: Plaintext to convert.
        entities: List of UTF-8 characters to replace with HTML entities.
        css: Path to the CSS file to include in the HTML output file.

    Returns:
        Converted HTML text.
    """
	entities.remove("\n")
	content = txt.strip().split("\n\n")

	html = "<!DOCTYPE html>\n<html>\n<head>\n\t<meta charset=\"utf-8\">\n"
	html += "\t<link rel=\"stylesheet\" href=\"{0}\">\n".format("file:///" + os.path.abspath(css))
	html += "\t<title>" + content[0] + "</title>\n"
	html += "</head>\n"
	html += "<body>\n"
	html += "\t<h1>" + content[0] + "</h1>\n"

	if len(content) > 1:
		html += "\n"
		for line in content[1:]:
			p = ""
			for char in line:
				if char in entities:
					p += "&#{0};".format(ord(char))
				else:
					p += char
			html += "\t<p>" + p.replace("\n", "<br>") + "</p>\n"

	html += "</body>\n"
	html += "</html>"

	return html

def generate_text_table_of_contents(source, destination):
	"""
	Generates a table of contents for text works.

    Args:
        source: Path to the directory with individual chapters.
		destination: Path to the directory to place the table of contents.

    Returns:
        Path to the generated table of contents.
    """
	title = os.path.basename(os.path.normpath(source))
	content = "<!DOCTYPE html>\n<html>\n<head>\n\t<meta charset=\"utf-8\">\n"
	content += "\t<title>{0}</title>\n".format(title)
	content += "</head>\n"
	content += "<body>\n"
	content += "\t<h1>{0}</h1>\n".format(title)
	content += "\t<h2>Table Of Contents</h2>\n"
	content += "\t<p>\n"

	with os.scandir(source) as it:
		for entry in sorted(it, key=lambda e: e.name):
			if entry.is_file() and entry.name.endswith(".html"):
				with open(entry.path, "r", encoding="utf-8-sig") as html_chapter:
					html_content = html_chapter.read()
					start = html_content.find("<title>")
					end = html_content.find("</title>")
					length = len("<title>")
					if start == -1 or end == -1 or html_content[start + length: end].strip() == "":
						chapter_title = "No Title"
					else:
						chapter_title = html_content[start + length: end].strip()
					content += "\t\t<a href=\"{0}\">{1}</a><br>\n".format("file:///" + entry.path, chapter_title)

	content += "\t</p>\n"
	content += "</body>\n"
	content += "</html>"

	if not os.path.exists(destination):
		os.makedirs(destination)
	html = os.path.join(destination, title + ".html")
	with open(html, "w", encoding="utf-8-sig") as toc:
		toc.write(content)
	return html

def generate_comic_table_of_contents(source, destination):
	"""
	Generates a table of contents for comic works.

    Args:
        source: Path to the directory with individual chapters.
		destination: Path to the directory to place the table of contents.

    Returns:
        Path to the generated table of contents.
    """
	content = ""
	with os.scandir(source) as it:
		for entry in sorted(it, key=lambda e: e.name):
			if entry.is_file() and entry.name.endswith(".cbz"):
				content += "{0}:{1}\n".format(entry.name, os.path.splitext(os.path.basename(os.path.normpath(entry.name)))[0])

	if not os.path.exists(destination):
		os.makedirs(destination)
	txt = os.path.join(destination, "comics.txt")
	with open(txt, "w", encoding="utf-8-sig") as toc:
		toc.write(content)
	return txt

def generate_cbc(source, destination, txt):
	"""
	Generates a .cbc file from .cbz files and a comics.txt table of contents.

    Args:
        source: Path to the directory with individual chapters.
		destination: Path to the directory to place the table of contents.
		txt: Path to the comics.txt table of contents file.

    Returns:
        Path to the generated cbc file.
    """
	cbc = os.path.join(destination, "{0}.cbc".format(os.path.basename(os.path.normpath(source))))
	cbc_zip_file = ZipFile(cbc, "w", ZIP_STORED)
	with os.scandir(source) as it:
		for entry in sorted(list(it), key=lambda x: x.name):
			if entry.is_file() and entry.name.endswith(".cbz"):
				cbc_zip_file.write(entry.path, entry.name)
	cbc_zip_file.write(txt, os.path.basename(os.path.normpath(txt)))
	return cbc

def import_comics(sources, destination):
	"""
	Import comic chapters. Each chapter must be either a .cbz file or a directory with images.

    Args:
        sources: List of paths to the individual chapters to import.
		destination: Path to the directory to place the chapters.

    Returns:
        Nothing.
    """
	for source in sources:
		if not os.path.isdir(source):
			ext = os.path.splitext(source)[1]
			if ext == ".cbz":
				shutil.copy(source, os.path.join(destination, os.path.basename(os.path.normpath(source))))
		else:
			cbz = ZipFile(os.path.join(destination, "{0}.cbz".format(os.path.basename(os.path.normpath(source)))), "w", ZIP_STORED)
			with os.scandir(source) as it:
				file_list = sorted(list(it), key=lambda x: x.name)
				length = len(file_list)
				digits = int(math.log10(length)) + 1
				for i in range(length):
					entry = file_list[i]
					if entry.is_file():
						cbz.write(entry.path, "{0}{1}".format(str(i + 1).zfill(digits), os.path.splitext(entry.path)[1]))

def import_texts(sources, destination, css):
	"""
	Import text chapters. Each chapter must be either a .txt or .html file.

    Args:
        sources: List of paths to the individual chapters to import.
		destination: Path to the directory to place the chapters.

    Returns:
        Nothing.
    """
	entities = set([v for v in html5.values() if len(v) == 1])
	for source in sources:
		if not os.path.isdir(source):
			ext = os.path.splitext(source)[1]
			if ext == ".txt":
				with open(source, "r", encoding="utf-8-sig") as txt:
					with open(os.path.join(destination, "{0}.html".format(os.path.splitext(os.path.basename(os.path.normpath(source)))[0])), "w", encoding="utf-8") as html:
						html.write(txt_to_html(txt.read(), entities, css))
			elif ext == ".html":
				shutil.copy(source, os.path.join(destination, os.path.basename(os.path.normpath(source))))

def find_cover(folder, cover_names):
	"""
	Search folder for a cover, with filename from cover_names.

    Args:
        folder: Path to the directory to search.
		cover_names: List of possible cover filenames to search for.

    Returns:
        First cover found, nothing if no cover exists.
    """
	for candidate_cover in cover_names:
		if os.path.isfile(os.path.join(folder, candidate_cover)):
			return os.path.abspath(os.path.join(folder, candidate_cover))
	return None

def build_comic(source, destination, config):
	"""
	Build a comic EPUB.

    Args:
        source: Path to the directory with individual chapters.
		destination: Path to the directory to place the EPUB.
		config: The Config configuration file to use.

    Returns:
        Nothing.
    """
	txt = generate_comic_table_of_contents(source, destination)
	cover = find_cover(source, config.get_covers())
	cbc = generate_cbc(source, destination, txt)
	command = config.get_comic_epub_command(cbc, "{0}.epub".format(os.path.splitext(cbc)[0]), cover)
	subprocess.run(command)
	os.remove(txt)
	os.remove(cbc)
	

def build_text(source, destination, config):
	"""
	Build a text EPUB.

    Args:
        source: Path to the directory with individual chapters.
		destination: Path to the directory to place the EPUB.
		config: The Config configuration file to use.

    Returns:
        Nothing.
    """
	html = generate_text_table_of_contents(source, destination)
	cover = find_cover(source, config.get_covers())
	command = config.get_text_epub_command(html, "{0}.epub".format(os.path.splitext(html)[0]), cover)
	subprocess.run(command)
	os.remove(html)

def find_epub(folder, title):
	"""
	Find the EPUB.

    Args:
        folder: Path to the directory to search.
		title: The filename without extension of the EPUB to search for.

    Returns:
        Path to the EPUB if one is found, nothing otherwise.
    """
	epub = os.path.join(folder, "{0}.epub".format(title))
	if os.path.isfile(epub):
		return epub
	return None

def open_epub(epub, config):
	"""
	Open the EPUB.

    Args:
        epub: Path to the EPUB to open.
		config: The Config configuration file to use.

    Returns:
        Nothing.
    """
	command = config.get_view_epub_command(epub)
	subprocess.run(command)