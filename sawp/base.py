# -*- coding: utf-8 -*-

import requests
import json
import logging
import aiohttp

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
        self.graphql_url = self.host + '/graphql'
     
    def _wrap_in_brackets(self, string):
        return '{' + string + '}'
    
    def batch_add_data(self, json_data):
        if not self._authenticated:
            raise Exception('Must authenticate before adding data')
        batch_data_url = self.host + '/add_batch_data'
        response = requests.post(batch_data_url, headers=self._headers, json=json_data)
        response.raise_for_status()
        return response

    # async batch add data
    async def async_batch_add_data(self, json_data):
        if not self._authenticated:
            raise Exception('Must authenticate before adding data')
        batch_data_url = self.host + '/add_batch_data'
        async with aiohttp.ClientSession() as session:
            async with session.post(batch_data_url, headers=self._headers, json=json_data) as response:
                response.raise_for_status()
                return await response.json()

    def _generate_query_string(self, kind, fields, subfields, **kwargs):
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
                
        kwargs = {key: value for key, value in kwargs.items() if value}
        variables_str = ', '.join(f'{key}: "{value}"' if isinstance(value, str) else f'{key}: {str(value)}' for key, value in kwargs.items())
        variables_str = variables_str.replace("'", '')
                
        graphql_post_func = f'{kind}({variables_str}) ' if len(variables_str) else f'{kind} '
        
        fields = self._wrap_in_brackets(' \n '.join(fields))
        body = graphql_post_func + self._wrap_in_brackets(f'success errors {kind} ' + fields)
        query = 'query ' + self._wrap_in_brackets(body)
        
        return query

    def _query(self, kind, fields, subfields, **kwargs):
        
        query = self._generate_query_string(kind, fields, subfields, **kwargs)
        
        log.debug(' Running query: ' + query)
        response = requests.post(self.graphql_url, 
                          data=json.dumps({'query': query}), 
                          headers={'Content-Type': 'application/json'})
        
        response_json = response.json()

        # There are so many ways the error message can be delivered its hard to keep track of them all and
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
                for item in result:
                    yield item

            else:
                raise Exception('Unknown type received from api. Expected dict or list.')
            

    def query(self, kind, fields = None, subfields = None, **kwargs):

        kind_is_plural = kind.endswith('s')
        id_params = ['byId', 'reddit_id', 'name']
        any_term_present = any(x in kwargs for x in id_params)
        if kind_is_plural and any_term_present:
            raise ValueError('Use plural ID argument for plural kind.')

        elif not kind_is_plural and not any_term_present:
            raise ValueError('Provide a single ID if searching for a single object.')
        
        
        result = self._query(kind, 
                            fields = fields, 
                            subfields = subfields, 
                            **kwargs)
        if kind_is_plural:
            return result
        else:
            return next(result)