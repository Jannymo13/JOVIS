from jtts import JTTS

if __name__ == "__main__":
    print("Loaded Modules")
    tts = JTTS()
    jstt.speechToTextLoop(tts.speak)
    tts.requestStop()
