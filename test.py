
def convert_txt_to_sentencelist(corpus, n):
	n-=1
	sentencelist = []
	with open(corpus) as data_file:
		sentence = ["START/START"] * n
		for line in data_file:
			if line != "======================================\n":
				if line == "./. \n":
					for i in range(n):
						sentence.append("STOP/STOP")	
					sentencelist.append(sentence)
					continue
				for word in line.split(" "):
					if word.endswith("\n"):
						word = word.replace("\n", "")
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
	sequence_dict = {}
	tag_dict = {}
	for sentence in sentencelist:
		for word_index in range(len(sentence)):
			if word_index >= n-1:
				sequence = ""
				tagSeq = ""
				for offset in range(n):
					if offset == 0:
						split = sentence[word_index].split("/")
						sequence = split[0] + " " + split[1]
						tagSeq = split[1]
					else:
						split = sentence[word_index - offset].split("/")
						tagSeq = split[1] + " " + tagSeq
				if sequence in sequence_dict:
					sequence_dict[sequence] += 1
				else:
					sequence_dict[sequence] = 1
				if tagSeq in tag_dict:
					tag_dict[tagSeq] += 1
				else:
					tag_dict[tagSeq] = 1

	return sequence_dict, tag_dict

if __name__ == "__main__":
	corpus = "WSJ02-21.pos"
	sentencelist = convert_txt_to_sentencelist(corpus, 2)
	word_dict, tag_dict = get_frequencies_sequences(sentencelist, 2)
	for element in word_dict:
		print(element)
		print(word_dict[element])
		break
	for element in tag_dict:
		print(element)
		print(tag_dict[element])
		break