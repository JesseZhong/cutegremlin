from asyncio import AbstractEventLoop, get_event_loop
from typing import Union, Dict, Any

def ytdl_format_options(directory: str):
    return {
        'format': 'bestaudio/best',
        'outtmpl': f'{directory}/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0', # bind to ipv4 since ipv6 addresses cause issues sometimes
        'cachedir': False # https://stackoverflow.com/a/32105062/10167844
    }

class YTDL:

    def __init__(
        self,
        url: str,
        directory: str,
        *,
        use_ytdlp: bool = True,
        loop: AbstractEventLoop = None,
        stream: bool = None
    ) -> None:
        self._url = url
        self._directory = directory
        self._use_ytdlp = use_ytdlp
        self._loop = loop
        self._stream = stream


    @classmethod
    async def create(
        cls,
        url: str,
        directory: str,
        *,
        use_ytdlp: bool = True,
        loop: AbstractEventLoop = None,
        stream: bool = None
    ):
        self = YTDL(
            url,
            directory,
            use_ytdlp=use_ytdlp,
            loop=loop,
            stream=stream
        )

        await self.load()

        return self


    async def load(self):
        '''
            Extract info from video.
        '''
        if self._use_ytdlp:
            import yt_dlp as ytdl
        else:
            import youtube_dl as ytdl

        # Suppress noise about console usage from errors
        ytdl.utils.bug_reports_message = lambda: ''

        self._ytdl = ytdl.YoutubeDL(ytdl_format_options(self._directory))

        # Get the video info.
        self._loop = self._loop or get_event_loop()
        self._data = await self._loop.run_in_executor(
            None,
            lambda: self._ytdl.extract_info(
                self._url,
                download=False
            )
        )
        
        # If it's a playlist, grab the first item.
        if 'entries' in self._data:
            self._data = self._data['entries'][0]

        # Get the filename.
        self._filename = self._data['url'] \
            if self._stream \
            else self._ytdl.prepare_filename(self._data)


    def download(self) -> None:
        self._ytdl.download([self._url])

    @property
    def data(self) -> Union[Any, Dict[str, Any], None]:
        return self._data

    @property
    def filename(self) -> str:
        return self._filename