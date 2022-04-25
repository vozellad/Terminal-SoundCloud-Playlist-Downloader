# Gecko Driver for using Selenium with Firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

import subprocess
import io
from time import sleep

def main():
	url = input("Enter SoundCloud playlist url:\n")

	# No other site is supported
	if "soundcloud.com" not in url.lower():
		print("Can't find soundcloud website in", url)
		return
	
	# Run headless browser
	options = Options()
	options.headless = True
	driver = webdriver.Firefox(options=options)
	
	# Try to go to the url unless it's invalid
	try:
		driver.get(url)
	except WebDriverException:
		print("Not a valid url.")
		return
	
	# Check playlist is available by comparing expected text
	xpath = "//*[@class='errorText sc-font-light']"
	# Wait for element to appear
	try:
		element_text = WebDriverWait(driver, 1).until(
			EC.presence_of_element_located((By.XPATH, xpath))
		).text

		expected_text = "This playlist is not available anymore."
	
		if expected_text in element_text:
			print("This playlist is not available. Is it private?")
			return
	except TimeoutException:
		pass

	# All guards passed at this point

	# Get scroll height
	last_height = driver.execute_script("return document.body.scrollHeight")

	# Scroll to bottom of webpage to display all tracks
	while True:
		# Scroll down to bottom
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

		# Wait to load page
		sleep(1)

		# Calculate new scroll height and compare with last scroll height
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			break
		last_height = new_height

	# Get list of tracks as an element
	xpath = (".//*[@class='trackItem__trackTitle "
		+ "sc-link-dark sc-link-primary sc-font-light']")
	element_tracklist = driver.find_elements(By.XPATH, xpath)
	
	# Get link of tracks (href) into list
	tracklist = []
	for item in element_tracklist:
		tracklist.append(
			item.get_attribute("href").split('?')[0]
		)

	# Tracks go in this folder
	subprocess.Popen("mkdir -p tracks", shell=True).wait()

	print(len(tracklist), "tracks to download.\n")

	for i, link in enumerate(tracklist):
		# Get format to download track
		proc = subprocess.Popen(
			f"youtube-dl -F " + link, 
			shell=True, 
			stdout=subprocess.PIPE, 
			stderr=subprocess.PIPE,
			universal_newlines=True
		)
		
		out, err = proc.communicate()
		form = out.split('\n')[-2].split(' ')[0]

		command = f"youtube-dl -o 'tracks/%(title)s.%(ext)s' -f {form} "
		print(command + link)
		subprocess.Popen(command + link, shell=True).wait()
		
		print("Track(s) downloaded:", i + 1, '\n')

	print("Tracks downloaded in the 'tracks' folder.")

if __name__ == "__main__":
	driver = None

	try:
		main()
	# Make sure browser closes if program is exited early
	except KeyboardInterrupt:
		print("\tProgram closed")

	if driver != None:
		driver.quit()
		