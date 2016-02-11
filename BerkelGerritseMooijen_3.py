# Authors:
# Lucas van Berkel, 10747958
# Ruben Gerritse, 10760326
# Gideon Mooijen, 10686290

import operator
import argparse
import itertools
from sys import stdout
import time

from lxml import etree
import json
import pickle
import re

parser = argparse.ArgumentParser()
parser.add_argument("-corpus", help="set the corpus", type=str)
parser.add_argument("-n", help="set the sequence length", type=int)
args = parser.parse_args()

# Reads a txt-file and returns a list. This list contains lists, which each represents a paragraph.
# Input(s):
# - corpus is a path to the text-file to be read and converted to a list
# - n is a natural number which represents the length of the sequences
# Output(s):
# - sentencelist is a list of lists which contains all the paragraphs of the inputted txt-file
def convert_txt_to_sentencelist(corpus, n):
	n-=1
	sentencelist = []
	firstline = 1
	previousline = ""
	with open(corpus) as data_file:
		sentence = ["<s>"] * n
		for line in data_file:
			if line != "\n":
				if previousline == "\n":
					sentence = ["<s>"] * n
				for word in line.split(" "):
					if word.endswith("\n"):
						word = word.replace("\n", "")
					if word != "":
						sentence.append(word)
			elif previousline != "\n":
				for i in range(n):
					sentence.append("</s>")
				sentencelist.append(sentence)
			previousline = line
		for i in range(n):
				sentence.append("</s>")
		sentencelist.append(sentence)
	return sentencelist

# Reads a list of lists (paragraphs) and counts the number of times a sequence of n words is contained in this list.
# Input(s):
# - sentencelist is a list of lists which contains all the paragraphs of the inputted txt-file
# - n is a natural number which represents the length of the sequences
# Output(s):
# - sequence_dict is a dict which contains sequences of words and their frequencies in the wordlist
def get_frequencies_sequences(sentencelist, n):
	sequence_dict = {}
	for sentence in sentencelist:
		for word_index in range(len(sentence)):
			if word_index >= n-1:
				sequence = ""
				for offset in range(n):
					if offset == 0:
						sequence = sentence[word_index]
					else:
						sequence = sentence[word_index - offset] + " " + sequence
				if sequence in sequence_dict:
					sequence_dict[sequence] += 1
				else:
					sequence_dict[sequence] = 1
	return sequence_dict

# Calculates the posterior probability given the full sentence
# Input(s):
# - line is the sentence for which the probability is to be calculated, the last word of the line will be cut of later on
# - sequence_dictN is the dict containing the frequencies of sequences of length n
# - sequence_dictN1 is the dict containing the frequencesie of sequences of length n-1
# - n is a number which represents the length of the sequences
# Output:
# - posterior probability given the sentence
def calculate_propability(line, sequence_dictN, sequence_dictN1, n, offset=0):
	line = line.split("\n")
	line = line[0]
	splitLine = line.split(" ")
	if len(splitLine)==n:
		W_n, N1 = get_wn_and_n1(splitLine)
		try:
			valueN = sequence_dictN[line]
		except Exception:
			return 0.0
		valueN1 = sequence_dictN1[N1]
		
		print(valueN)
		print(valueN1)
		print(offset)
		
		return valueN/(valueN1+offset)		
	else:
	 	return -1

# Returns the strings of the last word of a string and the sentence without this last word
# Input(s):
# - splitLine is a list of words (strings)
# Outputs(s):
# - W_n is the last word of splitLine
# - N1 is a string of the which equals to splitLine without the last word
def get_wn_and_n1(splitLine):
	W_n = splitLine[-1]
	del splitLine[-1]
	N1 = " ".join(splitLine)
	return W_n, N1

def addOneSmoothing(seq_dict):
	for element in seq_dict:
		seq_dict[element] += 1

def makeZeros(sequence_dictAddOneN, sequence_dictN1):
	length = len(sequence_dictN1)
	counter = 0
	with open("temp.txt", "w") as File:
		for firstElement in sequence_dictN1:
			writestatus(counter, length)
			counter += 1
			for secondElement in sequence_dictN1:
				checkString = firstElement + " " + secondElement
				if not(checkString in sequence_dictAddOneN):
					File.write(checkString + "\n")

def appendDict(seq_dict):
	with open("temp.txt", "r") as File:
		counter = 0
		for line in File:
			line = line.split("\n")
			actualLine = line[0]
			seq_dict[actualLine] = 0
			stdout.write("\r%s" % counter)
			stdout.flush()
			counter += 1
	createdatadump('dataset', seq_dict)

# create datadump
def createdatadump(o, dict):
    filename = str(o) + ".json"
    with open(filename, 'w') as fp:
        json.dump(dict, fp)

    filename = str(o) + ".p"
    with open(filename, 'wb') as fp:
        pickle.dump(dict, fp)


def writestatus(currentline, totallines):
    i = getpercent(currentline, totallines)
    stdout.write("\r%s" % i)
    stdout.flush()

def getpercent(currentline, totallines):
    i = (currentline / totallines) * 100
    return i

def readDict():
	pkl_file = open('dataset.p', 'rb')
	seq_dict = pickle.load(pkl_file)
	pkl_file.close()

if __name__ == "__main__":
	corpus = args.corpus
	n = args.n
	sentencelistCorpus = convert_txt_to_sentencelist(corpus, n)
	# Assignment 1
	sequence_dictN = get_frequencies_sequences(sentencelistCorpus, n)
	sequence_dictN1 = get_frequencies_sequences(sentencelistCorpus, n-1)
	# Assignment 2
	sequence_dictAddOneN = sequence_dictN.copy()
	start = time.clock()
	#makeZeros(sequence_dictAddOneN, sequence_dictN1)
	appendDict(sequence_dictAddOneN)
	end = time.clock()
	elapsed = end - start
	print("Elapsed time: " + str(elapsed))
	# addOneSmoothing(sequence_dictAddOneN)
	# vocabularySize = len(get_frequencies_sequences(sentencelistCorpus, 1))
	# print(calculate_propability("of the", sequence_dictAddOneN, sequence_dictN1, n, vocabularySize))