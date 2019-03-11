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
urls = ['https://www.vlive.tv/video/116623']

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


#
# remove the temp files in the input folder
def cleanup():
    pass


# Completely process a video from start to end
# Downloads, burns in subtitles, and cleans up.
def process_video(url):
    # give user info
    print("Starting to rip " + url)
    start_time = time.time()

    # download the video
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(url)
    download_time = time.time()
    print("Downloading the video took " + str(download_time - start_time))

    # covert the subtitles to srt (which handbrake likes working in)
    convert_sub(str(input_path / 'temp.en_US.vtt'))
    convert_sub_time = time.time()
    print("Converting the subtitles took " +
          str(convert_sub_time - download_time))

    # Burn in (Hardcode) in subtitles to the video.
    burn_in()
    burn_in_time = time.time()
    print("Buring in the subtitles took " +
          str(burn_in_time - convert_sub_time))

    # Delete any temporary working files in the input directory
    cleanup()
    cleanup_time = time.time()
    print("Cleaning up took " + str(cleanup_time - burn_in_time))

    # give use info
    print("Processing everything video took " + str(time.time() - start_time))


# THE STORY BEGINS
def __main__():
    for request in urls:
        process_video(request)


__main__()
