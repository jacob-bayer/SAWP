# -*- coding: utf-8 -*-

from .models import models
from itertools import chain


class SunbeltReadGeneratorBase():
    """
    Base class for all SunbeltReadGenerators
    """
    
    def __init__(self, sunbelt):
        self._sunbelt = sunbelt

    
    def _first(self, fields = None, subfields = None):
        """
        Returns the first instance of the object from the database
        """

        #if 'sun_unique_id' in kwargs and kwargs['sun_unique_id'] is None:
        #    del kwargs['sun_unique_id']

        data = next(self._sunbelt.query(self.kinds, fields = fields, 
                                            subfields = subfields,
                                            orderBy = {'sun_unique_id': 'asc'}, 
                                            limit = 1))
        if data:
            return self.model(self._sunbelt, data)


    def _last(self, fields = None, subfields = None):
        """
        Returns the last instance of the object from the database
        """

        #if 'sun_unique_id' in kwargs and kwargs['sun_unique_id'] is None:
        #     del kwargs['sun_unique_id']

        data = next(self._sunbelt.query(self.kinds, fields = fields, 
                                        subfields = subfields,
                                        orderBy = {'sun_unique_id': 'desc'},
                                        limit = 1))
        
        if data:
            return self.model(self._sunbelt, data)


    def search(self, fields = None, subfields = None, **kwargs):
        """
        Returns objs
        """
        
        hard_limit = kwargs.pop('limit', None)
        limit = 10000 #basically not active but it's ready to be used. Just make the number lower.
        kwargs['limit'] = limit = min(limit, hard_limit) if hard_limit else limit
        kwargs['offset'] = 0

        all_results = []
        all_results_count = 0
        while True:
            query = self._sunbelt.query(self.kinds, fields = fields, 
                                           subfields = subfields,
                                           using_pagination = True,
                                           **kwargs)
            
            results = list(query)
            
            if any(results):
                all_results_count += len(results)
                print('\r', all_results_count,' loaded', end = '')
                all_results += results
                kwargs['offset'] += limit
                
                if hard_limit and all_results_count >= hard_limit:
                    break
            else:
                break

        return [self.model(self._sunbelt, x) for x in all_results]

    
    def search_generator(self, fields = None, subfields = None, **kwargs):

        """
        Alias for query but for self.kinds
        """
        
        query = self._sunbelt.query(self.kinds, fields = fields, 
                                    subfields = subfields, **kwargs)
        for data in query:
            if data:
                yield self.model(self._sunbelt, data)
        
    def _all(self, fields = None, subfields = None, limit = None):
        """
        Alias for search but uses no search terms
        """
        kwargs = {}
        if limit:
            kwargs['limit'] = limit

        # Returns a generator
        return self.search(fields = fields,
                           subfields = subfields, **kwargs)    


    def get(self, sun_or_reddit_id, fields = None, subfields = None):
        """
        Returns the first object with the given sun_unique_id or reddit_unique_id
        """
        if isinstance(sun_or_reddit_id, str):
            kwargs = {'reddit_id': sun_or_reddit_id}
        else:
            kwargs = {'byId': sun_or_reddit_id}

        data = self._sunbelt.query(self.kind, fields = fields, 
                                   subfields = subfields, **kwargs)
        if data:
            return self.model(self._sunbelt, data)

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

