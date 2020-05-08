from typing import Any, Set, List
import os
import pika

from instabot import Bot
from time import sleep
import argparse
import random
import json
import logging
from graypy import GELFTCPHandler
from instabot.bot.bot_get import get_user_id_from_username
from instabot.api import api

bot = Bot()
parser = argparse.ArgumentParser(description="Download videos and photos for all followings")
parser.add_argument('-u', '--username', help="Account username", default=os.environ.get('USERNAME', None))
parser.add_argument('-p', '--password', help="Account password", default=os.environ.get('PASSWORD', None))
parser.add_argument('-r', '--rabbit', help="Rabbit host name", default=os.environ.get('RABBIT_HOST', 'localhost'))
parser.add_argument('-g', '--graylog', help="Rabbit host name", default=os.environ.get('GRAYLOG_HOST', 'localhost'))
parser.add_argument('-c', '--channels', help="Channels name split by commas",
                    default=os.environ.get('CHANNELS', 'instagram'))

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s')
logger = None


class RabbitUnitOfWor:

    def __init__(self, host: str, channels: [str]):
        self._host = host
        self._channels = channels

    def start(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self._host))
        self.channel = self.connection.channel()
        for channel in self._channels:
            self.channel.queue_declare(queue=channel)

    def finish(self):
        self.connection.close()

    def out(self, data: str):
        for channel in self._channels:
            self.channel.basic_publish(exchange='',
                                       routing_key=channel,
                                       body=data)


def sleep_a_little():
    sleep(random.randint(25, 35))


Rabbit: RabbitUnitOfWor = None


def login(username: str, password: str):
    sleep_a_little()
    bot.login(username=username, password=password)


def get_user_following(username: str, next_max_id=None) -> List:
    sleep_a_little()
    user_id = get_user_id_from_username(bot, username)
    sleep_a_little()
    success = bot.api.get_user_followings(user_id, next_max_id)

    if not success:
        return get_user_following(username)

    partial_feed = bot.api.last_json

    users: List = partial_feed['users']

    if partial_feed.get('next_max_id', None) is None:
        return users
    else:
        return users + get_user_following(username, partial_feed['next_max_id'])


def write_out_user_feed(user_id: str, user) -> List:
    user_feed_items: List = []
    next_max_id = ""
    while True:
        sleep_a_little()
        success = bot.api.get_user_feed(user_id, next_max_id)
        if not success:
            continue

        partial_feed = bot.api.last_json

        user_feed_items += partial_feed['items']

        Rabbit.start()
        for item in partial_feed['items']:
            Rabbit.out(json.dumps({"user": user,
                                   "post": item}))

        logger.info(f"[POSTED] {len(partial_feed['items'])} posts of user {user['username']}")
        Rabbit.finish()

        if partial_feed.get('next_max_id', None) is None:
            return user_feed_items
        else:
            next_max_id = partial_feed['next_max_id']
            continue


def write_out_stories(user_id: str, user):
    bot.api.get_user_stories(user_id)
    if bot.api.last_json.get('reel', None) is not None and int(bot.api.last_json["reel"]["media_count"]) > 0:
        Rabbit.start()
        for item in bot.api.last_json["reel"]["items"]:
            Rabbit.out(json.dumps({"user": user,
                                   "post": item}))
        Rabbit.finish()


def feed(username: str):
    following = get_user_following(username)
    for user in following:
        write_out_stories(user['pk'], user)
        write_out_user_feed(user['pk'], user)


if __name__ == "__main__":
    try:
        args = parser.parse_args()
        username = args.username
        password = args.password
        logger = logging.getLogger("instabot version: " + api.version)
        handler = GELFTCPHandler(args.graylog, port=12202)
        logger.addHandler(handler)

        Rabbit = RabbitUnitOfWor(args.rabbit, args.channels.split(","))

        login(username, password)
        while True:
            sleep_a_little()
            feed(args.username)

    except Exception as e:
        logger.exception("An main error ocurred")
