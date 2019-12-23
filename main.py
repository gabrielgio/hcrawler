from instabot import Bot
from typing import Set
from time import sleep
import os
import argparse

from tqdm import tqdm

bot = Bot()
parser = argparse.ArgumentParser(description="Download videos and photos for all followings")
parser.add_argument('-u', '--username', help="Account username", default=os.environ.get('USERNAME', None))
parser.add_argument('-p', '--password', help="Account password", default=os.environ.get('PASSWORD', None))


def login(username: str, password: str):
    bot.login(username=username, password=password)


def download_photos_and_videos(username, user_medias):
    folder = f"out/{username}"
    if not os.path.exists(folder):
        os.mkdir(folder)

    print(f"Downloading {username}")
    for media_id in tqdm(user_medias):
        bot.api.media_info(media_id)
        json = bot.api.last_json
        media = json["items"][0]
        media_type = media["media_type"]
        if media_type == 2:
            bot.download_video(media_id, folder=folder)
        else:
            bot.api.download_photo(media_id, None, media, folder)


def download_all_medias(user_id: str):
    username = bot.get_username_from_user_id(user_id)
    medias = bot.get_total_user_medias(user_id)
    download_photos_and_videos(username, medias)


def run_crawler(username: str):
    following: Set = bot.get_user_following(username)
    for user_id in following:
        sleep(900)
        download_all_medias(user_id)


if __name__ == "__main__":
    args = parser.parse_args()
    username = args.username
    password = args.password

    login(username, password)
    while True:
        try:
            run_crawler(args.username)
        except:
            print("Exception!")
            continue
