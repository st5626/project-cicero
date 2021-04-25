from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
from time import gmtime, strftime

# # Load myHolidays.mp4 and select the subclip 00:00:50 - 00:00:60
# clip = VideoFileClip("sourceVideo.mp4")#.subclip(50,60)

# # Reduce the audio volume (volume x 0.8)
# clip = clip.volumex(0.8)

# # Generate a text clip. You can customize the font, color, etc.
# txt_clip = TextClip("My Holidays 2013",fontsize=70,color='white')

# # Say that you want it to appear 10s at the center of the screen
# txt_clip = txt_clip.set_pos('center').set_duration(10)

# # Overlay the text clip on the first video clip
# video = CompositeVideoClip([clip, txt_clip])

# # Write the result to a file (many options available !)
# video.write_videofile("sourceVideoDone.webm")

def annotate(clip,txt,txt_color='white',bg_color=(0,0,255)):
    """ Writes a text at the bottom of the clip. """
    
    txtclip = TextClip(txt, fontsize=20, font='Ubuntu-bold',
                       color=txt_color)
                       
    txtclip = txtclip.on_color((clip.w,txtclip.h+6), color=(0,0,255),
                        pos=(6,'center'))
                        
    cvc =  CompositeVideoClip([clip , txtclip.set_pos((0,'bottom'))])
    
    return cvc.set_duration(clip.duration)

def createVideo( originalClipName, subtitlesFileName, outputFileName, alternateAudioFileName):
    clip = VideoFileClip(originalClipName)
    audio = AudioFileClip(alternateAudioFileName)
    audio = audio.subclip( 0, clip.duration )
    audio.set_duration(clip.duration)
    clip = clip.set_audio( audio )

    generator = lambda txt: TextClip(txt, font='Arial-Bold', fontsize=24, color='white')
    # read in the subtitles files
    print ("\t" + strftime("%H:%M:%S", gmtime()), "Reading subtitle file: " + subtitlesFileName)
    subs = SubtitlesClip(subtitlesFileName, generator)
    print ("\t\t==> Subtitles duration before: " + str(subs.duration))
    subs = subs.subclip( 0, clip.duration - .001)
    subs.set_duration( clip.duration - .001 )
    print ("\t\t==> Subtitles duration after: " + str(subs.duration))
    print ("\t" + strftime("%H:%M:%S", gmtime()), "Reading subtitle file complete: " + subtitlesFileName )

    print ("\t" + strftime( "%H:%M:%S", gmtime()), "Creating Subtitles Track...")
    annotated_clips = [annotate(clip.subclip(from_t, to_t), txt) for (from_t, to_t), txt in subs]

    print ("\t" + strftime( "%H:%M:%S", gmtime()), "Creating composited video: " + outputFileName)
    # Overlay the text clip on the first video clip
    final = concatenate_videoclips( annotated_clips ) 

    print ("\t" + strftime( "%H:%M:%S", gmtime()), "Writing video file: " + outputFileName )
    final.write_videofile(outputFileName)

createVideo( "sourceVideo.mp4", "spanish.srt", "example_done.webm", "spanishAudio.mp3")