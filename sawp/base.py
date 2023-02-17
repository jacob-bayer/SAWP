# -*- coding: utf-8 -*-

import requests
import json
import logging

log = logging.getLogger('SAWP:BASE')

def print_error_msg(errors, query):
    # so many ways for the error message to be delivered...
    if isinstance(errors[0], dict):
        error_msg = '\n\n'.join(x['message'] for x in errors)
    else:
        error_msg = '\n\n'.join(x for x in errors)
    
    print(" Failed query: " + query + '\n')
    print(" Error message: " + error_msg + '\n')


class SunbeltClientBase:
    
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
        
        log.debug(' Running mutation: ' + mutation)
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


       

    def _query(self, kind, limit = None, fields = None, subfields = None, **kwargs):
        """
        Search for a kind of object in the database.

        Parameters
        ----------
        kind : str
            The kind of object to search for. Can be 'posts', 'comments', 'subreddits', or 'accounts'.
        **kwargs : str
            The fields to filter the search by. Can updated_before, updated_after, posted_before, or posted_after.
        """
        
        fields = fields if fields else []
        subfields = subfields if subfields else {}
        
        if 'sun_unique_id' not in fields:
            fields += ['sun_unique_id']
            
        for field, values in subfields.items():
            values_str = ' '.join(values)
            subfield_str = f'{field} { {values_str} }'.replace("'",'')
            fields += [subfield_str]
            
            
        if kwargs.get('detail') and 'sun_version_id' not in fields:
            fields += ['sun_version_id','sun_detail_id']
            del kwargs['detail']

        list_args = ['names','reddit_ids']
        for list_arg in list_args:
            if list_arg in kwargs:
                kwargs[list_arg] = ['"' + '","'.join(kwargs[list_arg]) + '"']
                
                

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
        
        
        fields = self._wrap_in_brackets(' \n '.join(fields))
        body = graphql_post_func + self._wrap_in_brackets(f'success errors {kind} ' + fields)
        body = self._wrap_in_brackets(body)
        
        query = 'query ' + graphql_query_name + body

        data = {
          'query': query,
          #'variables' : variables
        }

        headers = {'Content-Type': 'application/json'}
        
        log.debug(' Running query: ' + query)
        
        response = requests.post(self.host, 
                          data=json.dumps(data), 
                          headers=headers)
        
        response_json = response.json()

        # There are so many ways the error message can be delivered its hard to keep trackof them all and
        # handle them all
        errors = response_json.get('errors') or response_json.get('data').get(kind).get('errors')
        if errors:
            print_error_msg(errors, query)
            yield None
        else: # Response is 200 if no errors
            result = response_json['data'][kind][kind]
            if not len(result):
                yield None
                

            if isinstance(result, dict): # kinds is singular
                yield result
            elif isinstance(result, list): # kinds is plural
                results_yielded = 0
                for item in result:
                    if limit and results_yielded >= limit:
                        break
                    else:
                        yield item
                        results_yielded += 1

            else:
                raise Exception('Unknown type received from API. Expected dict or list.')
            

    def query(self, kind, limit = None, fields = None, subfields = None, **kwargs):

        kind_is_plural = kind.endswith('s')
        id_params = ['byId', 'reddit_id', 'name']
        any_term_present = any(x in kwargs for x in id_params)
        if kind_is_plural and any_term_present:
            raise ValueError('Use plural ID argument for plural kind.')

        elif not kind_is_plural and not any_term_present:
            raise ValueError('Provide a single ID if searching for a single object.')
        
        
        result = self._query(kind, limit = limit, 
                            fields = fields, 
                            subfields = subfields, 
                            **kwargs)
        if kind_is_plural:
            return result
        else:
            return next(result)