
![Sunbelt](/assets/logo-no-background.png)


# SAWP: Sunbelt API Wrapper for Python
Author: Jacob Bayer

##### Introduction
Sunbelt is a database that stores information mined from Reddit. Unlike other services such as Pushshift and Reveddit, which store data on posts and comments immediately after they are posted (Pushshift), or create a new way for users to see live data on Reddit (Reveddit), Sunbelt stores information about how posts, comments, redditors, and subreddits have changed over time. 

**Sunbelt is the only service that does this** *(as far as I know)*, but it is still in a very early stage of development and does not have data at the same scale as Pushshift, nor will it any time soon. If you're interested in using Sunbelt for your project and you'd like to have data from a specific subreddit (or subreddits) loaded into the Sunbelt database, please contact me at jacobbenjaminbayer@gmail.com.

To start using Sunbelt, install the [Sunbelt API Wrapper for Python (SAWP)](https://pypi.org/project/sawp/) by running 

` pip install sawp `

Then import and instantiate the SunbeltClient from SAWP as follows.


```python
from sawp import SunbeltClient
sunbelt = SunbeltClient()
```

SAWP enables a user to query the Sunbelt database using a GraphQL API. In this example, I select the first post in the Sunbelt database.

Posts stored in the Sunbelt database are called "SunPosts" to differentiate them from other reddit objects you may be analyzing (for example PRAW Submissions).


```python
post = sunbelt.posts.first()
post
```




    SunPost(1)



The SunPost object can be used to access attributes of the post.



```python
post.permalink
```




    '/r/AskReddit/comments/10kzboh/happy_birthday_askreddit/'




```python
post.title
```




    'Happy Birthday AskReddit!'



We can list the comments for this post using the post.comments attribute.


```python
post.comments
```




    [SunComment(1),
     SunComment(2),
     SunComment(3),
     SunComment(4),
     SunComment(5),
     ...
     SunComment(48),
     SunComment(49),
     SunComment(50)]



Sunbelt stores multiple versions of data for any given object, representing different times that the SunCrawler saw the entity on Reddit. These versions describe the non-permanent attributes of an object such as upvotes, karma, or subreddit subscribers.

Let's take a look at how many versions we have for a comment on SunPost(2).


```python
post = sunbelt.posts.get(2)
comment = post.comments[3]
comment
```




    SunComment(59)




```python
comment.versions
```




    [CommentVersion(SunComment = 59 , SunVersion = 1),
     CommentVersion(SunComment = 59 , SunVersion = 2)]



Let's look at some of the version data.


```python
print('\n Upvotes over time for Comment:', comment.reddit_comment_id, '\n') #, '\n Posted in r/', post.subreddit.display_name, '\n')
for v in comment.versions:
    print(v.ups, 'upvotes at', v.sun_created_at)
```

    
     Upvotes over time for Comment: t1_j5t0ysc 
    
    22389 upvotes at 25-01-2023 18:06:12
    24792 upvotes at 26-01-2023 14:45:14


By looking at the comment body text of each version, we can see that this comment has been deleted by the author.


```python
[x.body for x in comment.versions]
```




    ['Being a YouTube "prankster"', '[deleted]']



The details from the most recent version of any object are also stored as attributes with the "most_recent_" prefix.


```python
print(comment.most_recent_ups)
print(comment.most_recent_body)
```

    24792
    [deleted]


#### Sunbelt to Pandas

Sunbelt uses a GraphQL API to query only the data specifically requested by the user. When a Sun object is first initalized by SAWP, it contains only bare minimum of information necessary to initialize the object unless additional information is specifically requested by the user. When an attribute is requested, a new API call is made to obtain that attribute from the database. A batch request for many attributes can be made by passing the requested attributes as arguments.


```python
all_comments = sunbelt.comments.all(# Requested fields can be passed as args
                                 'sun_post_id',
                                 'sun_comment_id',
                                 'reddit_post_id',
                                 'reddit_comment_id',
                                 'reddit_parent_id',
                                 'most_recent_body',
                                 'most_recent_ups',
                                 'most_recent_downs',
                                 'created_utc',
                                 'most_recent_edited',
                                 'most_recent_gilded',
                                 'depth')
```

Sunbelt objects have a useful to_dict method, which can be used to create a pandas dataframe.


```python
comment = all_comments[0]
comment.to_dict()
```




    {'kind': 'comment',
     'uid': 1,
     'created_utc': 1674655786.0,
     'depth': '0',
     'most_recent_body': "Happy birthday to the world's internet town square.",
     'most_recent_downs': 0,
     'most_recent_edited': 0,
     'most_recent_gilded': '0',
     'most_recent_ups': 28,
     'reddit_comment_id': 't1_j5tm5b1',
     'reddit_parent_id': None,
     'reddit_post_id': 't3_10kzboh',
     'sun_comment_id': '1',
     'sun_post_id': 1,
     'sun_unique_id': 1}




```python
import pandas as pd
comments_df = pd.DataFrame(x.to_dict() for x in all_comments)
comments_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>kind</th>
      <th>uid</th>
      <th>created_utc</th>
      <th>depth</th>
      <th>most_recent_body</th>
      <th>most_recent_downs</th>
      <th>most_recent_edited</th>
      <th>most_recent_gilded</th>
      <th>most_recent_ups</th>
      <th>reddit_comment_id</th>
      <th>reddit_parent_id</th>
      <th>reddit_post_id</th>
      <th>sun_comment_id</th>
      <th>sun_post_id</th>
      <th>sun_unique_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>comment</td>
      <td>1</td>
      <td>1.674656e+09</td>
      <td>0</td>
      <td>Happy birthday to the world's internet town sq...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>28</td>
      <td>t1_j5tm5b1</td>
      <td>None</td>
      <td>t3_10kzboh</td>
      <td>1</td>
      <td>1</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>comment</td>
      <td>2</td>
      <td>1.674656e+09</td>
      <td>0</td>
      <td>ask reddit is aquarius</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>8</td>
      <td>t1_j5tlz13</td>
      <td>None</td>
      <td>t3_10kzboh</td>
      <td>2</td>
      <td>1</td>
      <td>2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>comment</td>
      <td>3</td>
      <td>1.674655e+09</td>
      <td>0</td>
      <td>Cool</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>7</td>
      <td>t1_j5tlfri</td>
      <td>None</td>
      <td>t3_10kzboh</td>
      <td>3</td>
      <td>1</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>comment</td>
      <td>4</td>
      <td>1.674658e+09</td>
      <td>0</td>
      <td>Thanks for being there for 15 years so we coul...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>8</td>
      <td>t1_j5tq7nj</td>
      <td>None</td>
      <td>t3_10kzboh</td>
      <td>4</td>
      <td>1</td>
      <td>4</td>
    </tr>
    <tr>
      <th>4</th>
      <td>comment</td>
      <td>5</td>
      <td>1.674656e+09</td>
      <td>0</td>
      <td>happy birthday reddits most disturbing comment...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>8</td>
      <td>t1_j5tmm97</td>
      <td>None</td>
      <td>t3_10kzboh</td>
      <td>5</td>
      <td>1</td>
      <td>5</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>655</th>
      <td>comment</td>
      <td>648</td>
      <td>1.674667e+09</td>
      <td>0</td>
      <td>What a fucking asshole.</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>t1_j5udej5</td>
      <td>None</td>
      <td>t3_10kzjx3</td>
      <td>648</td>
      <td>15</td>
      <td>648</td>
    </tr>
    <tr>
      <th>656</th>
      <td>comment</td>
      <td>649</td>
      <td>1.674667e+09</td>
      <td>0</td>
      <td>Yep, like a cancer.</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>t1_j5uf640</td>
      <td>None</td>
      <td>t3_10kzjx3</td>
      <td>649</td>
      <td>15</td>
      <td>649</td>
    </tr>
    <tr>
      <th>657</th>
      <td>comment</td>
      <td>650</td>
      <td>1.674658e+09</td>
      <td>1</td>
      <td>I mean if you're a leading religious figure in...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>39</td>
      <td>t1_j5tselp</td>
      <td>None</td>
      <td>t3_10kzjx3</td>
      <td>650</td>
      <td>15</td>
      <td>650</td>
    </tr>
    <tr>
      <th>658</th>
      <td>comment</td>
      <td>655</td>
      <td>1.674662e+09</td>
      <td>2</td>
      <td>Except the ones involving invading your country</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>11</td>
      <td>t1_j5u073l</td>
      <td>None</td>
      <td>t3_10kzjx3</td>
      <td>655</td>
      <td>15</td>
      <td>655</td>
    </tr>
    <tr>
      <th>659</th>
      <td>comment</td>
      <td>657</td>
      <td>1.674670e+09</td>
      <td>2</td>
      <td>There are many Islamic movements that aren't c...</td>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>1</td>
      <td>t1_j5unxzh</td>
      <td>None</td>
      <td>t3_10kzjx3</td>
      <td>657</td>
      <td>15</td>
      <td>657</td>
    </tr>
  </tbody>
</table>
<p>660 rows × 15 columns</p>
</div>

