# Authors:
# Lucas van Berkel, 10747958
# Ruben Gerritse, 10760326
# Gideon Mooijen, 10686290

import operator
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("corpus", help="set the carpus", type=str)
parser.add_argument("n", help="set the sequence length", type=int)
parser.add_argument("m", help="set the toplist length", type=int)
args = parser.parse_args()

# Reads a txt-file and puts all the words in a list. Then returns the list
# Input(s):
# - file is a path to the list to be read and converted
# Output(s):
# - wordlist is a list which contains all the words of the inputted txt-file
def convert_txt_to_wordlist(file):
	wordlist = []
	with open(file) as data_file:
		for line in data_file:
			for word in line.split(" "):
				if word.endswith("\n"):
					word = word.replace("\n", "")
				if word != "":
					wordlist.append(word)
	return wordlist

# Reads a list and counts the number of times a sequence of n words is contained in the list/
# Input(s):
# - wordlist is a list of words (strings if individual words)
# - n is a natural number which represents the length of the sequences
# Output(s):
# - sequence_dict is a dict which contains sequences of words and their frequencies in the wordlist
def get_frequencies_sequences(wordlist, n):
	sequence_dict = {}
	for word_index in range(len(wordlist)):
		sequence = ""
		if word_index < n-1:
			for offset in range(word_index, -1 , -1):
				if offset == word_index:
					sequence = wordlist[word_index]
				else:
					sequence = wordlist[offset] + " " + sequence
		else:
			for offset in range(n):
				if offset == 0:
					sequence = wordlist[word_index]
				else:
					sequence = wordlist[word_index - offset] + " " + sequence
		if sequence in sequence_dict:
			sequence_dict[sequence] += 1
		else:
			sequence_dict[sequence] = 1
	return sequence_dict

# Prints the top m most occuring sequences
# Input(s):
# - sequence_dict is a dict which contains sequences of words and their frequencies in the wordlist
# - m is a natural number which represents the top m of most occuring sequences
def get_top_m(sequence_dict, m, n):
	sorted_sequence_dict = sorted(sequence_dict.items(), key=operator.itemgetter(1))
	if m > len(sorted_sequence_dict):
		limit = -1
		print("Top {} most occuring sequences of length {}".format(len(sorted_sequence_dict), n))
	else:
		limit = len(sorted_sequence_dict)-m-1
		print("Top {} most occuring sequences of length {}".format(m, n))
	for i in range(len(sorted_sequence_dict)-1, limit, -1):
		print(sorted_sequence_dict[i])

# Prints  the sum of all frequencies of all sequences for the given n
# Input(s):
# - sequence_dict is a dict which contains sequences of words and their frequencies in the wordlist
# - n is a natural number which represents the length of the sequences
def get_sum_frequencies(sequence_dict, n):
	sum_frequencies = 0
	for key, value in sequence_dict.items():
		sum_frequencies+=value
	print("")
	print("Sum of the frequencies with length {}: {}".format(n, sum_frequencies))


def partAstep1(n, m, file):
	wordlist = convert_txt_to_wordlist(file)
	sequence_dict = get_frequencies_sequences(wordlist, n)
	get_top_m(sequence_dict, m, n)
	get_sum_frequencies(sequence_dict, n)

if __name__ == "__main__":
	corpus = args.corpus
	n = args.n
	m = args.m
	partAstep1(n, m, corpus)