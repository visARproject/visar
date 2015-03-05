import network
import audio
import interface
import time

def audioCallback(event1, event2):
  print event1, event2
  
def networkCallback(event):
  print event
  
class voice_event(interface.Interface):
  def __init__(self):
    interface.Interface.__init__(self)
    
def voiceCallback(event):
  print event
  
def test():
  network_state = network.NetworkState('test_laptop', 'testname', 'status')
  network_state.add_callback(networkCallback)
  print 'Started Network'
  
  #audio_state = audio.AudioController()
  #audio_state.add_callback(audioCallback)
  #print 'Started Audio'
  
  #time.sleep(1)
  #print 'starting audio'
  #audio_state.start('127.0.0.1')
  
  time.sleep(3)
  #print 'starting vc'
  #voice = voice_event()
  #voice.add_callback(voiceCallback)
  #audio_state.start_voice(voice)
  
  time.sleep(3)
  #print 'stopping vc'
  #audio_state.stop_voice()
  
  time.sleep(3)
  #print 'stopping audio'
  #audio_state.stop()
  
  #clean up the objects
  time.sleep(1)
  print 'cleanup'
  network_state.destroy()
  #audio_state.destroy()
  
  time.sleep(1)
  print 'Done'
  
if __name__ == '__main__':
  test()
