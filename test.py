def createSmoothedN1Dict(seq_dict):
	uniGramDict = {}
	for element in seq_dict:
		words = element.split(" ")
		if words[0] in uniGramDict:
			uniGramDict[words[0]] += seq_dict[element]
		else:
			uniGramDict[words[0]] = seq_dict[element]
	return uniGramDict

poep = {"key hoi": 1, "key praat": 2, "computer praat": 2, "plaatje Praat": 2, "Leuk leuk": 2}
print(createSmoothedN1Dict(poep))