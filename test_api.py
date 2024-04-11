import json
import os
import time

import requests
from api import *
from requests import get as rget


def test_get_info(aid):
    info = get_info(aid)
    print(f"SONG INFO {aid}:\n", info)
    return info


def test_save_song(aid):
    result = save_song(aid)
    print(f"SONG SAVE {aid}:\n", result)


def test_generate_music_with_description_false():
    id_m, clips_ids, status = generate_music_with_description("Song by Eminem")
    return id_m, clips_ids


def test_generate_music_with_description_true():
    id_m, clips_ids, status = generate_music_with_description("Песня про девочку, живущую в лесу.")
    return id_m, clips_ids


def test_generate_music_true():
    id_m, clips_ids, status = generate_music_with_lyrics(
        title="Your Music",
        lyrics="""(Verse 1)
Well, I walked in the diner, hungry as can be,
Ordered up three cheeseburgers, but now everyone's looking at me,
I took a seat at the counter, tried to act real cool,
But something's got folks whispering, like I broke some kinda rule.
(Chorus)
I only ate three cheeseburgers, so why's everybody staring at me?
Did I eat 'em too fast or too slow, or is there something they don't see?
I swear I'm just a hungry soul, with an appetite wild and free,
I only ate three cheeseburgers, why's everybody staring at me?
(Verse 2)
I didn't mean to cause a scene, didn't mean to turn no heads,
But now the whole place is buzzing, like I did something they all dread,
I just wanted some comfort food, to fill my empty belly,
But now it seems I'm the talk of the town, and that's just downright silly.
(Chorus)
I only ate three cheeseburgers, so why's everybody staring at me?
Did I eat 'em too fast or too slow, or is there something they don't see?
I swear I'm just a hungry soul, with an appetite wild and free,
I only ate three cheeseburgers, why's everybody staring at me?""",
    )
    return id_m, clips_ids


if __name__ == "__main__":
    test_get_info("57b71a9e-614e-40bb-b0a4-a73e886e825e")
    ##                   TRUE MUSIC WITH Lyrics
    id_m, clips_ids = test_generate_music_true()
    for clip_id in clips_ids:
        while True:
            data, status_gen = test_get_info(clip_id)
            print("GENERATE SONG | FALSE:\n", status_gen)
            if status_gen == Song_generate_status.complete:
                test_save_song(clip_id)
                break
            elif status_gen == Song_generate_status.error:
                # Song either refund or credits returned
                ## TODO: Return credit to user
                break
    ##                   FALSE MUSIC WITH DESC
    # # False
    # id_m, clips_ids = test_generate_music_with_description_false()
    # for clip_id in clips_ids:
    #     while True:
    #         data, status_gen = test_get_info(clip_id)
    #         print("GENERATE SONG | FALSE:\n", status_gen)
    #         if status_gen == Song_generate_status.complete:
    #             test_save_song(clip_id)
    #             break
    #         elif status_gen == Song_generate_status.error:
    #             # Song either refund or credits returned
    #             ## TODO: Return credit to user
    #             break
    # # test_get_lyrics(id_m)

    ##                   TRUE MUSIC WITH DESC
    # True
    # id_m, clips_ids = test_generate_music_with_description_true()
    # for clip_id in clips_ids:
    #     while True:
    #         data, status_gen = test_get_info(clip_id)
    #         print("GENERATE SONG | TRUE:\n", status_gen)
    #         if status_gen == Song_generate_status.complete or Song_generate_status.submitted:
    #             test_save_song(clip_id)
    #             break
    #         elif status_gen == Song_generate_status.error:
    #             # Song either refund or credits returned
    #             ## TODO: Return credit to user
    #             break
    # test_get_lyrics(id_m)
