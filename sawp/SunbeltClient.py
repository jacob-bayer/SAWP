# -*- coding: utf-8 -*-

from .base import SunbeltClientBase
from .generators import generators

class SunbeltClient(SunbeltClientBase):

    def __init__(self, username = None, password = None, dev = False, disable_postfetching = False):

        if dev:
            self.host = "http://127.0.0.1:5000"
        else:
            self.host = 'https://sunbelt.herokuapp.com'
            
        self._authenticated = False
        self.current_user = None
        self.graphql_url = self.host + '/graphql'

        if username and password:
            self._authenticate(host, username, password)
            self.current_user = username
        
        self._disable_postfetching = disable_postfetching

        self.posts = generators.PostGenerator(self)
        self.comments = generators.CommentGenerator(self)
        self.accounts = generators.AccountGenerator(self)
        self.subreddits = generators.SubredditGenerator(self)
        self.post_details = generators.PostDetailGenerator(self)
        self.comment_details = generators.CommentDetailGenerator(self)


        self.generator_lookup = {'posts': self.posts,
                                'comments': self.comments,
                                'accounts': self.accounts,
                                'subreddits': self.subreddits,
                                'postdetails': self.post_details,
                                'commentdetails': self.comment_details}


    def search(self, kind, limit = None, fields = [], **kwargs):
        """
        Access the search method of the generators by passing a string
        
        """

        if kind in ['post', 'comment', 'account', 'subreddit', 'postdetail', 'commentdetail']:
            kind = kind + 's'

        if kind not in ['posts', 'comments', 'accounts', 'subreddits', 'postdetails', 'commentdetails']:
            raise Exception('Invalid kind')

        generator = self.generator_lookup[kind]
        return generator.search(limit = limit, fields = fields, **kwargs)