# -*- coding: utf-8 -*-

import requests
import json
import logging
import aiohttp
import asyncio
import time
from itertools import islice, chain
import threading

log = logging.getLogger('SAWP:BASE')

def print_error_msg(errors, query):
    # so many ways for the error message to be delivered...
    if isinstance(errors[0], dict):
        error_msg = '\n\n'.join(x['message'] for x in errors)
    else:
        error_msg = '\n\n'.join(x for x in errors)
    
    print(" Failed query: " + query + '\n')
    print(" Error message: " + error_msg + '\n')

def chunk_list(some_list, chunk_size):
    #result = []
    iterable = iter(some_list)
    while True:
        chunk = list(islice(iterable, chunk_size))
        if not chunk:
            break
        yield chunk

class SunbeltClientBase:
    

    def _authenticate(self, host = None, username = None, password = None):
        if not host and self.host:
            host = self.host
            
        auth_url = host + '/auth'
        self._session = requests.Session()
        self._headers = {'Content-Type': 'application/json'}
        self._session.headers.update(self._headers)
        if username and password:
            data = {'username': username, 'password': password}
            response = self._session.post(auth_url, json = data)
        elif self._refresh_token: # use refresh token
            refresh_header = {'refresh_token': self._refresh_token}
            response = requests.post(host + '/refresh', headers = refresh_header, json = refresh_header)
            if response.ok: log.info('TOken was refreshed.')
        else:
            raise Exception('Need to login with username and password in order to write.')
        
        response.raise_for_status()
        response_json = response.json()
        self._token = response_json['access_token']
        self._headers.update({'Authorization': 'Bearer ' + self._token})
        self._session.headers.update(self._headers)
        self._refresh_token = response_json['refresh_token']
        self._authenticated = True


    def _wrap_in_brackets(self, string):
        return '{' + string + '}'
    
    def batch_add_data(self, json_data):
        if not self._authenticated:
            self._authenticate()
        batch_data_url = self.host + '/add_batch_data'
        response = self._session.post(batch_data_url, json=json_data)
        if response.status_code == 401:
            self._authenticated = False
            self.batch_add_data(json_data)
        response.raise_for_status()
        return response

    # async batch add data
    async def async_batch_add_data(self, json_data):
        if not self._authenticated:
            self._authenticate()
        batch_data_url = self.host + '/add_batch_data'
        async with aiohttp.ClientSession() as session:
            async with session.post(batch_data_url, headers = self._headers, json=json_data) as response:
                #if response.status_code == 401:
                #    self._authenticated = False
                #    await self.async_batch_add_data(json_data)
                response.raise_for_status()
                return await response.json()

    def _generate_query_string(self, kind, fields = None, subfields = None, total_count_only = False, **kwargs):
        fields = fields if fields else []
        subfields = subfields if subfields else {}
        
        if total_count_only:
            kwargs['limit'] = 1
            # offset ==0 is required for total_count to work
            kwargs['offset'] = 0
        
        
        total_count = 'total_count' if kind.endswith('s') else ''
        
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
        
        kwargs = {key: value for key, value in kwargs.items() if value or value==0}
        variables_str = ', '.join(f'{key}: "{value}"' if isinstance(value, str) else f'{key}: {str(value)}' for key, value in kwargs.items())
        variables_str = variables_str.replace("'", '')
                
        graphql_post_func = f'{kind}({variables_str}) ' if len(variables_str) else f'{kind} '
        
        if not total_count_only:
            fields = f'{kind} ' + self._wrap_in_brackets(' \n '.join(fields))
        else:
            fields = ''

        body = graphql_post_func + self._wrap_in_brackets(f'success {total_count} errors ' + fields)
        query = 'query ' + self._wrap_in_brackets(body)
        
        return query

    def _query(self, kind, query, total_count_only = False, using_pagination = False):
        log.debug(' Running query: ' + query)
        response = requests.post(self.graphql_url, data=json.dumps({'query': query}), headers={'Content-Type': 'application/json'})
        
        response_json = response.json()

        # There are so many ways the error message can be delivered its hard to keep track of them all and
        # handle them all
        errors = response_json.get('errors') or response_json.get('data').get(kind).get('errors')
        if errors:
            print_error_msg(errors, query)
            yield None
        else: # Response is 200 if no errors
            data = response_json['data'][kind]
            if using_pagination or total_count_only:
                total_count_result = data['total_count']
                if total_count_result:
                    print('\r', 'Total', total_count_result, kind + ':')#, end = ' ')
                if total_count_only:
                    yield total_count_result
                    
            result = data[kind]
            
            if not result:
                yield None

            elif isinstance(result, dict): # kinds is singular
                yield result
            elif isinstance(result, list): # kinds is plural
                for item in result:
                    yield item

            else:
                raise Exception('Unknown type received from api. Expected dict or list.')
            

    def query(self, kind, fields = None, subfields = None, 
              total_count_only = False, using_pagination = False, **kwargs):
        
        kind_is_plural = kind.endswith('s')


        query = self._generate_query_string(kind, fields, subfields, total_count_only, **kwargs)

        result = self._query(kind, query, total_count_only, using_pagination)
        
        if kind_is_plural:
            return result
        else:
            return next(result)
        
    async def _async_query(self, kind, fields = None, subfields = None, **kwargs):

        total_count = next(self.query(kind, total_count_only = True, **kwargs))

        kwargs['limit'] = limit = 10000
        kwargs['offset'] = 0
        chunks = total_count//limit + 1
        print(f'Getting {total_count} {kind} in {chunks} chunks of {limit} each')
        queries = []
        for i in range(chunks):
            queries += [self._generate_query_string(kind, fields, **kwargs)]
            kwargs['offset'] += limit


        async def fetch_data(query):
            async with aiohttp.ClientSession(headers={'Content-Type': 'application/json'}) as session:
                data = json.dumps({'query': query})
                async with session.post(self.graphql_url, data=data) as r:
                    r.raise_for_status()
                    data = await r.json()
                    return data['data'][kind][kind]
        
        

        # The loop only exists for the main thread so it has to be created in a new thread if doing multithreading
        #loop = asyncio.new_event_loop()
        #asyncio.set_event_loop(loop)
        start_time = time.time()
        loop = asyncio.get_event_loop()
        all_results = []
        for chunk in chunk_list(queries, 100):
            tasks = []
            for query in chunk:
                task = loop.create_task(fetch_data(query))
                tasks.append(task)
            all_results += await asyncio.gather(*tasks)
        log.info('Waiting for async query tasks to complete...')
        all_results = list(chain.from_iterable(all_results))
        end_time = time.time()
        print('Time taken:', end_time - start_time)
        return all_results

    def async_query(self, kind, fields = None, subfields = None, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._async_query(kind, fields, subfields, **kwargs))
