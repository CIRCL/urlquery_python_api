#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import urlquery
import json
import smtplib
from email.mime.text import MIMEText
import time
import datetime

regex_url = '.*(\.lu[$/]).*'
c = 'Luxembourg'
sender = 'urlquery@example.com'
to = 'dest@example.com'
smtp_server = 'smtp_server'

def get_country():
    feed = urlquery.urlfeed_get()
    entries = []
    for v in feed:
        if type(v) != type({}) or v.get('url') is None:
            continue
        if v.get('country') == c or re.findall(regex_url, v['url']):
            entries.append(v)
    return entries

def prepare_mail(entry):
    to_return = {}
    to_return['subject'] = 'UrlQuery report for {}'.format(entry['ip'])
    to_return['body'] = json.dumps(entry, sort_keys=True, indent=4)
    reports = urlquery.urlquery_search(entry['ip'],
            urlquery_from = datetime.datetime.now() - datetime.timedelta(hours=2))
    if reports is None:
        response = urlquery.urlquery_submit(entry['url'])
        queue_id = response.get('queue_id')
        i = 0
        while queue_id is None:
            time.sleep(10)
            response = urlquery.urlquery_submit(entry['url'])
            queue_id = response.get('queue_id')
            i += 1
            if i >= 3:
                return to_return
        time.sleep(10)
        status = urlquery.urlquery_get_queue_status(queue_id)
        i = 0
        while status.get('status') is None:
            i += 1
            time.sleep(10)
            status = urlquery.urlquery_get_queue_status(queue_id)
            if i >= 10:
                return to_return
        while int(status['status']) != 3:
            print 'Waiting for', entry['url']
            time.sleep(10)
            status = urlquery.urlquery_get_queue_status(queue_id)
        full_report = urlquery.urlquery_get_report(status['report_id'], flag=11)
        to_return['body'] += '\n' + json.dumps(full_report,
                sort_keys=True, indent=4)
    else:
        for report in reports:
            try:
                full_report = urlquery.urlquery_get_report(report['id'], flag=11)
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
                if e['ip'] in ips:
                    continue
                ips.append(e['ip'])
                mail_content = prepare_mail(e)
                send_mail(mail_content)
            print 'Done, waiting 3500s'
            time.sleep(3500)
        except Exception, e:
            print 'Somethifng failed.'
            print e
            time.sleep(200)
