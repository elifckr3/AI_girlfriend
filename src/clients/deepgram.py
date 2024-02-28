# Copyright 2023 Deepgram SDK contributors. All Rights Reserved.
# Use of this source code is governed by a MIT license that can be found in the LICENSE file.
# SPDX-License-Identifier: MIT

from dotenv import load_dotenv
# import logging, verboselogs
from time import sleep,time
import os
from threading import Event
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
)
import logging
from src.system_conf import (
    DEEPGRAM_KEY,
)
load_dotenv()

def deepgram_trascription():
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
        stime = 0

        def on_message(self, result, **kwargs):
            nonlocal sentence_buffer
            nonlocal sentences_added
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            if len(sentence) < len(sentence_buffer):
                logging.info(f"speaker: {sentence_buffer}")
                sentences_added.append(sentence_buffer)
                sentence_buffer = ''
            sentence_buffer = sentence


        # def on_metadata(self, metadata, **kwargs):
        #     print(f"\n\n{metadata}\n\n")

        # def on_speech_started(self, speech_started, **kwargs):
        #     print(f"\n\n{speech_started}\n\n")

        def on_utterance_end(self, utterance_end, **kwargs):
            nonlocal sentences_added
            nonlocal sentence_buffer
            nonlocal stime
            nonlocal microphone
            logging.info(f"speaker: {sentence_buffer}")
            sentences_added.append(sentence_buffer)
            # print(f"\n\n{utterance_end}\n\n")
            microphone.finish()
            stime = time()
            return 

        def on_error(self, error, **kwargs):
            print(f"\n\n{error}\n\n")

        dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
        # dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
        # dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
        dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
        dg_connection.on(LiveTranscriptionEvents.Error, on_error)

        options: LiveOptions = LiveOptions(
            model="nova-2-phonecall",
            punctuate=False,
            language="en-US",
            encoding="linear16",
            channels=1,
            sample_rate=16000, # To get UtteranceEnd, the following must be set:
            interim_results=True,
            utterance_end_ms="1000",
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
            sleep(0.2)
        dg_connection.finish()
        final_text = " ".join(sentences_added)
        tdiff = time()-stime
        logging.info("Time taken for stt deepgram: %s"%tdiff)
        return final_text
    except Exception as e:
        logging.WARN(f"Could not open socket: {e}")
        return
