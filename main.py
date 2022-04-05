import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from dhooks import Webhook, Embed, File

import os

with open('discord_hook.txt', 'r') as file_hook:
	hook = file_hook.read().strip()

def fix_hook(hook):
	if "app" in hook:
		hook = hook[:15]+hook[18:]
		return hook
	else: return hook

hook_corrected = fix_hook(hook)
hook_fin = Webhook(hook_corrected)

# Starting Discord embed
embed = Embed()
stats_ups = 'https://cdn.discordapp.com/attachments/739982164933738538/785176029530030120/statups.gif'


total_streams = 0

artists_list = []

artists = open('artists.txt', 'r').read().splitlines()
artists = [artist for artist in artists if artist != ""]

logs = open('logs.txt', 'r').read().split(':')

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument('log-level=3')
options=options

driver = webdriver.Chrome(options=options)


def connexion():
		"""
		Connects to the main account
		"""

		wait = WebDriverWait(driver, 30)
		driver.get('https://accounts.spotify.com/fr/login?continue=https:%2F%2Fartists.spotify.com%2F')
		driver.refresh()
		login_un = driver.find_element_by_name('username')
		login_un.send_keys(logs[0])
		login_pw = driver.find_element_by_name('password')
		login_pw.send_keys(logs[1], Keys.RETURN)
		wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="s4a-page-main-content"]/div/div[2]/div/h1')))
		time.sleep(3)
		url = driver.current_url
		log_ID = url[37:len(url)-5]
		logs.append(log_ID)

		time.sleep(2)
		driver.get('https://artists.spotify.com/c/artist/'+logs[2]+'/audience?audience-filter=streams')

		print('Connected')

def streams_artiste_logged():
		"""
		Gets statistics from the on which we are logged
		"""

		global total_streams
		wait = WebDriverWait(driver, 30)
		wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'CircleShadow_shadow__G-Qkd')))
		artiste_logged = driver.find_element_by_xpath('//*[@id="root"]/div/div/div/header/div[3]/button/span')
		artiste_logged = artiste_logged.text
		streams_logged = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'TimelineTooltip_timeline_tooltip-value__2ipLx')))
		streams_logged = streams_logged.text
		print(artiste_logged, ' : ',streams_logged)
		if "k" in streams_logged.lower():
			total_streams += float(streams_logged.replace(',', '.').replace('k',''))
		else:
			total_streams += float(streams_logged)/1000
		with open('daily_stats.txt', 'w') as stats:
			stats.write(artiste_logged+' : '+streams_logged+' stream.\n')
		embed.add_field(name=artiste_logged, value=streams_logged)

def streams_artists_list():
		"""
		Gets statistics for the artists in the artists.txt file
		"""

		global artists
		global total_streams
		for i in range(0, len(artists)):
			wait = WebDriverWait(driver, 30)
			aSearch = driver.find_element_by_class_name('EntityPicker_entitypicker-input__30riJ')
			aSearch.send_keys(artists[i])
			aSearch = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="timeline"]/section/div/div/div[2]/div[1]/ul/li/a/div')))
			aSearch.click()
			wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="timeline"]/section/div/div/div[2]/div[2]/button/div')))
			aStreams = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'TimelineTooltip_timeline_tooltip-value__2ipLx')))
			aStreams = aStreams.text
			print(artists[i], ' : ',aStreams)


			if "k" in aStreams.lower():
						total_streams += float(aStreams.replace(',', '.').replace('k',''))
			else :
						total_streams += float(aStreams)/1000
			aClose = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="timeline"]/section/div/div/div[2]/div[2]/button')))
			aClose.click()

			# Adding artist statistics
			if i < 23:
				embed.add_field(name=artists[i], value=aStreams)
			with open('daily_stats.txt', 'a') as stats:
				stats.write(artists[i]+' : '+aStreams+' streams.\n')

def reset():
	"""
	Resets global variable to avoid conflicts if something fails while checking for new statistics
	"""

	global total_streams
	global embed
	total_streams = 0
	embed = Embed()

def send():
	with open('daily_stats.txt', 'a') as stats:
		stats.write('\n\nTotal streams of the day: {}k\nThat is {}€ with a 0.0025€ per stream ratio'.format(round(total_streams, 2), round(total_streams*2.5, 2)))
	
	file = File('daily_stats.txt')

	embed.add_field(name='__**TOTAL**__', value='\n\nTotal streams of the day: {}k\nThat is {} with a 0.0025€ per stream ratio'.format(round(total_streams, 2), round(total_streams*2.5, 2)))
	embed.set_image(stats_ups)
	hook_fin.send('**Daily statistics : :money_with_wings:**', embed=embed, file=file)



connexion()


############################################
# CHECKER RUNNING 24/24 FOR NEW STATISTICS #
############################################


cycle = 0

while True:

	try: 
		driver.refresh()
		time.sleep(5)
		print('Amount of checks: {}'.format(cycle))
		with open('last_date.txt', 'r') as date:
			last_date = date.read()

		wait = WebDriverWait(driver, 30)
		wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'CircleShadow_shadow__G-Qkd')))

		date_scrape_raw = driver.find_element_by_xpath('//*[@id="timeline"]/p')
		date_scrape = date_scrape_raw.text[13:]
		print('Last statistics: {}\nDaily statistics: {}'.format(last_date, date_scrape))
		if date_scrape == last_date:
			print('Statistics are up to date')
			time.sleep(600)
		else:
			print('Statistics are up, wait 5 minutes !')
			time.sleep(3 if cycle == 0 else 300) 
			streams_artiste_logged()
			streams_artists_list()

			send()
			print('Statistics have been sent to your Discord')

			# Writing date for the next cycle
			with open('last_date.txt', 'w') as date:
				date.write(date_scrape)
			time.sleep(10)
			reset()
			
	except:
		reset()
		pass
	cycle += 1		