#!/usr/bin/python
# -*- coding: utf-8 -*-

try:
    import simplejson as json
except:
    import json

import requests
from dateutil.parser import parse
from datetime import datetime, timedelta
import time
try:
    from api_key import key
except:
    key = ''

base_url = 'https://uqapi.net/v3/json'
gzip_default = False

__feed_type = ['unfiltered', 'flagged']
__intervals = ['hour', 'day']
__priorities = ['urlfeed', 'low', 'medium', 'high']
__search_types = ['string', 'regexp', 'ids_alert', 'urlquery_alert', 'js_script_hash']
__result_types = ['reports', 'url_list']
__url_matchings = ['url_host', 'url_path']
__access_levels = ['public', 'nonpublic', 'private']


def __set_default_values(gzip=False):
    to_return = {}
    to_return['key'] = key
    if gzip_default or gzip:
        to_return['gzip'] = True
    return to_return


def __query(query, gzip=False):
    if query.get('error') is not None:
        return query
    query.update(__set_default_values(gzip))
    r = requests.post(base_url, data=json.dumps(query))
    return r.json()


def urlfeed(feed='unfiltered', interval='hour', timestamp=None):
    """
        The urlfeed function is used to access the main feed of URL from
        the service. Currently there are two distinct feed:


            :param feed: Currently there are two distinct feed:

                * *unfiltered*: contains all URL received by the service, as
                    with other API calls some restrictions to the feed might
                    apply depending. (default)
                * *flagged*: contains URLs flagged by some detection by
                    urlquery, it will not contain data triggered by IDS
                    alerts as that not possible to correlate correctly to a
                    given URL. Access to this is currently restricted.

            :param interval: Sets the size of time window.
                    * *hour*: splits the day into 24 slices which each
                        goes from 00-59 of every hour,
                        for example: 10:00-10:59 (default)
                    * *day*: will return all URLs from a given date

            :param timestamp: This selects which slice to return.
                              Any timestamp within a given interval/time
                              slice can be used to return URLs from that
                              timeframe. (default: now)


            :return: URLFEED

                {
                    "start_time"    : string,
                    "end_time"      : string,
                    "feed"          : [URLs]    Array of URL objects (see README)
                }

    """
    query = {'method': 'urlfeed'}
    if feed not in __feed_type:
        query.update({'error': 'Feed can only be in ' + ', '.join(__feed_type)})
    if interval not in __intervals:
        query.update({'error': 'Interval can only be in ' + ', '.join(__intervals)})
    if timestamp is None:
        ts = datetime.now()
        if interval == 'hour':
            ts = ts - timedelta(hours=1)
        if interval == 'day':
            ts = ts - timedelta(days=1)
        timestamp = time.mktime(ts.utctimetuple())
    else:
        try:
            timestamp = time.mktime(parse(timestamp).utctimetuple())
        except:
            query.update({'error': 'Unable to convert time to timestamp: ' + str(time)})
    query['feed'] = feed
    query['interval'] = interval
    query['timestamp'] = timestamp
    return __query(query)


def submit(url, useragent=None, referer=None, priority='low',
           access_level='public', callback_url=None, submit_vt=False,
           save_only_alerted=False):
    """
        Submits an URL for analysis.

        :param url: URL to submit for analysis

        :param useragent: See user_agent_list API function. Setting an
            invalid UserAgent will result in a random UserAgent getting
            selected.

        :param referer: Referer to be applied to the first visiting URL

        :param priority: Set a priority on the submission.
            * *urlfeed*: URL might take several hour before completing.
                Used for big unfiltered feeds. Some filtering applies
                before accepting to queue so a submitted URL might not
                be tested.
            * *low*: For vetted or filtered feeds (default)
            * *medium*: Normal submissions
            * *high*: To ensure highest priority.

        :param access_level: Set accessibility of the report
            * *public*: URL is publicly available on the site (default)
            * *nonpublic*: Shared with other security organizations/researchers.
            * *private*: Only submitting key has access.

        :param callback_url: Results are POSTed back to the provided
            URL when processing has completed. The results will be
            originating from uqapi.net. Requires an API key.

        :param submit_vt: Submits any unknown file toVirusTotal for
            analysis. Information from VirusTotal will be included the
            report as soon as they have finished processing the sample.
            Most likely will the report from urlquery be available
            before the data is received back from VirusTotal.
            Default: false

            Only executables, zip archives and pdf documents are
            currently submitted.

            .. note:: Not fully implemented yet.

        :param save_only_alerted: Only reports which contains alerts
            (IDS, UQ alerts, Blacklists etc.) are kept. The main purpose
            for this flag is for mass testing URLs which has not been
            properly vetted so only URLs of interest are kept.
            Default: false

            Combining this with a callback URL will result in only those
            that has alerts on them beingPOSTed back to the callback URL.

        :return: QUEUE_STATUS

            {
                "status"     : string,  ("queued", "processing", "done")
                "queue_id"   : string,
                "report_id"  : string,   Included once "status" = "done"
                "priority"   : string,
                "url"        : URL object,      See README
                "settings"   : SETTINGS object  See README
            }


    """
    query = {'method': 'submit'}
    if priority not in __priorities:
        query.update({'error': 'priority must be in ' + ', '.join(__priorities)})
    if access_level not in __access_levels:
        query.update({'error': 'assess_level must be in ' + ', '.join(__access_levels)})
    query['url'] = url
    if useragent is not None:
        query['useragent'] = useragent
    if referer is not None:
        query['referer'] = referer
    query['priority'] = priority
    query['access_level'] = access_level
    if callback_url is not None:
        query['callback_url'] = callback_url
    if submit_vt:
        query['submit_vt'] = True
    if save_only_alerted:
        query['save_only_alerted'] = True
    return __query(query)


def user_agent_list():
    """
        Returns a list of accepted user agent strings. These might
        change over time, select one from the returned list.

        :return: A list of accepted user agents
    """
    query = {'method': 'user_agent_list'}
    return __query(query)


def mass_submit(urls, useragent=None, referer=None,
                access_level='public', priority='low', callback_url=None):
    """
        See submit for details. All URLs will be queued with the same settings.

        :return:

            {
                [QUEUE_STATUS]  Array of QUEUE_STATUS objects, See submit
            }
    """
    query = {'method': 'mass_submit'}
    if access_level not in __access_levels:
        query.update({'error': 'assess_level must be in ' + ', '.join(__access_levels)})
    if priority not in __priorities:
        query.update({'error': 'priority must be in ' + ', '.join(__priorities)})
    if useragent is not None:
        query['useragent'] = useragent
    if referer is not None:
        query['referer'] = referer
    query['access_level'] = access_level
    query['priority'] = priority
    if callback_url is not None:
        query['callback_url'] = callback_url
    return __query(query)


def queue_status(queue_id):
    """
        Polls the current status of a queued URL. Normal processing time
        for a URL is about 1 minute.

        :param queue_id: QueueIDis returned by the submit API calls

        :return: QUEUE_STATUS (See submit)
    """
    query = {'method': 'queue_status'}
    query['queue_id'] = queue_id
    return __query(query)


def report(report_id, recent_limit=0, include_details=False,
           include_screenshot=False, include_domain_graph=False):
    """
        This extracts data for a given report, the amount of data and
        what is included is dependent on the parameters set and the
        permissions of the API key.

        :param report_id: ID of the report. To get a valid report_id
            either use search to look for specificreports or report_list
            to get a list of recently finished reports.
            Can be string or an integer

        :param recent_limit: Number of recent reports to include.
            Only applies when include_details is true.
            Integer, default: 0

        :param include_details: Includes details in the report, like the
            alert information, Javascript and transaction data.
            Default: False

        :param include_screenshot: A screenshot is included in the report
            as a base64. The mime type of the image is also included.
            Default: False

        :param include_domain_graph: A domain graph is included in the
            report as a base64. The mime type of the image is also included.
            Default: False


        :return: BASICREPORT

            {
                "report_id": string,
                "date"     : string,    Date formatted string
                "url"      : URL,       URL object      - See README
                "settings" : SETTINGS,  SETTINGS object - See README
                "urlquery_alert_count"  : int,  Total UQ alerts
                "ids_alert_count"       : int,  Total IDS alert
                "blacklist_alert_count" : int,  Total Blacklist alerts
                "screenshot"    : BINBLOB,      BINBLOB object - See README
                "domain_graph"  : BINBLOB       BINBLOB object - See README
            }
    """
    query = {'method': 'report'}
    query['report_id'] = report_id
    if recent_limit is not None:
        query['recent_limit'] = recent_limit
    if include_details:
        query['include_details'] = True
    if include_screenshot:
        query['include_screenshot'] = True
    if include_domain_graph:
        query['include_domain_graph'] = True
    return __query(query)


def report_list(timestamp=None, limit=50):
    """
    Returns a list of reports created from the given timestamp, if it’s
    not included the most recent reports will be returned.

    Used to get a list of reports from given timestamp, along with basic
    information about the report like number of alerts and the
    submitted URL.

    To get reports which are nonpublic or private a API key is needed
    which has access to these.

    :param timestamp: Unix Epoch timestamp from the starting point to get
        reports.
        Default: If None, setted to datetime.now()

    :param limit: Number of reports in the list
        Default: 50

    :return:

        {
            "reports": [BASICREPORTS]   List of BASICREPORTS - See report
        }

    """
    query = {'method': 'report_list'}
    if timestamp is None:
        ts = datetime.now()
        timestamp = time.mktime(ts.utctimetuple())
    else:
        try:
            timestamp = time.mktime(parse(timestamp).utctimetuple())
        except:
            query.update({'error': 'Unable to convert time to timestamp: ' + str(time)})
    query['timestamp'] = timestamp
    query['limit'] = limit
    return __query(query)


def search(q, search_type='string', result_type='reports',
           url_matching='url_host', date_from=None, deep=False):
    """
        Search in the database

        :param q: Search query

        :param search_type: Search type
            * *string*: Used to find URLs which contains a given string.
                To search for URLs on a specific IP use string. If a
                string is found to match an IP address it will automaticly
                search based on the IP. (default)
            * *regexp*: Search for a regexp pattern within URLs
            * *ids_alert*: Search for specific IDS alerts
            * *urlquery_alert*: ????? FIXME ?????
            * *js_script_hash*: Used to search for URLs/reports which
                contains a specific JavaScript. The scripts are searched
                based on SHA256, the hash value for each script are
                included in the report details. Can be used to find other

        :param result_type: Result type
            * *reports*: Full reports (default)
            * *url_list*: List of urls

        :param url_matching: What part of an URL to do pattern matching
            against. Only applies to string and regexp searches.
            * *url_host*: match against host (default)
            * *url_path*: match against path


        :param date_from: Unix epoch timestamp for starting searching point.
            Default: If None, setted to datetime.now()


        :param deep: Search all URLs, not just submitted URLs.
            Default: false
            Experimental! Should be used with care as it’s very resource
            intensive.
    """
    query = {'method': 'search'}
    if search_type not in __search_types:
        query.update({'error': 'search_type can only be in ' + ', '.join(__search_types)})
    if result_type not in __result_types:
        query.update({'error': 'result_type can only be in ' + ', '.join(__result_types)})
    if url_matching not in __url_matchings:
        query.update({'error': 'url_matching can only be in ' + ', '.join(__url_matchings)})

    if date_from is None:
        ts = datetime.now()
        timestamp = time.mktime(ts.utctimetuple())
    else:
        try:
            timestamp = time.mktime(parse(date_from).utctimetuple())
        except:
            query.update({'error': 'Unable to convert time to timestamp: ' + str(time)})

    query['q'] = q
    query['search_type'] = search_type
    query['result_type'] = result_type
    query['url_matching'] = url_matching
    query['from'] = timestamp
    if deep:
        query['deep'] = True
    return __query(query)


def reputation(q):
    """
        Searches a reputation list of URLs detected over the last month.
        The search query can be a domain or an IP.

        With an API key, matching URLs will be returned along with the
        triggering alert.

        :param q: Search query
    """

    query = {'method': 'reputation'}
    query['q'] = q
    return __query(query)
