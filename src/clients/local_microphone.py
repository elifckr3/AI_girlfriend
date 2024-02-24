import io
import os
import openai
import sounddevice as sd
import soundfile as sf
import logging

import speech_recognition as sr
from clients.openai import OpenAiClient
from time import time
from utils import timeit

from system_conf import (
    get_conf,
    LOCAL_RECORDING_PAUSE_THRESHOLD,
    LOCAL_RECORDING_NON_SPEAKING_DURATION,
    LOCAL_RECORDING_PHRASE_THRESHOLD,
    LOCAL_RECORDING_ENERGY_ADJUSTMENT_DURATION,
    LOCAL_RECORDING_ENERGY_THRESHOLD,
    LOCAL_RECORDING_DYNAMIC_ENERGY_THRESHOLD,
    LOCAL_RECORDING_DYNAMIC_ENERGY_ADJUSTMENT_DAMPING,
)

CURR_DIR = os.getcwd()


def local_record_online_transcribe():
    """
    Start point to bring STT locally and lower latency - please read all _speech_recon_lib too

    # NOTE big question here = what is the pass audio bytes to transcribe strategy ?
    # is it best to sample the samples ad infinitum ?
    # then get downstream models to tell us when entropy_threshold is reached necessitating a response
    # this is both latency and natural conversation feel


    # NOTE
    # one idea to discretely sample audio - e.g. 200Hz and then slide window over the disretization and algorithmically determine process strategies

    # the simplest process strategy is a line break and punctuation, but is not necessarily the end

    # assemblyAI will solve the line break and punctuation problem - but not the entropy threshold problem

    # buffer = source.stream.read(source.CHUNK) -> capturing the sound from AudioSource

    """

    recording = _speech_recon_lib()

    # logging.debug(f"ADJHAGD. {recording}")

    transcription = OpenAiClient().stt(recording)

    return transcription


# @timeit.PROFILE
def _speech_recon_lib():
    """
    Simple speech recognition library. Detects phrases based on energy of what means silence and bunch of duration params
        - pause_threshold
        - non_speaking_duration
        - phrase_threshold
        - energy_threshold (reference for silence) equations belows

    Useful to study the fundamentals of phrase discretization of audio speech.

    See below for full details:
    """
    r = sr.Recognizer()

    r.pause_threshold = get_conf(LOCAL_RECORDING_PAUSE_THRESHOLD)
    r.non_speaking_duration = get_conf(LOCAL_RECORDING_NON_SPEAKING_DURATION)
    r.phrase_threshold = get_conf(LOCAL_RECORDING_PHRASE_THRESHOLD)
    r.energy_threshold = get_conf(LOCAL_RECORDING_ENERGY_THRESHOLD)
    r.dynamic_energy_threshold = get_conf(LOCAL_RECORDING_DYNAMIC_ENERGY_THRESHOLD)
    r.dynamic_energy_adjustment_damping = get_conf(
        LOCAL_RECORDING_DYNAMIC_ENERGY_ADJUSTMENT_DAMPING
    )

    with sr.Microphone() as source:
        logging.debug("Listen start...")
        # NOTE TODO this costs by default 1 second at minimum 0.5 seconds
        # should be on a seperate thread constantly sampling on periods of background noise # TODO - define this
        # once sampled then dynamically adjust sr.Recognizer()'s self.energy_threshold < # NOTE
        r.adjust_for_ambient_noise(
            source, duration=get_conf(LOCAL_RECORDING_ENERGY_ADJUSTMENT_DURATION)
        )
        # self.energy_threshold = self.energy_threshold * damping + target_energy * (1 - damping)
        # target_energy = energy * self.dynamic_energy_ratio
        # damping = self.dynamic_energy_adjustment_damping ** seconds_per_buffer
        # seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
        # NOTE w/ DEFAULTS of
        # self.dynamic_energy_adjustment_damping = 0.15
        # self.energy_threshold = 300  # minimum audio energy to consider for recording

        logging.debug("Recording.")

        # NOTE .listen()
        # - Records a single phrase from ``source`` (an ``AudioSource`` instance) into an ``AudioData`` instance, which it returns.
        # - waits until audio has an energy above ``recognizer_instance.energy_threshold`` (the user has started speaking)
        # - and then recording until it encounters ``recognizer_instance.pause_threshold`` seconds of non-speaking or there is no more audio input.
        # - ending silence is not included.
        # NOTE w/ DEFAULTS of
        # self.pause_threshold = 0.8  # seconds of non-speaking audio before a phrase is considered complete
        # self.non_speaking_duration = 0.5  # seconds of non-speaking audio to keep on both sides of the recording
        # self.phrase_threshold = 0.3  # minimum seconds of speaking audio before we consider the recording a phrase
        data = r.listen(source)
        # TODO test snowboy hotword engine performance and generalizeable setup
        # - ``snowboy_configuration`` parameter allows integration with `Snowboy <https://snowboy.kitt.ai/>`__
        # - an offline, high-accuracy, power-efficient hotword recognition engine.
        # - When used, this function will pause until Snowboy detects a hotword, after which it will unpause.
        # - tuple of the form ``(SNOWBOY_LOCATION, LIST_OF_HOT_WORD_FILES)``,
        # - where ``SNOWBOY_LOCATION`` is the path to the Snowboy root directory
        # - ``LIST_OF_HOT_WORD_FILES`` is a list of paths to Snowboy hotword configuration files (`*.pmdl` or `*.umdl` format).

        recording = data.get_wav_data()
        # NOTE - data
        # Audio data is sequence of audio samples representing bytes - PCM WAV format
        # sample-width: each sample, in bytes, respresent a single audio sample
        # sample-rate: samples of audio per second (Hz)
        # def __init__(self, frame_data, sample_rate, sample_width)
        # recording.get_wav_data(): PCM WAV -> WAV

        logging.debug("Listen stop.")

    return recording


def _record_audio_fixed():
    """
    Most basic and manual way to record audio using the sounddevice library.

    Shows the most basic way to fix duration - leading to the ultimate question being solved

    What is the nature of the callback manifesting the data discritization strategies
    """

    # NOTE no point to enable config for this as this is only for educational purposes
    # educaion on the nature of how to solve the listen problem
    duration = 5  # seconds
    fs = 44100

    logging.debug("Recording...")

    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype="int16")

    sd.wait()

    logging.debug("Recording complete.")

    return recording
