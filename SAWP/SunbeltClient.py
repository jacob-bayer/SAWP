# -*- coding: utf-8 -*-

from .base import SunbeltClientBase
from .generators import generators

class SunbeltClient(SunbeltClientBase):
    
    def __init__(self, env = 'dev'):
        hosts = {'local': "http://127.0.0.1:5000/graphql",
                 'dev_gcloud' : 'https://sunbeltapi.uc.r.appspot.com/graphql',
                 'dev' : 'https://sunbelt.herokuapp.com/graphql',
                  'prod' : ''}
        self.host = hosts[env]
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
    def post_details(self):#, sun_post_id = None):
        return generators.PostDetailGenerator(self)#, sun_post_id = sun_post_id)

    @property
    def comment_details(self):#, sun_comment_id = None):
        return generators.CommentDetailGenerator(self)#, sun_comment_id = sun_comment_id)

        