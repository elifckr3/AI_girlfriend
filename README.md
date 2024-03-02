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

<b>Accessibility:</b> Easy-to-understand codebase and well-documented features for all skill levels.

<b>Innovation:</b>  A playground for your most creative ideas to take shape and evolve.

<b>Community:</b>  A supportive and collaborative space where questions are welcomed, and knowledge is shared.

<b>Open-Source:</b>  We're committed to being open-source and empowering people to create the technology they want.


## Project Architecture Overview
Work in Progress Technical Architecture: https://docs.google.com/document/d/1yp--z4FfSuFPeo2WAHFhK2l-vD85TCIgqeVTpSUI5xE/edit#heading=h.hug0acjqpx7j

<b>The Heart of OpenHome:</b> A Dynamic, Ever-Evolving Core At the core of OpenHome is a unique and powerful loop that continuously evolves the personality of your smart speaker. This isn't just about responding to commands; it's about creating an experience that's deeply personal and constantly refreshing. Every interaction with OpenHome is a step towards a more nuanced and tailored experience.

<b>How It Works:</b> The Magic Behind the Scenes Dynamic Personality: OpenHome begins with a foundation of diverse personalities, each ready to provide a distinct interaction experience. But here's the twist – these personalities aren't static. They evolve with every conversation, adapting to your preferences, your style, and your world.

<b>Seamless Interactions:</b> Through our advanced audio module, OpenHome listens and understands, converting your spoken words into a digital format that it can process. This is where the conversation begins.

<b>Smart Processing:</b> Leveraging the power of OpenAI's GPT model, OpenHome intelligently processes your input. Whether it's a command, a query, or casual chatter, the system is designed to understand and respond in the most relevant way.

<b>Personalized Responses:</b> The heart of OpenHome beats in its ability to learn from each interaction. Using our DynamicPersonalityConstructor, the system crafts responses that aren't just accurate but also personalized, taking into account your history and preferences.

<b>Audible Magic:</b> What good is a smart response if it can't be enjoyed? Our text-to-speech module brings the conversation to life, turning text responses into natural, fluent speech.

Sure, here's the complete markdown for your GitHub README.md file:


# OpenHome Installation Guide

Welcome to OpenHome! We're excited to have you join us on this journey to create an open-source AI smart speaker that learns and grows with you. Whether you're here to build, learn, or contribute, we've got you covered with this step-by-step guide to get OpenHome running on your system.

## Prerequisites

Before you start, ensure you have the following installed on your system:

- **Python 3.11**: The preferred Python version for OpenHome.
- **Homebrew** (macOS users): For installing Python and other dependencies.
- **PDM (Python Dependency Manager)**: For managing Python packages.

## Installation Steps

### For macOS Users

1. **Install Homebrew** (if you haven't already):
   ```sh
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python 3.11** using Homebrew:
   ```sh
   brew install python@3.11
   ```

3. **Install PDM**:
   ```sh
   curl -sSL https://pdm.fming.dev | python3 -
   ```

4. **Update your PATH**:
   Add PDM to your PATH by inserting the following line into your `.zshrc` or `.bash_profile`:
   ```sh
   export PATH=/Users/your-username/.local/bin:$PATH
   ```
   Replace `your-username` with your macOS username.

5. **Install MPV** for media playback:
   ```sh
   brew install mpv
   ```

### For Linux Users

1. **Ensure Python 3.11 is installed**:
   If your Python version is below 3.11, add the deadsnakes PPA and install Python 3.11:
   ```bash
   sudo add-apt-repository ppa:deadsnakes/ppa
   sudo apt install python3.11
   ```

2. **Install curl** (if not installed):
   ```bash
   sudo apt install curl
   ```

3. **Install PDM**:
   ```bash
   curl -sSL https://pdm-project.org/install-pdm.py | python3 -
   ```

4. **Update your PATH**:
   ```bash
   echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
   source ~/.bashrc
   ```

5. **Fix PyAudio errors** (if any after running `pdm install`):
   ```bash
   sudo apt install python3.11-dev build-essential gcc
   pdm install
   ```

6. **Install MPV** for media playback:
   ```bash
   sudo apt-get install mpv
   ```

## Install Dependencies

Run the following command in the OpenHome directory to install required dependencies:

```bash
pdm install
```

## Running OpenHome

To start OpenHome, run:

```bash
pdm run main
```

### Flags

- `--debug`: Show all logs.
- `--default`: Load the preset/default personality.
- `--config`: Toggle prompts to update system configuration.
- `--speech-off`: Disable speech output, with results visible in logs.
- `--cold-start`: Clear previous history for a fresh conversation start.

Example:

```bash
pdm run main --default
```

For a full list of flags, run:

```bash
pdm run main --help
```

### Error Handling

If you encounter errors, reset the database and upload environment variables:

```bash
pdm run reset_db
pdm run upload_env
```

## Building a Capability

To add new capabilities to OpenHome:

1. Copy and modify `template.py` in the `capabilities/` folder.
2. Register the capability with its function call, as shown below:

```python
class TimerCapability(Capability):
    @classmethod
    def register_capability(cls):
        return cls(unique_name="timer", hotwords=["call", "timer"])

    def call(self):
        # Your code here
```
