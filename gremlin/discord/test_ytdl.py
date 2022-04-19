import pytest
import pytest_asyncio
from gremlin.discord.ytdl import YTDL
from pathlib import Path
from shutil import rmtree


example_files = [
    ('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'youtube-dQw4w9WgXcQ-Rick_Astley_-_Never_Gonna_Give_You_Up_Official_Music_Video.webm'),  # rickroll
    ('https://www.youtube.com/watch?v=QXUSvSUsx80', 'youtube-QXUSvSUsx80-I_d_just_like_to_interject_for_a_moment_uwu.webm'),  # uwu linux
    ('https://www.youtube.com/watch?v=hFcLyDb6niA', 'youtube-hFcLyDb6niA-Todd_and_the_sweet_little_lies.webm'),  # todd
    ('https://www.youtube.com/watch?v=2rCP4CRRO7E', 'youtube-2rCP4CRRO7E-Gandalf_Europop_Nod.webm'),  # gandalf
    ('https://www.youtube.com/watch?v=dbn-QDttWqU', 'youtube-dbn-QDttWqU-_.webm'),  # peace and tranquility
    ('https://www.youtube.com/watch?v=YJg_2r09Ips', 'youtube-YJg_2r09Ips-Gura_reads_the_dummy_thicc_meme_in_an_Ara_Ara_voice....webm'),  # gura
]

example_data = [
    ('https://www.youtube.com/watch?v=dQw4w9WgXcQ'),  # rickroll
    ('https://www.youtube.com/watch?v=QXUSvSUsx80'),  # uwu linux
    ('https://www.youtube.com/watch?v=hFcLyDb6niA'),  # todd
    ('https://www.youtube.com/watch?v=2rCP4CRRO7E'),  # gandalf
    ('https://www.youtube.com/watch?v=dbn-QDttWqU'),  # peace and tranquility
    ('https://www.youtube.com/watch?v=YJg_2r09Ips'),  # gura
]

test_directory = 'test_cache'

@pytest.mark.asyncio
@pytest_asyncio.fixture
async def manage_directory():
    path = Path(test_directory)

    # Remove an existing directory.
    if path.exists():
        rmtree(path, ignore_errors=True)

    # Create a fresh directory.
    path.mkdir()

    # Run test.
    yield None

    # Remove directory.
    rmtree(path, ignore_errors=True)
    print('yest')


@pytest.mark.asyncio
@pytest.mark.timeout(2)
@pytest.mark.parametrize(
    'url, expected',
    example_files
)
async def test_filename(
    url: str,
    expected: str,
    manage_directory
):
    '''
        Filename should be available and formatted
        a certain way after info is retrieved from YT.
    '''
    ytdl = await YTDL.create(
        url,
        test_directory
    )

    expected_path = f'{test_directory}/{expected}'

    assert ytdl.filename == expected_path, f'Should be {expected_path}.'


@pytest.mark.asyncio
@pytest.mark.timeout(2)
@pytest.mark.parametrize(
    'url',
    example_data
)
async def test_data(
    url: str,
    manage_directory
):
    ytdl = await YTDL.create(
        url,
        test_directory
    )

    assert ytdl.data != None, 'Data expected.'


@pytest.mark.asyncio
@pytest.mark.timeout(10)
@pytest.mark.parametrize(
    'url, expected',
    example_files
)
async def test_download(
    url: str,
    expected: str,
    manage_directory
):
    ytdl = await YTDL.create(
        url,
        test_directory
    )

    ytdl.download()

    filepath = f'{test_directory}/{expected}'

    assert Path(filepath).exists(), f'File should be downloaded to {filepath}.' 