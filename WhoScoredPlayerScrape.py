"""

Javascript/HTML web scraper for "WhoScored" 

Scrapes the web pages and gets all player data for 2013-2017 regular season

By The_Glove

"""

# Import selenium components
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# Import other components
import time
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np

# Add extension to chrome
ext = webdriver.ChromeOptions()
ext.add_extension('/Users/nlomb/Documents/Development/Python/Chrome/Ext/1.13.5_0.crx')
ext.add_argument('--no-first-run')

# Initialize web driver and get the URL
wd = webdriver.Chrome(executable_path='/Users/nlomb/Documents/Development/Python/Chrome/chromedriver', chrome_options=ext)
wd.get('https://www.whoscored.com/Regions/233/Tournaments/85/Seasons/3672/Stages/7250/Fixtures/USA-Major-League-Soccer-2013')

# Wait for the dynamic elements to load
WebDriverWait(wd, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'layout-content-2col-left')))

# Grab page source
html_page = wd.page_source

# Parse with BeautifulSoup
soup = bs(html_page, 'html.parser')


"""

BEGIN SELECTING ITEMS FROM HTML PARSE

"""

# Build lists of all years (starting at 2013)
for menu in soup.select('select[name]'):
    if menu['name'] == 'seasons':
        years = [(option['value'], option.contents[0]) 
        		for option in menu.find_all('option')
				if option.text == '2013' or option.text == '2014' or option.text == '2015'  
				or option.text == '2016' or option.text == '2017']

# Loop through years
for year in years:
	# Declare all dataframes used to store the data
	player_data = pd.DataFrame()
	data_foul = pd.DataFrame()
	data_card = pd.DataFrame()
	data_off = pd.DataFrame()
	data_clear = pd.DataFrame()
	data_block = pd.DataFrame()
	data_save = pd.DataFrame()
	data_shot = pd.DataFrame()
	data_goal = pd.DataFrame()
	data_drib = pd.DataFrame()
	data_poss = pd.DataFrame()
	data_aer = pd.DataFrame()
	data_pass = pd.DataFrame()
	data_key = pd.DataFrame()
	data_ass = pd.DataFrame()
	data_tack = pd.DataFrame()
	data_int = pd.DataFrame()
	
	# Go to the site link for each year and get the site link for regular season for each year
	wd.get('https://www.whoscored.com'+str(year[0]))
	WebDriverWait(wd, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'layout-content-2col-left')))
	html_page = wd.page_source
	soup = bs(html_page, 'html.parser')	
	
	for menu2 in soup.select('select[name]'):
		if menu2['name'] == 'stages':
			RegSeasonLink = [option['value']
							for option in menu2.find_all('option')
							if option.text == 'Major League Soccer']
							
	for seas in RegSeasonLink:
		
		# Go to the site link for the regular season
		wd.get('https://www.whoscored.com'+str(seas))
		WebDriverWait(wd, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'layout-content-2col-left')))
		html_page = wd.page_source
		soup = bs(html_page, 'html.parser')
		
		# Go to the player stats page
		player_stats_page = [a['href'] for a in soup.select('div[id=sub-navigation] ul li a[href]')
							if a.text == 'Player Statistics']
		wd.get('https://www.whoscored.com'+player_stats_page[0])
		time.sleep(2)
		
		# Select the detailed tab
		details = WebDriverWait(wd,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#detailed-statistics-tab > a'))).click()
		time.sleep(5)
		
		# Select the accumulation type as 'total'
		accum_total = Select(wd.find_element_by_id('statsAccumulationType'))
		accum_total.select_by_value('2')
		
		# Let info load and then scrape the page
		time.sleep(2)
		html_page = wd.page_source
		soup2 = bs(html_page, 'html.parser')
		
		# Get dropdown selections and loop through each
		select = Select(wd.find_element_by_id('category'))
		for category in soup2.select('select[id=category] option[value]'):
			select.select_by_value(category['value'])
			header = [category.contents[0]]
			time.sleep(5)
			print(header)
			
			# Scrape new table
			html_page = wd.page_source
			game_soup = bs(html_page, 'html.parser')
			
			# Find and get the last page of the data table
			for dl in game_soup.select('dl[class="listbox right"] a[id=last]'):
				last_page = dl['data-page']
				
			# Loop through all the pages already on first page so don't need to add one
			for page in range(1,int(last_page)):
				count = 0				
				# Loop through table and pull out all elements
				for tr in game_soup.select('tbody[id=player-table-statistics-body] tr'):
					if count < 10:
						count += 1
					else:
						if "Tackles" in header and count < 20:
							player_name = [a.contents[0].strip() for a in tr.select('td[class=pn] a[class=player-link]')]
							player_team = [span.contents[0].split(',')[0] for span in 
											tr.select('td[class=pn] a[class=player-meta-data] span[class=team-name]')]
							player_position = [span.contents[0].split(',')[-1].strip() for span in 
											tr.select('td[class=pn] span[class=player-meta-data]')
											if ',' in span.contents[0]]
							player_mins = [td.contents[0].strip() for td in tr.select('td[class="minsPlayed "]')]
							player_tackles_won = [td.contents[0].strip() for td in tr.select('td[class="tackleWonTotal "]')]
							player_tackles_attempted = [td.contents[0].strip() for td in tr.select('td[class="tackleTotalAttempted "]')]												
							data_tack = data_tack.append({"Name": [player_name], "Team": [player_team], 
															"Pos": [player_position], "Mins_Tot": [player_mins],
															"Tackles_Won": [player_tackles_won], "Tackles_Att": 
															[player_tackles_attempted]}, ignore_index=True)
						elif "Interception" in header and count < 20:
							player_interceptions = [td.contents[0].strip() for td in tr.select('td[class="interceptionAll "]')]
							data_int = data_int.append({"Interceptions": [player_interceptions]}, ignore_index=True)
						elif "Fouls" in header and count < 20:
							player_fouls_taken = [td.contents[0].strip() for td in tr.select('td[class="foulGiven "]')]
							player_fouls_committed = [td.contents[0].strip() for td in tr.select('td[class="foulCommitted "]')]
							data_foul = data_foul.append({"Fouls_Taken": [player_fouls_taken], 
															"Fouls_Committed": [player_fouls_committed]}, ignore_index=True)		
						elif "Cards" in header and count < 20:
							player_yellowCards = [td.contents[0].strip() for td in tr.select('td[class="yellowCard "]')]
							player_redCards = [td.contents[0].strip() for td in tr.select('td[class="redCard "]')]
							data_card = data_card.append({"Y_Crds": [player_yellowCards], 
															"R_Crds": [player_redCards]}, ignore_index=True)	
						elif "Offside" in header and count < 20:
							player_offsides = [td.contents[0].strip() for td in tr.select('td[class="offsideGiven "]')]
							data_off = data_off.append({"Offsides": [player_offsides]}, ignore_index=True)
						elif "Clearances" in header and count < 20:
							player_clearances = [td.contents[0].strip() for td in tr.select('td[class="clearanceTotal"]')]
							data_clear = data_clear.append({"Clearances": [player_clearances]}, ignore_index=True)		
						elif "Blocks" in header and count < 20:
							player_blocked_shots = [td.contents[0].strip() for td in tr.select('td[class="outfielderBlock "]')]
							player_blocked_crosses = [td.contents[0].strip() for td in tr.select('td[class="passCrossBlockedDefensive "]')]
							player_blocked_passes = [td.contents[0].strip() for td in tr.select('td[class="outfielderBlockedPass "]')]
							data_block = data_block.append({"Blk_Shts": [player_blocked_shots], "Blk_Pas": [player_blocked_passes],
												"Blk_Crs": [player_blocked_crosses]}, ignore_index=True)	
						elif "Saves" in header and count < 20:
							player_saves_total = [td.contents[0].strip() for td in tr.select('td[class="saveTotal "]')]
							player_saves_6yd = [td.contents[0].strip() for td in tr.select('td[class="saveSixYardBox "]')]
							player_saves_penalty = [td.contents[0].strip() for td in tr.select('td[class="savePenaltyArea "]')]
							player_saves_outBox = [td.contents[0].strip() for td in tr.select('td[class="saveObox "]')]
							data_save = data_save.append({"Saves_Tot": [player_saves_total], "Saves_6": [player_saves_6yd],
												"Saves_P": [player_saves_penalty], "Saves_Out": [player_saves_outBox]}, ignore_index=True)	
						elif "Shots" in header and count < 20:
							player_shots_total = [td.contents[0].strip() for td in tr.select('td[class="shotsTotal "]')]
							player_shots_outBox = [td.contents[0].strip() for td in tr.select('td[class="shotOboxTotal "]')]
							player_shots_6yd = [td.contents[0].strip() for td in tr.select('td[class="shotSixYardBox "]')]
							player_shots_penalty = [td.contents[0].strip() for td in tr.select('td[class="shotPenaltyArea "]')]
							data_shot = data_shot.append({"Shots_Tot": [player_shots_total], "Shots_6": [player_shots_6yd],
												"Shots_P": [player_shots_penalty], "Shots_Out": [player_shots_outBox]}, ignore_index=True)							
						elif "Goals" in header and count < 20:
							player_goals_total = [td.contents[0].strip() for td in tr.select('td[class="goalTotal "]')]
							player_goals_outBox = [td.contents[0].strip() for td in tr.select('td[class="goalObox "]')]
							player_goals_6yd = [td.contents[0].strip() for td in tr.select('td[class="goalSixYardBox "]')]
							player_goals_penalty = [td.contents[0].strip() for td in tr.select('td[class="goalPenaltyArea "]')]
							data_goal = data_goal.append({"Goals_Tot": [player_goals_total], "Goals_6": [player_goals_6yd],
												"Goals_P": [player_goals_penalty], "Goals_Out": [player_goals_outBox]}, ignore_index=True)							
						elif "Dribbles" in header and count < 20:
							player_dribbles_total = [td.contents[0].strip() for td in tr.select('td[class="dribbleTotal "]')]
							player_dribbles_won = [td.contents[0].strip() for td in tr.select('td[class="dribbleWon "]')]
							data_drib = data_drib.append({"Dribs_Tot": [player_dribbles_total], "Dribs_Won": [player_dribbles_won]}, ignore_index=True)							
						elif "Possession loss" in header and count < 20:
							player_turnover = [td.contents[0].strip() for td in tr.select('td[class="turnover "]')]
							player_dispossessed = [td.contents[0].strip() for td in tr.select('td[class="dispossessed "]')]
							data_poss = data_poss.append({"Turn": [player_turnover], "Disposs": [player_dispossessed]}, ignore_index=True)		
						elif "Aerial" in header and count < 20:
							player_aerialDuels_total = [td.contents[0].strip() for td in tr.select('td[class="duelAerialTotal "]')]
							player_aerialDuels_won = [td.contents[0].strip() for td in tr.select('td[class="duelAerialWon "]')]
							data_aer = data_aer.append({"AirDuel_Tot": [player_aerialDuels_total], "AirDuel_Won": [player_aerialDuels_won]}, ignore_index=True)							
						elif "Passes" in header and count < 20:
							player_passes_total = [td.contents[0].strip() for td in tr.select('td[class="passTotal "]')]
							player_passes_lb_acc = [td.contents[0].strip() for td in tr.select('td[class="passLongBallAccurate "]')]
							player_passes_lb_inacc = [td.contents[0].strip() for td in tr.select('td[class="passLongBallInaccurate "]')]
							player_passes_sb_acc = [td.contents[0].strip() for td in tr.select('td[class="shortPassAccurate "]')]
							player_passes_sb_inacc = [td.contents[0].strip() for td in tr.select('td[class="shortPassInaccurate "]')]
							data_pass = data_pass.append({"Pass_Tot": [player_passes_total], "Pass_LB_Acc": [player_passes_lb_acc],
												"Pass_LB_Inacc": [player_passes_lb_inacc], "Pass_SB_Acc": [player_passes_sb_acc],
												"Pass_SB_Inacc": [player_passes_sb_inacc]}, ignore_index=True)							
						elif "Key passes" in header and count < 20:
							player_keyPasses_total = [td.contents[0].strip() for td in tr.select('td[class="keyPassesTotal "]')]
							player_keyPasses_long = [td.contents[0].strip() for td in tr.select('td[class="keyPassLong "]')]
							player_keyPasses_short = [td.contents[0].strip() for td in tr.select('td[class="keyPassShort "]')]
							data_key = data_key.append({"KeyPass_Tot": [player_keyPasses_total], "KeyPass_L": [player_keyPasses_long],
												"KeyPass_S": [player_keyPasses_short]}, ignore_index=True)			
						elif "Assists" in header and count < 20:
							player_assists_total = [td.contents[0].strip() for td in tr.select('td[class="assist "]')]
							player_assists_cross = [td.contents[0].strip() for td in tr.select('td[class="assistCross "]')]
							player_assists_corner = [td.contents[0].strip() for td in tr.select('td[class="assistCorner "]')]
							player_assists_throughball = [td.contents[0].strip() for td in tr.select('td[class="assistThroughball "]')]
							player_assists_throwin = [td.contents[0].strip() for td in tr.select('td[class="assistThrowin "]')]
							player_assists_other = [td.contents[0].strip() for td in tr.select('td[class="assistOther "]')]
							data_ass = data_ass.append({"Ass_Tot": [player_assists_total], "Ass_Crss": [player_assists_cross],
												"Ass_Cor": [player_assists_corner], "Ass_Thrh": [player_assists_throughball],
												"Ass_Thrw": [player_assists_throwin], "Ass_Oth": [player_assists_other]}, ignore_index=True)		
						count += 1
				
				# Clicks next page to load next set of players content for the header											
				next = WebDriverWait(wd,10).until(EC.presence_of_element_located((By.LINK_TEXT, 'next'))).click()
				time.sleep(5)
				
				# Scrape new table
				html_page = wd.page_source
				game_soup = bs(html_page, 'html.parser')
		
		player_data = pd.concat((data_tack, data_pass, data_key, data_shot, data_goal, data_ass, data_block, data_clear, data_int, data_poss, data_card, data_aer, data_drib, data_foul, data_off, data_save), axis=1)		
						
		# Clean the data first three and last three characters from each element
		for i in player_data:
			player_data[i] = player_data[i].map(lambda x: str(x)[:-3]).map(lambda y: str(y)[3:])
										
		player_data.to_csv('/Users/nlomb/Documents/Development/Python/MLS/csv/data_' + str(year[1]) + '.csv', encoding='utf-8')

wd.quit()