import boto3
import json
import os
import logging

def main(event, context):
    polly = boto3.client('polly')
    s3 = boto3.resource('s3')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    record = event['Records'][0]
    logger.info(record)
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    
    content_object = s3.Object(bucket, key)
    logger.info(content_object)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    logger.info(json_content)
    # textToSynthesize = json_content['results']['transcripts'][0]['transcript']
    # job_name = json_content["jobName"]
    textToSynthesize = json_content['TranslatedText']
    output_bucket = os.getenv('OUTPUT_BUCKET')

    synthesis_task = polly.start_speech_synthesis_task(
        Engine='neural',                            # 'standard'|'neural'
        OutputFormat='mp3',
        OutputS3BucketName=output_bucket,           # 'json'|'mp3'|'ogg_vorbis'|'pcm'
        Text=textToSynthesize,
        VoiceId='Kevin'
        # LanguageCode='en-AU',                     # 'arb'|'cmn-CN'|'cy-GB'|'da-DK'|'de-DE'|'en-AU'|'en-GB'|'en-GB-WLS'|'en-IN'|'en-US'|'es-ES'|'es-MX'|'es-US'|'fr-CA'|'fr-FR'|'is-IS'|'it-IT'|'ja-JP'|'hi-IN'|'ko-KR'|'nb-NO'|'nl-NL'|'pl-PL'|'pt-BR'|'pt-PT'|'ro-RO'|'ru-RU'|'sv-SE'|'tr-TR'
        # SpeechMarkTypes=[],                       # ['sentence'|'ssml'|'viseme'|'word'],
        # TextType='text',                          # 'ssml'|'text'
    )
