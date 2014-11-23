import socket
import decoder

FILENAME = 'test.mp3'
CHUNK = 1024

def send_sound():
  # setup the connection
  f_in = decoder.open(FILENAME)
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # get a socket
  sock.connect(('127.0.0.1',9001)) # connect to remote host
  sock.send('S') # indicate that we wish to send data only
  rate = f_in.getframerate() # store the sample rate
  sock.send(chr(rate >> 8)) # send 1st byte of sample rate
  sock.send(chr(rate & 0xFF)) # send 2nd byte of sample rate
  sock.send(chr(f_in.getnchannels())) # send the number of channels
  sock.send(chr(f_in.getsampwidth())) # send the samle width

  # start sending data
  bytes = f_in.readframes(CHUNK)
  while bytes != '':
    sock.send(bytes)
    bytes = f_in.readframes(CHUNK)
  sock.close()
  f_in.close()
    
  
if __name__ == '__main__':
  send_sound()
