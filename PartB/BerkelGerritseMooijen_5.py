import re
import ast # string to list literal
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-input", help="path to non-binarized file", type=str)
parser.add_argument("-output", help="path to binarized file", type=str)
args = parser.parse_args()

# Converts the textfile to a list
def convert_txt_to_sentencelist(non_binarized_file):
	sentencelist = []
	with open(non_binarized_file) as data_file:
		for line in data_file:
			if line != '\n':
				line = line.replace('\n', '')
				terminalList = re.findall("\(\S+\s", line)
				for terminal in terminalList:
					word = re.findall("[^(\s+]+", terminal)
					substitute = "[\'{}\' ".format(word[0])
					line = line.replace(terminal, substitute)
				terminalList = re.findall("\s[^\s)]+\)", line)
				for terminal in terminalList:
					word = re.findall("[^)\s+]+", terminal)
					substitute = " \'{}\']".format(word[0])
					line = line.replace(terminal, substitute)
				line = line.replace(' ', ',')
				line = line.replace(')', ']')
				sentence = ast.literal_eval(line)
				sentencelist.append(sentence)
	return sentencelist
			
# def binarize(sentencelist):
# 	binarizedList
# 	for sentence in sentencelist
# 		print

if __name__ == "__main__":
	non_binarized_file = args.input
	binarized_file = args.output
	sentencelist = convert_txt_to_sentencelist(non_binarized_file)
	# binarizedlist = binarize(sentencelist)