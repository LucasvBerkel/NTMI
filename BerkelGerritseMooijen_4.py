import argparse
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
		for line in data_file:
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
	for sentence in sentencelist:
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

			

if __name__ == "__main__":
	smoothing = args.smoothing
	train_set = args.train_set
	test_set = args.test_set
	test_set_predicted = args.test_set_predicted
	n = 2
	

	sentencelist = convert_txt_to_sentencelist(train_set, n)
	attemptedSentence = sentencelist[0]
	print(attemptedSentence)
	print(sentencelist[1])
	print(sentencelist[2])
	# sentence, tags = convertSentence(attemptedSentence)
	# print(attemptedSentence)
	# wordTag_dict, tagSeq_dict, tag_dict  = get_frequencies_sequences(sentencelist, n)
	# viterbi_dict = calculateTag(wordTag_dict, tagSeq_dict, tag_dict, sentence)
	# for element in viterbi_dict:
	# 	lijst = element.split(" ")
	# 	print(lijst)
	# print(tags)
	# counter = 0
	# for x in range(len(tags)):
	# 	if (tags[x] == lijst[x]):
	# 		counter += 1
	# print(counter/len(tags)*100)
	# print("Great Succes")
	# print(len(tags))
	# print(counter)
	# sentence = ["START", "change"]
	# viterbi_dict = calculateTag(wordTag_dict, tagSeq_dict, tag_dict, sentence)
	# print(viterbi_dict)