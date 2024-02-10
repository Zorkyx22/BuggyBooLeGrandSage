from PyPDF2 import PdfReader
import argparse
import os
import pandas as pd
import re
from config import DATA_FILE_NAME

from rich.table import Table
from rich import print as rprint
from rich.style import Style
from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)

progress = Progress(
    TextColumn("[bold green]{task.fields[task_name]}", justify="left"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    SpinnerColumn("dots"),
    TimeRemainingColumn(),
)

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", help="Directory from which to read files. Defaults to current directory", default=os.getcwd())
parser.add_argument("-d", "--destination", help=f"File or directory in which to save the data. If file name is not in path, defaults to current_directory/{DATA_FILE_NAME}. File name must be a .csv file that does not exist.", default=os.getcwd())
parser.add_argument("-f", "--fileType", action="append", help="Target file types. Valid file types are : pdf, txt. If none are specified, none are read.", choices=['pdf', 'txt'])

args = parser.parse_args()



def readAllFiles(dir, destination, fileTypes):
	rows = []
	for (root, _, files) in os.walk(dir):
		total_sections = 0
		task_name_template = f"Reading from {root}"
		read_task_id = progress.add_task("read", task_name=task_name_template, start=True, total=len(files))
		for file in files:
			absPath = os.path.join(root, file)
			progress.update(read_task_id, advance=1)
			if os.path.isfile(absPath):
				readContent = []
				if file.endswith(".pdf") and "pdf" in fileTypes:
					pdfReader = PdfReader(absPath)
					for page in pdfReader.pages:
						temp_page = page.extract_text().replace("\n", "")
						readContent.extend(temp_page)
					readContent = split_text(readContent)
				elif file.endswith(".txt") and "txt" in fileTypes:
					with open(absPath, 'rb') as f:
						readContent = split_text(f.readLines().replace("\n", ""))
				total_sections += len(readContent)
				for line in readContent:
					if(line.strip()!=""):
						rows.append((file, line))
		progress.update(read_task_id, task_name = task_name_template + f" - DONE ({total_sections} sections read)", advance=1, )
	df = pd.DataFrame(data=rows, columns=["document", "content"])
	df = df[df["content"].str.split().str.len() > 15]
	pathToSave = destination if destination.endswith(".csv") else os.path.join(destination, DATA_FILE_NAME)
	df.to_csv(pathToSave, escapechar="\\")
	progress.stop()
	progress.console.print(f"Saving data to file : {pathToSave}\n\n", style="bold yellow", justify="center")
	

def split_text(pages):
	text = "".join(pages)
	CHAR_MAX = 1000
	OVERLAPP = 200
	position = 0
	sections = []

	while position < len(text):
		sections.append(text[position:position+CHAR_MAX])
		position += CHAR_MAX - OVERLAPP
	return sections
	# Devrait optimiser pour terminer sur un sentence_ending ou un word break


if __name__ == "__main__":
	hello = Table(show_header=False)
	hello.add_column("the only column")
	hello.add_row("[bold][yellow]File Reader Utility[/yellow][/bold]")
	progress.console.print(hello, justify="center")
	if os.path.isdir(args.source) and (os.path.isdir(args.destination) or args.destination.endswith(".csv")):
		with progress:
			readAllFiles(args.source, args.destination, args.fileType)
	elif os.path.isdir(args.source):
		console.print("Specified source was not found.\nExiting...", style="bold red", justify="center")
	else:
		console.print("Specified destination was not found.\nExiting...", style="bold red", justify="center")