from typing import Any, Set, List
import os
import pika

from instabot import Bot
from time import sleep
import argparse
import random
import json
import logging
from instabot.bot.bot_get import get_user_id_from_username

bot = Bot()
parser = argparse.ArgumentParser(description="Download videos and photos for all followings")
parser.add_argument('-u', '--username', help="Account username", default=os.environ.get('USERNAME', None))
parser.add_argument('-p', '--password', help="Account password", default=os.environ.get('PASSWORD', None))
parser.add_argument('-r', '--rabbit', help="Rabbit host name", default=os.environ.get('RABBIT_HOST', 'localhost'))

logging.basicConfig(filename='out/app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')


def sleep_a_little():
    sleep(random.randint(21, 30))


def login(username: str, password: str):
    sleep_a_little()
    bot.login(username=username, password=password)


def get_user_following(username: str, next_max_id=None) -> List:
    sleep_a_little()
    user_id = get_user_id_from_username(bot, username)
    sleep_a_little()
    success = bot.api.get_user_followings(user_id, next_max_id)

    if not success:
        raise Exception("Something went wrong at `get_user_following`, you should take a look at it")

    partial_feed = bot.api.last_json

    users: List = partial_feed['users']

    if partial_feed.get('next_max_id', None) is None:
        return users
    else:
        return users + get_user_following(username, partial_feed['next_max_id'])


def write_out_user_feed(user_id: str, user, out) -> List:
    user_feed_items: List = []
    next_max_id = ""
    while True:
        sleep_a_little()
        success = bot.api.get_user_feed(user_id, next_max_id)
        if not success:
            raise Exception("Something went wrong at `get_user_feed`, you should take a look at it")

        partial_feed = bot.api.last_json

        user_feed_items += partial_feed['items']

        for item in partial_feed['items']:
            out(json.dumps({"user": user,
                            "post": item}))

        if partial_feed.get('next_max_id', None) is None:
            return user_feed_items
        else:
            next_max_id = partial_feed['next_max_id']
            continue


def feed(username: str, out: Any):
    following = get_user_following(username)
    for user in following:
        write_out_user_feed(user['pk'], user, out)


def wrap_rabbit_out(hostname: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(hostname))
    channel = connection.channel()
    channel.queue_declare(queue='instagram')

    def out(data: str):
        channel.basic_publish(exchange='',
                              routing_key='instagram',
                              body=data)

    return out


if __name__ == "__main__":
    try:
        args = parser.parse_args()
        username = args.username
        password = args.password

        out = wrap_rabbit_out(args.rabbit)

        login(username, password)
        while True:
            sleep_a_little()
            feed(args.username, out)

    except Exception as e:
        logging.exception("An main error ocurred")
