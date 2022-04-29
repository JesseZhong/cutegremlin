#!/bin/python

import asyncio
import os
from discord import \
    PCMVolumeTransformer, FFmpegPCMAudio, VoiceChannel, VoiceClient
from typing import List
from urllib.parse import urlparse, parse_qs, ParseResult
from os import path, system
import subprocess
from gremlin.discord.timestamps import from_seconds, parse_timestamp, stringify, duration
from gremlin.discord.ytdl import YTDL


def wrap(
    filename: str,
    prefix: str,
    suffix: str
) -> str:
    """
        Adds a prefix to the beginning of the filename.
    """
    filePath, baseName = path.split(filename)
    name, ext = path.splitext(baseName)
    baseName = prefix + name + suffix + ext
    return path.join(filePath, baseName)


clip_prefix = 'clipped_'
class Audio(PCMVolumeTransformer):

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')


    @classmethod
    async def from_url(
        cls,
        url: str,
        *,
        start: str = None,
        end: str = None,
        clip: List[float],
        loop: asyncio.AbstractEventLoop = None,
        stream: bool = False
    ):
        # Parse time stamps if there are any.
        startTime = parse_timestamp(start) if start else None
        endTime = parse_timestamp(end) if end else None

        # Check if a time stamp was specified with the URL.
        parsedUrl: ParseResult = urlparse(url)
        if parsedUrl.query:
            query = parse_qs(parsedUrl.query)

            if query and 't' in query:
                try:
                    startTime = from_seconds(int(query['t'][0]))
                except ValueError:
                    pass

        yt = await YTDL.create(
            url,
            'cache',
            loop=loop,
            stream=stream
        )

        # Clip the video if time stamps are specified.
        if startTime or endTime or (clip and len(clip) == 2):

            clippedFile = wrap(
                yt.filename,
                clip_prefix,
                (f'_s{start}' if start else '') + \
                (f'_e{end}' if end else '') + \
                (f'_c{str(clip[0])}_{str(clip[1])}' if clip else '')
            )

            if not path.exists(clippedFile):

                # Download the video audio before editing.
                yt.download()

                # If clipping range is specifed, override.
                if clip:
                    result = subprocess.run(
                        [
                            'ffprobe',
                            '-v', 'error',
                            '-show_entries', 'format=duration',
                            '-of', 'default=noprint_wrappers=1:nokey=1',
                            yt.filename
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT
                    )
                    pulledDuration = float(result.stdout)
                    startTime = from_seconds(clip[0] * pulledDuration)
                    endTime = from_seconds(clip[1] * pulledDuration)

                # Order matters for cutting speed.
                # https://stackoverflow.com/a/42827058/10167844
                before = f'-ss {stringify(startTime)}' if startTime else ''
                if endTime:
                    dur = duration(endTime, (startTime if startTime else from_seconds(0)))
                after = f'-to {stringify(dur)}' if endTime else ''

                system(f'ffmpeg -y -hide_banner -loglevel error {before} -i {yt.filename} -vn {after} -c copy {clippedFile}')

                # Remove the original file.
                os.remove(yt.filename)


            # Use the clipped file.
            final_filename = clippedFile

        # Handle unclipped files.
        else:

            # Download video audio if it wasn't previously downloaded.
            if not (path.exists(yt.filename)):
                yt.download()

            final_filename = yt.filename

        return cls(
            FFmpegPCMAudio(
                final_filename,
                options='-vn'
            ),
            data=yt.data
        )


    @staticmethod
    async def play(
        url: str,
        voice_clients: List[VoiceClient],
        voice_channel: VoiceChannel,
        loop: asyncio.AbstractEventLoop,
        *,
        start: str = None,
        end: str = None,
        clip: List[float] = None
    ):
        """
            Plays the audio of a YouTube video into a voice channel.
        """

        # Check if the client is already connected to the targetted voice channel.
        voiceClient = next(
            (v for v in voice_clients if v.channel == voice_channel),
            None
        )

        # Connect if not already connected.
        if not voiceClient:
            voiceClient = await voice_channel.connect()
            
        player = await Audio.from_url(
            url,
            start=start,
            end=end,
            clip=clip
        )

        # Play audio into the voice channel.
        voiceClient.play(
            player,
            after=lambda error: asyncio.run_coroutine_threadsafe(
                voiceClient.disconnect(),
                loop
            )
        )