
# OpenAI Whisper
## Overview
OpenAI Whisper is a cloud-based service for audio transcription and translation. It provides a convenient and efficient way to transcribe audio files into text and translate them into multiple languages. This README.md file provides an overview of the OpenAI Whisper codebase, including its functionalities, setup instructions, and usage guidelines.
## Features

- Audio Transcription: Convert audio files into text transcripts.
- Translation: Translate text transcripts into multiple languages.
- Media Conversion: Convert audio files into different formats (e.g., MP3).
- Integration: Integration with AWS services for media processing and storage.
- Real-time Updates: Push notifications for job status updates using Pusher.
## Prerequisites

Before using OpenAI Whisper, ensure you have the following prerequisites installed and configured:

- Python 3.9+
- AWS Account with necessary permissions and credentials configured
- Pusher Account for real-time notifications
- Required Python packages (specified in requirements.txt)
## Installation

To use this solution, make sure you have the required libraries installed. You can install them using pip:
```bash
pip install -r requirements/production.txt
```

## Setup Instructions
- Clone the OpenAI Whisper repository to your local machine.
- Install dependencies using `pip install -r requirements/production.txt`.
- Configure AWS credentials and Pusher credentials using environment variables or a .env file.
- Ensure necessary AWS services (e.g., S3, SQS, MediaConvert) are set up and accessible.
- Customize configuration variables in the code according to your requirements.
## Usage
- Ensure all setup steps are completed successfully.
- Run the `worker.py` file to start processing audio files.
- Monitor job status and progress through real-time updates using Pusher.
- Retrieve processed files from the specified `S3` bucket or download links provided.
## Authors

- [@farankhalid](https://www.github.com/farankhalid)
- [@aromabear](https://github.com/aromabear)
- [@Tabed23](https://github.com/Tabed23)



