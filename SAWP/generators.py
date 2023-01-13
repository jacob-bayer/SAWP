# -*- coding: utf-8 -*-

from SAWP.SunbeltClientBase import SunbeltClientBase
from SAWP.models import Comment, Account, Subreddit, Post

class SunbeltGeneratorBase(SunbeltClientBase):
    
    def first(self, *args, **kwargs):
        """
        Returns the first instance of the object from the database
        """
        try:
            data = next(self.search(self.kind, ById = 1))
        except:
            data = next(self.search(self.kinds))
        return self.model(data, self.host)

    def all(self, *args, **kwargs):
        for data in self.search(self.kinds, *args, **kwargs):
            yield self.model(data, self.host)

    def get(self, zen_id, *args):
        data = next(self.search(self.kind, ById = zen_id, *args))
        return self.model(data, self.host)
                
class CommentGenerator(SunbeltGeneratorBase):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'comment'
        self.kinds = 'comments'
        self.model = Comment


class AccountGenerator(SunbeltGeneratorBase):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'account'
        self.kinds = 'accounts'
        self.model = Account

class SubredditGenerator(SunbeltGeneratorBase):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'subreddit'
        self.kinds = 'subreddits'
        self.model = Subreddit
    
class PostGenerator(SunbeltGeneratorBase):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'post'
        self.kinds = 'posts'
        self.model = Post
    

