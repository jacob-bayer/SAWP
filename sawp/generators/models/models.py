# -*- coding: utf-8 -*-

# TODO:
# Try to use graphql sub objects 
# like comment {subreddit {etc...}}

class SunbeltModelBase():
    def _update_self_attrs(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)
    
    def __init__(self, sunbelt, data):
        self.__dict__.update(data)
        self._sunbelt = sunbelt


    def _add_fields(self, *fields):
        # Can only take fields, not subfields
        data = self._sunbelt.query(self.kind, byId = self.uid, 
                                    fields = list(fields))
        if data:
            self._update_self_attrs(data)
        


    def __getattr__(self, name):
        
        #breakpoint()
        # https://stackoverflow.com/a/61413243/11477615
        if name.startswith('_') or name in ['shape','size']:
            raise AttributeError
            
        # This is a mess and should be changed
        
        try:
            return getattr(super().__getattribute__(name), name)
        except AttributeError:
            try:
                # Adding subfields should be done via the model
                self._add_fields(name)
                return super().__getattribute__(name)
            except AttributeError as msg:
                raise AttributeError(msg)


    def __repr__(self):
        return f'Sun{self.kind.capitalize()}({self.sun_unique_id})'

    def to_dict(self):
        fields_to_del = ['data','kinds','_sunbelt','sun_unique_id']
        return {k:v for k,v in self.__dict__.items() if k not in fields_to_del}

class Account(SunbeltModelBase):

    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'account'
        self.kinds = 'accounts'
        self.uid = data['sun_unique_id']
        super().__init__(sunbelt, data)

    def comments(self):
        return self._sunbelt.comments.search(sun_account_id = self.sun_unique_id)

class Subreddit(SunbeltModelBase):
    
    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'subreddit'
        self.kinds = 'subreddits'
        self.uid = data['sun_unique_id']
        super().__init__(sunbelt, data)
    
class Post(SunbeltModelBase):

    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'post'
        self.kinds = 'posts'
        self.uid = data['sun_unique_id']
        super().__init__(sunbelt, data)

    @property
    def author(self):
        if self.sun_account_id:
            return self._sunbelt.accounts.get(self.sun_account_id)
        else:
            return None

    @property
    def versions(self):
        if 'versions' not in self.data:
            data_w_version = self._sunbelt.query(self.kind, byId = self.uid, 
                                        subfields = {'versions' : {
                                            'sun_unique_id',
                                            'sun_post_version_id',
                                            'sun_detail_id'}})
        else:
            data_w_version = self.data
            
        for version_data in data_w_version['versions']:
            yield PostDetail(self._sunbelt, version_data)
    
    @property
    def comments(self):
        return self._sunbelt.comments.search(sun_post_id = self.sun_unique_id)
     
    @property
    def subreddit(self):
        if 'subreddit' not in self.data:
            data_w_subreddit = self._sunbelt.query(self.kind, byId = self.uid, 
                                        subfields = {'subreddits' : {
                                            'sun_unique_id', 'display_name'}})
        else:
            data_w_subreddit = self.data
            
        return Subreddit(self._sunbelt, data_w_subreddit['subreddit'])
            
        
class CommentDetail(SunbeltModelBase):

    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'commentdetail'
        self.kinds = 'commentdetails'
        super().__init__(sunbelt, data)
        
        # This overrides the data that was put in, which is necessary
        # if you want these to be the final values
        self.sun_comment_id = data['sun_unique_id']
        self.uid = data['sun_detail_id']

        
        
    def __repr__(self):
        return f'CommentVersion(SunComment = {self.sun_comment_id} , SunVersion = {self.sun_version_id})'


class Comment(SunbeltModelBase):
    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'comment'
        self.kinds = 'comments'
        self.uid = data['sun_unique_id']
        super().__init__(sunbelt, data)

    @property
    def author(self):
        if self.sun_account_id:
            return self._sunbelt.accounts.get(self.sun_account_id)
        else:
            return None

    @property
    def versions(self):
        if 'versions' not in self.data:
            data_w_version = self._sunbelt.query(self.kind, byId = self.uid, 
                                        subfields = {'versions' : {
                                            'sun_unique_id',
                                            'sun_comment_version_id',
                                            'sun_detail_id'}})
        else:
            data_w_version = self.data
            
        for version_data in data_w_version['versions']:
            yield CommentDetail(self._sunbelt, version_data)


                
    @property
    def post(self):
        if 'post' not in self.data:
            data_w_post = self._sunbelt.query(self.kind, byId = self.uid, 
                                        subfields = {'post' : {
                                            'sun_unique_id'}})
        else:
            data_w_post = self.data
        
        post_data = data_w_post['post']
        if post_data:
            return Post(self._sunbelt, post_data)

    @property
    def parent(self):
        if self.reddit_parent_id:
            return self._sunbelt.comments.get(self.reddit_parent_id) or self._sunbelt.posts.get(self.reddit_parent_id)

    @property
    def subreddit(self):
        if 'subreddit' not in self.data:
            data_w_subreddit = self._sunbelt.query(self.kind, byId = self.uid, 
                                        subfields = {'subreddit' : {
                                            'sun_unique_id', 'display_name'}})
        else:
            data_w_subreddit = self.data
            
        return Subreddit(self._sunbelt, data_w_subreddit['subreddit'])

    
class PostDetail(SunbeltModelBase):

    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'postdetail'
        self.kinds = 'postdetails'
        super().__init__(sunbelt, data)
        
        # This overrides the data that was put in, which is necessary
        # if you want these to be the final values
        self.sun_post_id = data['sun_unique_id']
        self.uid = data['sun_detail_id']
        
    def __repr__(self):
        return f'PostVersion(SunPost = {self.sun_post_id} , SunVersion = {self.sun_version_id})'


class SubredditDetail(SunbeltModelBase):

    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'subredditdetail'
        self.kinds = 'subredditdetails'
        super().__init__(sunbelt, data)
        
        # This overrides the data that was put in, which is necessary
        # if you want these to be the final values
        self.sun_subreddit_id = data['sun_unique_id']
        self.uid = data['sun_detail_id']
        
        
    def __repr__(self):
        return f'SubredditVersion(SunSubreddit = {self.sun_subreddit_id} , SunVersion = {self.sun_version_id})'

class AccountDetail(SunbeltModelBase):

    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'accountdetail'
        self.kinds = 'accountdetails'
        super().__init__(sunbelt, data)
        self.sun_account_id = data['sun_unique_id']
        self.uid = data['sun_detail_id']

        
    def __repr__(self):
        return f'AccountVersion(SunAccount = {self.sun_account_id} , SunVersion = {self.sun_version_id})'
        
