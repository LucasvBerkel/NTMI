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
parser.add_argument("-train_corpus", help="set the training corpus", type=str)
parser.add_argument("-test_corpus", help="set the test_corpus", type=str)
parser.add_argument("-n", help="set the sequence length", type=int)
parser.add_argument("-smoothing", help="set the smoothing to be used (no, add1 or gt)", type=str)
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
def calculate_propability(line, sequence_dictN, sequence_dictN1, n, offset, smoothing):
	line = line.split("\n")
	line = line[0]
	splitLine = line.split(" ")

	W_n, N1 = get_wn_and_n1(splitLine)
	try:
		valueN = sequence_dictN[line]
	except Exception:
		if(smoothing == "add1"):
			try:
				valueN1 = sequence_dictN1[N1]
				return(1/valueN1+offset)
			except Exception:
				return(1/offset)
		else:
			return 0.0
	valueN1 = sequence_dictN1[N1]
	return valueN/valueN1		

# Returns the strings of the last word of a string and the sentence without this last word
# Input(s):
# - splitLine is a list of words (strings)
# Outputs(s):
# - wN is the last word of splitLine
# - evidence is a string of the which equals to splitLine without the last word
def get_wn_and_n1(splitLine):
	wN = splitLine[-1]
	del splitLine[-1]
	evidence = " ".join(splitLine)
	return wN, evidence

# Adds one to the count of each sequence in the sequence dictonary
# Inputs
def addOneSmoothing(seq_dict):
	for element in seq_dict:
		seq_dict[element] += 1

def goodTuringSmoothingUnseen(seq_dict):
	length = len(seq_dict)
	totalUnseen = (length**2)-length
	totalSeenOnce = countValueOccurances(seq_dict, 1) 
	print(length)
	print(totalSeenOnce)
	print(totalUnseen)
	return (totalSeenOnce/totalUnseen)

def countValueOccurances(seq_dict, value):
	counter = 0
	for element in seq_dict:
		if(seq_dict[element]==value):
			counter += 1
	return counter

def goodTuringSmoothingSeenTillK(seq_dict, k):
	n1 = countValueOccurances(seq_dict, 1)
	n_k1 = countValueOccurances(seq_dict, k+1)
	for r in range(1, k+1):
		n_r = countValueOccurances(seq_dict, r)
		n_r1 = countValueOccurances(seq_dict, r+1)
		rStar = (((r+1)*(n_r1)/(n_r))-(r*(((k+1)*n_k1)/(n1))))/(1-(((k+1)*n_k1)/(n1)))

		for element in seq_dict:
			if (seq_dict[element] == r):
				seq_dict[element] = rStar
	return seq_dict

def createSmoothedN1Dict(seq_dict):
	uniGramDict = {}
	for element in seq_dict:
		words = element.split(" ")
		if words[0] in uniGramDict:
			uniGramDict[words[0]] += seq_dict[element]
		else:
			uniGramDict[words[0]] = seq_dict[element]
	return uniGramDict

if __name__ == "__main__":
	train_corpus = args.train_corpus
	test_corpus = args.test_corpus
	n = args.n
	smoothing = args.smoothing

	# Assignment 1
	sentencelistCorpus = convert_txt_to_sentencelist(train_corpus, n)
	sequence_dictN = get_frequencies_sequences(sentencelistCorpus, n)
	sequence_dictN1 = get_frequencies_sequences(sentencelistCorpus, n-1)



	sentencelistTestCorpus = convert_txt_to_sentencelist(test_corpus, n)
	sequenceTestCorpus_dict = get_frequencies_sequences(sentencelistTestCorpus, n)

	for line in sequenceTestCorpus_dict:
		if smoothing == "add1":
			# Assignment 2
			sequence_dictAddOneN = sequence_dictN.copy()
			addOneSmoothing(sequence_dictAddOneN)

			vocabularySize = len(get_frequencies_sequences(sentencelistCorpus, 1))
			probability = calculate_propability(line, sequence_dictAddOneN, sequence_dictN1, n, vocabularySize, smoothing)
		elif smoothing == "gt":
			# Assignment 3
			if not line in sequence_dictN:
				probability = goodTuringSmoothingUnseen(sequence_dictN)
				print(probability)
			else:
				sequence_dictTuringSmoothN = sequence_dictN.copy()
				sequence_dictTuringSmoothN = goodTuringSmoothingSeenTillK(sequence_dictTuringSmoothN, 5)
				sequence_dictTuringSmoothN1 = createSmoothedN1Dict(sequence_dictTuringSmoothN)
				probablity = calculate_propability(line, sequence_dictTuringSmoothN, sequence_dictTuringSmoothN1, n, 0, smoothing)		
		else:
			probability = calculate_propability(line, sequence_dictN, sequence_dictN1, n, 0, smoothing)
		sequenceTestCorpus_dict[line] = probability

	for key, value in sequenceTestCorpus_dict.items():
		if value == 0:
			print(key)