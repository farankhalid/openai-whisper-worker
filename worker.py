import json
import boto3
import os
import subprocess
import zipfile
import time
import shutil
import logging
import pysrt
import traceback

from pusher import Pusher
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to desired log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    filename="logging.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def translate_doc(file_path, target_language):
    """
    Translate the subtitles in an SRT (SubRip) file to the specified target language and save as a new SRT file.

    Parameters:
    - srt_file_path (str): The file path to the input SRT file for translation.
    - target_language (str): The language code (e.g., "fr" for French) to which the subtitles should be translated.

    Returns:
    - None

    Raises:
    - FileNotFoundError: If the specified SRT file 'srt_file_path' is not found.
    - ValueError: If 'srt_file_path' does not have a valid '.srt' file extension.
    - Exception: Any other exceptions raised during the translation or file saving process.

    Example:
    >>> translate_doc("input.txt", "fr")

    This function reads the content of an SRT file, translates each subtitle line using the 'translate_document' function,
    and then saves the translated subtitles as a new SRT file with the target language code appended to the filename.

    Note:
    - Ensure that your AWS credentials and the 'translate_document' function are properly configured to use this function.
    - The 'target_language' parameter should be a valid language code supported by the 'translate_document' function.
    """

    # Read the content of the SRT file
    with open(file_path, "rb") as file:
        file_content = file.read()

    # Translate the content using AWS Translate
    translated_content = translate_document(file_content, target_language)

    # Save the translated content to a new SRT file
    translated_srt_path = file_path.replace(".txt", f"_{target_language}.txt")
    with open(translated_srt_path, "wb") as file:
        file.write(translated_content)


def translate_document(content, target_language):
    """
    Translate a text document from its detected source language to the specified target language using AWS Translate.

    Parameters:
    - content (str): The content of the document to be translated.
    - target_language (str): The language code (e.g., "fr" for French) of the desired translation.

    Returns:
    - str: The translated content of the document in the specified target language.

    Raises:
    - botocore.exceptions.NoCredentialsError: If AWS credentials are not properly configured.
    - botocore.exceptions.ParamValidationError: If invalid parameters are provided.
    - botocore.exceptions.ClientError: If an error occurs during the translation process.

    Example:
    >>> translated_content = translate_document("Hello, world!", "fr")
    >>> print(translated_content)
    "Bonjour, le monde!"

    This function uses the AWS Translate service to automatically detect the source language of the input document
    and then translate it to the specified target language. The translated content is returned as a string.

    Note:
    - Ensure that your AWS credentials and the AWS SDK (Boto3) are properly configured to use this function.
    - The 'target_language' parameter should be a valid language code supported by the AWS Translate service.
    """

    translate = boto3.client("translate", region_name="us-east-1")

    response = translate.translate_document(
        SourceLanguageCode="auto",
        TargetLanguageCode=target_language,
        TerminologyNames=[],
        Document={"Content": content, "ContentType": "text/plain"},
    )

    return response["TranslatedDocument"]["Content"]


def translate_srt(srt_path, target_language):
    """
    Translate the subtitles in an SRT (SubRip) file to the specified target language and save as a new SRT file.

    Parameters:
    - srt_path (str): The file path to the input SRT file for translation.
    - target_language (str): The language code (e.g., "fr" for French) to which the subtitles should be translated.

    Returns:
    - None

    Raises:
    - FileNotFoundError: If the specified SRT file 'srt_path' is not found.
    - ValueError: If 'srt_path' does not have a valid '.srt' file extension.
    - Exception: Any other exceptions raised during the translation process, including AWS Translate errors.

    Example:
    >>> translate_srt("input.srt", "fr")

    This function uses the 'pysrt' library to load an SRT file, translates each subtitle line using the 'translate_text' function,
    and then saves the translated subtitles as a new SRT file with the target language code appended to the filename.

    Note:
    - Ensure that your AWS credentials and the 'translate_text' function are properly configured to use this function.
    - The 'target_language' parameter should be a valid language code supported by the 'translate_text' function.
    - Make sure 'pysrt' and 'boto3' (for AWS Translate) are installed in your Python environment.
    """

    # Load SRT file using pysrt
    subs = pysrt.open(srt_path, encoding="utf-8")

    # Translate each subtitle line
    for sub in subs:
        translated_text = translate_text(sub.text, target_language)
        sub.text = translated_text

    # Save translated SRT
    translated_srt_path = srt_path.replace(".srt", f"_{target_language}.srt")
    subs.save(translated_srt_path, encoding="utf-8")


def translate_text(text, target_language):
    """
    Translates input text from its detected source language to the specified target language.

    Parameters:
    - text (str): The text to be translated.
    - target_language (str): The language code (e.g., "en" for English) of the desired translation output.

    Returns:
    - str: The translated text in the specified target language.

    Raises:
    - botocore.exceptions.NoCredentialsError: If AWS credentials are not properly configured.
    - botocore.exceptions.ParamValidationError: If invalid parameters are provided.
    - botocore.exceptions.ClientError: If an error occurs during the translation process.

    Example:
    >>> translated_text = translate_text("Hello, world!", "fr")
    >>> print(translated_text)
    "Bonjour, le monde!"

    This function uses the AWS Translate service to automatically detect the source language of the input text
    and then translate it to the specified target language. The translated text is returned as a string.

    Note:
    - Ensure that your AWS credentials and the AWS SDK (Boto3) are properly configured to use this function.
    - The 'target_language' parameter should be a valid language code supported by the AWS Translate service.
    """

    translate = boto3.client("translate", region_name="us-east-1")

    response = translate.translate_text(
        Text=text, SourceLanguageCode="auto", TargetLanguageCode=target_language
    )

    return response["TranslatedText"]


def translate_txt(txt_file_path, target_language):
    translated_lines = []  # Store translated lines

    with open(txt_file_path, "r") as file:
        for line in file:
            translated_line = translate_text(line.strip(), target_language)
            translated_lines.append(translated_line)

    translated_txt = "\n".join(translated_lines)

    translated_txt_path = txt_file_path.replace(".txt", f"_{target_language}.txt")

    with open(translated_txt_path, "w") as translated_file:
        translated_file.write(translated_txt)


def create_transcode_job(input_key, output_key):
    """
    Create a transcoding job using AWS Elemental MediaConvert to convert media files.

    Parameters:
    - input_key (str): The S3 object key for the input media file.
    - output_key (str): The desired S3 object key for the output transcoded file.

    Returns:
    - str: The unique identifier (ID) of the created MediaConvert job.

    Raises:
    - Exception: Any errors that occur during the MediaConvert job creation.

    Example:
    >>> create_transcode_job("input/video.mp4", "output/audio.mp3")

    This function configures and submits a transcoding job to AWS Elemental MediaConvert, converting the specified input
    media file to the desired output format and storing it in the specified S3 bucket location. The function returns the
    unique job ID for tracking and monitoring the job's progress.

    Note:
    - Ensure that your AWS credentials and MediaConvert settings (specified in environment variables) are properly configured.
    - The 'input_key' and 'output_key' parameters should be valid S3 object keys.
    - Customize the settings in the 'job_settings' dictionary to meet your specific transcoding requirements.
    - AWS Elemental MediaConvert should be set up and available in your AWS account.
    """

    mediaconvert_client = boto3.client(
        "mediaconvert",
        endpoint_url=os.environ.get("AWS_MEDIACONVERT_ENDPOINT_URL"),
        region_name=os.environ.get("AWS_REGION_NAME"),
    )

    # Specify the input and output settings for the job
    job_settings = {
        "Settings": {
            "Inputs": [
                {
                    "TimecodeSource": "ZEROBASED",
                    "VideoSelector": {},
                    "AudioSelectors": {
                        "Audio Selector 1": {"DefaultSelection": "DEFAULT"}
                    },
                    "FileInput": input_key,
                }
            ],
            "OutputGroups": [
                {
                    "Name": "File Group",
                    "OutputGroupSettings": {
                        "Type": "FILE_GROUP_SETTINGS",
                        "FileGroupSettings": {
                            "Destination": os.path.join(
                                os.environ.get("MEDIACONVERT_BUCKET"),
                                "transcoder_outputs",
                                output_key,
                            )
                        },
                    },
                    "Outputs": [
                        {
                            "AudioDescriptions": [
                                {
                                    "CodecSettings": {
                                        "Codec": "MP3",
                                        "Mp3Settings": {
                                            "RateControlMode": "CBR",
                                            "SampleRate": 22050,
                                            "Bitrate": 16000,
                                            "Channels": 1,
                                        },
                                    },
                                    "AudioSourceName": "Audio Selector 1",
                                }
                            ],
                            "ContainerSettings": {"Container": "RAW"},
                            "Extension": "mp3",
                        }
                    ],
                    "CustomName": "mediaconvert-outputs",
                }
            ],
            "TimecodeConfig": {"Source": "ZEROBASED"},
        },
        "Role": os.environ.get("MEDIACONVERT_ROLE_ARN"),
        "Queue": os.environ.get("MEDIACONVERT_QUEUE_ARN"),
        "HopDestinations": [
            {
                "Queue": os.environ.get("MEDIACONVERT_HOP_QUEUE_ARN"),
                "WaitMinutes": 5,
            }
        ],
    }

    # Create the mediaconvert job
    response = mediaconvert_client.create_job(**job_settings)

    return response["Job"]["Id"]


class MediaConvertJobError(Exception):
    pass


def custom_mediaconvert_waiter(job_id, max_attempts=100, delay_seconds=5):
    """
    Wait for the completion of an AWS Elemental MediaConvert job and handle potential errors.

    Parameters:
    - job_id (str): The unique identifier (ID) of the MediaConvert job to monitor.
    - max_attempts (int): The maximum number of attempts to check the job status before giving up (default is 100).
    - delay_seconds (int): The number of seconds to wait between each status check attempt (default is 5).

    Returns:
    - None

    Raises:
    - MediaConvertJobError: If the MediaConvert job encounters an error during processing.
    - Exception: Any other errors that occur during the status check process.

    Example:
    >>> custom_mediaconvert_waiter("abcdefg12345")

    This function monitors the progress of an AWS Elemental MediaConvert job with the specified 'job_id'. It checks the
    status of the job repeatedly, with a delay between attempts, until the job is either marked as "COMPLETE" or
    "ERROR." If the job encounters an error, it raises a 'MediaConvertJobError' and logs an error message.

    Note:
    - Ensure that your AWS credentials and MediaConvert settings (specified in environment variables) are properly configured.
    - Customize the 'max_attempts' and 'delay_seconds' parameters based on your desired waiting behavior.
    - AWS Elemental MediaConvert should be set up and available in your AWS account.
    """

    mediaconvert_client = boto3.client(
        "mediaconvert",
        endpoint_url=os.environ.get("AWS_MEDIACONVERT_ENDPOINT_URL"),
        region_name=os.environ.get("AWS_REGION_NAME"),
    )

    for _ in range(1, max_attempts + 1):
        response = mediaconvert_client.get_job(Id=job_id)
        status = response["Job"]["Status"]

        if status == "COMPLETE":
            return

        if status == "ERROR":
            logging.error(f"MediaConvert job {job_id} encountered an error.")
            raise MediaConvertJobError(
                f"MediaConvert job {job_id} encountered an error."
            )

        # Wait for the specified delay before the next attempt
        time.sleep(delay_seconds)


def initialize_pusher():
    pusher = Pusher(
        app_id=os.environ.get("PUSHER_APP_ID"),
        key=os.environ.get("PUSHER_KEY"),
        secret=os.environ.get("PUSHER_SECRET"),
        cluster=os.environ.get("PUSHER_CLUSTER"),
        ssl=True,
    )

    return pusher


def is_file_size_within_limit(file_path, max_size_bytes):
    """
    Check if the size of a file is within a specified limit.

    Parameters:
    - file_path (str): The path to the file to check.
    - max_size_bytes (int): The maximum allowed file size in bytes.

    Returns:
    - bool: True if the file size is within the limit, False otherwise.
    """
    file_size = os.path.getsize(file_path)
    return file_size <= max_size_bytes


def trigger_pusher_event(channel, event_name, data):
    pass


def download_file_s3(source_key, local_path):
    pass


def upload_file_s3(local_path, destination_key):
    pass


def process_message(message):
    pass


def process_job():
    language_codes = [
        "af",
        "sq",
        "am",
        "ar",
        "hy",
        "az",
        "bn",
        "bs",
        "bg",
        "ca",
        "zh",
        "zh-TW",
        "hr",
        "cs",
        "da",
        "fa-AF",
        "nl",
        "en",
        "et",
        "fa",
        "tl",
        "fi",
        "fr",
        "fr-CA",
        "ka",
        "de",
        "el",
        "gu",
        "ht",
        "ha",
        "he",
        "hi",
        "hu",
        "is",
        "id",
        "ga",
        "it",
        "ja",
        "kn",
        "kk",
        "ko",
        "lv",
        "lt",
        "mk",
        "ms",
        "ml",
        "mt",
        "mr",
        "mn",
        "no",
        "ps",
        "pl",
        "pt",
        "pt-PT",
        "pa",
        "ro",
        "ru",
        "sr",
        "si",
        "sk",
        "sl",
        "so",
        "es",
        "es-MX",
        "sw",
        "sv",
        "ta",
        "te",
        "th",
        "tr",
        "uk",
        "ur",
        "uz",
        "vi",
        "cy",
    ]

    aws_translate = None
    response = None
    pusher = initialize_pusher()

    try:
        # Initialize SQS client
        sqs = boto3.client(
            "sqs",
            region_name=os.environ.get("AWS_REGION_NAME"),
        )
    except Exception:
        logging.error(f"An error occurred: {traceback.format_exc()}")
        return

    try:
        # Initialize S3 client
        s3 = boto3.client(
            "s3",
            region_name=os.environ.get("AWS_REGION_NAME"),
        )
    except Exception:
        logging.error(f"An error occurred: {traceback.format_exc()}")
        return

    while True:
        try:
            # Poll for a single message
            response = sqs.receive_message(
                QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                MaxNumberOfMessages=1,
                WaitTimeSeconds=5,
            )
        except Exception:
            logging.error(f"An error occured: {traceback.format_exc()}")

        if "Messages" in response:
            message = json.loads(response["Messages"][0]["Body"])
            receipt_handle = response["Messages"][0]["ReceiptHandle"]

            file_uri = message["file_uri"]
            language = message["language"]
            sub_language = message["sub_language"]
            job_id = message["pusher_channel"]

            logging.info(f"file_uri: {file_uri}")
            logging.info(f"language: {language}")
            logging.info(f"sub_language: {sub_language}")
            logging.info(f"job_id: {job_id}")

            # Process the message
            logging.info(f'Processing message: {message["pusher_channel"]}')

            try:
                logging.info("Creating mediaConvert job...")
                mc_job_id = create_transcode_job(
                    input_key=file_uri,
                    output_key=job_id,
                )
                logging.info("MediaConvert job created successfully.")
            except Exception as e:
                logging.error(f"An error occurred: {traceback.format_exc()}")
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 500,
                        "message": str(e),
                        "progress": 10,
                    },
                )
                try:
                    logging.info(f"Deleting message from the queue.")
                    # Delete the message after processing is complete
                    sqs.delete_message(
                        QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                        ReceiptHandle=receipt_handle,
                    )
                    logging.info("Message deleted successfully.")
                except Exception as e:
                    logging.error(f"An error occurred: {traceback.format_exc()}")
                    pusher.trigger(
                        job_id,
                        "job-update",
                        {
                            "statusCode": 500,
                            "message": str(e),
                            "progress": 10,
                        },
                    )
                return

            try:
                logging.info("Waiting for mediaConvert job to complete.")
                custom_mediaconvert_waiter(mc_job_id)
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 200,
                        "message": "Downscaled the audio sample successfully.",
                        "progress": 20,
                    },
                )
                logging.info(f"MediaConvert job {mc_job_id} completed successfully.")
            except Exception as e:
                logging.error(f"An error occurred: {traceback.format_exc()}")
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 500,
                        "message": str(e),
                        "progress": 20,
                    },
                )
                try:
                    logging.info(f"Deleting message from the queue.")
                    # Delete the message after processing is complete
                    sqs.delete_message(
                        QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                        ReceiptHandle=receipt_handle,
                    )
                    logging.info("Message deleted successfully.")
                except Exception as e:
                    logging.error(f"An error occurred: {traceback.format_exc()}")
                    pusher.trigger(
                        job_id,
                        "job-update",
                        {
                            "statusCode": 500,
                            "message": str(e),
                            "progress": 20,
                        },
                    )
                return

            download_file_name = "".join([job_id, ".mp3"])
            output_file_path = os.path.join(
                os.environ.get("DATA_DIR"), "data", download_file_name
            )

            try:
                # Download the file from S3 and save it locally
                s3.download_file(
                    os.environ.get("AWS_STORAGE_BUCKET_NAME"),
                    os.path.join(
                        os.environ.get("OUTPUT_KEY_PREFIX"), download_file_name
                    ),
                    output_file_path,
                )
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 200,
                        "message": "Analyzing your audio file.",
                        "progress": 30,
                    },
                )
                logging.info("File downloaded successfully...")
            except Exception as e:
                logging.error(f"An error occurred: {traceback.format_exc()}")
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 500,
                        "message": str(e),
                        "progress": 30,
                    },
                )
                try:
                    logging.info(f"Deleting message from the queue.")
                    # Delete the message after processing is complete
                    sqs.delete_message(
                        QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                        ReceiptHandle=receipt_handle,
                    )
                    logging.info("Message deleted successfully.")
                except Exception as e:
                    logging.error(f"An error occurred: {traceback.format_exc()}")
                    pusher.trigger(
                        job_id,
                        "job-update",
                        {
                            "statusCode": 500,
                            "message": str(e),
                            "progress": 30,
                        },
                    )
                return

            logging.info(
                f"File '{job_id}'.mp3 downloaded from {os.environ.get('AWS_STORAGE_BUCKET_NAME')} and saved to {output_file_path}."
            )

            if sub_language == "en":
                job = "translate"
                aws_translate = False
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 200,
                        "message": "Generating an SRT and TXT file for your audio, please wait because this might "
                        "take a while.",
                        "progress": 40,
                    },
                )
                logging.info("Performing whisper translate...")
            elif sub_language == language:
                job = "transcribe"
                aws_translate = False
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 200,
                        "message": "Generating an SRT and TXT file for your audio, please wait because this might "
                        "take a while.",
                        "progress": 40,
                    },
                )
                logging.info("Performing whisper transcribe...")
            elif sub_language in language_codes:
                job = "translate"
                aws_translate = True
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 200,
                        "message": "Generating an SRT and TXT file for your audio, please wait because this might "
                        "take a while.",
                        "progress": 40,
                    },
                )
                logging.info("Performing whisper translate first then aws translate.")
            else:
                logging.error("Language support does not exist.")
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 500,
                        "message": "Language support does not exist.",
                        "progress": 40,
                    },
                )
                try:
                    logging.info(f"Deleting message from the queue.")
                    # Delete the message after processing is complete
                    sqs.delete_message(
                        QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                        ReceiptHandle=receipt_handle,
                    )
                    logging.info("Message deleted successfully.")
                except Exception as e:
                    logging.error(f"An error occurred: {traceback.format_exc()}")
                    pusher.trigger(
                        job_id,
                        "job-update",
                        {
                            "statusCode": 500,
                            "message": str(e),
                            "progress": 40,
                        },
                    )
                return

            command = [
                "./whisper/generate_transcript_c.sh",
                "-f",
                output_file_path,
                "-l",
                language,
                "-d",
                os.path.join(os.environ.get("DATA_DIR"), os.environ.get("MODEL_DIR")),
                "-o",
                os.path.join(os.environ.get("DATA_DIR"), "outputs", job_id),
                "-m",
                os.environ.get("MODEL"),
                "-h",
                os.environ.get("DEVICE"),
                "-t",
                os.environ.get("THREADS"),
                "-j",
                job,
                "-e",
                os.environ.get("ENV"),
            ]

            try:
                logging.info("Starting Whisper job.")
                # Process the file with your Whisper
                result = subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 200,
                        "message": "Whisper ran successfully.",
                        "progress": 60,
                    },
                )
                logging.info(f"Whisper ran with return code: {result.returncode}")
            except Exception as e:
                logging.error(f"An error occurred: {traceback.format_exc()}")
                print("Hello i am an error: ", str(e))
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 500,
                        "message": str(e),
                        "progress": 60,
                    },
                )
                try:
                    logging.info(f"Deleting message from the queue.")
                    # Delete the message after processing is complete
                    sqs.delete_message(
                        QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                        ReceiptHandle=receipt_handle,
                    )
                    logging.info("Message deleted successfully.")
                except Exception as e:
                    logging.error(f"An error occurred: {traceback.format_exc()}")
                    pusher.trigger(
                        job_id,
                        "job-update",
                        {
                            "statusCode": 500,
                            "message": str(e),
                            "progress": 60,
                        },
                    )
                return

            output_folder = os.path.join(os.environ.get("DATA_DIR"), "outputs", job_id)
            os.remove(output_folder + f"/{job_id}.json")
            os.remove(output_folder + f"/{job_id}.vtt")
            os.remove(output_folder + f"/{job_id}.tsv")
            file_size_limit_txt = is_file_size_within_limit(
                os.path.join(output_folder, f"{job_id}.txt"), 100 * 1024
            )

            logging.info(f"Translate flag set to {aws_translate}")
            logging.info(f"Output folder set to {output_folder}")

            if aws_translate:
                try:
                    logging.info("Translating SRT file.")
                    translate_srt(
                        os.path.join(output_folder, f"{job_id}.srt"),
                        sub_language,
                    )
                    pusher.trigger(
                        job_id,
                        "job-update",
                        {
                            "statusCode": 200,
                            "message": "SRT compiled successfully.",
                            "progress": 65,
                        },
                    )
                    logging.info("SRT compiled successfully.")
                except Exception as e:
                    logging.error(f"An error occurred: {traceback.format_exc()}")
                    pusher.trigger(
                        job_id,
                        "job-update",
                        {
                            "statusCode": 500,
                            "message": str(e),
                            "progress": 65,
                        },
                    )
                    try:
                        logging.info(f"Deleting message from the queue.")
                        # Delete the message after processing is complete
                        sqs.delete_message(
                            QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                            ReceiptHandle=receipt_handle,
                        )
                        logging.info("Message deleted successfully.")
                    except Exception as e:
                        logging.error(f"An error occurred: {traceback.format_exc()}")
                        pusher.trigger(
                            job_id,
                            "job-update",
                            {
                                "statusCode": 500,
                                "message": str(e),
                                "progress": 65,
                            },
                        )
                    return
                if file_size_limit_txt:
                    try:
                        logging.info("File size is within the limits.")
                        logging.info(
                            "Translating TXT file using document translation operation."
                        )
                        translate_doc(
                            os.path.join(output_folder, f"{job_id}.txt"),
                            sub_language,
                        )
                        pusher.trigger(
                            job_id,
                            "job-update",
                            {
                                "statusCode": 200,
                                "message": "TXT compiled successfully.",
                                "progress": 70,
                            },
                        )
                    except Exception as e:
                        logging.error(f"An error occurred: {traceback.format_exc()}")
                        pusher.trigger(
                            job_id,
                            "job-update",
                            {
                                "statusCode": 500,
                                "message": str(e),
                                "progress": 70,
                            },
                        )
                        try:
                            logging.info(f"Deleting message from the queue.")
                            # Delete the message after processing is complete
                            sqs.delete_message(
                                QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                                ReceiptHandle=receipt_handle,
                            )
                            logging.info("Message deleted successfully.")
                        except Exception as e:
                            logging.error(
                                f"An error occurred: {traceback.format_exc()}"
                            )
                            pusher.trigger(
                                job_id,
                                "job-update",
                                {
                                    "statusCode": 500,
                                    "message": str(e),
                                    "progress": 70,
                                },
                            )
                        return
                else:
                    try:
                        logging.info("File size is not within the limits.")
                        logging.info(
                            "Translating TXT file using line-by-line operation."
                        )
                        translate_txt(
                            os.path.join(output_folder, f"{job_id}.txt"),
                            sub_language,
                        )
                        pusher.trigger(
                            job_id,
                            "job-update",
                            {
                                "statusCode": 200,
                                "message": "TXT compiled successfully.",
                                "progress": 70,
                            },
                        )
                        logging.info("TXT compiled successfully.")
                    except Exception as e:
                        logging.error(f"An error occurred: {traceback.format_exc()}")
                        pusher.trigger(
                            job_id,
                            "job-update",
                            {
                                "statusCode": 500,
                                "message": str(e),
                                "progress": 70,
                            },
                        )
                        try:
                            logging.info(f"Deleting message from the queue.")
                            # Delete the message after processing is complete
                            sqs.delete_message(
                                QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                                ReceiptHandle=receipt_handle,
                            )
                            logging.info("Message deleted successfully.")
                        except Exception as e:
                            logging.error(
                                f"An error occurred: {traceback.format_exc()}"
                            )
                            pusher.trigger(
                                job_id,
                                "job-update",
                                {
                                    "statusCode": 500,
                                    "message": str(e),
                                    "progress": 70,
                                },
                            )
                        return
            os.remove(output_folder + f"/{job_id}.srt")
            os.remove(output_folder + f"/{job_id}.txt")

            logging.info(f"Zipping Files to {output_folder}...")

            zip_filename = f"{output_folder}.zip"
            with zipfile.ZipFile(zip_filename, "w") as zip_file:
                for root, dirs, files in os.walk(output_folder):
                    for file in files:
                        zip_file.write(os.path.join(root, file), file)

            logging.info(f"Removing {output_folder}...")
            # Delete the temporary output folder
            shutil.rmtree(output_folder)

            upload_zip_key = os.path.join("whisper_outputs", job_id + ".zip")

            logging.info(f"Uploading {upload_zip_key} to S3...")

            # Upload the zip file to S3 bucket
            try:
                logging.info("Uploading files to S3.")
                s3.upload_file(
                    zip_filename,
                    os.environ.get("AWS_STORAGE_BUCKET_NAME"),
                    upload_zip_key,
                )
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 200,
                        "message": "Uploaded files to S3 successfully.",
                        "progress": 90,
                    },
                )
                logging.info("Uploaded files to S3 successfully.")
            except Exception as e:
                logging.error(f"An error occurred: {traceback.format_exc()}")
                pusher.trigger(
                    job_id,
                    "job-update",
                    {
                        "statusCode": 500,
                        "message": str(e),
                        "progress": 90,
                    },
                )
                try:
                    logging.info(f"Deleting message from the queue.")
                    # Delete the message after processing is complete
                    sqs.delete_message(
                        QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                        ReceiptHandle=receipt_handle,
                    )
                    logging.info("Message deleted successfully.")
                except Exception as e:
                    logging.error(f"An error occurred: {traceback.format_exc()}")
                    pusher.trigger(
                        job_id,
                        "job-update",
                        {
                            "statusCode": 500,
                            "message": str(e),
                            "progress": 90,
                        },
                    )
                return

            logging.info(f"Removing {zip_filename} file...")
            # Delete the temporary zip file
            os.remove(zip_filename)
            os.remove(output_file_path)

            # Return the URL of the zip file to the user
            zip_file_url = (
                f"https://{os.environ.get('AWS_S3_CUSTOM_DOMAIN')}/{upload_zip_key}"
            )

            logging.info(f"Zipped file URL: {zip_file_url}")

            pusher.trigger(
                job_id,
                "job-update",
                {
                    "statusCode": 200,
                    "message": "Job completed with a success flag!",
                    "progress": 100,
                    "zip_file_url": zip_file_url,
                },
            )
            try:
                logging.info(f"Deleting message from the queue.")
                # Delete the message after processing is complete
                sqs.delete_message(
                    QueueUrl=os.environ.get("WORKER_QUEUE_URL"),
                    ReceiptHandle=receipt_handle,
                )
                logging.info("Task terminated with success.")
            except Exception as e:
                logging.error(f"An error occurred: {traceback.format_exc()}")
                return


# Call the process_job function
if __name__ == "__main__":
    try:
        process_job()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {traceback.format_exc()}")
