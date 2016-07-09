import time
import logging
from google.appengine.ext import ndb
from google.appengine.api import memcache

POSTS_KEY = 'posts'
JSON_KEY = 'posts_json'
POST_COUNT = 200
USER_POST_COUNT = 20

###############################################################################
# FiveUser - this is the main user object representation.
###############################################################################
class FiveUser(ndb.Model):
  name = ndb.StringProperty()
  email = ndb.StringProperty()
  background = ndb.StringProperty()
  foreground = ndb.StringProperty()
  picture = ndb.StringProperty()
  
  #############################################################################
  # This object method creates a post made by this user.
  def create_post(self, text, original, link):
    p = Post(parent=self.key)
    p.text = text
    p.reply_to = original
    p.link = link
    p.username = self.name
    p.time_posted = int(time.time() * 1000)
    p.background = self.background
    p.foreground = self.foreground
    p.save()
    memcache.incr(self._get_rate_key(), initial_value=0)
    memcache.delete('p_' + self.email)
    return p
    
  #############################################################################
  # Retrieve the recent posts made by this user.  This automatically handles 
  # caching the results in memcache.
  def get_posts(self):
    posts = memcache.get('p_' + self.email)
    if not posts:
      posts = list()
      q = Post.query(ancestor=self.key)
      q = q.order(-Post.time_posted)
      result = q.fetch(USER_POST_COUNT)
      for post in result:
        posts.append(post)
      memcache.set('p_' + self.email, posts)
    return posts

  #############################################################################
  # Retrive the cached rate - this is a counter that represents the user's 
  # recent posts.  This is to prevent one user from overwhelming / spamming
  # the system with too many posts.
  def get_user_rate(self):
    result = 0
    cached_rate = memcache.get(self._get_rate_key())
    if cached_rate:
      result = cached_rate
    return cached_rate
    
  #############################################################################
  # Reset the post rate counter.
  def reset_rate(self):
    memcache.set(self._get_rate_key(), 0)
    
  #############################################################################
  # Retrieve the key for the memcache entry for this user.
  def _get_rate_key(self):
    return 'rate_' + self.email
    
  #############################################################################
  # Save this user to the datastore and recache the updated object in memcache.
  def save(self):
    self.put()
    self._recache()
            
  #############################################################################
  # Set this user's colors and save the user.
  def set_colors(self, background, foreground):
    self.foreground = foreground
    self.background = background
    self.save()
    
  #############################################################################
  # Recache this object in memcache.  This should be called whenever any data
  # is changed.
  def _recache(self):
    memcache.set('e_' + self.email, self)
    if self.name:
      memcache.set('u_' + self.name, self)
      
  #############################################################################
  # Set the user's name.  Since we're using username as a pertinent value in 
  # the post object, we do not want user's to change this. We also don't want
  # users to have the same name, so we check that here before setting the name.
  def set_user_name(self, name):
    result = False
    if not self.name:
      q = FiveUser.query().filter(FiveUser.name == name) 
      if len(q.fetch(1)) == 0:
        self.name = name
        self.save()
        result = True
    return result

  #############################################################################
  # Set the user's picture.  This is an ID from blobstore.
  def set_picture(self, blob_id):
    self.picture = str(blob_id)
    self.save()
    
###############################################################################
# Save a user to the datastore based on default values.
###############################################################################
def save_user(email):
  result = FiveUser()
  result.email = email
  result.background = '#ffffff'
  result.foreground = '#000000'
  result.save()
  return result
  
###############################################################################
# Retrieve all of the users.
###############################################################################
def get_users():
  result = list()
  q = FiveUser.query()
  for user in q.fetch(100000):
    result.append(user)
  return result

###############################################################################
# Retrieve a user based on the user's email.
###############################################################################
def get_user(email):
  result = memcache.get('e_' + email)
  if not result:
    users = FiveUser.query().filter(FiveUser.email == email).fetch(1)
    if len(users) > 0:
      result = users[0]
      result._recache()
  return result
  
###############################################################################
# Retrieve a user by username.
###############################################################################
def get_user_by_name(name):
  result = memcache.get('u_' + name)
  if not result:
    users = FiveUser.query().filter(FiveUser.name == name).fetch(1)
    if len(users) > 0:
      result = users[0]
      result._recache()
  return result

###############################################################################
# Provide a cleaned value for JSON output.
###############################################################################
def clean(value):
  result = ''
  if value:
    for i in range(0, len(value)):
      c = value[i]
      if c == "'":
        result += '&#39;'
      elif c == '<':
        result += '&lt;'
      elif c == '"':
        result += '&quot;'
      elif c == '\n':
        result += '<br>'
      elif c == '\\':
        result += '\\\\'
      else:
        result += c
  return result
  
###############################################################################
# Retrieve the user's recent posts as a JSON string.
###############################################################################
def get_user_posts_as_json(username):
  user = get_user_by_name(username)
  return build_data_json(user.get_posts())
  
###############################################################################
# Create a JSON string for the loaded posts and users.
# We use a user-mapping within the JSON object here to minimize space.
#
# Note that we are saving the JSON to memcache here because there's no sense
# in using additional processing cycles to build the exact same JSON string 
# over and over again.
###############################################################################
def get_posts_as_json():
  post_json = memcache.get(JSON_KEY)
  if not post_json:
    logging.info('Building posts_json.')
    posts = get_posts(POST_COUNT)
    my_time = 0
    if len(posts) > 0:
      my_time = posts[0].time_posted
    logging.info('Retrieved ' + str(len(posts)) + ' posts to build JSON.')
    
    json_text = build_data_json(posts)
    
    post_json = (my_time, json_text)
    memcache.set(JSON_KEY, post_json)
    logging.info('Saved posts_json with timestamp ' + str(my_time))
  else:
    logging.info('Loading posts_json from memcache.')
  return post_json[1]

###############################################################################
# Build JSON from the set of posts; first, extract the user information and
# then build the post JSON using the user mapping.
###############################################################################
def build_data_json(posts):
  users = build_users_map(posts)
  user_json = build_users_json(users)
  post_json = build_posts_json(posts, users)
  return '{"users":' + user_json + ',"posts":' + post_json + '}'

###############################################################################
# Build a map of users to counter - this can be used to minimize space in JSON.
###############################################################################
def build_users_map(posts):
  users = dict()
  counter = 0
  for post in posts:
    if post.username not in users:
      # It's not a best practice, but we're using a tuple here to store these
      # values.  We'll use these later to populate post data in the JSON.
      users[post.username] = (counter, post.foreground, post.background)
      counter += 1
  return users
  
###############################################################################
# Build the JSON from the users; we'll take these from the tuple built in 
# the build_users_map function.
###############################################################################
def build_users_json(users):
  result = '['
  first = True
  for u in users:
    user = users[u]
    if first:
      first = False
    else:
      result += ','
    result += '{'
    result += '"n":"' + u + '",'
    result += '"i":' + str(user[0]) + ','
    if user[1]:
      result += '"fg":"' + user[1] + '",'
    else:
      result += '"fg":"#000000",'
    if user[2]:
      result += '"bg":"' + user[2] + '"'
    else:
      result += '"bg":"#ffffff"'
    result += '}'
  result += ']'
  return result
  
###############################################################################
# Build JSON out of the retrieved posts.  
###############################################################################
def build_posts_json(posts, users):
  result = '['
  first = True
  for post in posts:
    if first:
      first = False
      my_time = post.time_posted
    else:
      result += ','
    result += '{"text":"' + clean(post.text) + '",'
    result += '"time":"' + str(post.time_posted) + '",'
    result += '"u":' + str(users[post.username][0]) + '}'
  result += ']'
  return result

###############################################################################
# Get JSON for posts newer than a specific time.  If there are no newer posts,
# return '{"users":[],"posts":[]}' 
# - if there are newer posts, return all 200 as JSON.
###############################################################################
def get_posts_if_new(time):
  result = '{"users":[],"posts":[]}'
  post_json = memcache.get(JSON_KEY)
  if post_json:
    if post_json[0] > time:
      logging.info('Retrieving fresh posts_json.')
      result = post_json[1]
    else:
      logging.info('Cached post_json is not new.')
  else:
    result = get_posts_as_json()
  return result

###############################################################################
# Object representation of posts.  Includes method for saving.
###############################################################################
class Post(ndb.Model): 
  text = ndb.StringProperty()
  time_posted = ndb.IntegerProperty()
  reply_to = ndb.StringProperty()
  link = ndb.StringProperty()
  username = ndb.StringProperty()
  background = ndb.StringProperty()
  foreground = ndb.StringProperty()

  #############################################################################
  # Save this post and update the set of cached posts.
  def save(self):
    self.put()
    logging.info('Saved post to datastore.')
    client = memcache.Client()
    counter = 0
    while counter < 100:
      counter += 1
      posts = client.gets(POSTS_KEY)
      if not posts:
        counter = 100
      else:
        posts.insert(0, self)
        while len(posts) > POST_COUNT:
          posts.pop()
        if client.cas(POSTS_KEY, posts):
          logging.info('Saved updated post list to memcache.')
          break
    logging.info('Deleting posts_json from memcache.')
    memcache.delete(JSON_KEY)

###############################################################################
# Retrieve posts from the cache, or load the cache if posts are not yet
# cached.
###############################################################################
def get_posts(count):
  posts = memcache.get(POSTS_KEY)
  if not posts:
    logging.info('Loading posts from datastore.')
    posts = list()
    q = Post.query()
    q = q.order(-Post.time_posted)
    result = q.fetch(count)
    for post in result:
      posts.append(post)
    memcache.set(POSTS_KEY, posts)
  else:
    logging.info('Loading posts from memcache.')
  return posts