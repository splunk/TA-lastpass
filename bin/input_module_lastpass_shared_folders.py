
# encoding = utf-8

import os
import sys
import time
import json
import copy
import requests
import datetime
import traceback

LP_CHECKPOINT_KEY = 'LastPass_user'
CMD_REPORTING = 'getsfdata'
PAGE_SIZE = 2000
USER_EV_LIMIT = 50

'''
    IMPORTANT
    Edit only the validate_input and collect_events functions.
    Do not edit any other part in this file.
    This file is generated only once when creating the modular input.
'''
'''
# For advanced users, if you want to create single instance mod input, uncomment this method.
def use_single_instance_mode():
    return True
'''


def validate_input(helper, definition):
    """Implement your own validation logic to validate the input stanza configurations"""
    # This example accesses the modular input variable
    # lastpass_api_url = definition.parameters.get('lastpass_api_url', None)
    # time_start = definition.parameters.get('time_start', None)
    url = definition.parameters.get('lastpass_api_url', None)
    if 'https://' in url:
        return
    # replace if http but not https
    elif 'http' in url and 'https://' not in url:
        raise ValueError('"HTTP" protocol not allowed. Please update for HTTPS.')
    elif '.' not in url:
        raise ValueError('URL submission invalid. Please validate domain.')
    elif 'https://' not in url:
        # add proper url
        definition.parameters['lastpass_api_url'] = 'https://'+url


def save_checkpoint(helper, index):
    ''' 
        update checkpoint with time value as epoch
        @param index: page index for users
        @type index: int
    '''

    try:
        if isinstance(index, int):
            helper.save_check_point(LP_CHECKPOINT_KEY, index)
        else:
            raise Exception(f'Invalid index key. Please validate value for index: {index}')
    except Exception as e:
        raise IOError(f'Save checkpoint failed. index="{index}" reason="{e}"')


def get_checkpoint(helper):
    ''' 
        extract checkpoint index value
        :return: index value or None
    '''

    # if checkpoint corrupted or not readable, consider empty
    try:
        index = helper.get_check_point(LP_CHECKPOINT_KEY)
    except Exception as e:
        helper.log_warning(f'Loading checkpoint. Unable to load checkpoint. reason="{e.message}"') 
        return None

    if str(index).isdigit():
        return index

    helper.log_warning(f'Loading checkpoint. Checkpoint time value not of int type. index="{index}"')
    return None


def collect_events(helper, ew):
    """Implement your data collection logic here

    # The following examples get the arguments of this input.
    # Note, for single instance mod input, args will be returned as a dict.
    # For multi instance mod input, args will be returned as a single value.
    opt_text = helper.get_arg('text')
    opt_text_1 = helper.get_arg('text_1')
    # In single instance mode, to get arguments of a particular input, use
    opt_text = helper.get_arg('text', stanza_name)
    opt_text_1 = helper.get_arg('text_1', stanza_name)

    # get input type
    helper.get_input_type()

    # The following examples get input stanzas.
    # get all detailed input stanzas
    helper.get_input_stanza()
    # get specific input stanza with stanza name
    helper.get_input_stanza(stanza_name)
    # get all stanza names
    helper.get_input_stanza_names()

    # The following examples get options from setup page configuration.
    # get the loglevel from the setup page
    loglevel = helper.get_log_level()
    # get proxy setting configuration
    proxy_settings = helper.get_proxy()
    # get account credentials as dictionary
    account = helper.get_user_credential_by_username("username")
    account = helper.get_user_credential_by_id("account id")
    # get global variable configuration
    global_cid = helper.get_global_setting("cid")
    global_provhash = helper.get_global_setting("provhash")

    # The following examples show usage of logging related helper functions.
    # write to the log for this modular input using configured global log level or INFO as default
    helper.log("log message")
    # write to the log using specified log level
    helper.log_debug("log message")
    helper.log_info("log message")
    helper.log_warning("log message")
    helper.log_error("log message")
    helper.log_critical("log message")
    # set the log level for this modular input
    # (log_level can be "debug", "info", "warning", "error" or "critical", case insensitive)
    helper.set_log_level(log_level)

    # The following examples send rest requests to some endpoint.
    response = helper.send_http_request(url, method, parameters=None, payload=None,
                                        headers=None, cookies=None, verify=True, cert=None,
                                        timeout=None, use_proxy=True)
    # get the response headers
    r_headers = response.headers
    # get the response body as text
    r_text = response.text
    # get response body as json. If the body text is not a json string, raise a ValueError
    r_json = response.json()
    # get response cookies
    r_cookies = response.cookies
    # get redirect history
    historical_responses = response.history
    # get response status code
    r_status = response.status_code
    # check the response status, if the status is not sucessful, raise requests.HTTPError
    response.raise_for_status()

    # The following examples show usage of check pointing related helper functions.
    # save checkpoint
    helper.save_check_point(key, state)
    # delete checkpoint
    helper.delete_check_point(key)
    # get checkpoint
    state = helper.get_check_point(key)

    # To create a splunk event
    helper.new_event(data, time=None, host=None, index=None, source=None, sourcetype=None, done=True, unbroken=True)
    """

    '''
    # The following example writes a random number as an event. (Multi Instance Mode)
    # Use this code template by default.
    import random
    data = str(random.randint(0,100))
    event = helper.new_event(source=helper.get_input_type(), index=helper.get_output_index(), sourcetype=helper.get_sourcetype(), data=data)
    ew.write_event(event)
    '''

    '''
    # The following example writes a random number as an event for each input config. (Single Instance Mode)
    # For advanced users, if you want to create single instance mod input, please use this code template.
    # Also, you need to uncomment use_single_instance_mode() above.
    import random
    input_type = helper.get_input_type()
    for stanza_name in helper.get_input_stanza_names():
        data = str(random.randint(0,100))
        event = helper.new_event(source=input_type, index=helper.get_output_index(stanza_name), sourcetype=helper.get_sourcetype(stanza_name), data=data)
        ew.write_event(event)
    '''

    rest_url = helper.get_arg('lastpass_api_url')

    if not rest_url:
        rest_url = 'https://lastpass.com/enterpriseapi.php'
    # pre-fix domain to proper URL
    elif 'https://' not in rest_url:
        rest_url = f'https://{rest_url}'

    helper.log_debug(f'LastPass parameter check: rest_url={rest_url}')
    headers = { 'Content-Type': 'application/json' }

    # build data params
    data = {}
    data['cid'] = helper.get_global_setting('cid')
    data['provhash'] = helper.get_global_setting('provhash')
    data['cmd'] = CMD_REPORTING
    data['apiuser'] = 'splunk.collector'

    ''' algorithm w checkpointing:
        if results are larger than max page size, checkpoint page index
    '''
    
    time_val = datetime.datetime.now().timestamp()
    try:
        resp_ev = requests.post(rest_url, headers=headers, data=json.dumps(data))
        
        if resp_ev.status_code != 200:
            helper.log_critical('LastPass report collection. request data failed.')
            
        resp_ev_json = resp_ev.json()

        # track for malformed REST call
        if resp_ev_json.get('status') and 'OK' not in resp_ev_json.get('status'):
            helper.log_critical('Lastpass identity collection. REST call successful, but query is bad. Validate request params. Terminating script')
            return
            #sys.exit(1)

    except Exception as e:
        raise e                 

    # track all folders
    folders = {}
    user_count = 1
    temp_folder = None

    try:
        for folder_id in resp_ev_json:
            findex = 0
            temp_folder = resp_ev_json[folder_id]
            user_count = len(resp_ev_json[folder_id]['users'])

            if user_count > USER_EV_LIMIT:
                for ff in range(0, user_count, USER_EV_LIMIT):
                    folder_idx = f'{folder_id}-{findex}'
                    folders[folder_idx] = {}
                    folders[folder_idx]['folder_id'] = folder_idx
                    folders[folder_idx]['folder_index'] = findex
                    folders[folder_idx]['time_collected'] = time_val
                    folders[folder_idx]['event'] = 'list_folders'
                    
                    # copy all folder details into event entry,
                    # for user, copy slice of user list
                    for field in temp_folder.keys():
                        if field == 'users':
                            folders[folder_idx][field] = temp_folder[field][ff:(ff+USER_EV_LIMIT)]
                        else:
                            folders[folder_idx][field] = temp_folder[field]
                    folders[folder_idx]['user_count'] = len(folders[folder_idx][field])

                    event = helper.new_event(data=json.dumps(folders[folder_idx]),
                                            time=time_val,
                                            source=helper.get_input_type(),
                                            index=helper.get_output_index(),
                                            sourcetype=helper.get_sourcetype())
                    ew.write_event(event)
                    findex += 1
            else:
                folders[folder_id] = {}
                folders[folder_id].update(temp_folder)
                folders[folder_id]['folder_id'] = folder_id
                folders[folder_id]['time_collected'] = time_val
                folders[folder_id]['event'] = 'list_folders'
                folders[folder_id]['user_count'] = len(folders[folder_id]['users'])

                event = helper.new_event(data=json.dumps(folders[folder_id]),
                                        time=time_val,
                                        source=helper.get_input_type(),
                                        index=helper.get_output_index(),
                                        sourcetype=helper.get_sourcetype())
                ew.write_event(event)                

        # need to validate if need to paginate
        chk_ptr = 0
        '''
        if count < total:
            chk_ptr = 0
        
            save_checkpoint(helper, event_time)
            helper.log_debug(f'Updating checkpoint to index: {chk_ptr}')
            
            # TODO need to validate limits on collecting shared folders
        '''

    except Exception as e:
        helper.log_critical('Lastpass identity collection. Error in forwarding data: {traceback.format_exc()}')
        raise e                 
