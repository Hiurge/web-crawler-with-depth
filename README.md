# web-crawler-with-depth

# Readme:




### Program: 
web-crawler.py

### Purpose:

Get all links and their page titles from within the given domain on all depth levels as a json file.

### What is a depth level AKA crawl depth?

Level 0: Main page (The domain, url you gave).

Level 1: URLS to domain sub-pages gathered within the main page.

Level 2: URLS to domain sub-pages gathered within the URLS to domain sub-pages gathered on the main page.

Level 3: ... and so on.

Level X: Initially unknown. It's the level where there is nothing else to get.

### Suggested depth:
- Small pages: around 5 (but it doesn't hurt to set it higher).
- Medium pages: around 5-10
- Big/mega pages: above 10, sometimes above 20. (it will hurt your speed on deeper levels and most likely drop/ban you if you don't switch IP often).

### Ways to use crawler:

1. Just go with 'python3 web-crawler.py' and input your URL and crawl_depth in the console. 
You will recieve your output as an json file inside this program directory.

- Input 'demo' to use demo settings (coded in settings_by_input()):
		 DOMAIN =  'https://cyfrowa-wyprawka.org/'
		 CRAWL_DEPTH = 10

- Input your actual desired URL and crawl depth:
		 fg.  'https://cyfrowa-wyprawka.org/'
		 fg.  '10'

2. Use manual setting: lines 255-260:
	 main_url = ''     # write URL string
	 crawl_depth = 5   # default, try to play with it

3. Run by function:
	 delete 'if __main__ (...)'
	 use: get_sitemap(url, crawl_depth)

### Logic:

 -  AUTO-SETTINGS:
    - Input setup URL and crawl depth (demo/input).
    - By-function setup URL and crawl depth.
 - MAIN LOGIC:
    - Get main page links.
	 - Extend list of all visited links with main page links.
    - Thoes are also first next level links to crawl on.
    - Loop down each level of links untill desired CRAWL_DEPTH is reached. Each time: get this level URLs and their titles.
    
    - Display report: visited pages, gathered urls, final depth level, nr of next level urls, total crawl time, avrg crawl time per link. 
    - Save results as json.

### Logic by functions

1. Set target URL and crawl_depth by input OR use demo values.
2. Get page as a soup object.
3. Get links out of soup object.
4. Filter out and prepare valid links from soup.
5. Get intial page data.
6. Get links and title form target page.
7. Get one level down data.
8. Display full crawl statistics.
9. Auto settings and main logic.

# Example output:

~/web-crawler$ python web-crawler.py

Please enter:
a) URL link to scrap ('fg. 'https://cyfrowa-wyprawka.org/') or
b) 'demo' for demo example:
https://cyfrowa-wyprawka.org/
Please enter desired crawl depth (integer):10


Getting links from level 0: domain page.
There are at least 11 more valid links to get. We need to go deeper...

Going into depth 1.
Visited urls   :     21
Gathered urls  :     11
Total time     :      4 seconds
There are at least 10 valid links to get. We need to go deeper...

Going into depth 2.
Visited urls   :     29
Gathered urls  :     21
Total time     :      6 seconds
There are at least 8 valid links to get. We need to go deeper...

Going into depth 3.
Visited urls   :     37
Gathered urls  :     29
Total time     :      2 seconds
There are at least 8 valid links to get. We need to go deeper...

Going into depth 4.
Visited urls   :     53
Gathered urls  :     37
Total time     :      2 seconds
There are at least 16 valid links to get. We need to go deeper...

Going into depth 5.
Visited urls   :     61
Gathered urls  :     53
Total time     :     16 seconds
There are at least 8 valid links to get. We need to go deeper...

Going into depth 6.
Visited urls   :     62
Gathered urls  :     61
Total time     :      2 seconds
There are at least 1 valid links to get. We need to go deeper...

Going into depth 7.
Visited urls   :     62
Gathered urls  :     62
Total time     :      0 seconds

Nothing else to scrap.
 

Full crawl repport:
Depth level    :      8
Visited urls   :     62
Gathered urls  :     62
Next level urls:      0
Total time     :     33 seconds
Avrg time/link : 0.5323 seconds



All 62 pages URL with their titles and their inside-domain URLS saved to cyfrowa-wyprawka.json
