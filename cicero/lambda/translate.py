import boto3
import json
import os
import logging
import re

def main(event, context):
    translate = boto3.client('translate')
    s3 = boto3.resource('s3')
    dynamodb = boto3.resource("dynamodb")
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info(event)

    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    logger.info(key)
    content_object = s3.Object(bucket, key)
    logger.info(content_object)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    logger.info("file_content: " + file_content)
    json_content = json.loads(file_content)
    logger.info(json_content)
    lookup_uuid = key.split('.')[0]
    table_name = os.getenv("TABLE")
    table = dynamodb.Table(table_name)
    table_record = table.get_item(
        Key={
            'uuid': lookup_uuid,
        }
    )
    logger.info(table_record)
    SOURCE_LANGUAGE = table_record['Item']['input_language'][:2]
    TARGET_LANGUAGE = table_record['Item']['target_language'][:2]
    if (TARGET_LANGUAGE == 'arb'){
        TARGET_LANGUAGE = 'ar'
    } else if (TARGET_LANGUAGE == 'cmn') {
        TARGET_LANGUAGE = 'zh'
    } else if (TARGET_LANGUAGE == 'nb') {
        TARGET_LANGUAGE = 'no'
    }
    textToSynthesize = json_content['results']['transcripts'][0]['transcript']
    lastPronunIdx = len(json_content['results']['items']) - 1
    # Get last pronunciation
    while json_content['results']['items'][lastPronunIdx]['type'] != "pronunciation":
        lastPronunIdx -= 1
    firstPronunIdx = 0
    # Get first pronunciation
    while json_content['results']['items'][firstPronunIdx]['type'] != "pronunciation":
        firstPronunIdx += 1
    job_name = json_content["jobName"]
    output_bucket = os.getenv('OUTPUT_BUCKET')
    result = translate.translate_text(
        Text=textToSynthesize,
        SourceLanguageCode=SOURCE_LANGUAGE, 
        TargetLanguageCode=TARGET_LANGUAGE,
    )

    start = float( json_content['results']['items'][firstPronunIdx]["start_time"])
    end = float(json_content['results']['items'][lastPronunIdx]["end_time"])

    textToGetPhrases = result["TranslatedText"]

    phrases = getPhrasesFromTranslation(textToGetPhrases, start, end)
    logger.info("phrases: " + str(phrases))
    srtContent = writeSRT( phrases )

    logger.info(srtContent)
    output_name = job_name + ".srt"
    s3object = s3.Object(output_bucket, output_name)
    s3object.put(
        Body=(bytes(srtContent.encode('utf-8')))
    )

# Create phrases from translation input from aws translate
def getPhrasesFromTranslation( translation, start, end ):

    words = translation.split()
    phrase =  { 'start_time': '', 'end_time': '', 'words' : [] }
    phrases = []
    nPhrase = True
    x = 0
    c = 0

    for word in words:

        # If it is a new phrase, then get the start_time of the first item
        if nPhrase == True:
            nPhrase = False
            c += 1

        # Append the word to the phrase...
        phrase["words"].append(word)
        x += 1

        # Add the phrase to the phrases, generate a new phrase, etc.
        if x == 10:
            phrases.append(phrase)
            phrase = { 'start_time': '', 'end_time': '', 'words' : [] }
            nPhrase = True
            x = 0

    if(len(phrase['words']) > 0):
        phrases.append(phrase)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.info("C: " + str(c))
    logger.info("Generated Phrases" + str(phrases))

    timeDelta = (end-start) / c
    time = start
    for phraseIdx in range(len(phrases)):
        phrases[phraseIdx]['start_time'] = getTimeCode(time + 0.01)
        time += timeDelta
        phrases[phraseIdx]['end_time'] = getTimeCode(time)

    return phrases


# Create SRT file from phrases
def writeSRT( phrases ):

    output = ""
    x = 1
    
    for phrase in phrases:
        
        output +=  str(x) + "\n" 
        x += 1
        output +=  phrase["start_time"] + " --> " + phrase["end_time"] + "\n" 
        # Format words
        out = getPhraseText( phrase )
        output += out + "\n\n" 

    return output


# Format words to add proper spacing
def getPhraseText( phrase ):

    length = len(phrase["words"])

    out = ""
    for i in range( 0, length ):
        if re.match('[a-zA-Z0-9]', phrase["words"][i]):
            if i > 0:
                out += " " + phrase["words"][i]
            else:
                out += phrase["words"][i]
        else:
            out += phrase["words"][i]
            
    return out

# Turn seconds into formatted time code for SRT
def getTimeCode( seconds ):
    t_hund = int(seconds % 1 * 1000)
    t_seconds = int( seconds )
    t_secs = ((float( t_seconds) / 60) % 1) * 60
    t_mins = int( t_seconds / 60 )
    return str( "%02d:%02d:%02d,%03d" % (00, t_mins, int(t_secs), t_hund ))
