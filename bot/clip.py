from telegram.update import Update
from telegram import Message
from telegram.error import BadRequest
from telegram.ext import CallbackContext, CommandHandler
import subprocess
from bot.ffmpeg_runner import FfmpegRunner
from bot.status import ClipStatus
import bot.utils as utils
import youtube_dl
from typing import Optional
import os
from bot import dispatcher, updater
import logging


def clip(update: Update, context: CallbackContext):
    splits = update.message.text.split(' ')
    try:
        youtube_link = splits[1]
    except KeyError:
        context.bot.send_message(update.message.chat_id, text="Youtube link not provided")
        return
    try:
        start_time = splits[2]
        duration = splits[3]
    except KeyError:
        return context.bot.send_message(update.message.chat_id, text="Start or end time not provided",
                                        reply_to_message_id=update.message.message_id)
    uid = f'{update.message.chat_id}-{update.message.message_id}'

    status = ClipStatus(uid, "Extracting metadata", 0, '')
    message = context.bot.send_message(chat_id=update.message.chat_id, reply_to_message_id=update.message.message_id,
                                       text=utils.get_readable_message(status), parse_mode='html')
    r = subprocess.Popen(['youtube-dl', '--get-url', '--youtube-skip-dash-manifest', youtube_link],
                         stdout=subprocess.PIPE)
    out, err = r.communicate()
    if r.returncode == 0:
        outs = out.split(str.encode('\n'))
        print(outs)
        youtube_video = outs[0].decode("utf-8")
        youtube_audio = outs[1].decode("utf-8")
    else:
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        context.bot.send_message(chat_id=update.message.chat_id, text="Cannot extract url from youtube-dl! "
                                                                      "Try again later",
                                 reply_to_message_id=update.message.message_id)
        return
    with youtube_dl.YoutubeDL() as ydl:
        info = ydl.extract_info(youtube_link, download=False)
        if 'entries' in info:
            return context.bot.send_message(update.message.chat_id, text="Playlists cannot be clipped")
        status.name = os.path.basename(ydl.prepare_filename(info))
    status.status = "Clipping video"
    update_progress(status, context, message)
    video_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, 'outputs',
                              f'{update.message.chat_id}-{update.message.message_id}.mp4')
    print(video_path)
    ffmpeg_cmd = ['ffmpeg', '-ss', f'{start_time}', '-i', f'{youtube_video}', '-ss', f'{start_time}', '-i',
                  youtube_audio, '-t', f'{duration}', '-map', '0:v', '-map', '1:a',
                  '-c:v', 'libx264', '-c:a', 'aac',
                  video_path]
    runner = FfmpegRunner(cmd=ffmpeg_cmd)

    def on_clip_complete():
        status.status = utils.Status.STATUS_UPLOADING
        update_progress(status=status, context=context, message=message)
        with open(video_path, 'rb') as file:
            context.bot.send_video(chat_id=update.message.chat_id, video=file, filename=status.name + '.mp4',
                                   reply_to_message_id=update.message.message_id, supports_streaming=True)
            context.bot.delete_message(message.chat_id, message.message_id)
        os.remove(video_path)

    def on_error(_, __):
        context.bot.delete_message(message.chat_id, message.message_id)
        context.bot.send_message(update.message.chat_id, text="An error occurred while clipping video!",
                                 reply_to_message_id=update.message.message_id)

    runner.run_command(on_clip_complete, on_error)
    # progress wont work as ffmpeg does not provides progress for http downloads
    # update_task = utils.SetInterval(4, update_progress, args=(status, context, message, runner))
    # status.task = update_task


def update_progress(status: ClipStatus, context: CallbackContext, message: Message):
    try:
        msg = utils.get_readable_message(status)
        context.bot.edit_message_text(text=msg, chat_id=message.chat_id, message_id=message.message_id,
                                      parse_mode='html')

    except BadRequest as e:
        logging.info(e)


def add_handler():
    clip_handler = CommandHandler('clip', clip, run_async=True)
    dispatcher.add_handler(clip_handler)
