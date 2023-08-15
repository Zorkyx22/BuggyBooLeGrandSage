from PyPDF2 import PdfReader
import argparse
import os
import pandas as pd
from config import DATA_FILE_NAME

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", help="Directory from which to read files. Defaults to current directory", default=os.getcwd())
parser.add_argument("-d", "--destination", help=f"File or directory in which to save the data. If file name is not in path, defaults to current_directory/{DATA_FILE_NAME}. File name must be a .csv file that does not exist.", default=os.getcwd())
parser.add_argument("-f", "--fileType", action="append", help="Target file types. Valid file types are : pdf, txt. If none are specified, none are read.", choices=['pdf', 'txt'])

args = parser.parse_args()

def readAllFiles(dir, destination, fileTypes):
	print(f"-=[{'*'*25} Reading files from {dir} {'*'*25}]=-")
	rows = []
	for (root, _, files) in os.walk(dir):
		print(f"-=: Directory : {root}")
		for file in files:
			absPath = os.path.join(root, file)
			if os.path.isfile(absPath):
				readContent = []
				if file.endswith(".pdf") and "pdf" in fileTypes:
					print(f"-=: Reading Pdf File : {absPath}", end="")
					pdfReader = PdfReader(absPath)
					for page in pdfReader.pages:
						readContent.extend(page.extract_text())
					readContent = split_text(readContent)
				elif file.endswith(".txt") and "txt" in fileTypes:
					print(f"-=: Reading Txt File : {absPath}", end="")
					with open(absPath, 'rb') as f:
						readContent = split_text(f.readLines())
				print(f" -- Read {len(readContent)} sections")
				for line in readContent:
					if(line.strip()!=""):
						rows.append((file, line))
	print(f"-=: Saving data to file : {destination}")
	df = pd.DataFrame(data=rows, columns=["document", "content"])
	df = df[df["content"].str.split().str.len() > 15]
	pathToSave = destination if destination.endswith(".csv") else os.path.join(destination, DATA_FILE_NAME)
	df.to_csv(pathToSave, escapechar="\\")
	

def split_text(pages):
	text = " ".join(pages)
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
	if os.path.isdir(args.source) and (os.path.isdir(args.destination) or args.destination.endswith(".csv")):
		readAllFiles(args.source, args.destination, args.fileType)
	elif os.path.isdir(args.source):
		print("Specified source was not found.\nExiting...")
	else:
		print("Specified destination was not found.\nExiting...")