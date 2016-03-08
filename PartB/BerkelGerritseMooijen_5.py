import re
import ast # string to list literal
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-input", help="path to non-binarized file", type=str)
parser.add_argument("-output", help="path to binarized file", type=str)
args = parser.parse_args()

# Converts the textfile to a list
# Input(s):
# - non_binarized_file, string which represents the path to the txt-file to be read
# Output(s):
# - sentencelist, list containing unbinarized sencentes
def convert_txt_to_sentencelist(non_binarized_file):
	print("Convert text file to sentencelist:")
	sentencelist = []
	counter = 0
	with open(non_binarized_file) as data_file:
		for line in data_file:
			if ((counter % 100) == 0):
				writestatus(counter, 33335)
			counter += 1
			if line != '\n':
				line = line.replace('\n', '')
				terminalList = re.findall("\(\S+\s", line)
				for terminal in terminalList:
					word = re.findall("[^(\s+]+", terminal)
					substitute = "[\"{}\" ".format(word[0])
					line = line.replace(terminal, substitute)
				terminalList = re.findall("\s[^\s)]+\)", line)
				for terminal in terminalList:
					word = re.findall("[^)\s+]+", terminal)
					substitute = " \"{}\"]".format(word[0])
					line = line.replace(terminal, substitute)
				line = line.replace(' ', ',')
				line = line.replace(')', ']')
				sentence = ast.literal_eval(line)
				sentencelist.append(sentence)
	print("Completed            ")
	return sentencelist

# Function takes unbinarized sentencelist and binarizes the sentences
# Input(s):
# - sentencelist, list containting unbinarized sentences
# Output(s):
# - binarizedlist, list containing binarized sencentes
def binarizeSentenceList(sentencelist):
	print("Converting sentences to binarized sentences:")
	binarizedlist = []
	counter = 0
	length = len(sentencelist)
	for sentence in sentencelist:
		if((counter % 100) == 0):
			writestatus(counter, length)
		counter += 1
		binarizedlist.append(binarizeSentence(sentence))
	print("Completed            ")
	return binarizedlist

# Function recieves unbinarized sentence and binarizes it, due to recursing also 
# sub-sentences may be given as input
# Input(s):
# - sentence, whole or part of unbinarized sentence
# Output(s):
# - sentence, binarized part of sentence
def binarizeSentence(sentence):
	length = len(sentence)
	if isinstance(sentence[1], str) :
		return sentence
	sentence[1] = binarizeSentence(sentence[1])
	if length == 2:
		return sentence
	if length > 3:
		name = sentence[0]
		if "|" in name:
			name = name + "_" + sentence[1][0]
		else:
			name =  "@" + name + "|" + sentence[1][0]
		sentence[2] = [name] + sentence[2:]
	sentence[2] = binarizeSentence(sentence[2])
	del sentence[3:]
	return sentence

# Function to chechk if the binarized sentences does not contain errors
# Input(s):
# - sentencelist, list containing alleged binarized sentences
# Delivers no output(s)
def checkForBinarizeErrors(sentencelist):
	print("Check sentences for binarized errors:")
	errors = 0
	counter = 0
	length = len(sentencelist)
	for sentence in sentencelist:
		writestatus(counter, length)
		counter += 1
		errors = checkSentenceBinarizeErrors(sentence, errors)
	print("Completed            ")
	print("{} misstakes were made over {} sentences.".format(errors, length))

# Receives whole or part of sentence to check if it is binarized
# Input(s):
# - sentence, whole or part of sentence to be checked
# - counter, current counter of errors in sentencelist
# Output(s):
# - counter, current counter of errors in sentencelist after checking the sentence
def checkSentenceBinarizeErrors(sentence, counter):
	if len(sentence) > 3:
		counter += 1
	if isinstance(sentence[1], str):
		return counter
	counter = checkSentenceBinarizeErrors(sentence[1], counter)
	if len(sentence) == 2:
		return counter
	counter = checkSentenceBinarizeErrors(sentence[2], counter)
	return counter

# Prints the current status of a progress
# Input(s)
# - currentline, a counter which will eventualy add up to the totallines
# - totallines, total amount of steps in progress until convergence, default is length of trainingcorpus
# Delivers no output(s) 
def writestatus(currentline, totallines):
    i = (currentline / totallines) * 100
    print("{} %            ".format(i), end="\r")

# Converts the list of binarized sentences to strings and writes to a text specified by path binarized_file
# Input(s)
# - binarizedlist, list containing binarized sencentes
# - non_binarized_file, string which represents the path to the txt-file to be written to
# Delivers no output(s) 
def write_binarized_list_to_txt(binarizedlist, binarized_file):
	with open(binarized_file, "w") as textfile:
		for sentence in binarizedlist:
			sentence = ' '.join(map(str, [sentence]))
			terminalList = re.findall("\[\S+,", sentence)
			for terminal in terminalList:
				word = terminal[2:-2]
				substitute = "(" + word
				sentence = sentence.replace(terminal, substitute)
			terminalList = re.findall("\s[^\s+\]]+\]", sentence) # [^(\s+]+
			for terminal in terminalList:
				word = terminal[2:-2]
				substitute = " " + word + ")" 
				sentence = sentence.replace(terminal, substitute)
			sentence = sentence.replace(']', ')')
			sentence = sentence.replace('),', ')')
			textfile.write(sentence)


if __name__ == "__main__":
	non_binarized_file = args.input
	binarized_file = args.output

	if non_binarized_file and binarized_file:
		sentencelist = convert_txt_to_sentencelist(non_binarized_file)
		binarizedlist = binarizeSentenceList(sentencelist)
		checkForBinarizeErrors(binarizedlist)
		write_binarized_list_to_txt(binarizedlist, binarized_file)
	else:
		parser.print_help()
