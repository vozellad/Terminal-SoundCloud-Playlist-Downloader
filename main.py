# Gecko Driver for using Selenium with Firefox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

from subprocess import Popen

def main():
	q = "Are you running this script in the folder or directory you want to files to be downloaded in? Y/n\n"
	if (input(q) == 'n'):
		print("Make sure to do that.")
		return

	url = input("Enter SoundCloud playlist url:\n")

	# No other site is supported
	if "soundcloud.com" not in url.lower():
		print("Can't find soundcloud website in", url)
		return

	# Run headless browser
	options = Options()
	options.headless = True
	driver = webdriver.Firefox(options=options)
	print ("Headless Firefox Initialized")
	
	# Try to go to the url unless it's invalid
	try:
		driver.get(url)
	except WebDriverException:
		print("Not a valid url.")
		driver.quit()
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
			driver.quit()
			return
	except TimeoutException:
		pass

	print("All guards passed.")

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

	#print('\n'.join(tracklist)) # testing code

	# I could read from the terminal to make sure I'm getting 
	# the keywords right, but I don't need to because 
	# SoundCloud is consistent for now.
	for link in tracklist:
		Popen("youtube-dl -f http_mp3_128 " + link, shell=True).wait()



	driver.quit()

if __name__ == "__main__":
	main()