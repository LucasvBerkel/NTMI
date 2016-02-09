# Authors:
# Lucas van Berkel, 10747958
# Ruben Gerritse, 10760326
# Gideon Mooijen, 10686290

import operator
import argparse
import itertools

parser = argparse.ArgumentParser()
parser.add_argument("-corpus", help="set the corpus", type=str)
parser.add_argument("-n", help="set the sequence length", type=int)
parser.add_argument("-conditional_prob_file", help="conditional-prob-file", type=str)
parser.add_argument("-sequence_prob_file", help="sequence-prob-file", type=str)
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

# Prints the top m most occuring sequences
# Input(s):
# - sequence_dict is a dict which contains sequences of words and their frequencies in the wordlist
# - m is a natural number which represents the top m of most occuring sequences
def get_top_m(sequence_dict, n, m=10):
	sorted_sequence_dict = sorted(sequence_dict.items(), key=operator.itemgetter(1))
	if m > len(sorted_sequence_dict):
		limit = -1
		print("Top {} most occuring sequences of length {}".format(len(sorted_sequence_dict), n))
	else:
		limit = len(sorted_sequence_dict)-m-1
		print("Top {} most occuring sequences of length {}".format(m, n))
	for i in range(len(sorted_sequence_dict)-1, limit, -1):
		print(sorted_sequence_dict[i])

def conditional_prob(prob_file, sequence_dictN, sequence_dictN1, n):
	with open(prob_file) as data_file:
		for line in data_file:
			probability = calculate_propability(line, sequence_dictN, sequence_dictN1, n)
			print("P({}|{}) = {}".format(W_n, N1, probability))

def calculate_propability(line, sequence_dictN, sequence_dictN1, n):
	line = line.split("\n")
	line = line[0]
	splitLine = line.split(" ")
	if len(splitLine)==n:
		W_n = splitLine[-1]
		del splitLine[-1]
		N1 = " ".join(splitLine)
		try:
			valueN = sequence_dictN[line]
		except Exception:
			return 0.0
		valueN1 = sequence_dictN1[N1]
		return valueN/valueN1

def sequence_opener(seq_file, sequence_dictN, sequence_dictN1, n):
	with open(seq_file) as data_file:
		List = []
		for line in data_file:
			List = [line] + List
		sequence_prob(List, sequence_dictN, sequence_dictN1, n)

def sequence_prob(sentencelist, sequence_dictN, sequence_dictN1, n):
	for sentence in sentencelist:
		line = sentence.split("\n")
		line = line[0]
		splitLine = line.split(" ")
		splitLine = ["<s>"] * (n-1) + splitLine
		probability = 1
		for x in range(n, len(splitLine)+1):
			line = splitLine[x-n:x]
			line = " ".join(line)
			probability *= calculate_propability(line, sequence_dictN, sequence_dictN1, n)
		print("The probability of the line: '{}' is {}".format(sentence,probability))			


if __name__ == "__main__":
	m = 10
	if(args.corpus != None and 	args.n != None):
		n = args.n
		corpus = args.corpus
		sentencelistCorpus = convert_txt_to_sentencelist(corpus, n)
		sequence_dictN = get_frequencies_sequences(sentencelistCorpus, n)
		sequence_dictN1 = get_frequencies_sequences(sentencelistCorpus, n-1)
	if(args.corpus != None and args.n != None and args.conditional_prob_file != None):
		prob_file = args.conditional_prob_file
		conditional_prob(prob_file, sequence_dictN, sequence_dictN1, n)
	if(args.corpus != None and args.n != None and args.sequence_prob_file != None):
		seq_prob_file = args.sequence_prob_file
		sequence_prob(seq_prob_file, sequence_dictN, sequence_dictN1, n)
	if(args.corpus != None):
		set_of_words = {'I', 'do', 'not', 'know', 'what'}
		permutations = list(itertools.permutations(set_of_words))
		for x in range(len(permutations)):
			permutations[x] = " ".join(permutations[x])
		sequence_prob(permutations, sequence_dictN, sequence_dictN1, n)
	# get_top_m(sequence_dictN, n, m)
	# get_top_m(sequence_dictN1, n-1, m)


