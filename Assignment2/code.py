import os
import webapp2

from google.appengine.ext.webapp import template

def render_template(handler, templatename, templatevalues):
	path = os.path.join(os.path.dirname(__file__), 'templates/' + templatename)
	html = template.render(path, templatevalues)
	handler.response.out.write(html)


class MainPage(webapp2.RequestHandler):
  def get(self):
    render_template(self, 'index.html', {})
	

class ProcessForm(webapp2.RequestHandler):
  def post(self):
	num1 = self.request.get('num1')
	oper = self.request.get('oper')
	num2 = self.request.get('num2')
	if oper == '+':
		result = int(num1) + int(num2)
	elif oper == '-':
		result = int(num1) - int(num2)
	elif oper == '*':
		result = int(num1) * int(num2)
	else:
		result = int(num1) / int(num2)
	render_template(self, 'formresult.html', {
	  "num1": num1,
	  "oper": oper,
	  "num2": num2,
	  "result": result
	})
	
	
app = webapp2.WSGIApplication([
  ('/', MainPage),
  ('/processform', ProcessForm)
], debug=True)  