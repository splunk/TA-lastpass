
# encoding = utf-8

import re
import os
import sys
import time
import json
import copy
import requests
import datetime
import traceback
import hashlib

LP_CHECKPOINT_KEY = 'LastPass_user'
CMD_KEY = 'getuserdata'
PAGE_SIZE = 2000
PAGE_INDEX = 0

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


def save_checkpoint(helper, index_users, index_groups):
    ''' 
        update checkpoint with index values for both user and group lists
        @param index_users: page index for users
        @param index_groups: page index for groups
        @type index_users: int
        @type index_users: int
    '''

    try:
        if isinstance(index_users, int) and isinstance(index_groups, int):
            state_payload = {}
            state_payload['idx_user'] = index_users
            state_payload['idx_group'] = index_groups
            helper.save_check_point(LP_CHECKPOINT_KEY, state_payload)
        else:
            raise Exception(f'Invalid index key types for checkpointing LastPass user input: user_index={index_users} group_index={index_groups}')
    except Exception as e:
        raise IOError(f'Save LastPass user checkpoint failed. user_index={index_users} group_index={index_groups} reason="{e}"')


def get_checkpoint(helper):
    ''' 
        extract checkpoint index value
        :return: index value or None
    '''

    # if checkpoint corrupted or not readable, consider empty
    try:
        state_payload = helper.get_check_point(LP_CHECKPOINT_KEY)
    except Exception as e:
        helper.log_warning(f'Loading checkpoint. Unable to load checkpoint. reason="{e.message}"') 
        return None

    if isinstance(state_payload, dict):
        return state_payload

    helper.log_warning(f'Loading checkpoint. Invalid index key types for LastPass user input. checkpoint_payload="{repr(state_payload)}"')
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

    global PAGE_INDEX

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
    data['cmd'] = CMD_KEY
    data['apiuser'] = 'splunk.collector'

    ''' algorithm w checkpointing:
        if results are larger than max page size, checkpoint page index
    '''

    chk_user = 0

    while True:

        data['data'] = { 'pagesize': PAGE_SIZE, 'pageindex': PAGE_INDEX }

        try:
            helper.log_debug(f'LastPass identity collection. Collecting user identities. page_index={PAGE_INDEX}')
            resp_ev = requests.post(rest_url, headers=headers, data=json.dumps(data))
            
            if resp_ev.status_code != 200:
                helper.log_critical(f'LastPass identity collection. request data failed.')
            elif re.search(r"(Authorization Error)", resp_ev.text):
                helper.log_exception(f'LastPass identity collection. request data failed. 401: Unauthorized. Verify cid/provhash.')
                
            resp_ev_json = resp_ev.json()

            # track for malformed REST call
            if resp_ev_json.get('status') and 'OK' not in resp_ev_json.get('status'):
                helper.log_critical(f'Lastpass identity collection. REST call successful, but query is bad. Validate request params. Terminating script')
                #helper.log_debug(f'Lastpass identity collection. Failed request: {data}')
                return
                #sys.exit(1)

        except Exception as e:
            raise e                 

        total = resp_ev_json.get('total')
        count = resp_ev_json.get('count')

        helper.log_debug(f'LastPass identity collection. total_identities={total} current_count={count}')

        # track all identities
        users = {}
        groups = {}
        chk_group = 0
        chk_invited = False
        time_val = datetime.datetime.now().timestamp()

        try:
            for idx_user, user in enumerate(resp_ev_json.get('Users')):
                users[user] = copy.deepcopy(resp_ev_json.get('Users')[user])
                users[user]['user_id'] = user
                users[user]['time_collected'] = time_val
                users[user]['event'] = 'list_users'

                chk_user += 1

                if chk_user % 250 == 0:
                    time_val = datetime.datetime.now().timestamp()

                # attrib field cleanup
                if users[user].get('attribs'):
                    # detect and render if name is JSON
                    if users[user].get('attribs').get('name'):
                        try:
                            test = json.loads(users[user].get('attribs').get('name'))
                            users[user].get('attribs').update({'name': test})
                        # do not change if not a JSON value
                        except:
                            pass

                    # scrub password values from attribs
                    if users[user].get('attribs').get('password'):
                        users[user].get('attribs').update({'password': hashlib.sha1(users[user].get('attribs').get('password').encode()).hexdigest()})

                event = helper.new_event(data=json.dumps(users[user]),
                                        time=time_val,
                                        source=helper.get_input_type(),
                                        index=helper.get_output_index(),
                                        sourcetype=helper.get_sourcetype())
                ew.write_event(event)

            iter_group = resp_ev_json.get('Groups') if resp_ev_json.get('Groups') else {}
            for idx_group, group in enumerate(iter_group):
                groups[group] = {}
                groups[group]['members'] = copy.deepcopy(resp_ev_json.get('Groups')[group])
                groups[group]['count'] = len(resp_ev_json.get('Groups')[group])
                groups[group]['group_id'] = group
                groups[group]['time_collected'] = time_val
                groups[group]['event'] = 'list_groups'

                chk_group = idx_group

                if idx_group % 10 == 0:
                    time_val = datetime.datetime.now().timestamp()

                # can only specify one sourcetype per input, hardcode for groups
                event = helper.new_event(data=json.dumps(groups[group]),
                                        time=time_val,
                                        source=helper.get_input_type(),
                                        index=helper.get_output_index(),
                                        sourcetype='lastpass:groups')
                ew.write_event(event)

            if resp_ev_json.get('invited') and not chk_invited:
                invited = {}
                invited['members'] = copy.deepcopy(resp_ev_json.get('invited'))
                invited['count'] = len(resp_ev_json.get('invited'))
                invited['time_collected'] = time_val
                invited['event'] = 'list_invited'

                # can only specify one sourcetype per input, hardcode for groups
                event = helper.new_event(data=json.dumps(invited),
                                        time=time_val,
                                        source=helper.get_input_type(),
                                        index=helper.get_output_index(),
                                        sourcetype='lastpass:invited')
                ew.write_event(event)
                chk_invited = True

            # break out if no more records to processes
            if chk_user >= total or count < PAGE_SIZE:
                helper.log_debug(f'LastPass identity collection. Reached end of user list: idx_user={chk_user}')
                break

            # increment page index to capture more user/group identities 
            PAGE_INDEX += 1

            save_checkpoint(helper, chk_user, chk_group)
            helper.log_debug(f'LastPass identity collection. Updating LastPass identity checkpoint: idx_user={chk_user} idx_group={chk_group}')
                
        except Exception as e:
            helper.log_critical(f'LastPass identity collection. idx_user={chk_user} idx_group={chk_group} Error in forwarding data: {traceback.format_exc()}')
            raise e                 

    helper.log_debug(f'LastPass identity collection. Complete: user identity collection. page_index={PAGE_INDEX} total_identities={total} current_count={count}')
