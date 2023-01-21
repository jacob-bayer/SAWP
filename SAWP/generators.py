# -*- coding: utf-8 -*-

from SAWP.SunbeltClientBase import SunbeltClientBase
from SAWP.models import Comment, Account, Subreddit, Post, PostDetail

class SunbeltReadGeneratorBase():
    
    def __init__(self):
        self.client = SunbeltClientBase(self.host)

    
    def _first(self, *args, **kwargs):
        """
        Returns the first instance of the object from the database
        """

        if 'zen_unique_id' in kwargs and kwargs['zen_unique_id'] is None:
            del kwargs['zen_unique_id']

        try:
            data = next(self.client.query(self.kind, byId = 1, **kwargs))
        except:
            data = next(self.client.query(self.kinds, orderBy = {'zen_unique_id': 'asc'}, **kwargs))

        return self.model(data, self.host)

    def _last(self, *args, **kwargs):
        """
        Returns the last instance of the object from the database
        """

        if 'zen_unique_id' in kwargs and kwargs['zen_unique_id'] is None:
             del kwargs['zen_unique_id']

        data = next(self.client.query(self.kinds, orderBy = {'zen_unique_id': 'desc'}))
        
        return self.model(data, self.host)

    def _all(self, *args, **kwargs):
        if 'zen_unique_id' in kwargs and kwargs['zen_unique_id'] is None:
             del kwargs['zen_unique_id']

        for data in self.client.query(self.kinds, *args, **kwargs):
            yield self.model(data, self.host)

    def search(self, kind = None, *args, **kwargs):
        if not kind:
            kind = self.kind
        query = self.client.query(kind, *args, **kwargs)
        data = next(query)
        return self.model(data, self.host)

class SunbeltWriteGeneratorBase():
    
    def __init__(self):
        self.client = SunbeltClientBase(self.host)
    
    def create(self, from_json ):
        result = self.client.mutation(self.kind, from_json)
        return result
        

class MainObjectGenerator(SunbeltReadGeneratorBase, SunbeltWriteGeneratorBase):
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
        super().__init__(*args, **kwargs)


class AccountGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'account'
        self.kinds = 'accounts'
        self.model = Account
        super().__init__(*args, **kwargs)


class SubredditGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'subreddit'
        self.kinds = 'subreddits'
        self.model = Subreddit
        super().__init__(*args, **kwargs)

    
class PostGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'post'
        self.kinds = 'posts'
        self.model = Post
        super().__init__(*args, **kwargs)


class PostDetailGenerator(SunbeltReadGeneratorBase):
    def __init__(self, host, zen_post_id = None, *args, **kwargs):
        self.host = host
        self.kind = 'postdetail'
        self.kinds = 'postdetails'
        self.model = PostDetail
        super().__init__(*args, **kwargs)

        if zen_post_id:
            self.zen_post_id = zen_post_id

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
