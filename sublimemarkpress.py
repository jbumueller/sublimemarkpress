import sublime, sublime_plugin # sublime
import sys, os, imp
sys.path.append(os.path.dirname(__file__)) 
sys.path.append(os.path.join(os.path.dirname(__file__), "python-markdown2"))
from lib import markdown2

import apiGateway
apiGateway = imp.reload(apiGateway)

class PublishCommand(sublime_plugin.TextCommand):
	r""" 
		** Pushes the curent active file to a metaweblog compatible blog **

		# blog settings
		Relies on a settings file called "sublimemarkpress.sublime-settings" using the structure, where blog_id is optional. If blog_id is not set it is hanled as 0 integer:
			{
			    "xmlrpcurl": <URL to xml rpc endpoint>,
			    "username": <username>,
			    "password": <password>,
			    "blog_id" : <blog id> (if not set a default value is used),
			    "engine"  : <DotNetBlogEngine|WordPress|MovableType> (if not set plain MetaWeblog API is used)
			}

		# tags
		blog tags are optional at the top of the file in the structure:
		<!-- 
		#post_id:<id of existing post - optional>
		#tags:<comma delimited list of post tags - optional>
		#categories:<comma delimited list of post categories - optional>
		#status:<draft or publish - optional>
		-->
 
		# title
		blog title is the first line following that section; if it starts with "#" then it's assumed
		to be a markdown post

		# markdown
		If the file "markdown2.py" from the awesome repo https://github.com/trentm/python-markdown2/tree/master/lib exists, markdown is enabled
	"""
	def run(self, edit):
		self.blog_settings = apiGateway.LoadMetaBlogSettings()
		self.blog_api = apiGateway.GetBlogApi()
   
		# get page content
		all_lines_in_page = self.view.lines(sublime.Region(0, self.view.size()))
		header_lines = []
		
		# get the "header" (MB details)
		post_id, tags, categories, status, has_header_content = self.GetHeaderContent(all_lines_in_page, header_lines)

		#title
		title, is_markdown = self.GetTitle(self.view, all_lines_in_page, header_lines)

		# get the "body" (content)
		post_content = self.GetPostContent(self.view,all_lines_in_page, is_markdown)
 
		# create request
		content = self.BuildPostContent(self.view, {"content": post_content, "title": title, "tags": tags, "categories": categories, "status": status})

		# save to MB
		new_post, post_id = self.SaveToMetaWeblog(self.view, edit, post_id, content)

		#  update active window with post id, if new
		if new_post:
			self.PrefixPostHeader(self.view, edit, post_id, header_lines, has_header_content)
 
	def GetHeaderContent(self, all_lines_in_page, header_lines):
		page_info = {"has_header_content":False,"post_id":None, "tags":"", "categories":[], "status":""}

		if self.view.substr(all_lines_in_page[0]).startswith("<!--"):
			page_info["has_header_content"] = True
			self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			# post_id
			if self.view.substr(all_lines_in_page[0]).startswith("#post_id"):
				page_info["post_id"] = self.view.substr(all_lines_in_page[0]).split(":")[1]
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			#post tags
			if self.view.substr(all_lines_in_page[0]).startswith("#tags"):
				page_info["tags"] = self.view.substr(all_lines_in_page[0]).split(":")[1]
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)
			
			#post categories
			if self.view.substr(all_lines_in_page[0]).startswith("#categories"):
				page_info["categories"] = self.view.substr(all_lines_in_page[0]).split(":")[1].split(",")
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			#post status
			if self.view.substr(all_lines_in_page[0]).startswith("#status"):
				page_info["status"] = self.view.substr(all_lines_in_page[0]).split(":")[1]
				self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

			self.MoveCurrentLineToHeader(header_lines, all_lines_in_page) # removes the closing comment tag
		return page_info["post_id"],page_info["tags"],page_info["categories"],page_info["status"],page_info["has_header_content"]

	def GetTitle(self, view, all_lines_in_page, header_lines):
		is_markdown = False
		if self.view.substr(all_lines_in_page[0]).startswith("# "):
			title = self.view.substr(all_lines_in_page[0]).split("# ")[1]
			is_markdown = True
		else:
			title = self.view.substr(all_lines_in_page[0])
		
		# remove the title from the content (else it'll get repeated within the content)		
		self.MoveCurrentLineToHeader(header_lines, all_lines_in_page)

		return title, is_markdown

	def GetPostContent(self, view, all_lines_in_page, is_markdown):
		post_content = self.CombineContent(self.view, all_lines_in_page)

		# Can be dropped? Should not be required anymore as markdown2 is a submodule.
		# can_markdown = False
		# try: 
		# 	if int(sublime.version()) >= 3000:
		# 		from . import markdown2		
		# 	else:
		# 		import markdown2 # markdown

		# 	can_markdown = True
		# except ImportError:
		# 	can_markdown = False

		# markdown content
		if is_markdown: # and can_markdown:
			post_content = str(markdown2.markdown(post_content,extras=["code-friendly"]))

		return post_content

	def MoveCurrentLineToHeader(self, header_lines, all_lines_in_page):
			header_lines.insert(len(header_lines),all_lines_in_page[0])
			all_lines_in_page.remove(all_lines_in_page[0])

	def BuildPostContent(self, view, page_data):		
		return {"description": page_data["content"], "post_content": page_data["content"], "title": page_data["title"], "mt_keywords": page_data["tags"], "categories": page_data["categories"], "post_status": page_data["status"]}

	def CombineContent(self, view, lines):
		return view.substr(sublime.Region(lines[0].begin(),lines[len(lines)-1].end()))

	def PrefixPostHeader(self, view, edit, post_id, header_lines, has_header):
		post_header = "<!--" + '\n' + "#post_id:" + str(post_id) + '\n'
 
		if has_header:
			end_point = header_lines[1].begin()
			header_lines.remove(header_lines[0])
			view.replace(edit, sublime.Region(0, end_point), post_header)
		else:
			view.replace(edit, sublime.Region(0,0), post_header + "-->" + '\n')

	def RemoveFromMetaWeblog(self, post_id):
		self.blog_api.delete_post(post_id)

	def SaveToMetaWeblog(self, view, edit, post_id, content):
		updated = False
		publish = True

		if content["post_status"] == "draft":
			publish = False
        
		if post_id == None:
			post_id = self.blog_api.new_post(content, publish, self.blog_settings["blog_id"])
			updated = True
			print("created new:", post_id)
		else:
			self.blog_api.edit_post(post_id,content)
			print("updated existing:", post_id)

		return updated, post_id