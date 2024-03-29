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
    while True:
        try:
            # TODO new dg connection needs to be optimized 
            logging.info('starting mic...')
            api_key = os.environ.get(DEEPGRAM_KEY)
            # Open a microphone stream on the default input device
            microphone: Microphone
            dg_connection: DeepgramClient
            deepgram = DeepgramClient(api_key)
            dg_connection = deepgram.listen.live.v("1")
            sentence_buffer = ''
            sentences_added = []
            LISTENING = False
            def on_message(self, result, **kwargs):
                nonlocal sentence_buffer
                nonlocal sentences_added
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) == 0:
                    return
                if len(sentence) < len(sentence_buffer):
                    logging.debug(f"speaker: {sentence_buffer}")
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
                nonlocal microphone
                nonlocal LISTENING
                logging.debug(f"speaker: {sentence_buffer}")
                sentences_added.append(sentence_buffer)
                logging.debug('stopped listening...')
                # print(f"\n\n{utterance_end}\n\n")
                microphone.finish()
                LISTENING = False

                return 

            def on_error(self, error, **kwargs):
                print(f"\n\n{error}\n\n")

            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            # dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
            # dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
            dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)
            dg_connection.on(LiveTranscriptionEvents.Error, on_error)

            options: LiveOptions = LiveOptions(
                model="nova-2-general",
                punctuate=True,
                language="en-US",
                encoding="linear16",
                channels=1,
                sample_rate=16000, # To get UtteranceEnd, the following must be set:
                interim_results=True,
                utterance_end_ms="1000",
                vad_events=True,
                endpointing=100
            )
            dg_connection.start(options)

            logging.info('listening...')
            # Open a microphone stream on the default input device
            microphone: Microphone = Microphone(dg_connection.send)

            # start microphone
            microphone.start()
            LISTENING = True

            while LISTENING:
                # if not microphone.is_active():
                #     break
                sleep(0.1)

            dg_connection.signal_exit()
            dg_connection.finish()

            final_text = " ".join(sentences_added)

            return final_text
        except Exception as e:
            logging.error("Could not open socket, Make sure your mic is connected!")
            sleep(1)
            logging.info(f"Retrying Deepgram Connection!")
            continue
