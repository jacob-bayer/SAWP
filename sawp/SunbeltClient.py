# -*- coding: utf-8 -*-

from .base import SunbeltClientBase
from .generators import generators

class SunbeltClient(SunbeltClientBase):

    def __init__(self, username = None, password = None, host = 'local', disable_postfetching = False):
        hosts = {'local': "http://127.0.0.1:5000",
                 'heroku' : 'https://sunbelt.herokuapp.com',
                 'prod' : ''}

        host = hosts[host]
        self._authenticated = False
        self.current_user = None
        self.host = host
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

    # This is if args need to be added to the generator which shouldn't happen anymore
    # Post.comments, for example are now going to be loaded correctly from graphql using the query subfields arg

    # @property
    # def posts(self):
    #     return generators.PostGenerator(self)
    
    # @property
    # def comments(self):
    #     return generators.CommentGenerator(self)

    # @property
    # def accounts(self):
    #     return generators.AccountGenerator(self)

    # @property
    # def subreddits(self):
    #     return generators.SubredditGenerator(self)

    # @property
    # def post_details(self):
    #     return generators.PostDetailGenerator(self)

    # @property
    # def comment_details(self):
    #     return generators.CommentDetailGenerator(self)


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