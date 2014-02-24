Readme
======

API to access [urlquery](http://urlquery.net/index.php).


Intro to the API
================

The API uses JSON requests and responses. A json string is built with the
parameters and the function to call and POSTed over HTTPS to the API URL.

The functions to call is put in the "method" key within the JSON string, the
rest of the parameters to the functions has their respective parameter name as
key. The "method" key is required for all API calls.

The API key isn't always required for API calls, but by not using the key it
will often severely reduce the amount of data that are returned. The data
returned is determined by the key and its associated permissions.


Note: The access of the default key (no key) is very limited, even more than
whatis accessible on the public site.

API calls
=========

Common Objects in response structures:

* IP::

        {
            "addr"  : string,
            "cc"    : string,   Country code (NO, UK, SE, DK) etc..
            "country": string,
            "asn"   : int,      ASN number
            "as"    :  string   AS string (full name)
        }

* URL::

        {
            "addr"  : string,
            "fqdn"  : string,
            "domain": string,
            "tld"   : string,
            "ip"    : IP        IP object
        }

* SETTINGS::

    {
        "useragent" : string, UserAgent used
        "referer"   : string,
        "pool"      : string, Pool of exit nodes used
        "access_level": string
    }

* BINBLOB::

    {
        "base64_data"   : string, Base64 encoded data
        "media_type"    : string  mime type
    }


* Example::

        {
            "url":
                {
                    "addr": "www.youtube.com/watch?v=oHg5SJYRHA0",
                    "ip":
                        {
                            "addr": "213.155.151.148",
                            "cc": "IE",
                            "country": "Ireland",
                            "asn": 1299,
                            "as": "AS1299 TeliaSonera International Carrier"
                        },
                    "fqdn": "www.youtube.com",
                    "domain": "youtube.com",
                    "tld": "com"
                }
        }

All responses from the API includes a response object. Which holds the status
of the API call. This is called "_response_"

* RESPONSE::

    {
        "status"    : string,   "ok" or "error"
        "error"     : string    Error string if applicable
    }

API Key
=======

If you have an API Key, put it in apikey.py with the variable name 'key'.

Gzip
====

To get the responses of the api gzip'ed, change 'gzip_default' to True.

Dependencies
============

Hard:

* requests: https://github.com/kennethreitz/Requests
* dateutil

Optional:

* jsonsimple
