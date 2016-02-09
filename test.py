line = "Hoi jij daar achter de computer"
n = 4
line = line.split("\n")
line = line[0]
splitLine = line.split(" ")
splitLine = ["<s>"] * (n-1) + splitLine
print(splitLine)
for x in range(n, len(splitLine)+1):
	line = splitLine[x-n:x]
	print(line)