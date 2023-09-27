#!/bin/bash

# whisper-ctranslate2 ${1} --language ${2} --model_dir ${3} --model large --task transcribe --device gpu --output_dir ${} --threads 2

# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command filed with exit code $?."' EXIT

# direct all logs to after-install.log
exec 3>&1 4>&2
trap 'exec 2>&4 1>&3' 0 1 2 3
exec 1>/home/ubuntu/quick-translates-api-worker/whisper/execution.log 2>&1

set -e

usage() {
  echo "Usage: $0 -f file_name -l language -d model_dir -o output_dir -m model -h device -t threads -j job -e env"
}

while getopts ":f:l:d:o:m:h:t:j:e:" opt; do
  case $opt in
    f) file_name="$OPTARG";;
    l) language="$OPTARG";;
    d) model_dir="$OPTARG";;
    o) output_dir="$OPTARG";;
    m) model="$OPTARG";;
    h) device="$OPTARG";;
    t) threads="$OPTARG";;
    j) job="$OPTARG";;
    e) env="$OPTARG";;
    \?) echo "Invalid option -$OPTARG"; usage; exit 1;;
    :) echo "Option -$OPTARG requires an argument"; usage; exit 1;;
  esac
done

if [ -z "$file_name" ] || [ -z "$language" ] || [ -z "$model_dir" ] || [ -z "$output_dir" ] || [ -z "$model" ] || [ -z "$device" ] || [ -z "$threads" ] || [ -z "$job" ] || [ -z "$env" ]; then
  echo "Missing one or more mandatory arguments."
  usage
  exit 1
fi

echo "Transcription started."

if [ "$env" = "prod" ]; then
    /home/ubuntu/quick-translates-api-worker-env/bin/whisper-ctranslate2 "$file_name" \
      --language "$language" \
      --model_directory "$model_dir" \
      --model "$model" \
      --task "$job" \
      --dece "$device" \
      --output_dir "$output_dir" \
      --threads "$threads" \
      --local_files_only True
else
    /home/faran/PycharmProjects/quick-translates-api-worker/venv/bin/whisper-ctranslate2 "$file_name" \
      --language "$language" \
      --model_directory "$model_dir" \
      --model "$model" \
      --task "$job" \
      --device "$device" \
      --output_dir "$output_dir" \
      --threads "$threads" \
      --local_files_only False
fi

echo "Transcription complete."

exit 0
