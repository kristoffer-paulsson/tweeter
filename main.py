import datetime
import time
import re
from random import Random

import yaml
from twitter import Twitter, OAuth
from flask import Flask


app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello world!'


@app.route('/retweet/<tlist>/<ttimes>')
def tweeter(tlist, ttimes='1'):
    ttimes = int(ttimes) if int(ttimes) > 0 else 1

    with open('./config.yaml', 'r') as stream:
        config = yaml.load(stream)

    with open('tweets/' + tlist + '.yaml', 'r') as stream:
        tweets = yaml.load(stream)

    today = datetime.datetime.now()
    Random(today.year + int(ttimes/24*today.hour)).shuffle(tweets)
    regex = re.compile('\/([\d].*)$')
    tweet = regex.findall(
        tweets[len(tweets) & today.timetuple().tm_yday])[0]

    twitter = Twitter(auth=OAuth(
        config['token'], config['token_secret'],
        config['consumer_key'], config['consumer_secret']))

    twitter.statuses.unretweet(id=tweet)
    time.sleep(5)
    twitter.statuses.retweet(id=tweet)

    return ''


if __name__ == '__main__':
    app.run()
