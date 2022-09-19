import os
import sys
import requests

from time import sleep


API_KEY = "6bbb597d688f482480e2b166687174c1"
AUDIO_FILE = '/Users/paulpaliychuk/job/love/audio-filter/mlk_dream.mp3'
UPLOAD_ENDPOINT = 'https://api.assemblyai.com/v2/upload'
TRANSCRIPT_ENDPOINT = 'https://api.assemblyai.com/v2/transcript'
OUTPUT_TRANSCRIPT_FILE = 'i-have-a-dream-transcript.txt'


def read_audio_file(file):
    """Helper method that reads in audio files"""
    with open(file, 'rb') as f:
        while True:
            data = f.read(5242880)
            if not data:
                break
            yield data


# Create the headers for request
headers = {
    'authorization': API_KEY,
    'content-type': 'application/json'
}

res_upload = requests.post(
    UPLOAD_ENDPOINT,
    headers=headers,
    data=read_audio_file(AUDIO_FILE)
)
upload_url = res_upload.json()['upload_url']

res_transcript = requests.post(
    TRANSCRIPT_ENDPOINT,
    headers=headers,
    json={
        'audio_url': upload_url,
        'redact_pii': True,
        'redact_pii_policies': ['nationality'],
        'redact_pii_audio': True
    },
)
res_transcript_json = res_transcript.json()

print(res_transcript_json)

status = ''
while status != 'completed':
    res_result = requests.get(
        os.path.join(TRANSCRIPT_ENDPOINT, res_transcript_json['id']),
        headers=headers
    )
    if (status == 'completed'):
        print(res_result.json())

    status = res_result.json()['status']
    print(f'Status: {status}')

    if status == 'error':
        sys.exit('Audio file failed to process.')
    elif status != 'completed':
        sleep(10)

with open(OUTPUT_TRANSCRIPT_FILE, 'w') as f:
    print(res_result.json()['id'])
    f.write(res_result.json()['text'])

res_redacted_audio_file = requests.get(
    "https://api.assemblyai.com/v2/transcript/" +
    res_result.json()['id'] + "/redacted-audio",
    headers=headers,
)

print(res_redacted_audio_file.json())

print(f'Transcript file saved under {OUTPUT_TRANSCRIPT_FILE}')
