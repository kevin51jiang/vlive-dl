import youtube_dl
from pathlib import Path
from subprocess import call
import sys
from webvtt import WebVTT
import html
import os
from html2text import HTML2Text
from pysrt.srtitem import SubRipItem
from pysrt.srttime import SubRipTime
import time

# urls to download. Should eventually be able to be decided by cli option
url = ['https://www.vlive.tv/video/116623']

# where the stuff is intially downloaded. Treated like a temp folder.
input_path = Path('./vlive-input/')

# where the final, subtitled product is tranferred.
output_path = Path('./vlive-output/')

# Seems like english subtitles are always 'en_US', and they always come in vtt files
ydl_opts = {
    'writesubtitles': 'en_US',
    'outtmpl': str(input_path / 'temp.%(ext)s'),
}

# converts a VTT file to an SRT file, which handbrake likes working in.
# stolen from vtt-to-srt (https://github.com/lbrayner/vtt-to-srt/blob/master/vtt-to-srt)


def convert_sub(vtt_file):
    index = 0

    file_name, file_extension = os.path.splitext(vtt_file)

    if not file_extension.lower() == ".vtt":
        sys.stderr.write("Skipping %s.\n" % vtt_file)
        raise Exception("VTT file could not be found.")
        return

    srt = open(file_name + ".srt", "w")

    for caption in WebVTT().read(vtt_file):
        index += 1
        start = SubRipTime(0, 0, caption.start_in_seconds)
        end = SubRipTime(0, 0, caption.end_in_seconds)
        srt.write(SubRipItem(
            index, start, end, html.unescape(caption.text))
            .__str__()+"\n")

# burns the captions into the video


def burn_in():
    args = ['-i ' + '"' + str((input_path / 'temp.mp4').resolve()) + '"',
            '-o ' + '"' + str((output_path / 'output.mp4').resolve()) + '"',
            '--optimize',
            '--encoder x264',
            '--x264-preset medium',
            '--srt-file ' + '"' +
            str((input_path / 'temp.en_US.srt').resolve()) + '"',
            '--srt-burn']

    params = ''
    # concatenate the whole array into one string to send to the cli
    for arg in args:
        params += arg + ' '

    os.system("HandBrakeCLI " + params)

# remove the temp files in the input folder


def cleanup():
    pass

# The Story Begins


def __main__():

    # download the video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)

    # covert the subtitles to srt (which handbrake likes working in)
    convert_sub(str(input_path / 'temp.en_US.vtt'))
    burn_in()
    cleanup()
    print("F")


__main__()
