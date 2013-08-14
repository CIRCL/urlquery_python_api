#!/usr/bin/python
# -*- coding: utf-8 -*-


import re
import urlquery
import json
import smtplib
from email.mime.text import MIMEText

regex_url = '.*(\.lu[$/]).*'
c = 'Luxembourg'
sender = 'urlquery@example.com'
to = 'dest@example.com'
smtp_server = 'smtp_server'

def get_country():
    feed = urlquery.urlfeed_get()
    entries = []
    for k, v in feed.iteritems():
        if type(v) != type({}) or v.get('url') is None:
            continue
        if v.get('country') == c or re.findall(regex_url, v['url']):
            entries.append(v)
    return entries

def prepare_mail(entry):
    to_return = {}
    to_return['subject'] = 'UrlQuery report for {}'.format(entry['ip'])
    report = urlquery.urlquery_search(entry['ip'])
    to_return['body'] = '{}\n\n{}'.format(json.dumps(entry,
        sort_keys=True, indent=4), json.dumps(report,  sort_keys=True, indent=4))
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

    entries = get_country()
    #entries = [{'url': u'http://rootsrotterdam.com/', \
    #    'ip': '80.92.91.16', 'asn': 'AS24611 Datacenter Luxembourg S.A.', \
    #    'country': 'Luxembourg'}]

    for e in entries:
        mail_content = prepare_mail(e)
        send_mail(mail_content)

