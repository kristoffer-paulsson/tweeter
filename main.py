import datetime
import time
import re
from random import Random

import yaml
from twitter import Twitter, OAuth
from flask import Flask, request, abort


app = Flask(__name__)


@app.route('/retweet/<tlist>/<ttimes>')
def tweeter(tlist, ttimes='1'):
    if 'X-Appengine-Cron' not in request.headers:
        return abort(400)

    ttimes = int(ttimes) if int(ttimes) > 0 else 1

    with open('./config.yaml', 'r') as stream:
        config = yaml.load(stream)

    with open('tweets/' + tlist + '.yaml', 'r') as stream:
        tweets = yaml.load(stream)

    today = datetime.datetime.now()
    Random(today.year + int(ttimes/24*today.hour)).shuffle(tweets)
    regex = re.compile('\/([\d].*)$')
    tweet = regex.findall(
        tweets[(today.timetuple().tm_yday-1) % len(tweets)])[0]

    twitter = Twitter(auth=OAuth(
        config['token'], config['token_secret'],
        config['consumer_key'], config['consumer_secret']))

    twitter.statuses.unretweet(id=tweet)
    time.sleep(5)
    twitter.statuses.retweet(id=tweet)

    return '', 200


@app.route('/shoutout')
def shoutout():
    # if 'X-Appengine-Cron' not in request.headers:
    #    return abort(400)

    with open('./config.yaml', 'r') as stream:
        config = yaml.load(stream)

    twitter = Twitter(auth=OAuth(
        config['token'], config['token_secret'],
        config['consumer_key'], config['consumer_secret']))

    statuses = twitter.statuses.retweets_of_me(
        count=100, include_user_entities=True)

    today = datetime.date.today()
    screen_names = []
    for i in statuses:
        created = datetime.datetime.strptime(
            i['created_at'], '%a %b %d %H:%M:%S +0000 %Y').date()
        if today == created:  # FIX last 24 hours
            screen_names.append('@' + i['user']['screen_name'])

    if len(screen_names):
        time.sleep(3)
        twitter.statuses.update(
            status='Thank you for RT!\n\n' + ', '.join(screen_names))

    return '', 200


if __name__ == '__main__':
    app.run()
