#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
API Overview
============

Most "urlquery" functions are usable without a key, but will only return data which
are public (user submission). To access non-public or private reports a key is needed.
For some of the data within the reports a key is also needed, like Javascript data and
HTTP transactions.

The "urlfeed" functions needs a key, and will not return URLs submitted by your own
key. (All URLs submitted to urlQuery will be present in the feed).

The API uses JSON requests and responses. A json string is built with the parameters
and the function to call and POSTed over HTTP(S) to the API URL. The API should
be available over both HTTP and HTTPS. The use of HTTPS is preferred.

The functions to call is put in the “method” key within the JSON string, the rest of the
parameters to the functions has their respective parameter name as key. The
“method” key is required for all API calls.

General Informations
====================

* if you have a API Key, put it in api_key.py with the variable name `key`
* if you want to get the responses of the api gzip'ed, change `gzip_default`
  to True in constraints.py

"""


try:
    import simplejson as json
except:
    import json

import requests
from dateutil.parser import parse
from datetime import datetime, timedelta
import time

from . import constraints as c
if c.has_private_key:
    try:
        from .api_key import key
    except:
        c.has_private_key = False


__intervals = ['hour', 'day']
__query_types = ['string', 'regexp', 'urlquery_alert', 'ids_alert']

def __set_default_values(gzip = False):
    to_return = {}
    if c.has_private_key:
        to_return['key'] = key
    if c.gzip_default or gzip:
        to_return['gzip'] = 'true'
    return to_return

def __query(query, gzip = False):
    if query.get('error') is not None:
        return query
    query.update(__set_default_values(gzip))
    r = requests.post(c.base_url, data=json.dumps(query))
    return r.json()

def urlfeed_get(interval = 'hour', timestamp = None, gzip = False):
    """
            Get the full feed on an time frame (hour or day).

            :param interval: Sets the size of time window.

                .. note::

                    Allowed values:

                        * hour - (recommended) splits the day into 24
                                  slices Which each goes from 00-59 of
                                  every hour, for example: 10:00-10:59.
                        * day - will return all URLs from a given date.

            :param timestamp: This selects which slice to return.
                              Any timestamp within a given interval/time
                              slice can be used to return URLs from that
                              timeframe. (default: now)

                .. hint::

                    "20120714 17:30" returns the feed between 17:00 and 17:59 the 2012-07-14

    """
    query = {'method': 'urlfeed_get'}
    if not c.has_private_key:
        query.update({'error': 'Private key required.'})
    if interval not in __intervals:
        query.update({'error': 'Interval can only be in ' + ', '.join(__intervals)})
    if timestamp is None:
        ts = datetime.now()
        if interval == 'hour':
            ts = ts - timedelta(hours=1)
        timestamp = time.mktime(ts.utctimetuple())
    else:
        try:
            timestamp = time.mktime(parse(timestamp).utctimetuple())
        except:
            query.update({'error': 'Unable to convert time to timestamp: ' + str(time)})
    query['timestamp'] = timestamp
    query['interval'] = interval
    return __query(query, gzip)

def urlquery_search(q, urlquery_type = 'string', urlquery_from = None,
        urlquery_to = None, gzip = False):
    """
        Searches for the 50 most recent reports on an IP.

        :param q: Search string
        :param type: Type of search

            .. note::

                Allowed values:

                    * string - (recomended) Example: "91.229.143.59"
                    * regex - Example:  "\.php\?.{1,7}=[a-f0-9]{16}$"
                    * urlquery_alert
                    * ids_alert

                        .. warning::
                            Please use moderation when searching with regexp.

        :param urlquery_from: First date of the interval (default: last date - 30 days)
        :param urlquery_to: Last date of the interval (default: now)
    """
    query = {'method': 'urlquery_search'}
    if urlquery_type not in __query_types:
        query.update({'error': 'urlquery_type can only be in ' + ', '.join(__query_types)})
    if urlquery_to is None:
        urlquery_to = datetime.now()
    else:
        if type(urlquery_to) == type(str()):
            urlquery_to = parse(urlquery_to)
    if urlquery_from is None:
        urlquery_from = urlquery_to - timedelta(days=30)
    else:
        if type(urlquery_to) == type(str()):
            urlquery_from = parse(urlquery_from)
    query['type'] = urlquery_type
    query['from'] = time.mktime(urlquery_from.utctimetuple())
    query['to'] = time.mktime(urlquery_to.utctimetuple())
    query['q'] = q
    return __query(query, gzip)

def urlquery_submit(url, ua = None, referer = None, flags = None, priority = 2):
    """
        Submits an URL for analysis.

        :param url: URL to submit for analysis.
        :param ua: User-Agent to use. Only a few selected are approved.

            .. note::

                Some API keys have access to set custom User-Agent

            .. note::

                Allowed User-Agents:

                    * (default) Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13
                    * Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Chrome/8.0.552.237 Safari/534.1
                    * Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; SV1; .NET CLR 3.0.04506; .NET CLR 3.5.21022)
                    * Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; .NET CLR 1.1.4322)
                    * Opera/9.80 (Windows NT 6.1; U; en) Presto/2.5.24 Version/10.54

        :param referer: Referer to apply
        :param flags: Type of report

            .. note::

                * 0 - Only accept if it’s a new URL
                * 1 - Force submission, ignores if similar URLs exsists
                * 2 - Non-public report
                * 4 - Private report

                .. tip::
                    If both non-public and private bit is set, the report will be set to private.

        :param priority: Set a priority on the submission.

            .. note::

                * 0 - urlfeed: URL might take several hour before completing
                * 1 - Low: Used for mass submission through the API
                * 2 - Normal
                * 3 - High


    """
    query = {'method': 'urlquery_submit'}
    if flags > 7:
        query.update({'error': 'flags must be <= 7'})
    if priority not in list(range(4)):
        query.update({'error': 'priority must be in '
            + ', '.join(list(map(str, range(4))))})
    query['url'] = url
    if ua is not None:
        query['ua'] = ua
    if referer is not None:
        query['referer'] = referer
    if flags is not None:
        query['flags'] = flags
    query['priority'] = priority
    return __query(query)

def urlquery_get_queue_status(queue_id):
    """
        Returns status (int) of the queued item along with other misc info.
        The final report id of the report will be returned once the report
        is finished (status = 3).
        To get the report see ‘urlquery_get_report’

        :param queue_id: Queue ID returned from ‘urlquery_submit’

        .. note::

            The return status will be one of the following:

                * 0 - Queued
                * 1 - Processing
                * 2 - Analyzing
                * 3 - Done

    """
    query = {'method': 'urlquery_get_queue_status'}
    query['queue_id'] = queue_id
    return __query(query)

def urlquery_get_report(urlquery_id, flag = 0 , recent_limit = 6, gzip = False):
    """
        Get an URL Report.

        :param urlquery_id: ID of the report
        :param flag: What data to include in the reports

            .. note::

                * (default) 0 - Basic report
                * 1 - Include settings
                * 2 - Alerts (IDS and urlQuery Alerts)
                * 4 - Include recent report from same domain/IP/ASN.
                * 8 - Include report details (JavaScripts, HTTP Transactions etc.)

                The above values are added together to form a final value.
                To get all report data back use 15.

        :param recent_limit: Number of reports from same ASN / IP /
                             domain to include. Only basic info, regardless
                             of flags. Default: 6.
    """
    query = {'method': 'urlquery_get_report'}
    if flag > 15:
        query.update({'error': 'flag must be <= 15'})
    query['id'] = urlquery_id
    query['flag'] = flag
    query['recent_limit']= recent_limit
    return __query(query, gzip)

def urlquery_get_flagged_urls(interval = 'hour', timestamp = None,
        confidence = 2, gzip = False):
    """
        Get the URL list with a reputation.

        :param interval: Sets the size of time window.

            .. note::

                Allowed values:

                    * hour - (recommended) splits the day into 24 slices
                             Which each goes from 00-59 of every hour,
                             for example: 10:00-10:59.
                    * day - will return all URLs from a given date.

        :param timestamp: This selects which slice to return.
                          Any timestamp within a given interval/time
                          slice can be used to return URLs from that
                          timeframe. (default: now)

            .. hint::
                "20120714 17:30" returns the feed between 17:00 and 17:59 the 2012-07-14

        :param confidence: Return URLs based on confidence level. Each
                           URL is given a confidence level between 1-3
                           where 3 is the highest.

            .. note::

                * 1 - lowest, when IDS alerts triggers, return all URLs.
                * 2 - when suspicious URL patterns or alerts are detected
                * 3 - generally means a live exploit kit was detected
    """
    query = {'method': 'urlquery_get_flagged_urls'}
    if not c.has_private_key:
        query.update({'error': 'Private key required.'})
    if interval not in __intervals:
        query.update({'error': 'interval can only be in ' + ', '.join(__intervals)})
    if confidence not in [1,2,3]:
        query.update({'error': 'confidence can only be in ' + ', '.join([1,2,3])})
    if timestamp is None:
        ts = datetime.now()
        if interval == 'hour':
            ts = ts - timedelta(hours=1)
        timestamp = time.mktime(ts.utctimetuple())
    else:
        try:
            timestamp = time.mktime(parse(timestamp).utctimetuple())
        except:
            query.update({'error': 'Unable to convert time to timestamp: ' + str(time)})
    query['interval'] = interval
    query['timestamp'] = timestamp
    query['confidence'] = confidence
    return __query(query, gzip)
