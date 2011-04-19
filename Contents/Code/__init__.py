import re, string
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

PLUGIN_PREFIX		= "/video/dimecasts-net"
URL_MAIN			= "http://dimecasts.net"

###################################################################################################
def Start():
  Plugin.AddPrefixHandler(PLUGIN_PREFIX, MainMenu, 'Dime Casts.NET', 'dimecasts.jpg', 'art-default.jpg')
  Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")
  MediaContainer.title1 = 'Dime Casts.NET'
  MediaContainer.content = 'Items'
  MediaContainer.art = R('art-default.jpg')
  HTTP.SetCacheTime(CACHE_INTERVAL)

###################################################################################################
def MainMenu():
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(ListByUrl, 		title = 'Latest Episodes'), title = 'Current Episodes', url = '/'))
  
  dir.Append(Function(DirectoryItem(ByQuickLink, 		title="Episodes by Tags"), 		quickLink = 'Tag'))
  dir.Append(Function(DirectoryItem(ByQuickLink, 		title="Episodes by Authors"), 	quickLink = 'Author'))
  dir.Append(Function(DirectoryItem(ByQuickLink, 		title="Episodes by Levels"), 	quickLink = 'Level'))
  return dir

def ByQuickLink(sender, quickLink):
	dir = MediaContainer(title2 = quickLink + 's')
	for item in GetQuickLinks('Casts ' + quickLink + 's'):
		name = item['name']
		title = name + ' (' + item['items'] + ')'
		dir.Append(Function(DirectoryItem(ListByUrl,     title = title), title = quickLink + ' ' + name, url = '/Casts/By' + quickLink + '/' + name.replace(' ', '%20')))	
	return dir

def ListByUrl(sender, title, url):
	dir = MediaContainer(title2 = title, viewGroup='Details')
	e = XML.ElementFromURL(URL_MAIN + url, True)
	
	total = e.xpath("count(//div[@class='post'])")
	for i in range(1, total + 1):
		AddVideo(dir, e, i)

	return dir

def AddVideo(dir, element, index):
	# we have to parse the watch url for each video to be able to parse out the full path to the video file
	# http://dimecasts.net/Content/WatchEpisode/###
	# http://www.dimecasts.com/Episodes/###/SomeRandomName.wmv'
	
	basePath = "//div[@id='content']/div[@class='post'][" + str(index) + "]/div/table"
	
	dataItems = element.xpath(basePath + "//td[@class='EpisodeDataItem']")
	
	id = dataItems[0].text.strip('# ')
	date = dataItems[1].text
	author = dataItems[8].xpath('a')[0].text
	
	e = XML.ElementFromURL(URL_MAIN + '/Content/WatchEpisode/' + id, True)
	
	url = e.xpath("//embed")[0].get('src')
	
	durationData = element.xpath(basePath + "//td[@valign='bottom']/text()")[2].split('(')[2].split(')')[0].replace('.', ':').split(':')
	duration = 0
	
	duration = (int(durationData[0]) * 60 + int(durationData[1])) * 1000

	title = element.xpath(basePath + "//a[@class='EpisodeHeader']")[0].text
	
	summary = ''
	for t in element.xpath(basePath + "//td[@align='left']//td//text()"):
		summary += t + '\n'

	dir.Append(VideoItem(url, title=title, subtitle= date + ' by ' + author, summary=summary, duration=duration))
	return dir

def GetQuickLinks(title):
	result = []
	element = XML.ElementFromURL(URL_MAIN, True)
	for tagData in element.xpath("//td[text()='" + title + "']/../..//a"):
		t = tagData.text.split('(')
		result.append({'name': t[0].strip(), 'items': t[1].strip(')')})
	return result
