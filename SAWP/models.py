# -*- coding: utf-8 -*-

from sawp.SunbeltClientBase import SunbeltClientBase
from sawp import generators

class SunbeltModelBase(SunbeltClientBase):
    def _update_self_attrs(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)
    
    def __init__(self, data, host):
        # This is not ideal because ideally the client base of the
        # client creating the object would already be the same as the models
        # client base or something like that
        self.host = host
        self._update_self_attrs(data)

    def _add_fields(self, *args):
        query = self.query(self.kind, byId = self.sun_unique_id, *args)
        try:
            data = next(query)
            self._update_self_attrs(data)
        except StopIteration as msg:
            raise AttributeError(msg)
        

    def __getattr__(self, name):

        # https://stackoverflow.com/a/61413243/11477615
        if name.startswith('_') or name in ['shape','size']:
            raise AttributeError
            
        # This is a mess and should be changed
        try:
            return getattr(super().__getattribute__(name), name)
        except AttributeError:
            try:
                self._add_fields(name)
                return super().__getattribute__(name)
            except AttributeError as msg:
                raise AttributeError(msg)

    def __repr__(self):
        return f'Sun{self.kind.capitalize()}({self.sun_unique_id})'

    def to_dict(self):
        return self.__dict__['data']




                
class Comment(SunbeltModelBase):
    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'comment'
        self.kinds = 'comments'
        self.sun_unique_id = data['sun_unique_id']
    

class Account(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'account'
        self.kinds = 'accounts'
        self.sun_unique_id = data['sun_unique_id']

class Subreddit(SunbeltModelBase):
    
    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'subreddit'
        self.kinds = 'subreddits'
        self.sun_unique_id = data['sun_unique_id']
    
class Post(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'post'
        self.kinds = 'posts'
        self.sun_unique_id = data['sun_unique_id']

    @property
    def author(self):
        return Account(next(self.query('account', byId = self.sun_account_id)), self.host)

    @property
    def versions(self):
        return generators.PostDetailGenerator(host = self.host, sun_post_id = self.sun_unique_id)

    @property
    def comments(self):
        return generators.CommentGenerator(host = self.host, sun_post_id = self.sun_unique_id)


class PostDetail(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'postdetail'
        self.kinds = 'postdetails'
        self.sun_post_id = data['sun_unique_id']
        self.sun_version_id = data['sun_version_id']
        self.sun_unique_id = data['sun_detail_id']
        
    def __repr__(self):
        return f'PostVersion(SunPost = {self.sun_post_id} , SunVersion = {self.sun_version_id})'

class CommentDetail(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'commentdetail'
        self.kinds = 'commentdetails'
        self.sun_comment_id = data['sun_unique_id']
        self.sun_version_id = data['sun_version_id']
        self.sun_unique_id = data['sun_detail_id']
        
    def __repr__(self):
        return f'CommentVersion(SunComment = {self.sun_comment_id} , SunVersion = {self.sun_version_id})'

class SubredditDetail(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'subredditdetail'
        self.kinds = 'subredditdetails'
        self.sun_subreddit_id = data['sun_unique_id']
        self.sun_version_id = data['sun_version_id']
        self.sun_unique_id = data['sun_detail_id']
        
    def __repr__(self):
        return f'SubredditVersion(SunSubreddit = {self.sun_subreddit_id} , SunVersion = {self.sun_version_id})'

class AccountDetail(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'accountdetail'
        self.kinds = 'accountdetails'
        self.sun_account_id = data['sun_unique_id']
        self.sun_version_id = data['sun_version_id']
        self.sun_unique_id = data['sun_detail_id']
        
    def __repr__(self):
        return f'AccountVersion(SunAccount = {self.sun_account_id} , SunVersion = {self.sun_version_id})'
        
