
import json


class Reddit:
    reddit_info = {}

    def parser(self, info):

        min_info = info[0]['data']['children'][0]['data']
        self.reddit_info['subreddit'] = min_info['subreddit']
        self.reddit_info['titulo'] = min_info['title']
        self.reddit_info['texto'] = min_info['selftext']
        self.reddit_info['aprobacion'] = min_info['upvote_ratio']
        self.reddit_info['url'] = min_info['url']

    def __init__(self, stream):
        info = json.load(stream)
        self.parser(info)

    def info(self):
        return self.reddit_info
