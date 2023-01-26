# -*- coding: utf-8 -*-

# There are three ways to do this. One involves returning generators for the versions
# properties, which means a model needs to have a host pased to it, the other involves
# instantiating a client here and using that to get the versions. The other involves adding
# a client attribute to the model base. I think the second is the best, but I'm not sure.


class SunbeltModelBase():
    def _update_self_attrs(self, data):
        for attr, value in data.items():
            setattr(self, attr, value)
    
    def __init__(self, sunbelt, data):
        self._update_self_attrs(data)
        self._sunbelt = sunbelt

    def _add_fields(self, *args):
        query = self._sunbelt.query(self.kind, byId = self.uid, *args)
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
        fields_to_del = ['data','kinds','_sunbelt','sun_unique_id']
        return {k:v for k,v in self.__dict__.items() if k not in fields_to_del}

class Account(SunbeltModelBase):

    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'account'
        self.kinds = 'accounts'
        self.uid = data['sun_unique_id']
        super().__init__(sunbelt, data)

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
        return self._sunbelt.accounts.get(self.sun_account_id)

    @property
    def versions(self):
        return self._sunbelt.post_details.all(sun_post_id = self.sun_unique_id)

    @property
    def comments(self):
        return self._sunbelt.comments.all(sun_post_id = self.sun_unique_id)
      
class Comment(SunbeltModelBase):
    def __init__(self, sunbelt, data):
        self.data = data
        self.kind = 'comment'
        self.kinds = 'comments'
        self.uid = data['sun_unique_id']
        super().__init__(sunbelt, data)

    @property
    def author(self):
        return self._sunbelt.accounts.get(self.sun_account_id)

    @property
    def versions(self):
        return self._sunbelt.comment_details.all(sun_comment_id = self.sun_unique_id)

    @property
    def post(self):
        return self._sunbelt.posts.get(self.sun_post_id)

    @property
    def parent(self):
        if self.sun_parent_id:
            return self._sunbelt.comments.get(self.sun_parent_id) or self._sunbelt.posts.get(self.sun_parent_id)
        else:
            return None
    
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
        
