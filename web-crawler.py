from bs4 import BeautifulSoup
import certifi
import tldextract
import sys
import requests
import hashlib
import time
import validators
import json

# Ways to use crawler:
# --------------------
# A. Use manual setting: lines 255-260:
#	 main_url = ''     # write URL string
#	 crawl_depth = 5   # default, try to play with it

# B. Demo settings (coded in settings_by_input()):
#	 DOMAIN =  'https://cyfrowa-wyprawka.org/'
#	 CRAWL_DEPTH = 10

# C. Run by input (coded in settings_by_input()):
#	 DOMAIN =  'https://cyfrowa-wyprawka.org/'
#	 CRAWL_DEPTH = 10

# D. Run by function:
#	 delete 'if __main__ (...)'
#	 use: get_sitemap(url, crawl_depth)


# 1. Set target URL and crawl_depth by input OR use demo values.
# --------------------------------------------------------------
def settings_by_input():

	# A. Input URL or DEMO values
	while True:
		print("Please enter:\na) URL link to scrap ('fg. 'https://cyfrowa-wyprawka.org/') or\nb) 'demo' for demo example:")
		url = input()
		if url == 'demo':
			DOMAIN = 'https://cyfrowa-wyprawka.org/'
			CRAWL_DEPTH = 10
			break
		if not validators.url(url):
			('Mistake in url.')
			continue
		DOMAIN = url
		CRAWL_DEPTH = 'set me'
		break

	# B. Input crawl depth
	if CRAWL_DEPTH == 'set me':
		while True:
			try:
				CRAWL_DEPTH = input("Please enter desired crawl depth (integer):")
				CRAWL_DEPTH = int(CRAWL_DEPTH)
				break
			except ValueError:
				print("No valid integer! Please try again ...")

	return [DOMAIN, CRAWL_DEPTH]


# 2. Get page as a soup object.
# -----------------------------
def get_soup(link):
	# Return the BeautifulSoup object for input link
	request_object = requests.get(link, auth=('user', 'pass'))
	soup = BeautifulSoup(request_object.content, features='lxml')
	return soup


# 3. Get links out of soup object.
# --------------------------------
def get_raw_links(soup):
	return [a.get('href') for a in soup.find_all('a', href=True)]


# 4. Filter out and prepare valid links from soup.
# ------------------------------------------------
def clean_links(raw_links):
	
	# Filter popular websites with our URL suffix possibility (fg. twitter.com/clearcodehq )
	# Add more + Add regexp on: not DOMAIN-NAME + '.com'
	stop_phrases = ['twitter.com', 'facebook.com', 'google.com', 'linkedin.com', 'youtube.com', 'github.com'] 
	filtered_links = []
	for link in raw_links:
		if not any(s in link for s in stop_phrases):
			filtered_links.append(link)

	# Filter URLs outside of our domain [requires above]
	raw_links = list(set([link for link in filtered_links if DOMAIN_NAME in link]))

	# Filter Email links
	raw_links = list(set([link for link in raw_links if not 'mailto' in link]))
	
	# Make valid links.
	links = []
	exceptions = []
	for i, link in enumerate(raw_links):
		if "http" not in link and "/" in link:
			links.append(DOMAIN + link)
		elif "http" in link:
			links.append(link)
		elif "html" in link[5:]:
			links.append(DOMAIN + link)
		else:
			exceptions.append(link)

	# For testing.
	if exceptions:
		print('({}) Exceptions'.format(len(exceptions)))
		#[print('-' exception) for exception in exceptions]

	return list(set(links))


# 5. Get intial page data.
# -------------------
def get_main_page(url):
	soup = get_soup(url)
	raw_links = get_raw_links(soup)
	links = list(set(clean_links(raw_links)))
	sitemap = dict()
	for link in links:
		sitemap[link] = dict()

	if sitemap.keys():
		print('There are at least {} more valid links to get. We need to go deeper...\n'.format(len(sitemap)))

	return sitemap


# 6. Get links and title form target page.
# ----------------------------------------
def get_next_level_data(url):
	soup = get_soup(url)
	try:
		title = soup.title.string
	except:
		title = ''
	raw_links = get_raw_links(soup)
	links = list(set(clean_links(raw_links)))
	return title, links


# 7. Get one level down data.
# ---------------------------
def we_need_to_go_deeper(sitemap, VISITED_URLS, next_level_links):

	# Get this level crawl time for further statistics.
	start = time.time()
	
	for i, link in enumerate(next_level_links):
		title, links = get_next_level_data(link)
		sitemap[link] = {}
		sitemap[link]['title'] = title
		sitemap[link]['links'] = links

		for l in links:
			if l not in VISITED_URLS:
				VISITED_URLS.append(l)

	next_level_links = [link for link in VISITED_URLS if not link in sitemap.keys()]

	# Mini-report for this crawl level.
	print('Visited urls   : {:6}'.format(len(VISITED_URLS)))
	print('Gathered urls  : {:6}'.format(len(sitemap)))
	print('Total time     : {:6} seconds'.format(round(time.time() - start)))

	if next_level_links:
		print('There are at least {} valid links to get. We need to go deeper...\n'.format(len(next_level_links)))

	return sitemap, VISITED_URLS, next_level_links


# 8. Display full crawl statistics.
# ---------------------------------
def final_statistics(crawler_start_time, sitemap, VISITED_URLS, depth, next_level_links):
	
	total_time = round(time.time() - crawler_start_time)
	avrg_time_per_link = round(total_time / len(sitemap), 4)

	print('\n\nFull crawl repport:\n-------------------\n')
	print('Depth level    : {:6}'.format(depth))
	print('Visited urls   : {:6}'.format(len(VISITED_URLS)))
	print('Gathered urls  : {:6}'.format(len(sitemap)))
	print('Next level urls: {:6}'.format(len(next_level_links)))
	print('Total time     : {:6} seconds'.format((total_time)))
	print('Avrg time/link : {:6} seconds'.format((avrg_time_per_link)))


# 9. Auto settings and main logic.
# --------------------------------
def get_sitemap(main_url, crawl_depth):

	# AUTO-SETTINGS:
	# --------------

	global DOMAIN_NAME, DOMAIN, CRAWL_DEPTH, REPORT_SAVE_PATH

	if main_url == '':
		# Input setup URL and crawl depth (demo/input).
		initial_data = settings_by_input()
		DOMAIN = initial_data[0]
		CRAWL_DEPTH = initial_data[1]
	else:
		# By-function setup URL and crawl depth.
		DOMAIN = main_url
		CRAWL_DEPTH = crawl_depth

	DOMAIN_NAME = tldextract.extract(DOMAIN).domain

	REPORT_SAVE_PATH = DOMAIN_NAME + '.json'


	# MAIN LOGIC:
	# -----------

	# Dealing with unknown depth and amount of URL's, we would like to mesure the timings.
	crawler_start_time = time.time()

	# Get main page links.
	print('\n\nGetting links from level 0: domain page.')
	sitemap = get_main_page(DOMAIN)

	# Extend list of all visited links with main page links.
	VISITED_URLS = list(sitemap.keys())
	
	# Thoes are also first next level links to crawl on.
	next_level_links = list(sitemap.keys())
	
	# Loop down each level of links untill desired CRAWL_DEPTH is reached.
	depth = 1
	while depth < CRAWL_DEPTH and next_level_links:

		# Get this level URLs and their titles.
		print('Going into depth {}.\n-------------------'.format(depth))
		sitemap, VISITED_URLS, next_level_links = we_need_to_go_deeper(sitemap, VISITED_URLS, next_level_links)
		depth += 1

		if depth == CRAWL_DEPTH:
			print('\nMax crawl depth achieved.\n')
		elif not next_level_links:
			print('\nNothing else to scrap.\n')

	# Display report: visited pages, gathered urls, final depth level, nr of next level urls, 
	# total crawl time, avrg crawl time per link. 
	final_statistics(crawler_start_time, sitemap, VISITED_URLS, depth, next_level_links)

	# One key output format.
	final_site_map = {DOMAIN : sitemap}

	# Save results as json.
	with open(REPORT_SAVE_PATH, 'w') as fp:
		json.dump(final_site_map, fp)
	print('\nAll {} pages URL with their titles and their inside-domain URLS saved to {}\n'.format(len(sitemap), REPORT_SAVE_PATH))


# 10. Initiation
# --------------
if __name__ == "__main__":

	main_url = ''
	crawl_depth = 5 # default

	# option: print readme.txt

	get_sitemap(main_url, crawl_depth)



# Readme:
#
#
#

# Program: 
# web-crawler.py
# --------------------

# Purpose:
# --------
# Get all links and their page titles from within the given domain on all depth levels as a json file.

# What is a depth level AKA crawl depth?
# --------------------------------------

# Level 0: Main page (The domain, url you gave).
# Level 1: URLS to domain sub-pages gathered within the main page.
# Level 2: URLS to domain sub-pages gathered within the URLS to domain sub-pages gathered on the main page.
# Level 3: ... and so on.
# Level X: Initially unknown. It's the level where there is nothing else to get.

# Suggested depth:
# - Small pages: around 5 (but it doesn't hurt to set it higher).
# - Medium pages: around 5-10
# - Big/mega pages: above 10, sometimes above 20. (it will hurt your speed on deeper levels and most likely drop/ban you if you don't switch IP often).

# Ways to use crawler:
# --------------------

# 1. Just go with 'python3 web-crawler.py' and input your URL and crawl_depth in the console. 
#    You will recieve your output as an json file inside this program directory.

#	 A. Input 'demo' to use demo settings (coded in settings_by_input()):
#		 DOMAIN =  'https://cyfrowa-wyprawka.org/'
#		 CRAWL_DEPTH = 10

#	 B. Input your actual desired URL and crawl depth:
#		 fg.  'https://cyfrowa-wyprawka.org/'
#		 fg.  '10'

# 2. Use manual setting: lines 255-260:
#	 main_url = ''     # write URL string
#	 crawl_depth = 5   # default, try to play with it

# 3. Run by function:
#	 delete 'if __main__ (...)'
#	 use: get_sitemap(url, crawl_depth)

# Logic:
# ------
# -  AUTO-SETTINGS:
#    - Input setup URL and crawl depth (demo/input).
#    - By-function setup URL and crawl depth.
# - MAIN LOGIC:
#    - Get main page links.
#	 - Extend list of all visited links with main page links.
#    - Thoes are also first next level links to crawl on.
#    - Loop down each level of links untill desired CRAWL_DEPTH is reached.
#        - Each time: get this level URLs and their titles.
#    
#    - Display report: visited pages, gathered urls, final depth level, nr of next level urls, total crawl time, avrg crawl time per link. 
#    - Save results as json.

# Logic by functions:
# -------------------
# 1. Set target URL and crawl_depth by input OR use demo values.
# 2. Get page as a soup object.
# 3. Get links out of soup object.
# 4. Filter out and prepare valid links from soup.
# 5. Get intial page data.
# 6. Get links and title form target page.
# 7. Get one level down data.
# 8. Display full crawl statistics.
# 9. Auto settings and main logic.

# Example output:
# ---------------

# ~/web-crawler$ python web-crawler.py
#
# Please enter:
# a) URL link to scrap ('fg. 'https://cyfrowa-wyprawka.org/') or
# b) 'demo' for demo example:
# https://cyfrowa-wyprawka.org/
# Please enter desired crawl depth (integer):10
#
#
# Getting links from level 0: domain page.
# There are at least 11 more valid links to get. We need to go deeper...
#
# Going into depth 1.
# -------------------
# Visited urls   :     21
# Gathered urls  :     11
# Total time     :      4 seconds
# There are at least 10 valid links to get. We need to go deeper...
#
# Going into depth 2.
# -------------------
# Visited urls   :     29
# Gathered urls  :     21
# Total time     :      6 seconds
# There are at least 8 valid links to get. We need to go deeper...
#
# Going into depth 3.
# -------------------
# Visited urls   :     37
# Gathered urls  :     29
# Total time     :      2 seconds
# There are at least 8 valid links to get. We need to go deeper...
#
# Going into depth 4.
# -------------------
# Visited urls   :     53
# Gathered urls  :     37
# Total time     :      2 seconds
# There are at least 16 valid links to get. We need to go deeper...
#
# Going into depth 5.
# -------------------
# Visited urls   :     61
# Gathered urls  :     53
# Total time     :     16 seconds
# There are at least 8 valid links to get. We need to go deeper...
#
# Going into depth 6.
# -------------------
# Visited urls   :     62
# Gathered urls  :     61
# Total time     :      2 seconds
# There are at least 1 valid links to get. We need to go deeper...
#
# Going into depth 7.
# -------------------
# Visited urls   :     62
# Gathered urls  :     62
# Total time     :      0 seconds
#
# Nothing else to scrap.
# 
#
# Full crawl repport:
# -------------------
# Depth level    :      8
# Visited urls   :     62
# Gathered urls  :     62
# Next level urls:      0
# Total time     :     33 seconds
# Avrg time/link : 0.5323 seconds
#
#
#
# All 62 pages URL with their titles and their inside-domain URLS saved to cyfrowa-wyprawka.json
