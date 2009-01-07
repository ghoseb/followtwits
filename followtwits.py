#!/usr/bin/env python
## followtwits.py -- Follow Twitter Pals -*- Python -*-
## Time-stamp: "2009-01-07 20:40:36 ghoseb"

## Copyright (c) 2008, oCricket.com

import os
import logging
from cgi import escape
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.runtime import DeadlineExceededError

from twitter import Twitter

try:
    from google.appengine.api.urlfetch import DownloadError
except ImportError:
    pass

class MainPage(webapp.RequestHandler):
    """The request handler for the main-page
    """

    def get(self):
        """Handle the GET method
        """
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, {"success": False}))

    def post(self):
        """Handle the POST method
        """
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        try:
            username = escape(self.request.get('username'))
            password = escape(self.request.get('password'))
            logging.info("Handling request for %s" % username)
            t = Twitter(username, password)
            friends = set([f['screen_name'] for f in t.get_friends()])
            followers = set([f['screen_name'] for f in t.get_followers()])
            to_follow = followers.difference(friends)

            try:
                for user in to_follow:
                    try:
                        t.friendship_create(user, True)
                        logging.info("%s now follows %s" % (username, user))
                    except DownloadError:
                        logging.warning("Download error when %s tried to follow %s" % (username, user))
                        raise

                self.response.out.write(template.render(path, {"success": True}))

            except Exception, e:
                logging.warning("Caught an exception %s when %s tried to follow %s: %s" % (e, username, user))
                raise

        except DeadlineExceededError:
            self.response.out.write(template.render(path, {"error": True}))


application = webapp.WSGIApplication([('/', MainPage)], debug=False)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

