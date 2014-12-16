import sublime, sublime_plugin # sublime
import sys, os, imp

sys.path.append(os.path.join(os.path.dirname(__file__), "python-blogger"))

import pyblog
pyblog = imp.reload(pyblog)  

def LoadMetaBlogSettings():
	s = sublime.load_settings("sublimemarkpress.sublime-settings")
	return {"url": s.get("xmlrpcurl"), "username": s.get("username"), "password": s.get("password"), "blog_id": s.get("blog_id"), "engine": s.get("engine")}

def GetBlogApi():
	blog_settings = LoadMetaBlogSettings()
	if blog_settings["engine"] == "DotNetBlogEngine":
		return pyblog.DotNetBlogEngine(blog_settings["url"], blog_settings["username"], blog_settings["password"], blog_settings["blog_id"])

	if blog_settings["engine"] == "WordPress":
		return pyblog.WordPress(blog_settings["url"], blog_settings["username"], blog_settings["password"], blog_settings["blog_id"])

	if blog_settings["engine"] == "MovableType":
		return pyblog.MovableType(blog_settings["url"], blog_settings["username"], blog_settings["password"], blog_settings["blog_id"])

	return pyblog.MetaWeblog(blog_settings["url"], blog_settings["username"], blog_settings["password"], blog_settings["blog_id"])