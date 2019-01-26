import datetime
import time
import logging
import re
from random import Random

import yaml
from twitter import Twitter, OAuth
from flask import Flask, abort


app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello world!'


@app.route('/retweet/<tlist>/<ttimes>')
def tweeter(tlist, ttimes='1'):
    logger.info('/retweet/' + tlist + '/' + ttimes)
    ttimes = int(ttimes) if int(ttimes) > 0 else 1

    try:
        logger.info('Loading configuration.')
        with open('./config.yaml', 'r') as stream:
            config = yaml.load(stream)

        logger.info('Loading tweets.')
        with open('tweets/' + tlist + '.yaml', 'r') as stream:
            tweets = yaml.load(stream)

    except Exception as e:
        logger.error('Failed to load confugration or data.', e)
        abort(500)

    today = datetime.datetime.now()
    Random(today.year + int(ttimes/24*today.hour)).shuffle(tweets)
    regex = re.compile('\/([\d].*)$')
    tweet = regex.findall(
        tweets[len(tweets) & today.timetuple().tm_yday])[0]

    try:
        logger.info('Authenticates against Twitter OAuth.')
        twitter = Twitter(auth=OAuth(
            config['token'], config['token_secret'],
            config['consumer_key'], config['consumer_secret']))

        logger.info('Unretweet status with id: ' + tweet)
        twitter.statuses.unretweet(id=tweet)
        time.sleep(5)
        logger.info('Retweet status with id: ' + tweet)
        twitter.statuses.retweet(id=tweet)
    except Exception as e:
        logger.error('Failed to interact with twitter', e)
        abort(500)


logger = logging.getLogger()

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
