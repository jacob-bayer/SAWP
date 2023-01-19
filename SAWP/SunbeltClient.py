# -*- coding: utf-8 -*-

from SAWP import generators
from SAWP.SunbeltClientBase import SunbeltClientBase

class SunbeltClient(SunbeltClientBase):
    
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

        