import stt
import tts

print("Loaded Modules\nStarting TTS Server")
tts = tts.JTTS()
stt.P2TLoop(tts.speak)
tts.requestStop()
