# -*- coding: utf-8 -*-

import requests
import json

class SunbeltClientBase():
    def __init__(self, host):
        self.host = host
    
    def _wrap_in_brackets(self, string):
        return '{' + string + '}'
    
    def search(self, kind, *args, **kwargs):
        """
        Search for a kind of object in the database.

        Parameters
        ----------
        kind : str
            The kind of object to search for. Can be 'posts', 'comments', 'subreddits', or 'accounts'.
        *args : str
            The fields to return for each object. Can be any of the fields in the object.
        **kwargs : str
            The fields to filter the search by. Can updated_before, updated_after, posted_before, or posted_after.
        """

        if 'zen_unique_id' not in args:
            args = [x for x in args] + ['zen_unique_id']
            
        if 'ById' in kwargs:
            if kind.endswith('s'):
                kind = kind[:-1]
            
        #variables_dict = {'$' + key: value for key, value in kwargs.items()}
        variables_str = ', '.join(f'{key}: "{value}"' for key, value in kwargs.items())
        
    # =============================================================================
    #         declare_args = {'$updated_before': 'String!',
    #                      '$updated_after': 'String!',
    #                      '$posted_before': 'String!',
    #                      '$posted_after': 'String!'}
    # 
    #         declare_args = ', '.join(f'{key}: {value}' for key, value in declare_args.items()
    #                      if variables_dict.get(key))
    # =============================================================================
                
    
        graphql_query_name = '' #f'GetPosts({declare_args}) '
        graphql_post_func = f'{kind}({variables_str}) ' if len(variables_str) else f'{kind} '
        
        
        fields = self._wrap_in_brackets(' \n '.join(args))
        body = graphql_post_func + self._wrap_in_brackets(f'success errors {kind} ' + fields)
        body = self._wrap_in_brackets(body)
        
        query = 'query ' + graphql_query_name + body
        
        data = {
          'query': query,
          #'variables' : variables
        }
        
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(self.host, 
                          data=json.dumps(data), 
                          headers=headers)


        if response.ok:
            response = response.json()
            data = response['data'][kind]
            success = data.get('success')
            if success:
                if isinstance(data[kind], dict):
                    yield data[kind]
                elif isinstance(data[kind], list):
                    for item in data[kind]:
                        yield item
                else:
                    raise Exception('Unknown type. Expected dict or list.')
            else:
                return {'errors' : data['errors'],
                        'query' : query}
        else:
            print(query)
            return response.json()