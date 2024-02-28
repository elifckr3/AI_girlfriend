# Copyright 2023 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from dotenv import load_dotenv
# import logging, verboselogs
from time import sleep
import os
from threading import Event
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
from src.system_conf import (
    DEEPGRAM_KEY,
)
load_dotenv()

# class DeepGram():
#     message: str
#     result_event = Event

def deepgram_trascription():
    # self.result_event = result_event
    try:
        print('listening')
        api_key = os.environ.get(DEEPGRAM_KEY)
        # Open a microphone stream on the default input device
        microphone: Microphone
        dg_connection: DeepgramClient
        deepgram = DeepgramClient(api_key)
        dg_connection = deepgram.listen.live.v("1")
        sentence_buffer = ''
        sentences_added = []

        def on_message(self, result, **kwargs):
            nonlocal sentence_buffer
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            print(f"before speaker: {sentence_buffer}")
            if len(sentence) < len(sentence_buffer):
                sentences_added.append(sentence_buffer)
                sentence_buffer = ''
            sentence_buffer = sentence
            print(f"speaker: {sentence_buffer}")
            # message = sentence
            # return self.message


        def on_metadata(self, metadata, **kwargs):
            print(f"\n\n{metadata}\n\n")

        def on_speech_started(self, speech_started, **kwargs):
            print(f"\n\n{speech_started}\n\n")

        def on_utterance_end(self, utterance_end, **kwargs):
            print(f"\n\n{utterance_end}\n\n")
            microphone.finish()
            return 

        def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")
            # Set the event when done
            # result_event.set()

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options: LiveOptions = LiveOptions(
            model="nova-2",
            punctuate=False,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000,
            # To get UtteranceEnd, the following must be set:
            interim_results=True,
            utterance_end_ms="2000",
            vad_events=True,
        )
        dg_connection.start(options)

        # Open a microphone stream on the default input device
        microphone: Microphone = Microphone(dg_connection.send)

        # start microphone
        microphone.start()
        while True:
            if not microphone.is_active():
                break
        
        dg_connection.finish()

        return sentences_added
    except Exception as e:
        print(f"Could not open socket: {e}")
        return
        

# def on_message(self, result, *args, **kwargs):
#     sentence = result.channel.alternatives[0].transcript
#     if len(sentence) == 0:
#         return
#     # print(f"speaker: {sentence}")
#     else:
#         print(f"speaker: {sentence}")
#         # Wait for the microphone to close
#         self.microphone.finish()

#         # Indicate that we've finished
#         self.dg_connection.finish()

#         pyautogui.press('enter')
#         self.message = sentence
#         # Set the event when done
#         self.result_event.set()

# def on_metadata(self, metadata, *args, **kwargs):
#     print(f"\n\n{metadata}\n\n")

# def on_speech_started(self, speech_started, *args, **kwargs):
#     print(f"\n\n{speech_started}\n\n")

# def on_utterance_end(self, utterance_end, **kwargs):
#     print(f"\n\n{utterance_end}\n\n")

# def on_error(self, error, *args, **kwargs):
#     print(f"\n\n{error}\n\n")
#     pyautogui.press('enter')
#     self.message = 'error'
#     # Set the event when done
#     self.result_event.set()


# if __name__ == "__main__":
#     main()