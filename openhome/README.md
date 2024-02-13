# OpenHome

Prototype a Voice Assistant

## Project Overview
Development of a Python-Based Local Voice Assistant with OpenAI Whisper and LLM Integration.
The core functionality involves a wake word activation, speech-to-text conversion, 
interaction with an LLM API, and a text-to-speech output to vocalize the response.



## Install and configure

To get the project running locally first create and spin up a conda environment as follows:

```
conda create -n openhome python=3.10
conda activate openhome
```

Next install the required dependencies.

### Install dependencies

To install the required dependencies, run the following command:
```
python -m pip install -r requirements.txt 
```
Also install following:

```
sudo apt-get install libportaudio2
sudo apt install ffmpeg
sudo apt-get install portaudio19-dev
```
```
pip install PyAudio
```
## How to run the main pipeline?

To run the main pipeline, run the following command:

```
python main.py -p <Enter personality>
```

- `<Enter personality>`: Pass your desired personality

`Note: If you enter a name that do not exists in our personality list you will be given list of personalities to choose one from them.`