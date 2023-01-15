# -*- coding: utf-8 -*-

from SAWP.SunbeltClientBase import SunbeltClientBase
from SAWP import generators

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
        data = next(self.search(self.kind, byId = self.zen_unique_id, *args))
        self._update_self_attrs(data)

    def __getattr__(self, name):

        # https://stackoverflow.com/a/61413243/11477615
        if name.startswith('_') or name in ['shape','size']:
            raise AttributeError
        try:
            return getattr(super().__getattribute__(name), name)
        except AttributeError:
            self._add_fields(name)
            return super().__getattribute__(name)





                
class Comment(SunbeltModelBase):
    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'comment'
        self.kinds = 'comments'
        self.zen_unique_id = data['zen_unique_id']

    def __repr__(self):
        return f'ZenComment({self.zen_unique_id})'
    

class Account(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'account'
        self.kinds = 'accounts'
        self.zen_unique_id = data['zen_unique_id']

    def __repr__(self):
        return f'ZenAccount({self.zen_unique_id})'

class Subreddit(SunbeltModelBase):
    
    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'subreddit'
        self.kinds = 'subreddits'
        self.zen_unique_id = data['zen_unique_id']

    def __repr__(self):
        return f'ZenSubreddit({self.zen_unique_id})'
    
class Post(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'post'
        self.kinds = 'posts'
        self.zen_unique_id = data['zen_unique_id']

    @property
    def author(self):
        return Account(next(self.search('account', byId = self.zen_account_id)), self.host)

    @property
    def versions(self):
        return generators.PostDetailGenerator(host = self.host, zen_post_id = self.zen_unique_id)


    def __repr__(self):
        return f'ZenPost({self.zen_unique_id})'

class PostDetail(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'postdetail'
        self.kinds = 'postdetails'
        self.zen_post_id = data['zen_unique_id']
        self.zen_version_id = data['zen_version_id']
        self.zen_unique_id = data['zen_detail_id']
        
    def __repr__(self):
        return f'PostVersion(ZenPost = {self.zen_post_id} , ZenVersion = {self.zen_version_id})'

class CommentDetail(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'commentdetail'
        self.kinds = 'commentdetails'
        self.zen_comment_id = data['zen_unique_id']
        self.zen_version_id = data['zen_version_id']
        self.zen_unique_id = data['zen_detail_id']
        
    def __repr__(self):
        return f'CommentVersion(ZenComment = {self.zen_comment_id} , ZenVersion = {self.zen_version_id})'

class SubredditDetail(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'subredditdetail'
        self.kinds = 'subredditdetails'
        self.zen_subreddit_id = data['zen_unique_id']
        self.zen_version_id = data['zen_version_id']
        self.zen_unique_id = data['zen_detail_id']
        
    def __repr__(self):
        return f'SubredditVersion(ZenSubreddit = {self.zen_subreddit_id} , ZenVersion = {self.zen_version_id})'

class AccountDetail(SunbeltModelBase):

    def __init__(self, data, host):
        self.data = data
        self.host = host
        self.kind = 'accountdetail'
        self.kinds = 'accountdetails'
        self.zen_account_id = data['zen_unique_id']
        self.zen_version_id = data['zen_version_id']
        self.zen_unique_id = data['zen_detail_id']
        
    def __repr__(self):
        return f'AccountVersion(ZenAccount = {self.zen_account_id} , ZenVersion = {self.zen_version_id})'
        
