# -*- coding: utf-8 -*-

from .base import SunbeltClientBase
from .generators import generators

class SunbeltClient(SunbeltClientBase):
    
    def __init__(self, server = 'heroku'):
        servers = {'local': "http://127.0.0.1:5000/graphql",
                 'heroku' : 'https://sunbelt.herokuapp.com/graphql',
                 'prod' : ''}
        self.host = hosts[server]
        super().__init__(self.host)
    

    @property
    def posts(self):
        return generators.PostGenerator(self)
    
    @property
    def comments(self):
        return generators.CommentGenerator(self)

    @property
    def accounts(self):
        return generators.AccountGenerator(self)

    @property
    def subreddits(self):
        return generators.SubredditGenerator(self)

    @property
    def post_details(self):
        return generators.PostDetailGenerator(self)

    @property
    def comment_details(self):
        return generators.CommentDetailGenerator(self)

        