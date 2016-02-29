
import argparse
from sys import stdout

parser = argparse.ArgumentParser()
parser.add_argument("-smoothing", help="yes/no", type=str)
parser.add_argument("-train_set", help="path to the training set", type=str)
parser.add_argument("-test_set", help="path to the test set", type=str)
parser.add_argument("-test_set_predicted", help="path to test set predicted", type=str)
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

def emissionProbability(word, tag, tag_dict, wordTag_dict):
	temp = tag + " " + word
	countN = wordTag_dict[temp]
	countN1 = tag_dict[tag]
	return countN/countN1

def stateTranstitionProbability(previousTag, tag, tagSeq_dict, tag_dict):
	temp = previousTag + " " + tag
	if temp not in tagSeq_dict:
		return 0
	countN = tagSeq_dict[temp]
	countN1 = tag_dict[previousTag]
	return countN/countN1

def highestCandidate(viterbi_dict, tag, word, tag_dict, wordTag_dict, tagSeq_dict):
	maxProb = 0
	maxTag = ""
	for previousTags in viterbi_dict:
		previousTag = previousTags.split(" ")
		eProb = emissionProbability(word, tag, tag_dict, wordTag_dict)
		sTProb = stateTranstitionProbability(previousTag[-1], tag, tagSeq_dict, tag_dict)
		probNode = eProb*sTProb*viterbi_dict[previousTags]
		if(probNode > maxProb):
			maxProb = probNode
			maxTag = previousTags + " " + tag
	return maxProb, maxTag

def calculateTag(wordTag_dict, tagSeq_dict, tag_dict , sentence):
	viterbi_dict = {}
	viterbi_dict["START"] = 1
	for x in range(1, len(sentence)):
		tagList = retrievePossibleTags(sentence[x], tag_dict, wordTag_dict)
		temp_dict = {}
		for tag in tagList:
			maxProb, maxTag = highestCandidate(viterbi_dict, tag, sentence[x], tag_dict, wordTag_dict, tagSeq_dict) 
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

def evaluation(sentencelist, test_sentencelist, wordTag_dict, tagSeq_dict, tag_dict, test_set_predicted):
	


	correct_tag_count = 0
	total_tag_count = 0
	for sentence_counter, attemptedSentence in enumerate(test_sentencelist):
		print(sentence_counter)
		sentence, real_tags = convertSentence(attemptedSentence)
		print(sentence)		
		viterbi_dict = calculateTag(wordTag_dict, tagSeq_dict, tag_dict, sentence)
			
		# print("Original tags: {}".format(real_tags))			
		for element in viterbi_dict:
			predicted_tags = element.split(" ")
		# print("Predicted tags: {}".format(predicted_tags))

		for x in range(len(real_tags)):
			if not (real_tags[x] == "START" or real_tags[x] == "STOP"):
				if (real_tags[x] == predicted_tags[x]):
					correct_tag_count += 1
				total_tag_count += 1

	accuracy = correct_tag_count / total_tag_count
	print("Accuracy: {}".format(accuracy))
	

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

	evaluation(sentencelist, test_sentencelist, wordTag_dict, tagSeq_dict, tag_dict, test_set_predicted)	