import urllib.request

url = 'http://www.abc.net.au/res/streaming/audio/mp3/triplej.pls'

contents = str(urllib.request.urlopen(url).read())

#print(contents)

file1_pos = contents.find("File1")
after_file_1 = contents[file1_pos+6:]
new_line_pos = after_file_1.find('\\r')
radio_url = after_file_1[:new_line_pos-1]

print(radio_url)
