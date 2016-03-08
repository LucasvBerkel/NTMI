import re
import ast # string to list literal
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-input", help="path to non-binarized file", type=str)
parser.add_argument("-output", help="path to binarized file", type=str)
args = parser.parse_args()

def convert_txt_to_sentencelist(non_binarized_file):
	sentencelist = []
	with open(non_binarized_file) as data_file:
		for line in data_file:
			if line != '\n':
				line = line.replace('\n', '')
				terminalList = re.findall("\(\S+\s", line)
				print(terminalList)
				for terminal in terminalList:
					print(terminal)
					temp = re.compile(terminal)
					word = re.compile("\[\'\S+\'")
					
					line = temp.sub(word, line)
				# print(line)
				# print(temp)
					# line = line.replace(terminal, word)
				# print(line)
				# line = line.replace(' ', ',')
				# line = line.replace('(', '[')
				# line = line.replace(')', ']')
				# print(line)
				# terminalList = re.findall("\s[\w|.]+\s", line)
				# for terminal in terminalList:
					# line = line.replace(terminal, '\"{}\"'.format(terminal.strip()))
				# line = line.strip()
				# sentence = ast.literal_eval(line)
				# sentencelist.append(sentence)
	# return sentencelist
			

if __name__ == "__main__":
	non_binarized_file = args.input
	binarized_file = args.output
	sentencelist = convert_txt_to_sentencelist(non_binarized_file)
	# for sentence in sentencelist:
		# print(sentence)