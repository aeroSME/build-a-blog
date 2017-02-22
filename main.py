import jinja2
import os
import webapp2
import logging
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)


class MainPage(Handler):
    def render_base(self):
        posts = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("base.html", posts=posts)

    def get(self):
        self.render_base()

class NewPost(Handler):
    def render_post(self, title="", post="", error=""):
        self.render("post.html", title=title, post=post, error=error)

    def get(self):
        self.render_post()

    def post(self):
        title = self.request.get("title")
        post = self.request.get("post")

        if title and post:
            b= Blog(title = title, post = post)
            b.put()
            b.key().id()

            self.redirect("/blog")
        else:
            error = "We need both a title and a blog entry!"
            self.render_post(title, post, error)


class ViewPostHandler(Handler):
    def render_single(self, title="", post="", error=""):
        self.render("single-post.html", title=title, post=post, error=error)

    def get(self, id):
        data = Blog.get_by_id(int(id))
        # self.response.write(str([data.title, data.post]))
        title = data.title
        post = data.post
        self.render_single(title, post)


app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/newpost', NewPost),

    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
