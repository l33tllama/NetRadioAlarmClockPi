import urllib.request

stream_url = 'http://live-radio01.mediahubaustralia.com/7LRW/mp3/'
#stream_url = 'http://live-radio01.mediahubaustralia.com/UNEW/mp3/'
#stream_url = 'http://radio1.internode.on.net:8000/268'
stream_url = "http://live-radio01.mediahubaustralia.com/2TJW/mp3"
'''
request = urllib.request(stream_url)

try:
    request.add_header('Icy-MetaData', 1)
    response = urllib.urlopen(request)
    icy_metaint_header = response.headers.get('icy-metaint')
    if icy_metaint_header is not None:
        metaint = int(icy_metaint_header)
        read_buffer = metaint+255
        content = response.read(read_buffer)
        title = content[metaint:].split("'")[1]
        print(title)
except:
    print('Error')

'''

header = {'Icy-MetaData' : 1}


request = urllib.request.Request(stream_url, headers=header)
response = urllib.request.urlopen(request)
icy_metaint_header = response.headers.get('icy-metaint')
if icy_metaint_header is not None:
    metaint = int(icy_metaint_header)
    read_buffer = metaint+255
    content = response.read(read_buffer)
    content_str = ""
    for _byte in content:
        content_str += chr(int(_byte))
    #print(str(content))
    stream_title_pos = content_str.find("StreamTitle=")
    #print("stream title pos: " + str(stream_title_pos))
    if stream_title_pos > 0:
        post_title_content = content_str[stream_title_pos+13:]
        semicolon_pos = post_title_content.find(';')
        station_name = post_title_content[:semicolon_pos-1]
        print("Station: " + station_name)
    else:
        stream_url = stream_url[7:39]
        print("len: " + str(len(stream_url)))
        print(stream_url)

    #print(str(content_str))
    #title = content[metaint:].split("'")[1]
    #print(title)


