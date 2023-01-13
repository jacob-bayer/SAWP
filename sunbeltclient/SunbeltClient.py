# -*- coding: utf-8 -*-

from sunbeltclient import models
from sunbeltclient.SunbeltClientBase import SunbeltClientBase

class SunbeltClient(SunbeltClientBase):
    
    def posts(self, *args, **kwargs):
        data = self.search('posts', *args, **kwargs)
        for item in data:
            yield models.Post(item, self.host)
    
    @property
    def comments(self, *args, **kwargs):
        return models.CommentGenerator(self.host, *args, **kwargs)

        
    def subreddits(self, *args, **kwargs):
        data = self.search('subreddits', *args, **kwargs)
        for item in data:
            yield models.Subreddit(item, self.host)
    
    def accounts(self, *args, **kwargs):
        data = self.search('accounts', *args, **kwargs)
        for item in data:
            yield models.Account(item, self.host)
        
    def first():
        """
        Returns the first instance of the object from the database
        """
        try:
            return self.search(self.kind, ById = 1)
        except:
            return next(self.search(self.kinds))

        