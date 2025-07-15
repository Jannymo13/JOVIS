import warnings
from queue import Queue
import threading
import numpy as np
import sounddevice as sd
from kokoro import KPipeline
from torch import Tensor


class JTTS:
    def __init__(self, voice: str = "am_echo", SAMPLE_RATE: int = 24000) -> None:
        print("Starting TTS server")
        self.voice = voice
        self.SAMPLE_RATE = SAMPLE_RATE
        self.ttsQ = Queue()


        # Suppress warnings
        warnings.filterwarnings(
            "ignore",
            message="dropout option adds dropout after all but last recurrent layer",
        )
        warnings.filterwarnings(
            "ignore", message="`torch.nn.utils.weight_norm` is deprecated"
        )

        # Start the TTS pipeline
        self.pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
        

        #Start the TTS Thread
        self.queThread = threading.Thread(target=self.startTTS, daemon=True)
        self.queThread.start()
        print("Loaded TTS Model")

    def trim_audio(self, audio: Tensor, threshold: float = 1e-06) -> Tensor:
        """
        Trims the given audio to remove silence at the ends
        """
        endIdx = 1
        startIdx = 0

        for i in range(len(audio)):
            if abs(audio[i].item()) > threshold:
                startIdx = i
                break

        for i in range(len(audio) - 1, -1, -1):
            if abs(audio[i].item()) > threshold:
                endIdx = i
                break

        # bounding
        endIdx = min(len(audio) - 1, endIdx)
        startIdx = max(0, startIdx)

        return audio[startIdx:endIdx]

    def speak(self, text: str) -> None:
        """
        padding: length of time in seconds to play silence for in order to get bluetooth devices out
                 of standby
        """
        try:
            # Generate speech
            generator = self.pipeline(text, voice=self.voice)

            # generate the audio
            for _, _, audio in generator:
                # WARN: realistically, this should not be a problem
                audio = self.trim_audio(audio)
                self.ttsQ.put(audio)

        except Exception as ex:
            print(ex)

    def startTTS(self, padding: float = 0.25):
        while True:
            if not self.ttsQ.empty():

                # play a short period of silence to prime bluetooth devices, can be skipped by setting padding to 0
                if padding > 0:
                    sd.play(
                        np.zeros((int(self.SAMPLE_RATE * padding), 1), dtype=np.float32),
                        samplerate=24000,
                    )
                    sd.wait()

                while not self.ttsQ.empty():
                    # get the audio
                    audio = self.ttsQ.get()

                    if audio is None:  # end the tts if None is an entry
                        self.ttsQ.task_done()
                        return

                    sd.play(audio, 24000)
                    sd.wait()

                    self.ttsQ.task_done()

    def requestStop(self) -> None:
        self.ttsQ.put(None)
        self.queThread.join()

if __name__ == "__main__":
    tts = JTTS()
    # tts.speak(
    """
    According to all known laws of aviation, there is no way a bee should be able to fly. 
    Its wings are too small to get its fat little body off the ground. 
    The bee, of course, flies anyway because bees don't care what humans think is impossible.
    Yellow, black. Yellow, black. Yellow, black. Yellow, black.
    Ooh, black and yellow!
    """
    # )

    while True:
        inp = input()
        if inp == "\exit":
            print("Exiting...")
            break
        tts.speak(inp)

    tts.requestStop()
    print("Done")

