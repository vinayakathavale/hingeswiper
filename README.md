# HingeSwiper

A Python automation tool for the Hinge dating app that uses GPT to generate personalized comments while swiping.

## Features

- Automates profile swiping on Hinge
- Generates personalized comments using GPT
- Connects to Android devices via ADB
- Smart profile analysis and interaction

## Requirements

- Python 3.x
- Android device with USB debugging enabled
- OpenAI API key
- Hinge app installed on the Android device

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

3. Connect your Android device and enable USB debugging

4. Run the automation:
```bash
uv run main.py
```

## License

MIT License