"""

Javascript/HTML web scraper for "WhoScored" 

Scrapes the web pages for seasons 2013-2017 and gets all team data

By The_Glove

"""

# Import selenium components
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.chrome.options import Options

# Import other components (ray.dataframe is a faster compiler for pandas)
import time
from bs4 import BeautifulSoup as bs
import pandas as pd

# Initialize variables & parameters
team_data = pd.DataFrame()

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
				if option.text == '2013' or option.text == '2014']# or option.text == '2015'  
				#or option.text == '2016' or option.text == '2017']
				
# Build list of all months
months = ["Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"]


# Loop through years
for year in years:
	# Clear data frame to store data
	team_data = pd.DataFrame()
	test_data = pd.DataFrame()
	
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
		
		# Go to the fixtures page
		fixtures = [a['href'] for a in soup.select('div[id=sub-navigation] ul li a[href]')
					if a.text == 'Fixtures']
		print(fixtures)
		
		# Selects the first row of the months table and clicks the first two months of the season
		for i in range(3,5):
			wd.get('https://www.whoscored.com'+fixtures[0])
			WebDriverWait(wd, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, 'layout-content-2col-left')))
			month_menu = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.ID, 'date-config-toggle-button'))).click()
			month = WebDriverWait(wd,10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#date-config > div.datepicker-wrapper > div > table > tbody > tr > td:nth-child(2) > div > table > tbody > tr:nth-child(1) > td:nth-child('+str(i)+')'))).click()
			time.sleep(5)
			html_page = wd.page_source
			soup2 = bs(html_page, 'html.parser')
			
			# Get the link to the match report, open the match and scrape the root
			for match in soup2.select('td[class]'):
				if match['class'] == ['toolbar', 'right']:
					match_link = [a['href'] for a in match.find_all('a')]
					print ("Opening.. " + match_link[0])
					wd.get('https://www.whoscored.com/' + str(match_link[0]))
					time.sleep(5)
					game_page = wd.page_source
					game_soup = bs(game_page, 'html.parser')
					
					# Get date of game
					date = [dd.contents[0] for dd in game_soup.find_all('dd') 
							if "Sat" in dd.text
							or "Sun" in dd.text
							or "Mon" in dd.text
							or "Tue" in dd.text
							or "Wed" in dd.text
							or "Thu" in dd.text
							or "Fri" in dd.text]
												
					# Get home and away team names
					teams = []
					home_team = ''
					away_team = ''
							
					for team in game_soup.select('td[class=team]'):
						for a in team.find_all('a'):
							teams.append(a.text)		
									
					home_team = [teams[0]]
					away_team = [teams[1]]
					
					# Get home and away score
					score = ''
					home_score = ''
					awway_score = ''
							
					for result in game_soup.select('td[class=result]'):
						score = result.text.split(':')
						
					home_score = [score[0]]
					away_score = [score[1]]
										
					# Get game stats link
					for link in game_soup.select('div[class=side-box] a[href]'):
						if link['title'] == 'See all player statistics':
							StatsLink = link['href']
							
					print("Scraping: " + StatsLink)
					wd.quit()
							
					"""
					
					SCRAPE GAME STATISTICS PAGE
					
					"""
					
					# Opens game page link and gets the link for the game summary page
					wd = webdriver.Chrome(executable_path='/Users/nlomb/Documents/Development/Python/Chrome/chromedriver', chrome_options=ext)
					wd.get('https://www.whoscored.com' + str(StatsLink))
					game_page = wd.page_source
					game_soup = bs(game_page, 'html.parser')
					
					for link in game_soup.select('div[id=sub-sub-navigation] a[href]'):
						if link.contents[0] == 'Summary':
							Summary = link['href']
					try:	
						wd.get('https://www.whoscored.com' + str(Summary))
					except Exception:
						try:
							wd.get('https://www.whoscored.com' + str(Summary))
						except Exception:
							continue
						break
					
					time.sleep(5)
					game_page = wd.page_source
					game_soup = bs(game_page, 'html.parser')
					
					count = 0
					
					for match in game_soup.select('li[class="match-centre-stat match-centre-sub-stat"]'):
						# Get total shots 
						if match['data-for'] == 'shotsTotal' and match['data-sum'] != '0':
							home_TotalShots = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']
							away_TotalShots = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get shots on target 				
						if match['data-for'] == 'shotsOnTarget' and match['data-sum'] != '0':
							home_ShotsOnTarget = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_ShotsOnTarget = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						
							print(home_ShotsOnTarget)					
						
						# Get blocked shots				
						if match['data-for'] == 'shotsBlocked' and match['data-sum'] != '0':
							home_ShotsBlocked = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_ShotsBlocked = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get total passes			
						if match['data-for'] == 'passesTotal' and match['data-sum'] != '0':
							home_TotalPasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalPasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get accurate passes			
						if match['data-for'] == 'passesAccurate' and match['data-sum'] != '0':
							home_AcuratePasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_AcuratePasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get total dribbles			
						if match['data-for'] == 'dribblesAttempted' and match['data-sum'] != '0':
							home_TotalDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get successful dribbles			
						if match['data-for'] == 'dribblesWon' and match['data-sum'] != '0':
							home_SuccessfulDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_SuccessfulDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get total tackles			
						if match['data-for'] == 'tacklesTotal' and match['data-sum'] != '0':
							home_TotalTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get successful tackles			
						if match['data-for'] == 'tackleSuccessful' and match['data-sum'] != '0':
							home_SuccessfulTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_SuccessfulTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get clearances			
						if match['data-for'] == 'clearances' and match['data-sum'] != '0':
							home_Clearances = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_Clearances = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']	
						# Get interceptions			
						if match['data-for'] == 'interceptions' and match['data-sum'] != '0':
							home_Interceptions = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_Interceptions = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get Corners			
						if match['data-for'] == 'cornersTotal' and match['data-sum'] != '0':
							home_TotalCorners = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalCorners = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get Dispossessed			
						if match['data-for'] == 'dispossessed' and match['data-sum'] != '0':
							home_dispossessed = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_dispossessed = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get Fouls			
						if match['data-for'] == 'foulsCommited' and match['data-sum'] != '0':
							home_foulsCommited = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_foulsCommited = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']							
					
					if count == 20:
						test_data = test_data.append({"Date": [date], "Home Shots": [home_TotalShots], "Away Corner": [away_TotalCorners]}, ignore_index=True)
						count = 0
					else:
						count += 1
														
					# Write the data to a dataframe
					team_data = team_data.append({"Date": [date], "Home Team": [home_team], "Away Team": [away_team],
											"Home Goals": [home_score], "Away Goals": [away_score],
											"Home Shots": [home_TotalShots], "Away Shots": [away_TotalShots], 
											"Home SoT": [home_ShotsOnTarget], "Away SoT": [away_ShotsOnTarget],
											"Home SB": [home_ShotsBlocked], "Away SB": [away_ShotsBlocked],
											"Home Passes": [home_TotalPasses], "Away Passes": [away_TotalPasses],
											"Home AP": [home_AcuratePasses], "Away AP": [away_AcuratePasses],
											"Home DA": [home_TotalDribbles], "Away DA": [away_TotalDribbles],
											"Home DW": [home_SuccessfulDribbles], "Away DW": [away_SuccessfulDribbles],
											"Home Tackles": [home_TotalTackles], "Away Tackles": [away_TotalTackles],
											"Home ST": [home_SuccessfulTackles], "Away ST": [away_SuccessfulTackles],
											"Home C": [home_Clearances], "Away C": [away_Clearances],
											"Home I": [home_Interceptions], "Away I": [away_Interceptions],
											"Home Cor": [home_TotalCorners], "Away Cor": [away_TotalCorners],
											"Home D": [home_dispossessed], "Away D": [away_dispossessed],
											"Home FC": [home_foulsCommited], "AWay FC": [away_foulsCommited]}, ignore_index=True)
											
						
											
		# Selects the second row of the months table and clicks the next four months of the season
		for i in range(1,5):
			wd.get('https://www.whoscored.com'+fixtures[0])
			WebDriverWait(wd, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "layout-content-2col-left")))
			month_menu = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.ID, 'date-config-toggle-button'))).click()
			month = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#date-config > div.datepicker-wrapper > div > table > tbody > tr > td:nth-child(2) > div > table > tbody > tr:nth-child(2) > td:nth-child('+str(i)+')'))).click()
			time.sleep(5)
			html_page = wd.page_source
			soup2 = bs(html_page, 'html.parser')
			
			# Get the link to the match report, open the match and scrape the root
			for match in soup2.select('td[class]'):
				if match['class'] == ['toolbar', 'right']:
					match_link = [a['href'] for a in match.find_all('a')]
					print ("Opening.. " + match_link[0])
					wd.get('https://www.whoscored.com/' + str(match_link[0]))
					time.sleep(5)
					game_page = wd.page_source
					game_soup = bs(game_page, 'html.parser')
					
					# Get date of game
					date = [dd.contents[0] for dd in game_soup.find_all('dd') 
							if "Sat" in dd.text
							or "Sun" in dd.text
							or "Mon" in dd.text
							or "Tue" in dd.text
							or "Wed" in dd.text
							or "Thu" in dd.text
							or "Fri" in dd.text]
												
					# Get home and away team names
					teams = []
					home_team = ''
					away_team = ''
							
					for team in game_soup.select('td[class=team]'):
						for a in team.find_all('a'):
							teams.append(a.text)		
									
					home_team = [teams[0]]
					away_team = [teams[1]]
					
					# Get home and away score
					score = ''
					home_score = ''
					awway_score = ''
							
					for result in game_soup.select('td[class=result]'):
						score = result.text.split(':')
						
					home_score = [score[0]]
					away_score = [score[1]]
										
					# Get game stats link
					for link in game_soup.select('div[class=side-box] a[href]'):
						if link['title'] == 'See all player statistics':
							StatsLink = link['href']
							
					print("Scraping: " + StatsLink)
					wd.quit()
							
					"""
					
					SCRAPE GAME STATISTICS PAGE
					
					"""
					
					# Opens game page link and gets the link for the game summary page
					wd = webdriver.Chrome(executable_path='/Users/nlomb/Documents/Development/Python/Chrome/chromedriver', chrome_options=ext)
					wd.get('https://www.whoscored.com' + str(StatsLink))
					game_page = wd.page_source
					game_soup = bs(game_page, 'html.parser')
					
					for link in game_soup.select('div[id=sub-sub-navigation] a[href]'):
						if link.contents[0] == 'Summary':
							Summary = link['href']
					try:	
						wd.get('https://www.whoscored.com' + str(Summary))
					except Exception:
						try:
							wd.get('https://www.whoscored.com' + str(Summary))
						except Exception:
							continue
						break
					
					time.sleep(5)
					game_page = wd.page_source
					game_soup = bs(game_page, 'html.parser')
					
					count = 0
					
					for match in game_soup.select('li[class="match-centre-stat match-centre-sub-stat"]'):
						# Get total shots 
						if match['data-for'] == 'shotsTotal' and match['data-sum'] != '0':
							home_TotalShots = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']
							away_TotalShots = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get shots on target 				
						if match['data-for'] == 'shotsOnTarget' and match['data-sum'] != '0':
							home_ShotsOnTarget = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_ShotsOnTarget = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						
							print(home_ShotsOnTarget)					
						
						# Get blocked shots				
						if match['data-for'] == 'shotsBlocked' and match['data-sum'] != '0':
							home_ShotsBlocked = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_ShotsBlocked = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get total passes			
						if match['data-for'] == 'passesTotal' and match['data-sum'] != '0':
							home_TotalPasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalPasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get accurate passes			
						if match['data-for'] == 'passesAccurate' and match['data-sum'] != '0':
							home_AcuratePasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_AcuratePasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get total dribbles			
						if match['data-for'] == 'dribblesAttempted' and match['data-sum'] != '0':
							home_TotalDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get successful dribbles			
						if match['data-for'] == 'dribblesWon' and match['data-sum'] != '0':
							home_SuccessfulDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_SuccessfulDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get total tackles			
						if match['data-for'] == 'tacklesTotal' and match['data-sum'] != '0':
							home_TotalTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get successful tackles			
						if match['data-for'] == 'tackleSuccessful' and match['data-sum'] != '0':
							home_SuccessfulTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_SuccessfulTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get clearances			
						if match['data-for'] == 'clearances' and match['data-sum'] != '0':
							home_Clearances = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_Clearances = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']	
						# Get interceptions			
						if match['data-for'] == 'interceptions' and match['data-sum'] != '0':
							home_Interceptions = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_Interceptions = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get Corners			
						if match['data-for'] == 'cornersTotal' and match['data-sum'] != '0':
							home_TotalCorners = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalCorners = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get Dispossessed			
						if match['data-for'] == 'dispossessed' and match['data-sum'] != '0':
							home_dispossessed = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_dispossessed = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get Fouls			
						if match['data-for'] == 'foulsCommited' and match['data-sum'] != '0':
							home_foulsCommited = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_foulsCommited = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']							

					# Write the data to a dataframe
					team_data = team_data.append({"Date": [date], "Home Team": [home_team], "Away Team": [away_team],
											"Home Goals": [home_score], "Away Goals": [away_score],
											"Home Shots": [home_TotalShots], "Away Shots": [away_TotalShots], 
											"Home SoT": [home_ShotsOnTarget], "Away SoT": [away_ShotsOnTarget],
											"Home SB": [home_ShotsBlocked], "Away SB": [away_ShotsBlocked],
											"Home Passes": [home_TotalPasses], "Away Passes": [away_TotalPasses],
											"Home AP": [home_AcuratePasses], "Away AP": [away_AcuratePasses],
											"Home DA": [home_TotalDribbles], "Away DA": [away_TotalDribbles],
											"Home DW": [home_SuccessfulDribbles], "Away DW": [away_SuccessfulDribbles],
											"Home Tackles": [home_TotalTackles], "Away Tackles": [away_TotalTackles],
											"Home ST": [home_SuccessfulTackles], "Away ST": [away_SuccessfulTackles],
											"Home C": [home_Clearances], "Away C": [away_Clearances],
											"Home I": [home_Interceptions], "Away I": [away_Interceptions],
											"Home Cor": [home_TotalCorners], "Away Cor": [away_TotalCorners],
											"Home D": [home_dispossessed], "Away D": [away_dispossessed],
											"Home FC": [home_foulsCommited], "AWay FC": [away_foulsCommited]}, ignore_index=True)
		
		# Selects the third row of the months table and clicks the last two months of the season	
		for i in range(1,3):
			wd.get('https://www.whoscored.com'+fixtures[0])
			WebDriverWait(wd, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "layout-content-2col-left")))
			month_menu = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.ID, 'date-config-toggle-button'))).click()
			month = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,'#date-config > div.datepicker-wrapper > div > table > tbody > tr > td:nth-child(2) > div > table > tbody > tr:nth-child(3) > td:nth-child('+str(i)+')'))).click()
			time.sleep(5)
			html_page = wd.page_source
			soup2 = bs(html_page, 'html.parser')
				
			# Get the link to the match report, open the match and scrape the root
			for match in soup2.select('td[class]'):
				if match['class'] == ['toolbar', 'right']:
					match_link = [a['href'] for a in match.find_all('a')]
					print ("Opening.. " + match_link[0])
					wd.get('https://www.whoscored.com/' + str(match_link[0]))
					time.sleep(5)
					game_page = wd.page_source
					game_soup = bs(game_page, 'html.parser')
					
					# Get date of game
					date = [dd.contents[0] for dd in game_soup.find_all('dd') 
							if "Sat" in dd.text
							or "Sun" in dd.text
							or "Mon" in dd.text
							or "Tue" in dd.text
							or "Wed" in dd.text
							or "Thu" in dd.text
							or "Fri" in dd.text]
												
					# Get home and away team names
					teams = []
					home_team = ''
					away_team = ''
							
					for team in game_soup.select('td[class=team]'):
						for a in team.find_all('a'):
							teams.append(a.text)		
									
					home_team = [teams[0]]
					away_team = [teams[1]]
					
					# Get home and away score
					score = ''
					home_score = ''
					awway_score = ''
							
					for result in game_soup.select('td[class=result]'):
						score = result.text.split(':')
						
					home_score = [score[0]]
					away_score = [score[1]]
										
					# Get game stats link
					for link in game_soup.select('div[class=side-box] a[href]'):
						if link['title'] == 'See all player statistics':
							StatsLink = link['href']
							
					print("Scraping: " + StatsLink)
					wd.quit()
							
					"""
					
					SCRAPE GAME STATISTICS PAGE
					
					"""
					
					# Opens game page link and gets the link for the game summary page
					wd = webdriver.Chrome(executable_path='/Users/nlomb/Documents/Development/Python/Chrome/chromedriver', chrome_options=ext)
					wd.get('https://www.whoscored.com' + str(StatsLink))
					game_page = wd.page_source
					game_soup = bs(game_page, 'html.parser')
					
					for link in game_soup.select('div[id=sub-sub-navigation] a[href]'):
						if link.contents[0] == 'Summary':
							Summary = link['href']
					try:	
						wd.get('https://www.whoscored.com' + str(Summary))
					except Exception:
						try:
							wd.get('https://www.whoscored.com' + str(Summary))
						except Exception:
							continue
						break
					
					time.sleep(5)
					game_page = wd.page_source
					game_soup = bs(game_page, 'html.parser')
					
					count = 0
					
					for match in game_soup.select('li[class="match-centre-stat match-centre-sub-stat"]'):
						# Get total shots 
						if match['data-for'] == 'shotsTotal' and match['data-sum'] != '0':
							home_TotalShots = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']
							away_TotalShots = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get shots on target 				
						if match['data-for'] == 'shotsOnTarget' and match['data-sum'] != '0':
							home_ShotsOnTarget = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_ShotsOnTarget = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						
							print(home_ShotsOnTarget)					
						
						# Get blocked shots				
						if match['data-for'] == 'shotsBlocked' and match['data-sum'] != '0':
							home_ShotsBlocked = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_ShotsBlocked = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get total passes			
						if match['data-for'] == 'passesTotal' and match['data-sum'] != '0':
							home_TotalPasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalPasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get accurate passes			
						if match['data-for'] == 'passesAccurate' and match['data-sum'] != '0':
							home_AcuratePasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_AcuratePasses = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get total dribbles			
						if match['data-for'] == 'dribblesAttempted' and match['data-sum'] != '0':
							home_TotalDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get successful dribbles			
						if match['data-for'] == 'dribblesWon' and match['data-sum'] != '0':
							home_SuccessfulDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_SuccessfulDribbles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get total tackles			
						if match['data-for'] == 'tacklesTotal' and match['data-sum'] != '0':
							home_TotalTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get successful tackles			
						if match['data-for'] == 'tackleSuccessful' and match['data-sum'] != '0':
							home_SuccessfulTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_SuccessfulTackles = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get clearances			
						if match['data-for'] == 'clearances' and match['data-sum'] != '0':
							home_Clearances = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_Clearances = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']	
						# Get interceptions			
						if match['data-for'] == 'interceptions' and match['data-sum'] != '0':
							home_Interceptions = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_Interceptions = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get Corners			
						if match['data-for'] == 'cornersTotal' and match['data-sum'] != '0':
							home_TotalCorners = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_TotalCorners = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get Dispossessed			
						if match['data-for'] == 'dispossessed' and match['data-sum'] != '0':
							home_dispossessed = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_dispossessed = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']
						# Get Fouls			
						if match['data-for'] == 'foulsCommited' and match['data-sum'] != '0':
							home_foulsCommited = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'home']				
							away_foulsCommited = [span.contents[0] for span in match.select('span[data-field]')
											if span['data-field'] == 'away']							
				
					# Write the data to a dataframe
					team_data = team_data.append({"Date": [date], "Home Team": [home_team], "Away Team": [away_team],
											"Home Goals": [home_score], "Away Goals": [away_score],
											"Home Shots": [home_TotalShots], "Away Shots": [away_TotalShots], 
											"Home SoT": [home_ShotsOnTarget], "Away SoT": [away_ShotsOnTarget],
											"Home SB": [home_ShotsBlocked], "Away SB": [away_ShotsBlocked],
											"Home Passes": [home_TotalPasses], "Away Passes": [away_TotalPasses],
											"Home AP": [home_AcuratePasses], "Away AP": [away_AcuratePasses],
											"Home DA": [home_TotalDribbles], "Away DA": [away_TotalDribbles],
											"Home DW": [home_SuccessfulDribbles], "Away DW": [away_SuccessfulDribbles],
											"Home Tackles": [home_TotalTackles], "Away Tackles": [away_TotalTackles],
											"Home ST": [home_SuccessfulTackles], "Away ST": [away_SuccessfulTackles],
											"Home C": [home_Clearances], "Away C": [away_Clearances],
											"Home I": [home_Interceptions], "Away I": [away_Interceptions],
											"Home Cor": [home_TotalCorners], "Away Cor": [away_TotalCorners],
											"Home D": [home_dispossessed], "Away D": [away_dispossessed],
											"Home FC": [home_foulsCommited], "AWay FC": [away_foulsCommited]}, ignore_index=True)
				
		# Clean the data first three and last three characters from each element
		for i in team_data:
			team_data[i] = team_data[i].map(lambda x: str(x)[:-3]).map(lambda y: str(y)[3:])
										
		team_data.to_csv('/Users/nlomb/Documents/Development/Python/MLS/csv/data_' + str(year[1]) + '.csv', encoding='utf-8')

wd.quit()