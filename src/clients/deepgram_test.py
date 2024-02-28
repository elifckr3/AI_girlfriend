# Copyright 2023 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from dotenv import load_dotenv
import logging, verboselogs
from time import sleep
from src.system_conf import ELEVEN_LABS_KEY

from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)

load_dotenv()


def deepgram_trascription():
    try:
        # example of setting up a client config. logging values: WARNING, VERBOSE, DEBUG, SPAM
        # config = DeepgramClientOptions(
        #     verbose=logging.DEBUG, options={"keepalive": "true"}
        # )
        # deepgram: DeepgramClient = DeepgramClient("", config)
        # otherwise, use default config
        vad_events = ""

        deepgram: DeepgramClient = DeepgramClient(ELEVEN_LABS_KEY)

        dg_connection = deepgram.listen.live.v("1")

        sentence_buffer = "Test Message"

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            print("transcript:%s"%result.channel.alternatives)
            if len(sentence) == 0:
                return
            self.sentence_buffer = sentence
            print(f"speaker: {sentence}")

        def on_results(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            print(f"Results: {sentence}")

        def on_metadata(self, metadata, **kwargs):
            print(f"Meta Data:\n{metadata}\n")

        def on_speech_started(self, speech_started, **kwargs):
            print(f"Speach Started:\n{speech_started}\n")

        def on_utterance_end(self, utterance_end, **kwargs):
            print(f"\n{utterance_end}\n")
            # Wait for the microphone to close
            microphone.finish()

        def on_error(self, error, **kwargs):
            print(f"\n{error}\n")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Close, on_results)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options: LiveOptions = LiveOptions(
            model="nova-2",
            punctuate=True,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=30000,
            # To get UtteranceEnd, the following must be set:
            interim_results=True,
            utterance_end_ms="2000",
            vad_events=True,
        )
        dg_connection.start(options)

        # Open a microphone stream on the default input device
        microphone = Microphone(dg_connection.send)

        # start microphone
        microphone.start()

        # wait until finished
        while True:
            if not microphone.is_active():
                break
            sleep(1)

        # Wait for the microphone to close
        microphone.finish()

        # Indicate that we've finished
        dg_connection.finish()

        print("Finished")
        # sleep(30)  # wait 30 seconds to see if there is any additional socket activity
        # print("Really done!")
        return sentence_buffer

    except Exception as e:
        print(f"Could not open socket: {e}")
        return