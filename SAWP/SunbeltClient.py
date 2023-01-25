# -*- coding: utf-8 -*-

from sawp import generators
from sawp.SunbeltClientBase import SunbeltClientBase

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
        return generators.PostGenerator(self.host)
    
    @property
    def comments(self):
        return generators.CommentGenerator(self.host)

    @property
    def accounts(self):
        return generators.AccountGenerator(self.host)

    @property
    def subreddits(self):
        return generators.SubredditGenerator(self.host)

    @property
    def post_details(self):
        return generators.PostDetailGenerator(self.host)

        