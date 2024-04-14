import asyncio
import json
import os
import time
from enum import Enum

import aiofiles
import aiohttp
import requests
from requests import get as rget


class Song_generate_status(Enum):
    error = "error"
    in_process = "running"
    submitted = "submitted"
    streaming = "streaming"
    complete = "complete"
    queued = "queued"


class Song_download_status(Enum):
    no_song_yet = "Song wasn't generated yet"
    timeout = "Song downloading timeouted"
    complete = "Song downloading completed"
    refund = "Money for song were refund back"


def _get_info(song_id):
    """
    Get info for the given song (song_id).
    """
    response = requests.get(f"http://127.0.0.1:8000/feed/{song_id}")

    data = json.loads(response.text)[0]
    return data["audio_url"], data["metadata"]


def generate_music_with_description(gpt_description_prompt="", make_instrumental=False, mv="chirp-v3-0"):
    """
    Generate music by given description.

    For example, "A Blues song about a person who is feeling happy and optimistic about the future."
    """
    data = {
        "gpt_description_prompt": gpt_description_prompt,
        "make_instrumental": make_instrumental,
        "mv": mv,
        "prompt": "",
    }

    r = requests.post("http://127.0.0.1:8000/generate/description-mode", data=json.dumps(data))

    resp = r.json()
    if "id" in resp:
        id_m = resp["id"]
        clips_ids = [x["id"] for x in resp["clips"]]
        return id_m, clips_ids, Song_generate_status.submitted
    return None, None, Song_generate_status.error


def generate_music_with_lyrics(title="Song", lyrics="", tags="Country, catchy,", mv="chirp-v3-0"):
    """
    Generate music by given lyrics.

    For example, "[Verse]\nWake up in the morning, feeling brand new\nGonna shake off the worries, leave 'em in the rearview\nStep outside, feeling the warmth on my face\nThere's something 'bout the sunshine that puts me in my place\n\n[Verse 2]\nWalking down the street, got a spring in my step\nThe rhythm in my heart, it just won't forget\nEverywhere I go, people smiling at me\nThey can feel the joy, it's contagious, can't you see?\n\n[Chorus]\nI got sunshine in my pocket, happiness in my soul\nA skip in my stride, and I'm ready to go\nNothing gonna bring me down, gonna keep on shining bright\nI got sunshine in my pocket, this world feels so right"
    """
    data = {
        "prompt": lyrics,
        "mv": mv,
        "tags": tags,
        "title": title,
    }
    r = requests.post("http://127.0.0.1:8000/generate", data=json.dumps(data))

    resp = r.json()
    if "id" in resp:
        id_m = resp["id"]
        clips_ids = [x["id"] for x in resp["clips"]]
        return id_m, clips_ids, Song_generate_status.submitted
    return None, None, Song_generate_status.error


def generate_lyrics_with_description(description: str):
    """
    Generate music by given description.

    For example, "A Blues song about a person who is feeling happy and optimistic about the future."
    """
    data = {"prompt": description}

    r = requests.post("http://127.0.0.1:8000/generate/lyrics/", data=json.dumps(data))
    return r.text


def get_lyrics(lid):
    """
    Get lyrics for the given song
    """
    r = requests.get(f"http://127.0.0.1:8000/lyrics/{lid}")
    return r.text


def get_info(song_id):
    """
    Get info for the given song (data).

    Outputs:

    dict {} :
        "title": data["title"],

        "video_url": data["video_url"],

        "audio_url": data["audio_url"],

        "image_large_url": data["image_large_url"],

        "is_trashed": data["is_trashed"],

        "status": data["status"],

        "tags": data["metadata"]["tags"],

        "gpt_description_prompt": data["metadata"]["gpt_description_prompt"],

        "if_refund_credits": data["metadata"]["refund_credits"],

        "error_message": data["metadata"]["error_message"],
    """
    response = requests.get(f"http://127.0.0.1:8000/feed/{song_id}")

    data = json.loads(response.text)[0]
    data_out = {
        "title": data["title"],
        "video_url": data["video_url"],
        "audio_url": data["audio_url"],
        "image_large_url": data["image_large_url"],
        "is_trashed": data["is_trashed"],
        "status": data["status"],
        "tags": data["metadata"]["tags"],
        "gpt_description_prompt": data["metadata"]["gpt_description_prompt"],
        "if_refund_credits": data["metadata"]["refund_credits"],
        "error_message": data["metadata"]["error_message"],
    }
    return data_out, Song_generate_status(data_out["status"])


async def save_song(song_id, output_path=".suno/"):
    """
    save given song
    """
    await asyncio.sleep(5)
    audio_url, metadata = _get_info(song_id)
    if metadata["refund_credits"] == True:
        return Song_download_status.refund
    if audio_url:
        async with aiohttp.ClientSession() as session:
            response = await session.get(audio_url, allow_redirects=False)
            if response.status != 200:
                return Song_download_status.no_song_yet
            path = os.path.join(output_path, f"suno_{song_id}.mp3")
            os.makedirs(output_path, exist_ok=True)
            async with aiofiles.open(path, mode="wb") as handle:
                async for chunk in response.content.iter_chunked(1024):
                    # If the chunk is not empty, write it to the file.
                    if chunk:
                        await handle.write(chunk)
            return Song_download_status.complete
    return Song_download_status.no_song_yet
