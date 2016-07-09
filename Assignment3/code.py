import os
import webapp2
import time
import datetime

from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.api import users

def render_template(handler, templatename, templatevalues):
	path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
	html = template.render(path, templatevalues)
	handler.response.out.write(html)

#Main page just for logging in
class MainPage(webapp2.RequestHandler):
  def get(self):
    username = users.get_current_user()
    login = users.create_login_url('/notes')
    logout = users.create_logout_url('/')
    template_values = {
      'username': username,
      'login': login,
      'logout': logout
    }
    render_template(self,'index.html',template_values)
	
#Stores note info
class NoteInfo(ndb.Model):
  user = ndb.StringProperty()
  subject = ndb.StringProperty()
  note_text = ndb.StringProperty()
  time = ndb.StringProperty()
  date = ndb.StringProperty()

#Sets up the page that shows your notes
class NotePage(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    getNotes = NoteInfo.query(NoteInfo.user == user.nickname())
    #Building string that will show notes in a list
    buildList = '<ul>'
    for note in getNotes.iter():
      buildList += '<li><a href=\'/note/'+str(note.key.id())+'\'>'+note.date+': '+note.subject+'</a></li>'
    buildList += '</ul>'

    template_values = {
      'noteList': buildList
    }
    render_template(self, 'note_page.html', template_values)
	
#Allows users to add notes, takes you to editable note page
class AddNote(webapp2.RequestHandler):
  def get(self):
    user = users.get_current_user()
    note = NoteInfo()
    note.user = user.nickname()
    time = datetime.datetime.now(GetEST())
    note.time = time.strftime("%I: %M %p")
    note.date = time.strftime("%Y-%m-%d")
    note.subject = 'Untitled Note'
    note.note_text = ''
    note.put()
    note_id = note.key.id()
    self.redirect('/note/'+str(note_id))
	
#Allows users to edit their notes
class EditNote(webapp2.RequestHandler):
  def get(self,note_id):
	user = users.get_current_user()
	note = ndb.Key(NoteInfo,int(note_id)).get()
	note_subject = note.subject
	note_text = note.note_text
	note_date = note.date
	note_time = note.time
	template_values = {
	  'user': user,
	  'note_id': note.key.id(),
	  'subject': note_subject,
	  'note_text': note_text,
	  'date': note_date,
	  'time': note_time
	}
	render_template(self,'edit_note.html',template_values);
	
#Allow user to edit note title
class SaveTitle(webapp2.RequestHandler):
  def post(self):
	title = self.request.get('title')
	note_id = self.request.get('note_id')
	note = ndb.Key(Note,int(note_id)).get()
	note.subject = title
	time = datetime.datetime.now(GetEST())
	note.time = time.strftime("%I: %M %p")
	note.date = time.strftime("%Y-%m-%d")
	note.put()
	
#Allow user to manual save notes
class SaveNotes(webapp2.RequestHandler):
  def post(self):
	body = self.request.get('body')
	note_id = self.request.get('note_id')
	note = ndb.Key(NoteInfo,int(note_id)).get()
	note.note_text = body
	time = datetime.datetime.now(GetEST())
	note.time = time.strftime("%I: %M %p")
	note.date = time.strftime("%Y-%m-%d")
	note.put()
	
#Get EST 
class GetEST(datetime.tzinfo):
  def utcoffset(self, dt):
    return datetime.timedelta(hours=-4)

  def dst(self, dt):
    return datetime.timedelta(0)
	
	
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/notes', NotePage),
  ('/addnote',AddNote),
  ('/note/(\d+)',EditNote),
  ('/savetitle',SaveTitle),
  ('/savenotes',SaveNotes)
], debug=True)  