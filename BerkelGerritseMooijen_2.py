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
parser.add_argument("-scored_permutations", nargs='+', help="list of words")
parser.add_argument("-assignmentNumber", help="set which assignment to start", type=int)
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

# Reads the conditional probability file, retrieves the posterior probability and prints it
# Input(s):
# - prob_file is the path to the textfile containing the sentences to be calculated
# - sequence_dictN is the dict containing the frequencies of sequences of length n
# - sequence_dictN1 is the dict containing the frequencesie of sequences of length n-1
# - n is a number which represents the length of the sequences
def conditional_prob(prob_file, sequence_dictN, sequence_dictN1, n):
	with open(prob_file) as data_file:
		for line in data_file:
			line = line.split("\n")
			line = line[0]
			probability = calculate_propability(line, sequence_dictN, sequence_dictN1, n)
			if probability == -1:
				continue
			splitLine = line.split(" ")
			W_n, N1 = get_wn_and_n1(splitLine)
			print("P({}|{}) = {}".format(W_n, N1, probability))

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

# Reads the sequence probability file, in order to use the same code multiple times, every line in the file is put into a list.
# Input(s):
# - seq_file is the path to the textfile containing the sentences to be calculated
# - sequence_dictN is the dict containing the frequencies of sequences of length n
# - sequence_dictN1 is the dict containing the frequencesie of sequences of length n-1
# - n is a number which represents the length of the sequences
def sequence_opener(seq_file, sequence_dictN, sequence_dictN1, n):
	with open(seq_file) as data_file:
		List = []
		for line in data_file:
			line = line.split("\n")
			line = line[0]
			List = [line] + List
		sequence_prob(List, sequence_dictN, sequence_dictN1, n)

# Recieves the list of sentences, calculates the probabilities using the posterior probabilities and prints them
# Input(s):
# - sentencelist is the list containing the sentences to be calculated
# - sequence_dictN is the dict containing the frequencies of sequences of length n
# - sequence_dictN1 is the dict containing the frequencesie of sequences of length n-1
# - n is a number which represents the length of the sequences
# Output(s):
# - probability_dict is a dictionary which contains all the permutations and their probability (only for assignment 4)
def sequence_prob(sentencelist, sequence_dictN, sequence_dictN1, n, assignmentNumber=0):
	probability_dict = {}
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
		if assignmentNumber != 4:
			print("The probability of the line: '{}' is {}".format(sentence,probability))
		else:
			probability_dict[sentence] = probability
	if assignmentNumber == 4:
		return probability_dict

# Calculates the posterior probability given the full sentence
# Input(s):
# - line is the sentence for which the probability is to be calculated, the last word of the line will be cut of later on
# - sequence_dictN is the dict containing the frequencies of sequences of length n
# - sequence_dictN1 is the dict containing the frequencesie of sequences of length n-1
# - n is a number which represents the length of the sequences
# Output:
# - posterior probability given the sentence
def calculate_propability(line, sequence_dictN, sequence_dictN1, n):
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
		return valueN/valueN1		
	else:
	 return -1	

if __name__ == "__main__":
	# corpus = args.corpus
	# assignmentNumber = args.assignmentNumber
	# if(assignmentNumber == 1 or assignmentNumber == 2 or assignmentNumber == 3):
	# 	n = args.n
	# else:
	# 	n = 2
	# sentencelistCorpus = convert_txt_to_sentencelist(corpus, n)
	# sequence_dictN = get_frequencies_sequences(sentencelistCorpus, n)
	# sequence_dictN1 = get_frequencies_sequences(sentencelistCorpus, n-1)

	print(args.scored_permutations)

	# if(args.n != None and assignmentNumber == 1):
	# 	m = 10
	# 	get_top_m(sequence_dictN, n, m)
	# 	get_top_m(sequence_dictN1, n-1, m)
	# elif(args.n != None and args.conditional_prob_file != None and assignmentNumber == 2):
	# 	prob_file = args.conditional_prob_file
	# 	conditional_prob(prob_file, sequence_dictN, sequence_dictN1, n)
	# elif(args.n != None and args.sequence_prob_file != None and assignmentNumber == 3):
	# 	seq_prob_file = args.sequence_prob_file
	# 	sequence_opener(seq_prob_file, sequence_dictN, sequence_dictN1, n)
	# elif(assignmentNumber == 4):
	# 	set_of_words = args.scored_permutations
	# 	permutations = list(itertools.permutations(set_of_words))
	# 	for x in range(len(permutations)):
	# 		permutations[x] = " ".join(permutations[x])
	# 	probability_dict = sequence_prob(permutations, sequence_dictN, sequence_dictN1, n, assignmentNumber)
	# 	get_top_m(probability_dict, n, 2)
	# else:
	# 	print("Combation of inputs unknown")