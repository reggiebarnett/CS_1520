import cgi
import logging
import models
import os
import webapp2

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images

COUNT = 9

###############################################################################
# Render the named template from the /templates directory.
###############################################################################
def render_template(handler, templatename, templatevalues) :
  path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
  html = template.render(path, templatevalues)
  handler.response.out.write(html)


###############################################################################
# Retrieve the FiveUser object associated with the current user.
###############################################################################
def get_five_user():
  result = None
  user = users.get_current_user()
  if user: 
    result = models.get_user(user.email())
    # if we have a logged-in user but no FiveUser object, we will create one.
    if not result:
      result = models.save_user(user.email())
  return result


###############################################################################
# Retrieve default parameters for the current page template.  We'll use these
# for the header menu and for the user.
###############################################################################
def get_params():
  params = dict()
  user = get_five_user()
  if user:
    params['user'] = user
    params['user_url'] = users.create_logout_url('/')
    params['user_url_label'] = 'logout'
  else:
    params['user_url'] = users.create_login_url('/')
    params['user_url_label'] = 'login with google'
  return params

    
###############################################################################
# Handle an upload, store it to the blobstore if it's an image, and redirect
# the user to their user page.
###############################################################################
class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
  def post(self):
    upload_files = self.get_uploads('image')
    blob_info = upload_files[0]
    # now we need to save this for the user
    user = get_five_user()
    type = blob_info.content_type
    if type in ['image/jpeg', 'image/png', 'image/gif', 'image/webp']:
      if user.picture:
        # we want to delete the old picture first.
        old_blob = blobstore.BlobInfo.get(blobstore.BlobKey(user.picture))
        old_blob.delete()
      user.set_picture(blob_info.key())
      self.redirect('/u/' + user.name)
    else: 
      blob_info.delete()
      self.redirect('/u/' + user.name + '?code=119')

###############################################################################
# Render a basic index.html page.
###############################################################################
class MainPage(webapp2.RequestHandler):
  def get(self) :
    render_template(self, 'index.html', get_params())

###############################################################################
# Retrieve posts as a JSON array and send to client.
###############################################################################
class GetPosts(webapp2.RequestHandler):
  def post(self):
    self.get()
    
  def get(self):
    since_time = 0
    try:
      since_time = int(self.request.get('since'))
    except:
      since_time = 0
    logging.info('since: ' + str(since_time))
    self.response.out.write(models.get_posts_if_new(since_time))

###############################################################################
# Check the input parameters for validity, check the user's post rate, and 
# save the post if there are no issues.
###############################################################################
class CreatePost(webapp2.RequestHandler):
  def post(self):
    user = get_five_user()
    if user:
      if user.name:
        text = self.request.get('text')
        if len(text) <= COUNT:
          link = self.request.get('link')
          if len(link) <= 200:
            original = self.request.get('reply')
            if user.get_user_rate() <= 60:
              # prevent blank posts
              if text.strip() != '':
                user.create_post(text, original, link)
                self.response.out.write('OK')
              else:
                self.response.out.write('121')
            else:
              self.response.out.write('124')
          else:
            self.response.out.write('999')
        else:
          self.response.out.write('128')
      else:
        self.response.out.write('125')
    else:
      self.response.out.write('100')
      
  def get(self):
    self.post()

############################################################################### 
# Determine if a username is valid.
###############################################################################
def validate_username(username):
  result = True
  username = username.lower()
  if len(username) > 128 or len(username) == 0:
    result = False
  else:
    for c in username:
      if not (c.isalnum() or c == '_' or c == '-'):
        result = False
        break
  return result

###############################################################################
# Handler for setting username.  Username is required before a user can make
# a post.
###############################################################################
class SetUsername(webapp2.RequestHandler):
  def post(self):
    user = get_five_user()
    if user:
      username = self.request.get('username')
      if validate_username(username):
        if user.set_user_name(username):
          self.response.out.write('OK')
        else:
          self.response.out.write('127')
      else:
        self.response.out.write('126')
        
  def get(self):
    self.post()

###############################################################################
# Set the user's colors based on input parameters.
###############################################################################
class SetColors(webapp2.RequestHandler):
  def post(self):
    user = get_five_user()
    if user:
      background = self.request.get('background')
      foreground = self.request.get('foreground')
      if background[1:].isalnum() and foreground[1:].isalnum(): 
        user.set_colors(background, foreground);
        self.response.out.write('OK')
      else:
        self.response.out.write('123')
    else:
      self.response.out.write('100')
    
###############################################################################
# Retrieve the user for this user profile page, and render it using user.html.
###############################################################################
class UserPage(webapp2.RequestHandler):
  def get(self):
    page_username = self.request.path[3:]
    posts_json = models.get_user_posts_as_json(page_username)
    
    params = get_params()
    params['page_name'] = page_username
    
    params['posts_json'] = posts_json
    try:
      page_user = models.get_user_by_name(page_username)
      params['image_url'] = images.get_serving_url(page_user.picture)
    except:
      params['image_url'] = None

    user = get_five_user()
    if user:
      params['upload_url'] = blobstore.create_upload_url('/upload')
      params['user'] = user        
      if not params['user'].foreground: 
        params['user'].foreground = '#000000';
      if not params['user'].background:
        params['user'].background = '#ffffff';
    
    render_template(self, 'user.html', params)

###############################################################################
# Map the proper URLs to pages.
###############################################################################
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/posts', GetPosts),
  ('/create', CreatePost),
  ('/setuser', SetUsername),
  ('/setcolors', SetColors),
  ('/u/.*', UserPage),
  ('/upload', UploadHandler)
])