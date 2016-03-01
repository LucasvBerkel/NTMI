def filterTestSentence(sentenceList, limit):
	newSentenceList = []
	for sentence in sentenceList:
		if len(sentence) <= 17:
			newSentenceList.append(sentence)
	return newSentenceList