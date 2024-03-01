# OpenHome

👋 Hello, world

I'm thrilled to introduce you to OpenHome - an open-source AI smart speaker project.

<a href='https://openhome.xyz/' target='_blank'>
    <img src='https://i.postimg.cc/02Yq2NgB/OpenHome.png' border='0' alt='OpenHome' width='250' height='250'/>
</a>

<b>OpenHome Vision:</b> Imagine a world where your smart speaker is your companion. It adapts, learns, and grows with you. That's what we're building with OpenHome – a groundbreaking open-source AI smart speaker project designed to push the boundaries of imagination

At OpenHome, we believe in the power of community-driven development to create technology that's not only advanced but also accessible. Whether you're a seasoned developer, a curious beginner, or somewhere in between, OpenHome is your opportunity to contribute to an AI smart speaker that's as simple to get started with as it is powerful.

<b>Our Mission:</b> To build an AI smart speaker that's cutting edge, open, customizable, and versatile for every user. We're not just creating a product, we're creating an ecosystem where every idea counts and is integrated to one giant super brain.

# What sets OpenHome apart? Here, you'll find:

<li><b>Accessibility:</b></li> Easy-to-understand codebase and well-documented features for all skill levels.
<li><b>Innovation:</b></li>  A playground for your most creative ideas to take shape and evolve.
<li><b>Community:</b></li>  A supportive and collaborative space where questions are welcomed, and knowledge is shared.
<li><b>Open-Source:</b></li>  We're committed to being open-source and empowering people to create the technology they want.


## Project Architecture Overview
Work in Progress Technical Architecture: https://docs.google.com/document/d/1PInWfbWBY9571Hq4R0nf5Uj01agy6YVXV2UTBonUc4A/edit

<b>The Heart of OpenHome:</b> A Dynamic, Ever-Evolving Core At the core of OpenHome is a unique and powerful loop that continuously evolves the personality of your smart speaker. This isn't just about responding to commands; it's about creating an experience that's deeply personal and constantly refreshing. Every interaction with OpenHome is a step towards a more nuanced and tailored experience.

<b>How It Works:</b> The Magic Behind the Scenes Dynamic Personality: OpenHome begins with a foundation of diverse personalities, each ready to provide a distinct interaction experience. But here's the twist – these personalities aren't static. They evolve with every conversation, adapting to your preferences, your style, and your world.

<b>Seamless Interactions:</b> Through our advanced audio module, OpenHome listens and understands, converting your spoken words into a digital format that it can process. This is where the conversation begins.

<b>Smart Processing:</b> Leveraging the power of OpenAI's GPT model, OpenHome intelligently processes your input. Whether it's a command, a query, or casual chatter, the system is designed to understand and respond in the most relevant way.

<b>Personalized Responses:</b> The heart of OpenHome beats in its ability to learn from each interaction. Using our DynamicPersonalityConstructor, the system crafts responses that aren't just accurate but also personalized, taking into account your history and preferences.

<b>Audible Magic:</b> What good is a smart response if it can't be enjoyed? Our text-to-speech module brings the conversation to life, turning text responses into natural, fluent speech.



## Install and configure

To get the project running locally install pdm using python3.11.

Check your python version if it is below 3.11 run these two python related commands else you can directly run the curl command.

To add python repo to your system run the folowing deadsnakes command.

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
```

After adding python repo to your system install python 3.11.


```bash
sudo apt install python3.11
```

You can install `curl` using the following command if it is not already installed.

```bash
sudo apt  install curl
```

```bash
curl -sSL https://pdm-project.org/install-pdm.py | python3 -
```

After install run the prompted command

```bash
export PATH=/Users/your-username/.local/bin:$PATH
```

Next install the required dependencies.


### Install dependencies

To install the required dependencies, run the following command:

```bash
pdm install
```
After running `pdm install` command if you encounter the following error.

![Error log](/assets/pyAudio_error.png?raw=true "PyAudio Error")

Run the following command to fix PyAudio error.

```bash
sudo apt install python3.11-dev build-essential gcc
```
And again run.

```bash
pdm install
```

You can also use homebrew to install these modules. brew install ffmpeg, portaudio, etc

## How to install mpv?

For linux
```bash
apt-get install mpv
```
For Mac
```bash
brew install mpv
```

For Windows
- https://mpv.io/installation/


## How to run the main pipeline?

To run the main pipeline, run the following command:

```bash
pdm run main 
```

Here are some `FLAGS` you can use.

`--debug`: Shows all the logs.

`--default`: Load preset/default personality.

`--config`: Toggle prompts to update system configuration.

`--speech-off`:  Disables speech output, results are visible in the logs.

`--cold-start`: Clears previous history to provide a fresh start for conversation.

You can use `FLAGS` like this:

```bash
pdm run main --default
```

To check all `FLAGS`

```bash
pdm run main --help
```

#### Error handling in main pipeline

If you encounter any error during `pdm run main`, run the following:

```bash
pdm run reset_db
```
```bash
pdm run upload_env
```

## How to build a capability?

Copy and paste a new version of template.py in the capabilities/ folder.

Register the capability as follows alongside it's function call

#TODO 
- [ ] test tool
- [ ] unique hotword matching
- [ ] I/O passing to caller

```python
class TimerCapability(Capability):
    @classmethod
    def register_capability(cls):
        return cls(unique_name="timer", hotwords=["call", "timer"])

    def call(self):
        time.sleep(2)
```