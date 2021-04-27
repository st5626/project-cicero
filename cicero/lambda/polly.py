import boto3
import os
import logging

def main(event, context):

    # TARGET_LANGUAGE = "de"

    polly = boto3.client('polly')
    s3 = boto3.resource('s3')
    dynamodb = boto3.resource("dynamodb")
    table_name = os.getenv("TABLE")
    table = dynamodb.Table(table_name)
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    record = event['Records'][0]
    logger.info(record)
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    lookup_uuid = key.split('.')[0]

    table_record = table.get_item(
        Key={
            'uuid': lookup_uuid,
        }
    )
    TARGET_LANGUAGE = table_record['Item']["target_language"]

    content_object = s3.Object(bucket, key)
    logger.info(content_object)
    file_content = content_object.get()['Body'].read().decode('utf-8')

    # Extract text from SRT
    textToSynthesize = ""
    counter = 1
    inLine = False
    for line in file_content.split("\n"):
        if line.strip().isnumeric():
            counter += 1
            inLine = True
        elif inLine and not len(line.split("-->")) > 1:
            textToSynthesize += line + " "
            inLine = False
    
    
    logger.info("textToSynthesize: " + str(textToSynthesize))

    output_bucket = os.getenv('OUTPUT_BUCKET')

    synthesis_task = polly.start_speech_synthesis_task(
        Engine='neural',                            # 'standard'|'neural'
        OutputFormat='mp3',
        OutputS3BucketName=output_bucket,           # 'json'|'mp3'|'ogg_vorbis'|'pcm'
        Text=textToSynthesize,
        VoiceId=getVoiceId(TARGET_LANGUAGE)
        # LanguageCode='en-AU',                     # 'arb'|'cmn-CN'|'cy-GB'|'da-DK'|'de-DE'|'en-AU'|'en-GB'|'en-GB-WLS'|'en-IN'|'en-US'|'es-ES'|'es-MX'|'es-US'|'fr-CA'|'fr-FR'|'is-IS'|'it-IT'|'ja-JP'|'hi-IN'|'ko-KR'|'nb-NO'|'nl-NL'|'pl-PL'|'pt-BR'|'pt-PT'|'ro-RO'|'ru-RU'|'sv-SE'|'tr-TR'
        # SpeechMarkTypes=[],                       # ['sentence'|'ssml'|'viseme'|'word'],
        # TextType='text',                          # 'ssml'|'text'
    )

# Select voice that works with target language
def getVoiceId( targetLangCode ):
    # TODO: Figure out proper mapping
    # Note this mapping is different depending on which engine you're using.
    if targetLangCode == "es":
        voiceId = "Penelope"
    elif targetLangCode == "de":
        voiceId = "Kevin"
    else:
        voiceId = "Kevin"
        
    return voiceId
