import sublime_plugin
import sublime
import sys, os, imp

sys.path.append(os.path.dirname(__file__)) 

import apiGateway
apiGateway = imp.reload(apiGateway)

class blogCategoryCompletion(sublime_plugin.EventListener):
	def on_query_completions(self, view, prefix, locations):
		self.blog_settings = apiGateway.LoadMetaBlogSettings
		self.blog_api = apiGateway.GetBlogApi()

		for category in self.blog_api.get_categories():
			print(">>>>> " + category)
			self.words.append([category, category])

		return self.words