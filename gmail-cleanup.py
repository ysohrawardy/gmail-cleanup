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
DATE_RE = "\d+ (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}"
DATE_PATTERN = re.compile(DATE_RE)
DATE_FORMAT = '%d %b %Y'
DATE_FORMAT2 = '%d %b %Y'

def get_authorized_service():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service

def process_messages(service, message_dates, message_senders, message_subjects, messageIds):
    idx = 0
    for messageId in messageIds:
        idx += 1
        print ("Retrieving message " + messageId)
        message = service.users().messages().get(userId='me', id=messageId, format='metadata',
                                                 metadataHeaders=METADATA_HEADERS).execute()
        if not message:
            print('Message ' + messagesId + ' not retrieved')
        else:
            try:
                payload = message['payload']
                headers = payload['headers']
                print(f"payload {payload} headers {headers}")
                process_headers(headers, message_dates, message_senders, message_subjects)
            except Exception as e:
                print (f"Error processing message {messageId} {str(e)}")
        if idx == 90:
            print(str(message_dates))
            sys.exit(0)

def process_headers(headers, message_dates, message_senders, message_subjects):
    for header in headers:
#        print (header['name'] + ' ' + header['value'])
        if header['name'] == 'Date':
            process_date(message_dates, header['value'])
        elif header['name'] == 'From':
            process_sender(message_senders, header['value'])
        elif header['name'] == 'Subject':
            process_subject(message_subjects, header['value'])

def process_date(message_dates, email_datetime_str):
    try:
        date_str = DATE_PATTERN.search(email_datetime_str)
#        print(date_str)
        if not date_str:
            print ("Unable to find date in " + date_str)
        else:
            dt = datetime.datetime.strptime(date_str.group(), DATE_FORMAT2)

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

def process_subject(message_subjects, sender):
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
    message_subjects = {}
    pageNum = 0
    messageIds = ['12bac18dfba17d1e']
    process_messages(service, message_dates, message_senders, message_subjects, messageIds)
        
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
