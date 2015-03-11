import audio
import interface
import time

def audioCallback(event1, event2):
  print event1, event2
  
class voice_event(interface.Interface):
  def __init__(self):
    interface.Interface.__init__(self)
    
def voiceCallback(event):
  print event
  
def test():
  print 'Starting Audio'
  audio_state = audio.AudioController()
  audio_state.add_callback(audioCallback)
  
  time.sleep(1)
  print 'starting audio'
  audio_state.start('127.0.0.1')
  
  time.sleep(2)
  print 'starting vc'
  voice = voice_event()
  voice.add_callback(voiceCallback)
  audio_state.start_voice(voice)
  
  time.sleep(1)
  print 'muting speaker'
  audio_state.set_volume(0)
  
  time.sleep(2)
  print 'stopping vc'
  audio_state.stop_voice()

  time.sleep(1)
  print 'changing volume to max'
  audio_state.set_volume(100)
  
  time.sleep(2)
  print 'stopping audio'
  audio_state.stop()
  
  time.sleep(1)
  print 'cleaning up...'
  audio_state.destroy()
  
  time.sleep(2)
  print 'Done'
  
if __name__ == '__main__':
  test()
