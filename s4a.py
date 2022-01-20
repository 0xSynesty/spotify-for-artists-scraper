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

def corr_hook(hook):
	if "app" in hook:
		hook = hook[:15]+hook[18:]
		return hook
	else: return hook

hook_corr = corr_hook(hook)
hook_fin = Webhook(hook_corr)
embed = Embed()
stats_ups = 'https://cdn.discordapp.com/attachments/739982164933738538/785176029530030120/statups.gif'


total_streams = 0
artists_list = []

artists = open('artistes.txt', 'r').read().splitlines()
artists = [artiste for artiste in artists if artiste != ""]

logs = open('logs.txt', 'r').read().split(':')

#options = webdriver.ChromeOptions()
#options.add_argument("headless")
#options.add_argument('log-level=3')
#options=options

driver = webdriver.Chrome()


def connexion():
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
		print(logs)
		time.sleep(2)
		driver.get('https://artists.spotify.com/c/artist/'+logs[2]+'/audience?audience-filter=streams')
		print('Connecté')

def streams_artiste_logged():
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

def streams_artists_liste():
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
			if i < 23:
				embed.add_field(name=artists[i], value=aStreams)
			with open('daily_stats.txt', 'a') as stats:
				stats.write(artists[i]+' : '+aStreams+' streams.\n')

def reset():
	global total_streams
	global embed
	total_streams = 0
	embed = Embed()

def send():
	with open('daily_stats.txt', 'a') as stats:
		stats.write('\n\nTotal des streams du jour : {}k\nSoit {}€ avec un ratio de 0.0025€/stream'.format(round(total_streams, 2), round(total_streams*2.5, 2)))
	
	file = File('daily_stats.txt')

	embed.add_field(name='__**TOTAL**__', value='\n\nTotal des streams du jour : {}k\nSoit {}€ avec un ratio de 0.0025€/stream'.format(round(total_streams, 2), round(total_streams*2.5, 2)))
	embed.set_image(stats_ups)
	hook_fin.send('**Stats du jour gros bg :money_with_wings:**', embed=embed, file=file)



connexion()

cycle = 0

while True:

	try: 
		driver.refresh()
		time.sleep(5)
		print('Nb de checks : {}'.format(cycle))
		with open('last_date.txt', 'r') as date:
			last_date = date.read()
		wait = WebDriverWait(driver, 30)
		wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'CircleShadow_shadow__G-Qkd')))
		date_scrape_raw = driver.find_element_by_xpath('//*[@id="timeline"]/p')
		date_scrape = date_scrape_raw.text[13:]
		print('Dernière stats : {}\nStats du jour : {}'.format(last_date, date_scrape))
		if date_scrape == last_date:
			print('Les stats sont à jour')
			time.sleep(600)
		else:
			print('Stats up ! Wait 5 min')
			time.sleep(3 if cycle == 0 else 300) 
			streams_artiste_logged()
			streams_artists_liste()
			print('GG à toi, tu as fait {}k streams le {}'.format(round(total_streams, 2), date_scrape))
			send()
			print('Les stats ont été envoyées <3')
			with open('last_date.txt', 'w') as date:
				date.write(date_scrape)
			time.sleep(10)
			reset()
			
	except:
		reset()
		pass
	cycle += 1		
	
os.system('pause')