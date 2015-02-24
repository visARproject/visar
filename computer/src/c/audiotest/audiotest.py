# Use prebuilt deocde library to play test file over socket
import socket
import decoder
import time

FILENAME = 'test.mp3'
CHUNK = 32
OUT_PORT = 19101
IN_PORT  = 19102
HOSTNAME = "127.0.0.1"


def send_sound():
  # setup the connection
  #hostname = raw_input("Enter server address: ")
  hostname = HOSTNAME
  f_in = decoder.open(FILENAME)
  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # get a socket
  sock.bind((hostname,IN_PORT))
  #sock.connect((hostname,PORT)) # connect to remote host
  #sock.send('S') # indicate that we wish to send data only
  #sock.send('\n') # send newline to indicate lack of name
  #while not '\n' == sock.recv(1):
  #  a = 1

  #rate = f_in.getframerate() # store the sample rate
  #sock.send(chr(rate >> 8)) # send 1st byte of sample rate
  #sock.send(chr(rate & 0xFF)) # send 2nd byte of sample rate
  #sock.send(chr(f_in.getnchannels())) # send the number of channels
  #sock.send(chr(f_in.getsampwidth())) # send the samle width

  # print some basic stats
  print f_in.getframerate(), f_in.getnchannels(), f_in.getsampwidth()

  # use this for timings
  rate = f_in.getframerate()
  delay = 1.0/rate * CHUNK

  # start sending data
  bytes = f_in.readframes(CHUNK)
  average = 1
  while bytes != '':
    timer = time.time()
    sock.sendto(bytes,(hostname,OUT_PORT))
    sock.recvfrom(1)
    bytes = f_in.readframes(CHUNK)
    #time.sleep(delay) #sync with reciever
    #average = .875*average + (time.time() - timer)/delay*.125
    #print average  # scaling factor
  sock.close()
  f_in.close()
    
  
if __name__ == '__main__':
  send_sound()
