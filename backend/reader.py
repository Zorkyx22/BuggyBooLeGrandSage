from PyPDF2 import PdfReader
import argparse
import os
import pandas as pd
from config import DATA_FILE_NAME

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--source", help="Directory from which to read files", default=os.getcwd())
parser.add_argument("-d", "--destination", help="Directory in which to save the data", default=os.getcwd())
parser.add_argument("-f", "--fileType", action="append", help="Target file types. Valid file types are : pdf, txt", choices=['pdf', 'txt'])

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
						readContent.extend(page.extract_text().split("\n"))
				elif file.endswith(".txt") and "txt" in fileTypes:
					print(f"-=: Reading Txt File : {absPath}", end="")
					with open(absPath, 'rb') as f:
						readContent = f.readLines()
				print(f" -- Read {len(readContent)} lines")
				for line in readContent:
					if(line.strip()!=""):
						rows.append((file, line))
	print(f"-=: Saving data to file : {destination}")
	df = pd.DataFrame(data=rows, columns=["document", "content"])
	df = df[df["content"].str.split().str.len() > 15]
	df.to_csv(os.path.join(destination, DATA_FILE_NAME), escapechar="\\")
	
if __name__ == "__main__":
	if os.path.isdir(args.source) and os.path.isdir(args.destination):
		readAllFiles(args.source, args.destination, args.fileType)
	elif os.path.isdir(args.source):
		print("Specified source was not found.\nExiting...")
	else:
		print("Specified destination was not found.\nExiting...")