# -*- coding: utf-8 -*-

from .models import models

class SunbeltReadGeneratorBase():
    """
    Base class for all SunbeltReadGenerators
    """
    
    def __init__(self, sunbelt):
        self._sunbelt = sunbelt

    
    def _first(self, *args, **kwargs):
        """
        Returns the first instance of the object from the database
        """

        if 'sun_unique_id' in kwargs and kwargs['sun_unique_id'] is None:
            del kwargs['sun_unique_id']

        try:
            data = next(self._sunbelt.query(self.kind, byId = 1, **kwargs))
        except:
            data = next(self._sunbelt.query(self.kinds, orderBy = {'sun_unique_id': 'asc'}, **kwargs))

        return self.model(self._sunbelt, data)

    def _last(self, *args, **kwargs):
        """
        Returns the last instance of the object from the database
        """

        if 'sun_unique_id' in kwargs and kwargs['sun_unique_id'] is None:
             del kwargs['sun_unique_id']

        data = next(self._sunbelt.query(self.kinds, orderBy = {'sun_unique_id': 'desc'}))
        
        return self.model(self._sunbelt, data)

    def _all(self, *args, **kwargs):
        if 'sun_unique_id' in kwargs and kwargs['sun_unique_id'] is None:
             del kwargs['sun_unique_id']
        query = self._sunbelt.query(self.kinds, *args, **kwargs)
        return [self.model(self._sunbelt, data) for data in query]

    def search(self, kind = None, *args, **kwargs):
        if not kind:
            kind = self.kind
        query = self._sunbelt.query(kind, *args, **kwargs)
        # TODO: Query should return None instead of thowing 
        # an exception
        try:
            data = next(query)
            return self.model(self._sunbelt, data)
        except StopIteration as graphql_msg:
            return None
        
    
    def get(self, by_id):
        return self.search(self.kind, 'sun_unique_id', byId = by_id)

class SunbeltWriteGeneratorBase():
    """
    Base class for all SunbeltWriteGenerators
    """

    
    def __init__(self, sunbelt):
        self._sunbelt = sunbelt
    
    def create(self, from_json ):
        result = self._sunbelt.mutation(self.kind, from_json)
        return result
        

class MainObjectGenerator(SunbeltReadGeneratorBase, SunbeltWriteGeneratorBase):
    """
    Base class for all SunbeltReadGenerators
    """

    def __init__(self, sunbelt):
        super().__init__(sunbelt)

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

    def __init__(self, sunbelt, sun_post_id = None):
        self.kind = 'comment'
        self.kinds = 'comments'
        self.model = models.Comment
        self.query_kwargs = {}
        super().__init__(sunbelt)
        
        if sun_post_id:
            self.query_kwargs['sun_post_id'] = sun_post_id
            

class PostDetailGenerator(SunbeltReadGeneratorBase):
    def __init__(self, sunbelt, sun_post_id = None):
        self.kind = 'postdetail'
        self.kinds = 'postdetails'
        self.model = models.PostDetail
        self.query_kwargs = {}
        super().__init__(sunbelt)

        if sun_post_id:
            self.sun_post_id = sun_post_id
        else:
            self.sun_post_id = None

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


class CommentDetailGenerator(SunbeltReadGeneratorBase):
    def __init__(self, sunbelt, sun_comment_id = None):
        self.kind = 'commentdetail'
        self.kinds = 'commentdetails'
        self.model = models.CommentDetail
        self.query_kwargs = {}
        super().__init__(sunbelt)

        if sun_comment_id:
            self.sun_comment_id = sun_comment_id
        else:
            self.sun_comment_id = None

    def all(self, *args, **kwargs):
        return self._all(sun_unique_id = self.sun_comment_id, detail = True, *args, **kwargs)

    def first(self, *args, **kwargs):
        return self._first(sun_unique_id = self.sun_comment_id, detail = True, *args, **kwargs)

    def last(self, *args, **kwargs):
        return self._last(sun_unique_id = self.sun_comment_id, detail = True, *args, **kwargs)

    def __getattr__(self, name):

        # https://stackoverflow.com/a/61413243/11477615
        if name.startswith('_') or name in ['shape','size']:
            raise AttributeError
        else:
            setattr(self, name, [x.__getattr__(name) for x in self.all()])
            return getattr(self, name)


class AccountGenerator(MainObjectGenerator):
    def __init__(self, sunbelt):
        self.kind = 'account'
        self.kinds = 'accounts'
        self.model = models.Account
        self.query_kwargs = {}
        super().__init__(sunbelt)


class SubredditGenerator(MainObjectGenerator):
    def __init__(self, sunbelt):
        self.kind = 'subreddit'
        self.kinds = 'subreddits'
        self.model = models.Subreddit
        self.query_kwargs = {}
        super().__init__(sunbelt)

    
class PostGenerator(MainObjectGenerator):
    def __init__(self, sunbelt):
        self.kind = 'post'
        self.kinds = 'posts'
        self.model = models.Post
        self.query_kwargs = {}
        super().__init__(sunbelt)

