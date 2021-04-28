import boto3
import os
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from time import gmtime, strftime


def annotate(clip, txt, txt_color="white", bg_color=(0, 0, 255)):
    """ Writes a text at the bottom of the clip. """

    txtclip = TextClip(txt, fontsize=20, font="DejaVu-Sans", color=txt_color)

    txtclip = txtclip.on_color(
        (clip.w, txtclip.h + 6), color=(0, 0, 255), pos=(6, "center")
    )

    cvc = CompositeVideoClip([clip, txtclip.set_pos((0, "bottom"))])

    return cvc.set_duration(clip.duration)


def createVideo(
    originalClipName, subtitlesFileName, outputFileName, alternateAudioFileName
):
    clip = VideoFileClip(originalClipName)
    audio = AudioFileClip(alternateAudioFileName)
    # audio = audio.subclip(0, clip.duration)
    audio.set_duration(
        audio.duration if clip.duration > audio.duration else clip.duration
    )
    print(audio.duration)
    print(clip.duration)
    clip = clip.set_audio(audio)

    generator = lambda txt: TextClip(
        txt, font="DejaVu-Sans", fontsize=12, color="white"
    )
    # read in the subtitles files
    print(
        "\t" + strftime("%H:%M:%S", gmtime()),
        "Reading subtitle file: " + subtitlesFileName,
    )
    subs = SubtitlesClip(subtitlesFileName, generator)
    print("\t\t==> Subtitles duration before: " + str(subs.duration))
    subs = subs.subclip(0, clip.duration - 0.001)
    subs.set_duration(clip.duration - 0.001)
    print("\t\t==> Subtitles duration after: " + str(subs.duration))
    print(
        "\t" + strftime("%H:%M:%S", gmtime()),
        "Reading subtitle file complete: " + subtitlesFileName,
    )

    print("\t" + strftime("%H:%M:%S", gmtime()), "Creating Subtitles Track...")
    annotated_clips = [
        annotate(clip.subclip(from_t, to_t), txt) for (from_t, to_t), txt in subs
    ]

    print(
        "\t" + strftime("%H:%M:%S", gmtime()),
        "Creating composited video: " + outputFileName,
    )
    # Overlay the text clip on the first video clip
    final = concatenate_videoclips(annotated_clips)

    print(
        "\t" + strftime("%H:%M:%S", gmtime()), "Writing video file: " + outputFileName
    )
    final.write_videofile(outputFileName)


def main():
    (
        polly_bucket_name,
        source_bucket_name,
        srt_bucket_name,
        polly_file_name,
        uuid,
        output_bucket,
    ) = (
        os.getenv("POLLY_BUCKET_NAME"),
        os.getenv("SOURCE_BUCKET_NAME"),
        os.getenv("SRT_BUCKET_NAME"),
        os.getenv("POLLY_FILE_NAME"),
        os.getenv("UUID"),
        os.getenv("OUTPUT_BUCKET"),
    )
    source_filename, audio_filename, srt_filename = (
        "source.mp4",
        "audio.mp3",
        "translation.srt",
    )
    s3 = boto3.client("s3")
    s3.download_file(source_bucket_name, uuid, source_filename)
    print("downloaded source")

    s3.download_file(polly_bucket_name, polly_file_name, audio_filename)
    print("downloaded polly")

    s3.download_file(srt_bucket_name, uuid + ".srt", srt_filename)
    print("downloaded srt")

    output_name = uuid + ".webm"
    createVideo(source_filename, srt_filename, output_name, audio_filename)

    s3.upload_file(output_name, output_bucket, output_name)


main()
