from RealtimeSTT import AudioToTextRecorder
import keyboard

def P2TLoop(func)->None:

    recorder = AudioToTextRecorder(model="small", compute_type="float32")

    print("\n\n\nStarted STT!")
    while True:
        if keyboard.is_pressed('f9'):
            print("Starting Recording")
            recorder.start()
            while keyboard.is_pressed('f9'):
                pass
            print("Stopped Recording")
            recorder.stop()
            func(recorder.text())
        if keyboard.is_pressed('f8'):
            recorder.shutdown()
            return

if __name__ == '__main__':
    P2TLoop(print)
