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
	smoothing = args.smoothing
	train_set = args.train_set
	test_set = args.test_set
	test_set_predicted = args.test_set_predicted
	n = 2
	
	sentencelist = convert_txt_to_sentencelist(corpus, n)
	for x in range(len(sentencelist)):
		print(sentencelist[x])