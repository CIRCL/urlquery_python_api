#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import urlquery
import json
import smtplib
from email.mime.text import MIMEText
import time
import datetime

c = 'Luxembourg'
cc = 'LU'
tld = 'lu'
sender = 'urlquery@example.com'
to = 'dest@example.com'
smtp_server = 'smtp_server'

def get_country():
    feed = urlquery.urlfeed()
    entries = []
    for url in feed.get('feed'):
        if type(url) != type({}):
            continue
        if url.get('tld') == tld or url.get('ip').get('cc') == cc
            or url.get('ip').get('country') == c:
            entries.append(url)
    return entries

def prepare_mail(entry):
    to_return = {}
    to_return['subject'] = \
        'UrlQuery report for {}'.format(entry.get('ip').get('addr'))
    to_return['body'] = json.dumps(entry, sort_keys=True, indent=4)
    reports = urlquery.search(entry.get('ip').get('addr'),
            urlquery_from = datetime.datetime.now() - datetime.timedelta(hours=1))
    # FIXME: the output of a search is undefined
    if reports is None:
        response = urlquery.submit(entry['url'])
        queue_id = response.get('queue_id')
        report_id = response.get('report_id')
        i = 0
        while report_id is None:
            print 'Waiting for', entry.get('url').get('addr')
            time.sleep(30)
            response = urlquery.queue_status(queue_id)
            report_id = response.get('report_id')
            i += 1
            if i >= 5:
                return to_return
        full_report = urlquery.report(status['report_id'], include_details=True)
        to_return['body'] += '\n' + json.dumps(full_report,
                sort_keys=True, indent=4)
    else:
        for report in reports:
            try:
                full_report = urlquery.report(report['id'], include_details=True)
                to_return['body'] += '\n' + json.dumps(full_report,
                        sort_keys=True, indent=4)
            except:
                print report
    return to_return

def send_mail(content):
    msg = MIMEText(content['body'])
    msg['Subject'] = content['subject']
    msg['From'] = sender
    msg['To'] = to
    s = smtplib.SMTP(smtp_server)
    s.sendmail(sender, [to], msg.as_string())
    s.quit()

if __name__ == '__main__':

    while True:
        print 'URL Feed and reports...'
        try:
            entries = get_country()
            ips = []

            for e in entries:
                if e.get('ip').get('addr') in ips:
                    continue
                ips.append(e.get('ip').get('addr'))
                mail_content = prepare_mail(e)
                send_mail(mail_content)
            print 'Done, waiting 3500s'
            time.sleep(3500)
        except Exception, e:
            print 'Something failed.'
            print e
            time.sleep(200)
