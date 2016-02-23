
def convert_txt_to_sentencelist(corpus, n):
	n-=1
	sentencelist = []
	with open(corpus) as data_file:
		sentence = ["<s>"] * n
		for line in data_file:
			if line != "======================================\n":
				if line == "./. \n":
					for i in range(n):
						sentence.append("</s>")	
					sentencelist.append(sentence)
					continue
				for word in line.split(" "):
					if word.endswith("\n"):
						word = word.replace("\n", "")
					if word == "./.":
						for i in range(n):
							sentence.append("</s>")	
						sentencelist.append(sentence)
						sentence = ["<s>"] * n
					else:
						if word != "" and word[0].isalnum() :
							sentence.append(word)
			else:
				sentence = ["<s>"] * n
	return sentencelist

if __name__ == "__main__":
	corpus = "test.pos"
	sentencelist = convert_txt_to_sentencelist(corpus, 2)
	for x in range(len(sentencelist)):
		print(sentencelist[x])