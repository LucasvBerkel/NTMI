
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-smoothing", help="yes/no", type=str)
parser.add_argument("-train_set", help="path to the training set", type=str)
parser.add_argument("-test_set", help="path to the test set", type=str)
parser.add_argument("-test_set_predicted", help="path to write the predicted tags for test set", type=str)
args = parser.parse_args()

# Reads a txt-file and returns a list. This list contains lists, which each represents a paragraph.
# Input(s):
# - corpus, a path to the text-file to be read and converted to a list
# - n, a natural number which represents the length of the sequences
# Output(s):
# - sentencelist, the list of lists which contains all the sentences of the inputted txt-file
def convert_txt_to_sentencelist(corpus, n):
	n-=1
	sentencelist = []
	with open(corpus) as data_file:
		sentence = ["START/START"] * n
		counter = 0
		for line in data_file:
			counter += 1
			if(counter%100 == 0):
				writestatus(counter)
			line = line.replace("\n", "")
			if line != "======================================":
				if line == "./. ":
					for i in range(n):
						sentence.append("STOP/STOP")	
					sentencelist.append(sentence)
					sentence = ["START/START"] * n
					continue
				for word in line.split(" "):
					if word == "./.":
						for i in range(n):
							sentence.append("STOP/STOP")	
						sentencelist.append(sentence)
						sentence = ["START/START"] * n
					else:
						if word != "" and word[0].isalnum() :
							sentence.append(word)
			else:
				sentence = ["START/START"] * n
	writestatus(638073)
	return sentencelist

# Reads a list of lists (sentences) and counts the number of times a sequence of n words is contained in this list.
# Input(s):
# - sentencelist, a list of lists which contains all the paragraphs of the inputted txt-file
# - n, a natural number which represents the length of the sequences
# Output(s):
# - wordTag_dict, the dictionary containing the word and tag combinations and its frequency
# - tagSeq_dict, the dictionary containing the tag after tag sequence and its frequency
# - tag_dict, the dictionary containing every tag and its frequency
def get_frequencies_sequences(sentencelist, n):
	wordTag_dict = {}
	tagSeq_dict = {}
	tag_dict = {}
	counter = 0
	length = len(sentencelist)
	for sentence in sentencelist:
		writestatus(counter, length)
		counter += 1
		for word_index in range(len(sentence)):
			tag = "START"
			if word_index >= n-1:
				wordTag = ""
				tagSeq = ""
				tag = ""
				word = ""
				for offset in range(n):
					if offset == 0:
						split = sentence[word_index].split("/")
						wordTag = split[1] + " " + split[0]
						tagSeq = split[1]
						word = split[0]
						tag = split[1]
					else:
						split = sentence[word_index - offset].split("/")
						tagSeq = split[1] + " " + tagSeq
				if wordTag in wordTag_dict:
					wordTag_dict[wordTag] += 1
				else:
					wordTag_dict[wordTag] = 1

				if tagSeq in tagSeq_dict:
					tagSeq_dict[tagSeq] += 1
				else:
					tagSeq_dict[tagSeq] = 1

			if tag in tag_dict:
				tag_dict[tag] += 1
			else:
				tag_dict[tag] = 1
	writestatus(length, length)
	return wordTag_dict, tagSeq_dict, tag_dict 

# Obtains all the possible tags for a word
# Input(s):
# - word, a word in string form
# - tag_dict, a dict which contains all the tags 
# Output(s):
# - tagList is a list of tags corrosponding to the inputted word
def retrievePossibleTags(word, tag_dict, wordTag_dict):
	tagList = []
	for element in tag_dict:
		temp = element + " " + word
		if(temp in wordTag_dict):
			tagList.append(element)
	return tagList

# Calculates the emission probability for a word and a tag
# Input(s):
# - word, a word in string form
# - tag, a tag in string form
# - wordTag_dict is a dict which contains words and their corrosponding tag
# - unknown_dict is a dict which contains the emission probability for unknown words given a tag
# - smoothing, yes or no, according to the user if he/she wants to smooth the dicts
# Output(s):
# - the emission probability
def emissionProbability(word, tag, wordTag_dict, unknown_dict, smoothing):
	temp = tag + " " + word
	if not temp in wordTag_dict:
		if smoothing == "yes":
			return unknown_dict[tag]
		else:
			return 0
	countN = wordTag_dict[temp]
	countN1 = 0
	for element in wordTag_dict:
		tagWord = element.split(" ")
		if tagWord[0] == tag:
			countN1 += wordTag_dict[element]
	return countN/countN1

# Calculates the state transition probability for a sequence of tags
# Input(s):
# - previousTag, the tag from the previous state
# - tag, the tag from the current state
# - tagSeq_dict, the dictionary containing the tag after tag sequence and its frequency
# - tag_dict, the dictionary containing every tag and its frequency
# - smoothing, yes or no, according to the user if he/she wants to smooth the dicts
# Output(s):
# - the state transition probability
def stateTranstitionProbability(previousTag, tag, tagSeq_dict, tag_dict, smoothing):
	temp = previousTag + " " + tag
	if not temp in tagSeq_dict:
		if smoothing == "yes":
			countN = goodTuringSmoothingUnseen(tagSeq_dict, len(tagSeq_dict))
			countN1 = tag_dict[previousTag]
			return countN / countN1
		else:
			return 0
	countN = tagSeq_dict[temp]
	countN1 = tag_dict[previousTag]
	return countN/countN1

# Calculates and returns the tag and its probability with the highest probability
# Input(s):
# - viterbi_dict, the dictonary which contains the paths with the highest probability ending in a specific tag given time 
# - tag, the tag from the current state
# - word, the word in the current time
# - wordTag_dict, the dictionary containing the word and tag combinations and its frequency
# - tagSeq_dict, the dictionary containing the tag after tag sequence and its frequency
# - tag_dict, the dictionary containing every tag and its frequency
# - unknown_dict is a dict which contains the emission probability for unknown words given a tag
# - smoothing, yes or no, according to the user if he/she wants to smooth the dicts
# Output(s):
# - maxProb, highest probability 
# - maxTag, tag with the highest probability
def highestCandidate(viterbi_dict, tag, word, tag_dict, wordTag_dict, tagSeq_dict, unknown_dict, smoothing):
	maxProb = 0
	maxTag = ""
	for previousTags in viterbi_dict:
		previousTag = previousTags.split(" ")
		eProb = emissionProbability(word, tag, wordTag_dict, unknown_dict, smoothing)
		sTProb = stateTranstitionProbability(previousTag[-1], tag, tagSeq_dict, tag_dict, smoothing)
		probNode = eProb*sTProb*viterbi_dict[previousTags]
		if(probNode >= maxProb):
			maxProb = probNode
			maxTag = previousTags + " " + tag
	return maxProb, maxTag

# Calculates the tag sequences with the highest probability given a sentence
# Input(s):
# - wordTag_dict, the dictionary containing the word and tag combinations and its frequency
# - tagSeq_dict, the dictionary containing the tag after tag sequence and its frequency
# - tag_dict, the dictionary containing every tag and its frequency
# - unknown_dict, the dictionary with every tag as key and its emission probability as value for unseen words
# - sentence, 
# - smoothing, yes or no, according to the user if he/she wants to smooth the dicts
# Output(s)
# - viterbi_dict, the dictionary containing the tags with the highest probability for a sentence
def calculateTag(wordTag_dict, tagSeq_dict, tag_dict, unknown_dict, sentence, smoothing):
	viterbi_dict = {}
	viterbi_dict["START"] = 1
	for x in range(1, len(sentence)):
		tagList = retrievePossibleTags(sentence[x], tag_dict, wordTag_dict)
		if not tagList:
			if smoothing == "yes":
				tagList = list(tag_dict.keys())
			else:
				tagList = ['X']
		temp_dict = {}
		for tag in tagList:
			maxProb, maxTag = highestCandidate(viterbi_dict, tag, sentence[x], tag_dict, wordTag_dict, tagSeq_dict, unknown_dict, smoothing) 
			temp_dict[maxTag] = maxProb
		viterbi_dict = temp_dict
	return viterbi_dict

# Accepts a list of word-tag combinations, splits them apart and returns them
# Input(s)
# - sentence, a list of word-tag combinations
# Output(s)
# - wordSentence, a list of words which forms the sentence
# - tagSentence, a list of the corresponding tag given the sentence
def convertSentence(sentence):
	wordSentence = []
	tagSentence = []
	for word in sentence:
		parts = word.split("/")
		wordSentence.append(parts[0])
		tagSentence.append(parts[1])
	return wordSentence, tagSentence

# Prints the current status of a progress
# Input(s)
# - currentline, a counter which will eventualy add up to the totallines
# - totallines, total amount of steps in progress until convergence, default is length of trainingcorpus
# Delivers no output(s) 
def writestatus(currentline, totallines=638073):
    i = (currentline / totallines) * 100
    print("{} %            ".format(i), end="\r")

# Takes a list of sentences and filters it from sentences longer than the given limit
# Input(s)
# - sentencelist, the list of sentences of every length
# - limit, a number for which every sentence longer than it will be deleted
# Output(s)
# - newSentenceList, the list of sentences shorter than the limit
def filterTestSentence(sentenceList, limit):
	newSentenceList = []
	for sentence in sentenceList:
		if len(sentence) <= limit:
			newSentenceList.append(sentence)
	return newSentenceList

# Creates a dict only containing the word-tag combinations only of a given tag
# Input(s)
# - wordTag_dict, the dictionary containing the word and tag combinations and its frequency
# - tag, the tag for which the dict has to be filtered
# Output(s)
# - cleanDict, the dictionary with only word-tag combinations of a certain tag
def fixCleanDict(wordTag_dict, tag):
	cleanDict = {}
	for element in wordTag_dict:
		splitted = element.split(" ")
		if splitted[0] == tag:
			cleanDict[element] = wordTag_dict[element]
	return cleanDict

# Takes every tag and calculates the emission probability for unknown words if the dicts are smoothed
# Input(s)
# - wordTag_dict, the dictionary containing the word and tag combinations and its frequency
# - tag_dict, the dictionary containing every tag and its frequency
# Output(s)
# - unknown_dict, the dictionary with every tag as key and its emission probability as value for unseen words
def unknownEmissionProbabilityList(wordTag_dict, tag_dict):
	tagList = list(tag_dict.keys())
	unknown_dict = {}
	for tag in tagList:
		cleanDict = fixCleanDict(wordTag_dict, tag)
		n1_t = countValueOccurances(cleanDict, 1)
		N_t = tag_dict[tag]
		unknown_dict[tag] = 0.5*(n1_t/N_t)
	return unknown_dict

# Predicts the tags and writes them to a file.
# Input(s):
# - sentencelist, the list of sentences coming from the trainingcorpus
# - test_sentencelist, the list of sentences coming from the testcorpus
# - wordTag_dict, the dictionary containing the word and tag combinations and its frequency
# - tagSeq_dict, the dictionary containing the tag after tag sequence and its frequency
# - tag_dict, the dictionary containing every tag and its frequency
# - test_set_predicted, the path to the txt file with the predicted POS
# - smoothing, yes or no, according to the user if he/she wants to smooth the dicts
# Delivers no output(s)
def evaluation(sentencelist, test_sentencelist, wordTag_dict, tagSeq_dict, tag_dict, test_set_predicted, smoothing):
	unknown_dict = {}
	if smoothing == "yes":
		unknown_dict = unknownEmissionProbabilityList(wordTag_dict, tag_dict)
	with open(test_set_predicted, "w") as textfile:
		correct_tag_count = 0
		total_tag_count = 0
		test_sentencelist = filterTestSentence(test_sentencelist, 17)
		length = len(test_sentencelist)
		for sentence_counter, attemptedSentence in enumerate(test_sentencelist):
			writestatus(sentence_counter, length)
			sentence, real_tags = convertSentence(attemptedSentence)
			viterbi_dict = calculateTag(wordTag_dict, tagSeq_dict, tag_dict, unknown_dict, sentence, smoothing)
					
			for element in viterbi_dict:
				predicted_tags = element.split(" ")

			for x in range(len(real_tags)):
				if not (real_tags[x] == "START" or real_tags[x] == "STOP"):
					if (real_tags[x] == predicted_tags[x]):
						correct_tag_count += 1
					total_tag_count += 1
					textfile.write(sentence[x] + "/" + predicted_tags[x] + "\n")
				elif real_tags[x] == "START":
					textfile.write("======================================\n\n")
				else:
					textfile.write("\n")
		accuracy = correct_tag_count / total_tag_count
		print("Accuracy = {} / {} = {}".format(correct_tag_count, total_tag_count, accuracy))
		textfile.close()
	
# Function takes a dict and smooths it from one till k
# Input(s:
# - seq_dict, the dictionary to be smoothed
# - k, the value to which there has to be smoothed
# Output(s):
# - seq_dict, the smoothed dictionary
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

# Function that takes the Good-Turing smoothed bi-gram dictionary and calculates the uni-gram dict
# Input(s):
# - seq_dict, the already smoothed bi-gram dictionary
# Output(s):
# - uniGramDict, the dictionary with the smoothed uni-gram values
def createSmoothedN1Dict(seq_dict):
	uniGramDict = {}
	for element in seq_dict:
		words = element.split(" ")
		if words[0] in uniGramDict:
			uniGramDict[words[0]] += seq_dict[element]
		else:
			uniGramDict[words[0]] = seq_dict[element]
	return uniGramDict

# Takes a dictionary and calculates the frequency of the desired value
# Input(s):
# - seq_dict, the dictionary containing the frequencies
# - value, the desired value to be counted
# Output(s):
# - counter, the frequency of the given value in the dictionary
def countValueOccurances(seq_dict, value):
	counter = 0
	for element in seq_dict:
		if(seq_dict[element]==value):
			counter += 1
	return counter

# Takes the lexical dictionary containing the tag with a word and its frequency and reassigns the elements
# with value one as the assignment advises, also returns the total number of elements with value one
# Input(s):
# - wordTag_dict, the dictionary containing the tags and words combined
# Output(s):
# - wordTag_dict, the slightly smoothed dictionary
# - totalN_1, total number of occerances of the value one in the previous dictionary wordTag_dict
def smoothLexicalGoodTuring(wordTag_dict):
	totalN_1 = countValueOccurances(wordTag_dict, 1)
	for element in wordTag_dict:
		if wordTag_dict[element] == 1:
			wordTag_dict[element] = 0.5
	return wordTag_dict, totalN_1

# Takes the tagSeq dictionary and returns the value of zero-star, so the smoothed value of zero
# Input(s):
# - seq_dict, the dictionary containing the bi-grams of tags
# - lengthTag, the vocabulary size, needed to calculate the total number of unseen combinations of tags
# Output(s):
# - zero_star, the smoothed frequency of the elements which had zero originaly
def goodTuringSmoothingUnseen(seq_dict, lengthTag):
	length = len(seq_dict)
	totalUnseen = (lengthTag**2)-length
	totalSeenOnce = countValueOccurances(seq_dict, 1) 
	zero_star = totalSeenOnce/totalUnseen
	return (zero_star)

if __name__ == "__main__":
	smoothing = args.smoothing
	train_set = args.train_set
	test_set = args.test_set
	test_set_predicted = args.test_set_predicted
	n = 2

	if smoothing and train_set and test_set and test_set_predicted:
		print("Converting text to sentences: ")
		sentencelist = convert_txt_to_sentencelist(train_set, n)
		print("\nConverting text to sentences: Completed")

		print("Converting sentences into dicts:")
		wordTag_dict, tagSeq_dict, tag_dict  = get_frequencies_sequences(sentencelist, n)
		print("\nConverting sentences into dicts: Completed")

		test_sentencelist = convert_txt_to_sentencelist(test_set, n)

		if smoothing == "yes":
			# Smooth language model
			tagSeq_dictTuringSmoothN = tagSeq_dict.copy()
			tagSeq_dictTuringSmoothN = goodTuringSmoothingSeenTillK(tagSeq_dictTuringSmoothN, 4)
			tag_dictTuringSmoothN1 = createSmoothedN1Dict(tagSeq_dictTuringSmoothN)
			# Smooth lexical model
			wordTag_dictTuringSmoothN = wordTag_dict.copy()
			wordTag_dictTuringSmoothN, totalN_1 = smoothLexicalGoodTuring(wordTag_dictTuringSmoothN)

			evaluation(sentencelist, test_sentencelist, wordTag_dictTuringSmoothN, tagSeq_dictTuringSmoothN, tag_dict, test_set_predicted, smoothing)	
		else:
			evaluation(sentencelist, test_sentencelist, wordTag_dict, tagSeq_dict, tag_dict, test_set_predicted, smoothing)	
	else:
		parser.print_help()