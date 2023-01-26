# -*- coding: utf-8 -*-

import requests
import json

class SunbeltClientBase():
    
    def __init__(self, host):
        self.host = host
     
    def _wrap_in_brackets(self, string):
        return '{' + string + '}'
    
    def mutation(self, kind, from_json):
        """
        Create a new object in the database.

        Parameters
        ----------
        kind : str
            The kind of object to create. Can be 'post', 'comment', 'subreddit', or 'account'.
        from_json : dict
            The data to create the object with.

        Returns
        -------
        dict
            The data of the created object.
        """

        mutation_type = 'create' + kind.title()
        mutation_title = f' mutation new{mutation_type} '
        mutation_args = f' {mutation_type}(from_json: """{from_json}""") '
        kind_fields = kind + ' { sun_unique_id most_recent_sun_version_id most_recent_sun_detail_id } '
        mutation_return_fields = self._wrap_in_brackets(f' success errors created_new_version {kind_fields}')
        
        mutation = mutation_title + self._wrap_in_brackets(mutation_args + mutation_return_fields)
        
        headers = {'Content-Type': 'application/json'}

        host = self.host

        data = json.dumps({'query': mutation})

        response = requests.post(host, data=data, headers = headers)

        if response.ok:
            response = response.json()
            errors = response.get('errors')
            if not errors:
                return response['data'][mutation_type]
            else:
                debugger_mutation = mutation_title + f' {mutation_type}(from_json: """json""") ' + mutation_return_fields
                error_msg = '\n\n'.join(x['message'] for x in response['errors'])
                return {'errors' : error_msg,
                        'query' : debugger_mutation}
        else:
            debugger_mutation = mutation_title + f' {mutation_type}(from_json: """json""") ' + mutation_return_fields
            error_msg = '\n\n'.join(x['message'] for x in response.json()['errors'])
            return {'errors' : error_msg,
                    'query' : debugger_mutation}

       

    def query(self, kind, *args, **kwargs):
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

        if 'sun_unique_id' not in args:
            args = [x for x in args] + ['sun_unique_id']
            
        if kwargs.get('detail') and 'sun_version_id' not in args:
            args = [x for x in args] + ['sun_version_id','sun_detail_id']
            del kwargs['detail']

        # converts the kind to singular if it is not already
        # if only a single id is being passed.
        # Converts to plural in any other situation
        id_params = ['byId', 'reddit_id']
        any_term_present = any(x in kwargs for x in id_params)
        if any_term_present:
            any_id_list = any(isinstance(x, list) for x in kwargs.values())
            if not any_id_list and kind.endswith('s'):
                kind = kind[:-1]
        else:
            if not kind.endswith('s'):
                kind = kind + 's'
                
            

        #variables_dict = {'$' + key: value for key, value in kwargs.items()}
        variables_str = ', '.join(f'{key}: "{value}"' if isinstance(value, str) else f'{key}: {str(value)}' for key, value in kwargs.items())
        variables_str = variables_str.replace("'", '')
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
        
        response_json = response.json()
        if response.ok and not response_json.get('errors'):
            data = response_json['data']
            if data:
                data = data[kind]
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
                error_msg = '\n\n'.join(x['message'] for x in response_json['errors'])
                print(query)
                return 'GraphQL Msg: ' + error_msg
        else:
            error_msg = '\n\n'.join(x['message'] for x in response_json['errors'])
            print(query)
            return 'GraphQL Msg:' + error_msg
