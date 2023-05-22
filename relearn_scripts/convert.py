if __name__ == '__main__':
	f = open("times.txt", "r")
	times = []
	for line in f:
		times.append(line)
	times2 = []
	for i in range(len(times)):
		if times[i] != "\n":
			times2.append(times[i])
	times3 = []
	for i in range(len(times2)):
		line = times2[i].replace("\n", "")
		times3.append(line)
	times4 = []
	for i in range(len(times3)):
		t = times3[i].split(" ")
		times4.append(t[0])
		times4.append(t[1])
		times4.append(t[2])
		times4.append(t[3])
		times4.append(t[4])
	p = [32,64,128,256,512]
	s = [5000,6000,7000,8000,9000]
	t = [0.1,0.2,0.3,0.4,0.5]
	input_file = open("relearn_results.txt", "w")
	id = 0
	for a in range(len(p)):
		for b in range(len(s)):
			for c in range(len(t)):
				output = "{\"params\":{\"p\":" + str(p[ a ]) + "," + "\"size\":" + str(s[ b ]) + "," + "\"t\":" + str(t[ c ]) + "},\"metric\":\"" + "metr" + "\",\"value\":" + str(times4[id]) + "}\n"
				input_file.write(output)
				id += 1
	input_file.close()
