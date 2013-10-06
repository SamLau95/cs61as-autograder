import time
import logging
import json
import urllib2
import os
import urlparse

import xqueue_util as util
import config
import project_urls
import requests

log = logging.getLogger(__name__)
QNAME = config.QUEUE_NAME

def main():
    '''
    Pulls submission from xqueue, downloads file, grades, and posts back.
    '''
    def check_success(flag, message='Failed!'):
        if not flag: raise Exception(message)
    session = util.xqueue_login()
    flag, length = get_queue_length(QNAME, session)
    check_success(flag, 'Failed to get queue length.')
    if length == 0: print 'No items on queue' ; return
    print 'There are %d items on the queue' % length

    flag, queue_item = pull_from_queue(QNAME, session)
    check_success(flag, 'Failed to pull from queue.')
    flag, content = util.parse_xobject(queue_item, QNAME)
    check_success(flag, 'Failed to parse queue item.')

    result = grade(content)
    success, msg = post_result(content, session, result)
    if success:
        print 'Successfully posted back to xqueue.'


PAYLOAD_NAME = 'assignment_name'
def grade(content):
    '''
    Grades result.
    Returns the result of the grading.
    '''
    body = json.loads(content['xqueue_body'])

    grader_payload = json.loads(body.get('grader_payload', '{}'))
    hw_name = grader_payload.get(PAYLOAD_NAME) # Unicode string

    files = json.loads(content['xqueue_files'])
    filename, fileurl = files.items()[0]
    response = requests.get(fileurl)

    # Downloads file to current directory
    with open(filename, 'wb') as f:
        f.write(response.content)
        f.close()
        response.close()

    command = ' '.join(['grader', hw_name, filename])
    p = os.popen(command, 'r')
    result = p.read()

    return result

def post_result(content, session, result):
    '''
    Posts result back to xqueue. Returns a success flag and the post message.
    '''
    content_header = json.loads(content['xqueue_header'])
    content_body = json.loads(content['xqueue_body'])
    xqueue_header, xqueue_body = util.create_xqueue_header_and_body(
        content_header['submission_id'], 
        content_header['submission_key'], 
        True, 
        2, 
        '<pre>' + result + '</pre>', 
        'reference_dummy_grader')
    success, msg = util.post_results_to_xqueue(session, json.dumps(xqueue_header), json.dumps(xqueue_body))
    return success, msg

def get_queue_length(queue_name,xqueue_session):
    """
        Returns the length of the queue
    """
    try:
        success, response = util._http_get(xqueue_session,
                                           urlparse.urljoin(config.XQUEUE_INTERFACE['url'], project_urls.XqueueURLs.get_queuelen),
                                           {'queue_name': queue_name})
        
        if not success:
            return False,"Invalid return code in reply"
    
    except Exception as e:
        log.critical("Unable to get queue length: {0}".format(e))
        return False, "Unable to get queue length."
    
    return True, response

def pull_from_queue(queue_name,xqueue_session):
    """
        Get a single submission from xqueue.
        Returns a success flag and the response as a string.
    """
    try:
        success, response = util._http_get(xqueue_session,
                                           urlparse.urljoin(config.XQUEUE_INTERFACE['url'], project_urls.XqueueURLs.get_submission),
                                           {'queue_name': queue_name})
    except Exception as err:
        return False, "Error getting response: {0}".format(err)
    
    return success, response

while True:
    try:
        main()
    except Exception as e:
        print 'Exception raised!\n'
        print e
    finally:
        time.sleep(2)
