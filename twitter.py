#!/usr/bin/env python
## twitter.py -- Wrappers over Twitter API -*- Python -*-
## Time-stamp: "2008-10-17 16:33:03 ghoseb"

## Copyright (c) 2008, oCricket.com

import urllib
from StringIO import StringIO
from base64 import encodestring
from django.utils import simplejson
from google.appengine.api import urlfetch

class Twitter(object):
    """Class to represent the Twitter API
    """

    def __init__(self, username, password):
        """
        
        Arguments:
        - `username`: The Twitter username or email-id
        - `password`: The Twitter password
        """
        self._username = username
        self._password = password
        
    def get_auth_header(self):
        """Create the authentication headers
        """
        base64string = encodestring('%s:%s' % (self._username, self._password))[:-1]
        auth_header = {'Authorization': "Basic %s" % base64string}
        return auth_header

    def parse_json(self, data):
        """Convert JSON data to an object

        Arguments:
        - `data`: JSON data
        """
        json_str =  StringIO(data)
        return simplejson.load(json_str)

    
    def get_friends(self):
        """Get all friends on Twitter
        """
        # url = "http://twitter.com/statuses/friends.json"
        headers = self.get_auth_header()
        return self._get_friends(headers)
        
    def _get_friends(self, headers, data=[], page=1):
        """Get friends from a given page
        
        Arguments:
        - `headers`: The auth header
        - `data`: Intermediate data
        - `page`: The page number
        """
        url = "http://twitter.com/statuses/friends.json?page=" + str(page)
        result = urlfetch.fetch(url, headers=headers)
        newdata = self.parse_json(result.content)
        if (newdata and result.status_code == 200):
            return self._get_friends(headers, (data + newdata), page+1)
        return data
    
    def get_followers(self):
        """Get all followers on Twitter
        """
        url = "http://twitter.com/statuses/followers.json"
        headers = self.get_auth_header()
        result = urlfetch.fetch(url, headers=headers)
        if result.status_code == 200:
            return self.parse_json(result.content)

    def friendship_exists(self, username):
        """Check if a friendship exists with username
        
        Arguments:
        - `username`: The username to check friendship with
        """
        url = "http://twitter.com/friendships/exists.json?user_a=%s&user_b=%s" % (self._username, username)
        headers = self.get_auth_header()
        result = urlfetch.fetch(url, headers=headers)
        if result.status_code == 200:
            response = self.parse_json(result.content)
            if response == "true":
                return True
        return False

    def friendship_create(self, username, follow=False):
        """Create friendship with username
        
        Arguments:
        - `username`: The username to check friendship
        - `follow`: If we want to follow too        
        """
        url = "http://twitter.com/friendships/create/%s.json%s" % (username, "?follow=true" if follow else "")
        headers = self.get_auth_header()
        result = urlfetch.fetch(url, method=urlfetch.POST, headers=headers)
        if result.status_code == 200:
            return True
        return False
        
    
    def follow_user(self, username):
        """Follow a Twitter user
        
        Arguments:
        - `username`: The username or id to follow
        """
        if not self.friendship_exists(username):
            return self.create_friendship(username, follow=True)
        
        url = "http://twitter.com/notifications/follow/%s.json" % username
        headers = self.get_auth_header()
        result = urlfetch.fetch(url, method=urlfetch.POST, headers=headers)
        if result.status_code == 200:
            return True
        return False
    
      
