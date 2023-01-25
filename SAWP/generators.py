# -*- coding: utf-8 -*-

from sawp.SunbeltClientBase import SunbeltClientBase
from sawp.models import Comment, Account, Subreddit, Post, PostDetail

class SunbeltReadGeneratorBase():
    
    def __init__(self):
        self.client = SunbeltClientBase(self.host)

    
    def _first(self, *args, **kwargs):
        """
        Returns the first instance of the object from the database
        """

        if 'sun_unique_id' in kwargs and kwargs['sun_unique_id'] is None:
            del kwargs['sun_unique_id']

        try:
            data = next(self.client.query(self.kind, byId = 1, **kwargs))
        except:
            data = next(self.client.query(self.kinds, orderBy = {'sun_unique_id': 'asc'}, **kwargs))

        return self.model(data, self.host)

    def _last(self, *args, **kwargs):
        """
        Returns the last instance of the object from the database
        """

        if 'sun_unique_id' in kwargs and kwargs['sun_unique_id'] is None:
             del kwargs['sun_unique_id']

        data = next(self.client.query(self.kinds, orderBy = {'sun_unique_id': 'desc'}))
        
        return self.model(data, self.host)

    def _all(self, *args, **kwargs):
        if 'sun_unique_id' in kwargs and kwargs['sun_unique_id'] is None:
             del kwargs['sun_unique_id']

        query = self.client.query(self.kinds, *args, **kwargs)
        return [self.model(data, self.host) for data in query]

    def search(self, kind = None, *args, **kwargs):
        if not kind:
            kind = self.kind
        query = self.client.query(kind, *args, **kwargs)
        # TODO: Query should return None instead of thowing 
        # an exception
        try:
            data = next(query)
            return self.model(data, self.host)
        except StopIteration as graphql_msg:
            return None
        
    
    def get(self, by_id):
        query = self.client.query(self.kind, byId = by_id)
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
        kwargs = {**kwargs, **self.query_kwargs}
        return self._all(*args, **kwargs)
    
    def first(self, *args, **kwargs):
        kwargs = {**kwargs, **self.query_kwargs}
        return self._first(*args, **kwargs)
    
    def last(self, *args, **kwargs):
        kwargs = {**kwargs, **self.query_kwargs}
        return self._last(*args, **kwargs)
                
class CommentGenerator(MainObjectGenerator):
    def __init__(self, host, sun_post_id = None, *args, **kwargs):
        self.host = host
        self.kind = 'comment'
        self.kinds = 'comments'
        self.model = Comment
        self.query_kwargs = {}
        super().__init__(*args, **kwargs)
        
        if sun_post_id:
            self.query_kwargs['sun_post_id'] = sun_post_id
            
        


        

class AccountGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'account'
        self.kinds = 'accounts'
        self.model = Account
        self.query_kwargs = {}
        super().__init__(*args, **kwargs)


class SubredditGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'subreddit'
        self.kinds = 'subreddits'
        self.model = Subreddit
        self.query_kwargs = {}
        super().__init__(*args, **kwargs)

    
class PostGenerator(MainObjectGenerator):
    def __init__(self, host, *args, **kwargs):
        self.host = host
        self.kind = 'post'
        self.kinds = 'posts'
        self.model = Post
        self.query_kwargs = {}
        super().__init__(*args, **kwargs)


class PostDetailGenerator(SunbeltReadGeneratorBase):
    def __init__(self, host, sun_post_id = None, *args, **kwargs):
        self.host = host
        self.kind = 'postdetail'
        self.kinds = 'postdetails'
        self.model = PostDetail
        self.query_kwargs = {}
        super().__init__(*args, **kwargs)

        if sun_post_id:
            self.sun_post_id = sun_post_id

    def all(self, *args, **kwargs):
        return self._all(sun_unique_id = self.sun_post_id, detail = True, *args, **kwargs)

    def first(self, *args, **kwargs):
        return self._first(sun_unique_id = self.sun_post_id, detail = True, *args, **kwargs)

    def last(self, *args, **kwargs):
        return self._last(sun_unique_id = self.sun_post_id, detail = True, *args, **kwargs)

    def __getattr__(self, name):

        # https://stackoverflow.com/a/61413243/11477615
        if name.startswith('_') or name in ['shape','size']:
            raise AttributeError
        else:
            setattr(self, name, [x.__getattr__(name) for x in self.all()])
            return getattr(self, name)
