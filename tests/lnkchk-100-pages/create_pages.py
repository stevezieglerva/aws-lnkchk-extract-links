
total = 100

for file_num in range(1, total + 1):
	with open("page_" + str(file_num) + ".html", "w") as f:
		print(file_num)
		f.write("test")	
		for link_num in range(file_num, file_num + total):
			link = "<a href='page_" + str(link_num) + ".html'>Link to " + str(link_num) + "</a><br/>"
			f.write(link + "\n")


