# communication module (client/server), get/send audio
import SocketServer
import socket
import pyaudio
import threading
import time

CHUNK = 1024     # number of frames/packet
SAMPLE_RATE = 11025 # sending frequency, mic samples at 44100?
PORT = 9001 # application port number (likely to change)
 
class audio_server(SocketServer.BaseRequestHandler):
  def handle(self):
    # get data about communcation direction
    if(self.request.recv(1) == 'S'): output = False
    else: output = True
    
    # get information about client audio format
    rate = ord(self.request.recv(1)) << 8 # get the samle rate, byte 1
    rate = rate | ord(self.request.recv(1)) # get byte 2 of sample rate
    channels = ord(self.request.recv(1)) # get the number of channels
    width = ord(self.request.recv(1)) # get the samle width
    
    # setup the playback stream/thread
    p = pyaudio.PyAudio()
    speaker_stream = p.open(format = pyaudio.paInt16,
              channels = channels,
              rate = rate,
              output = True)          
    bytes = CHUNK * channels * width              
    kill_flag = threading.Event()
    in_thread = threading.Thread(target=get_sound, args=(speaker_stream,self.request,bytes,kill_flag))
    in_thread.start()
    
    # setup mic stream/thread
    if(output):
      mic_stream = p.open(format = pyaudio.paInt16,
                         channels = channels,
                         rate = rate,
                         input = True)
      out_thread = threading.Thread(target=send_sound, args=(mic_stream,self.request,bytes,kill_flag))
      out_thread.start()
    
    while not kill_flag.is_set():
      time.sleep(0.1)
    
    kill_flag.set() # signal threads to die
    if(output): mic_stream.close()  # close the mic stream
    speaker_stream.close() # close the speaker stream
    p.terminate() # kill pyaudio
   
# get sound gets audio from socket and plays over speakers   
def get_sound(stream, sock, bytes, kill_flag):
  # get/send data
  data = sock.recv(bytes) # get initial packet
  while data != '':  # go while we're getting data
    stream.write(data) # write audio to speakers
    data = sock.recv(bytes) # read from socket
    if(kill_flag.is_set()): return  # thread is kill
  kill_flag.set() # client disconnected, set flag
    
    
# send sound gets audio from mic and sends over socket   
def send_sound(stream, sock, bytes, kill_flag):
  data = stream.read(bytes) # get inital data
  while data != '': # go while we're getting data
    sock.send(data) # send the data over socket
    data = stream.read(bytes) # get audio from mic
    if(kill_flag.is_set()): return  # thread is kill
  kill_flag.set() # client disconnected, set flag

   
class Audio_Manager:
  def start_server():
    server = SocketServer.TCPServer(('',PORT), audio_server)
    server.serve_forever()
    
  def start_client():
    # setup the connection
    hostname = raw_input("Enter server address: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # get a socket
    sock.connect((hostname,PORT)) # connect to host
    
    # configure the settings
    sock.send('B') # biderictional communication
    rate = SAMPLE_RATE # store the sample rate
    sock.send(chr(rate >> 8)) # send 1st byte of sample rate
    sock.send(chr(rate & 0xFF)) # send 2nd byte of sample rate
    sock.send(chr(1)) # send the number of channels (1=mono)
    sock.send(chr(1)) # send the samle width (16-bit is 1)

    # start sending data
    # setup the playback stream/thread
    p = pyaudio.PyAudio()
    speaker_stream = p.open(format = pyaudio.paInt16,
              channels = 1,
              rate = SAMPLE_RATE,
              output = True)          
    bytes = CHUNK * 1 * 1 # num frames * channels * width
    kill_flag = threading.Event()
    in_thread = threading.Thread(target=get_sound, args=(speaker_stream,sock,bytes,kill_flag))
    in_thread.start()
      
    # setup mic stream/thread
    mic_stream = p.open(format = pyaudio.paInt16,
                       channels = 1,
                       rate = SAMPLE_RATE,
                       input = True)
    out_thread = threading.Thread(target=send_sound, args=(mic_stream,sock,bytes,kill_flag))
    out_thread.start()
      
    while not kill_flag.is_set():
      time.sleep(0.1)
      
    kill_flag.set() # signal threads to die
    sock.close() # close the socket
    mic_stream.close()  # close the mic stream
    speaker_stream.close() # close the speaker stream
    p.terminate() # kill pyaudio
    
    
    
if __name__ == '__main__':
  server = raw_input("Start as Server or Client (S/C):") == 'S'
  manager = Audio_Manager(server)
  if(server): start_server()
  else: start_client()
    
  
