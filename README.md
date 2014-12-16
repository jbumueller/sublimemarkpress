# Pushes the currently active SublimeText file to a metaweblog compatible blog
## Warning: still work in progress
- This project isn't tested yet.
- These are my first steps on python so excuse if I do not follow all conventions.

## History
This is a fork of https://github.com/rposbo/sublimemarkpress a Sublime Text 2 (ST2) plugin for posting content to Wordpress. I did like that approach pretty much, but had additional requirements therefore I built this fork.

### What did change
- Added support for ST3
- ST2 Support is not tested, but it might be compatible
- Added support for other blogging engines
- In Addition to tags I added category assignment to post
- Added an third party MetaWeblogApi Wrapper for Python (https://github.com/theatlantic/python-blogger)
- Embeded markdown2 lib (https://github.com/trentm/python-markdown2) to plugin, no custom install needed anymore

### What is going to change next
- Add Sublime Text Command Palette
- Completion for Tags and Categories
- Delivery through PackageControl
- Upload Images

## Usage
### Blog settings
	Relies on a settings file called "sublimemarkpress.sublime-settings" using the structure:
	{
	    "xmlrpcurl": <URL to xml rpc endpoint>,
	    "username": <username>,
	    "password": <password>,
	    "blog_id" : <blog id> (if not set a default value is used),
	    "engine"  : <DotNetBlogEngine|WordPress|MovableType> (if not set plain MetaWeblog API is used)
	}

### Post settings
	Blog tags are optional at the top of the file in the structure:
	<!-- 
	#post_id:<id of existing post - optional>
	#tags:<comma delimited list of post tags - optional>
	#categories:<comma delimited list of post categories - optional>
	#status:<draft or publish - optional>
	-->

### Title
Blog title is the first line following that section; if it starts with "#" then it's assumed to be a markdown post. Otherwise content is published without any preprocessing.

### Publishing
Currently, you need to copy this file into the sublimetext packages/user directory. Then on the file you wish to post press ctrl+' and type "view.run_command('publish')"

## key mapping
Doesn't pass the "view", so not sure how to do this correctly yet.