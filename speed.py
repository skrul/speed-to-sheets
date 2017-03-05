import speedtest
import sched
import time
import logging
from oauth2client.service_account import ServiceAccountCredentials
from httplib2 import Http
from apiclient import discovery

from datetime import datetime

# Silence error about 'file_cache is unavailable when using oauth2client'
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_speedtest():
    st = speedtest.Speedtest()
    st.get_best_server()
    st.download()
    st.upload()
    return st.results

def append_to_spreadsheet(results):
    values = []
    values.append({ 'userEnteredValue': { 'stringValue': results.timestamp } })
    values.append({ 'userEnteredValue': { 'numberValue': results.ping } })
    values.append({ 'userEnteredValue': { 'numberValue': results.download / 1000.0 / 1000.0 } })
    values.append({ 'userEnteredValue': { 'numberValue': results.upload / 1000.0 / 1000.0 } })
    values.append({ 'userEnteredValue': { 'stringValue': results.server['host'] } })
    request = {
        'appendCells': {
            'fields': '*',
            'rows': [{ 'values': values }]
        }
    }

    scopes = 'https://www.googleapis.com/auth/spreadsheets'
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'credentials.json', scopes)
    http_auth = credentials.authorize(Http())
    discoveryUrl = 'https://sheets.googleapis.com/$discovery/rest?version=v4'
    service = discovery.build('sheets', 'v4', http=http_auth,
                              discoveryServiceUrl=discoveryUrl)
    sheet_id = '1wUM4a8iGP2jYtYyjpi_23qq0o1oqRnsFD-mMwZFBUyo'
    service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body={ 'requests': [ request ] }
    ).execute()

def main():
    logger.info('Running speedtest...')
    results = run_speedtest()
    append_to_spreadsheet(results)
    logger.info('Sent results: ' + results.json())

while True:
    sleeptime = 60 - datetime.utcnow().second
    time.sleep(sleeptime)
    try:
        main()
    except Exception as e:
        logger.exception('test failed!')
