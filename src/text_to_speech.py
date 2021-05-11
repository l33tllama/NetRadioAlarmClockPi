import espeak

class TextToSpeech:
    speaker = None
    def __init__(self):
        espeak.init()
        self.speaker = espeak.Espeak()

    def say(self, text, on_done=None):
        if on_done is not None:
            self.speaker.add_callback(on_done)
        self.speaker.say(text)