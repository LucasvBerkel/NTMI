
import argparse
from sys import stdout

parser = argparse.ArgumentParser()
parser.add_argument("-smoothing", help="yes/no", type=str)
parser.add_argument("-train_set", help="path to the training set", type=str)
parser.add_argument("-test_set", help="path to the test set", type=str)
parser.add_argument("-test_set_predicted", help="path to write the predicted tags for test set", type=str)
args = parser.parse_args()

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
	return sentencelist

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

	return wordTag_dict, tagSeq_dict, tag_dict 

def retrievePossibleTags(word, tag_dict, wordTag_dict):
	tagList = []
	for element in tag_dict:
		temp = element + " " + word
		if(temp in wordTag_dict):
			tagList.append(element)
	return tagList

def emissionProbability(word, tag, wordTag_dict, smoothing):
	temp = tag + " " + word
	if not temp in wordTag_dict:
		if smoothing == "yes":
			print("please fix code at line 98")
			# formule for P(u|t) here. 
			# n1_t = 
			# N_t = 

			# for now return 0 so it doesn't crash
			return 0 
		else:
			return 0
	countN = wordTag_dict[temp]
	countN1 = 0
	for element in wordTag_dict:
		tagWord = element.split(" ")
		if tagWord[0] == tag:
			countN1 += wordTag_dict[element]
	return countN/countN1

def stateTranstitionProbability(previousTag, tag, tagSeq_dict, tag_dict):
	temp = previousTag + " " + tag
	if not temp in tagSeq_dict:
		return 0
	countN = tagSeq_dict[temp]
	countN1 = tag_dict[previousTag]
	return countN/countN1

def highestCandidate(viterbi_dict, tag, word, tag_dict, wordTag_dict, tagSeq_dict, smoothing):
	maxProb = 0
	maxTag = ""
	for previousTags in viterbi_dict:
		previousTag = previousTags.split(" ")
		eProb = emissionProbability(word, tag, wordTag_dict, smoothing)
		sTProb = stateTranstitionProbability(previousTag[-1], tag, tagSeq_dict, tag_dict)
		probNode = eProb*sTProb*viterbi_dict[previousTags]
		if(probNode >= maxProb):
			maxProb = probNode
			maxTag = previousTags + " " + tag
	return maxProb, maxTag

def calculateTag(wordTag_dict, tagSeq_dict, tag_dict , sentence, smoothing):
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
			maxProb, maxTag = highestCandidate(viterbi_dict, tag, sentence[x], tag_dict, wordTag_dict, tagSeq_dict, smoothing) 
			temp_dict[maxTag] = maxProb
		viterbi_dict = temp_dict
	return viterbi_dict

def convertSentence(sentence):
	wordSentence = []
	tagSentence = []
	for word in sentence:
		parts = word.split("/")
		wordSentence.append(parts[0])
		tagSentence.append(parts[1])
	return wordSentence, tagSentence

def getpercent(currentline, totallines):
    i = (currentline / totallines) * 100
    return i

# Prints the status to stdout
def writestatus(currentline, totallines=638073):
    i = getpercent(currentline, totallines)
    stdout.write("\r%s 	percent" % i)
    stdout.flush()

# Predicts the tags and writes them to a file.
def evaluation(sentencelist, test_sentencelist, wordTag_dict, tagSeq_dict, tag_dict, test_set_predicted, smoothing):
	with open(test_set_predicted, "w") as textfile:
		correct_tag_count = 0
		total_tag_count = 0
		length = len(test_sentencelist)
		for sentence_counter, attemptedSentence in enumerate(test_sentencelist):
			writestatus(sentence_counter, length)
			sentence, real_tags = convertSentence(attemptedSentence)
			viterbi_dict = calculateTag(wordTag_dict, tagSeq_dict, tag_dict, sentence, smoothing)
			# print(viterbi_dict)
					
			for element in viterbi_dict:
				predicted_tags = element.split(" ")
			# print("Predicted tags: {}".format(predicted_tags))

			# print(real_tags)
			# print(predicted_tags)

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
		print("Accuracy: {}".format(accuracy))
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

		evaluation(sentencelist, test_sentencelist, wordTag_dictTuringSmoothN, tagSeq_dictTuringSmoothN, tag_dict, test_set_predicted)	
	else:
		evaluation(sentencelist, test_sentencelist, wordTag_dict, tagSeq_dict, tag_dict, test_set_predicted, smoothing)	