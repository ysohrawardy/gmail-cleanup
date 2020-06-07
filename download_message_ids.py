from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

import sys, datetime, re

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

# Call messages query for list of ids, threadIds and nextPageToken
# For each id in list, get message metadata

def get_authorized_service():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service

def get_message_ids(service, query, nextPageToken = None):
    results = None
    if nextPageToken:
#        print(f"Using this one with page token {nextPageToken}")
        results = service.users().messages().list(userId='me', 
                                                  maxResults=500, q=query,
                                                  pageToken=nextPageToken).execute()
    else:
        results = service.users().messages().list(userId='me', 
                                                  maxResults=500, q=query).execute()
    if results:
#        print(str(results))
        messages = results.get('messages', [])
        nextPageToken = results.get('nextPageToken')
        return (messages, nextPageToken)

    return None

def get_year_query(year):
    if (year < 2000 or year > 2020):
        print(f"Invalid year {year}")
    query = f"after: {year-1}/12/31 before:{year+1}/01/01"
    return query

# Download all message ids and store in a local file
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
    
    pageNum = 0
    for y in range(2007,2021):
        query = get_year_query(y)
        print(f"Year {y} query {query}")
        numYearMessages = 0
        with open(f'message_ids_{y}.txt', 'w') as f: 
            (messageIds, nextPageToken) = get_message_ids(service, query)
            while (messageIds):
                pageNum += 1
                print (f"Page {str(pageNum)} nextPageToken {nextPageToken if nextPageToken is not None else 'None'}" )
                for messageId in messageIds:
                    numYearMessages += 1
                    f.write(str(messageId) + '\n')
                if (nextPageToken is not None):
                    (messageIds, nextPageToken) = get_message_ids(service, query, nextPageToken)
                else:
                    print(f"Found {numYearMessages} message_ids for {y}")
                    messageIds = None
        
if __name__ == '__main__':
    main()
