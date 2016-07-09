import webapp2
import models

from google.appengine.api import memcache

###############################################################################
# Reset the counters for user rate limits.
###############################################################################
class ResetRates(webapp2.RequestHandler):
  def get(self):
    users = models.get_users()
    for user in users:
      user.reset_rate()
    self.response.out.write('ok')
    
###############################################################################
# Map this Python file's RequestHandler objects to URLs.
###############################################################################
app = webapp2.WSGIApplication([
  ('/crontasks/reset', ResetRates)
])