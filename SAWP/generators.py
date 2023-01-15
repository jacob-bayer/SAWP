# -*- coding: utf-8 -*-

from SAWP.SunbeltClientBase import SunbeltClientBase
from SAWP.models import Comment, Account, Subreddit, Post, PostDetail

class SunbeltGeneratorBase(SunbeltClientBase):
    
    def _first(self, *args, **kwargs):
        """
        Returns the first instance of the object from the database
        """

        if 'zen_unique_id' in kwargs and kwargs['zen_unique_id'] is None:
            del kwargs['zen_unique_id']

        try:
            data = next(self.search(self.kind, byId = 1, **kwargs))
        except:
            data = next(self.search(self.kinds, orderBy = {'zen_unique_id': 'asc'}, **kwargs))
        return self.model(data, self.host)

    def _last(self, *args, **kwargs):
        """
        Returns the last instance of the object from the database
        """

        if 'zen_unique_id' in kwargs and kwargs['zen_unique_id'] is None:
             del kwargs['zen_unique_id']

        data = next(self.search(self.kinds, orderBy = {'zen_unique_id': 'desc'}))
        return self.model(data, self.host)

    def _all(self, *args, **kwargs):
        if 'zen_unique_id' in kwargs and kwargs['zen_unique_id'] is None:
             del kwargs['zen_unique_id']

        for data in self.search(self.kinds, *args, **kwargs):
            yield self.model(data, self.host)

    def get(self, zen_id, *args):
        data = next(self.search(self.kind, byId = zen_id, *args))
        return self.model(data, self.host)

class MainObjectGenerator(SunbeltGeneratorBase):
    def all(self, *args, **kwargs):
        return self._all(*args, **kwargs)
    
    def first(self, *args, **kwargs):
        return self._first(*args, **kwargs)
    
    def last(self, *args, **kwargs):
        return self._last(*args, **kwargs)

                
class CommentGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'comment'
        self.kinds = 'comments'
        self.model = Comment


class AccountGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'account'
        self.kinds = 'accounts'
        self.model = Account

class SubredditGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'subreddit'
        self.kinds = 'subreddits'
        self.model = Subreddit
    
class PostGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'post'
        self.kinds = 'posts'
        self.model = Post

class PostDetailGenerator(SunbeltGeneratorBase):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'postdetail'
        self.kinds = 'postdetails'
        self.model = PostDetail

        self.zen_post_id = kwargs.get('zen_post_id')

    def all(self, *args, **kwargs):
        return self._all(zen_unique_id = self.zen_post_id, detail = True, *args, **kwargs)

    def first(self, *args, **kwargs):
        return self._first(zen_unique_id = self.zen_post_id, detail = True, *args, **kwargs)

    def last(self, *args, **kwargs):
        return self._last(zen_unique_id = self.zen_post_id, detail = True, *args, **kwargs)

    def __getattr__(self, name):

        # https://stackoverflow.com/a/61413243/11477615
        if name.startswith('_') or name in ['shape','size']:
            raise AttributeError
        else:
            setattr(self, name, [x.__getattr__(name) for x in self.all()])
            return getattr(self, name)
