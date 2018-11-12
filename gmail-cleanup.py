from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import sys, datetime, re

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

# Call messages query for list of ids, threadIds and nextPageToken
# For each id in list, get message metadata

METADATA_HEADERS = ['From','To','Subject','Date']
DATE_FORMAT = '%d %b %Y'
#DATE_FORMAT2 = '%a, %d %b %Y %H:%M:%S %z %Z'
#DAYS_OF_WEEK_RE = 'Mon|Tue|Wed|Thu|Fri|Sat|Sun'
#DAYS_OF_WEEK_PATTERN = re.compile(DAYS_OF_WEEK_RE)
#TZ_RE = '\([A-Z]{3}\)'
#TZ_PATTERN = re.compile(TZ_RE)

def get_authorized_service():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service

def get_message_ids(service, nextPageToken = None):
    results = None
    if nextPageToken:
        results = service.users().messages().list(userId='me', labelIds='CATEGORY_PERSONAL', maxResults=100).execute()
    else:
        results = service.users().messages().list(userId='me', labelIds='CATEGORY_PERSONAL', maxResults=100,
                                                  pageToken=nextPageToken).execute()

    if results:
        messages = results.get('messages', [])
        nextPageToken = results.get('nextPageToken')
        return (messages, nextPageToken)

def process_messages(service, message_dates, message_senders, messageIds):
    idx = 0
    for messageId in messageIds:
        idx += 1
#       print ("Retrieving message " + messageId['id'])
        message = service.users().messages().get(userId='me', id=messageId['id'], format='metadata',
                                                 metadataHeaders=METADATA_HEADERS).execute()
        if not message:
            print('Message ' + messages[0]['id'] + ' not retrieved')
        else:
            try:
                payload = message['payload'] # if message['payload'] else print("No payload"); continue
                headers = payload['headers'] #if payload['headers'] else print("No headers"); continue
                process_headers(headers, message_dates, message_senders)
            except e:
                print ("Error processing message " + messageId['id'])
        if idx == 90:
            print(str(message_dates))
            sys.exit(0)

def process_headers(headers, message_dates, message_senders):
    for header in headers:
#        print (header['name'] + ' ' + header['value'])
        if header['name'] == 'Date':
            process_date(message_dates, header['value'])
        elif header['name'] == 'From':
            process_sender(message_senders, header['value'])

def process_date(message_dates, date_str):
    try:
        dt = None

        if not DAYS_OF_WEEK_PATTERN.match(date_str):
            print ("Working on parsing " + date_str)
        else:
            if TZ_PATTERN.search(date_str):
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT2)
            else:
                dt = datetime.datetime.strptime(date_str, DATE_FORMAT)

        if dt:
            key = str(dt.year) + '-' + str(dt.month)
            if key in message_dates:
                message_dates[key] = message_dates[key] + 1
            else:
                message_dates[key] = 1
    except ValueError:
        print ("Unable to parse " + date_str)

def process_sender(message_senders, sender):
    pass
#    print(sender)

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    service = get_authorized_service()
    if not service:
        print ("FATAL ERROR:  Unable to authorize")
        sys.exit(-1)
    
    message_dates = {}
    message_senders = {}
    pageNum = 0
    (messageIds, nextPageToken) = get_message_ids(service)
    while (nextPageToken is not None and pageNum < 3):
        pageNum += 1
        print ("Page " + str(pageNum))
        if not messageIds:
            print('No messages found.')
            break
        print("Processing messages page " + str(pageNum))
        process_messages(service, message_dates, message_senders, messageIds)
        (messageIds, nextPageToken) = get_message_ids(service, nextPageToken)
        
 #       
 #   else:
 #       message = service.users().messages().get(userId='me', id=messages[0]['id'], format='metadata',
 #                                                metadataHeaders=METADATA_HEADERS).execute()
 #       if not message:
 #           print('Message ' + messages[0]['id'] + ' not retrieved')
 #       else:
 #           payload = message['payload']
 #           headers = payload['headers']
 #           for v in headers:
 #               print (str(v))

if __name__ == '__main__':
    main()
