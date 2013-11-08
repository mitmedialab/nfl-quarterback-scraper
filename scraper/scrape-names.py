from BeautifulSoup import BeautifulSoup
import requests, sys, logging, json, csv

logging.basicConfig(level=logging.INFO)
SEASON = "2013"

team_list_page = requests.get('http://en.wikipedia.org/wiki/List_of_NFL_starting_quarterbacks')
doc = BeautifulSoup(team_list_page.text)

starting_quarterbacks = []

def add_qb(qb_link, division, team_name, team_link):
	logging.info("  "+qb_link.text)
	# try to grab the qb pic too
	qb_url = "http://en.wikipedia.org"+qb_link['href']
	qb_doc = BeautifulSoup(requests.get(qb_url).text)
	qb_table = qb_doc.find('table')
	qb_img_url = ''
	if qb_table.find('img'):
		qb_img_url = qb_table.find('img')['src']
	qb_info = {
		'division': division,
		'team': team_name,
		'team_wikipedia_url': team_link,
		'qb_name': qb_link.text,
		'qb_wikipedia_url': qb_url,
		'qb_image_url': 'http:'+qb_img_url
	}
	starting_quarterbacks.append( qb_info )

# process each team
table = doc.findAll('table')[0]
for team_row in table.findAll('tr')[1:]:
	logging.debug(team_row)
	team_columns = team_row.findAll('td')
	division = team_columns[0].text
	team_name = team_columns[1].findAll('a')[0].text
	team_link = "http://en.wikipedia.org"+team_columns[1].findAll('a')[0]['href']
	team_qb_list_link = "http://en.wikipedia.org"+team_columns[1].findAll('a')[1]['href']
	logging.info("Team: "+team_name)
	# grab the team page to get all starting qbs
	found_qb = False
	team_doc = BeautifulSoup(requests.get(team_qb_list_link).text)
	table_index = 0
	if team_name in ['St. Louis Rams', 'Cleveland Browns', 'Indianapolis Colts', \
					 'Miami Dolphins', 'Minnesota Vikings']:
		table_index=1
	season_rows = team_doc.findAll('table')[table_index].findAll('tr')
	for season_row in season_rows:
		season_columns = season_row.findAll('td')
		if len(season_columns)<2:
			continue
		season_col_index = 0
		qb_col_index = 1
		if team_name in ['Oakland Raiders']:
			season_col_index = 1
			qb_col_index = 2
		if season_columns[season_col_index].text!='2013':
			continue
		# found the right row - now parse it
		for qb_link in season_columns[qb_col_index].findAll('a'):
			add_qb(qb_link, division, team_name, team_link)
			found_qb = True
		break
	if not found_qb:
		# use the one from the main list of starting qbs
		qb_link = team_columns[2].find('a')
		add_qb(qb_link, division, team_name, team_link)
	
with open("qb_list.json", "w") as json_file:
    json_file.write( json.dumps(starting_quarterbacks, indent=2) )

with open("qb_list.csv", "w") as csv_file:
	writer = csv.writer(csv_file)
	cols = ['division','team','team_wikipedia_url','qb_name','qb_wikipedia_url','qb_image_url']
	writer.writerow(cols)
	for qb in starting_quarterbacks:
		info = []
		for col_name in cols:
			info.append(qb[col_name])
		writer.writerow(info)