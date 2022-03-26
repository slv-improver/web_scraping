import requests
from bs4 import BeautifulSoup
import shutil

SITE_URL = 'http://books.toscrape.com/'


def get_page_content(url):
	""" Get HTML content

	Parameters:
		url (string): URL of the web page

	Returns:
		bs4.BeautifulSoup: Parsed HTML content as BeautifulSoup Object

	"""
	# Get page content
	page = requests.get(url)
	# Convert page to Object
	return BeautifulSoup(page.content, 'html.parser')


def get_categories(soup):
	""" Get the category titles & URLs

	Parameters:
		soup (bs4.BeautifulSoup): Parsed HTML content as BeautifulSoup Object from get_page_content()

	Returns:
		list: Formatted like [[title, url], [title, url], ...]

	"""
	a_list = soup.find(class_='nav-list').find('ul').find_all('a')
	list_title_and_url = []
	for a in a_list:
		# Text without whitespace & relative category URL formatted
		list_title_and_url.append([a.text.strip(), SITE_URL + a['href']])
	return list_title_and_url


def get_product_page_url(soup, url):
	""" Get the product page URLs of the entire category page.
	If there is pagination, it gets the next page and so on.

	Parameters:
		soup (bs4.BeautifulSoup): Category page content
		url (string): URL of the category page

	Returns:
		list: Books URL

	"""
	# Get parents elements
	div_list = soup.find_all(class_='image_container')
	books_url = []
	# Get URL & format it from relative to absolute
	for div in div_list:
		product_relative_url = div.find('a')['href']
		product_url_list = product_relative_url.split('/')[3:]
		product_url = SITE_URL + 'catalogue/' + '/'.join(product_url_list)
		books_url.append(product_url)
	# Check if there is next page
	try:
		next_page = soup.find(class_='pager').find(class_='next').find('a')['href']
	except AttributeError:
		next_page = ''
	if next_page:
		# Format URL by adding next_page
		url_in_list = url.split('/')[:-1]
		next_page_url = '/'.join(url_in_list) + '/' + next_page
		books_url += get_product_page_url(get_page_content(next_page_url), next_page_url)
	# Info
	print('Category')
	###
	return books_url


def extract_data(soup, book_category):
	""" Try to extract all data. If nothing there, assign default value.

	Parameters:
		soup (bs4.BeautifulSoup): Product page content
		book_category (string): Category name for assign category

	Returns:
		list: All needed information

	"""
	default_value = 'No Value'
	# Get next td node after element
	try:
		universal_product_code = soup.find(text='UPC').findNext('td').string
	except AttributeError:
		universal_product_code = default_value

	# Get first h1
	try:
		title = soup.h1.string
	except AttributeError:
		title = default_value

	# Get next td node after element
	try:
		price_including_tax = soup.find(text='Price (incl. tax)').findNext('td').string
	except AttributeError:
		price_including_tax = default_value

	# Get next td node after element
	try:
		price_excluding_tax = soup.find(text='Price (excl. tax)').findNext('td').string
	except AttributeError:
		price_excluding_tax = default_value

	# Get next td node after element
	try:
		number_available_text = soup.find(text='Availability').findNext('td').string
		# Extract number from text
		number = ''
		for letter in number_available_text:
			if letter.isdigit():
				number += letter
		number_available = int(number)
	except AttributeError:
		number_available = default_value

	# Get next p node after element
	try:
		product_description = soup.find(id='product_description').findNext('p').string
	except AttributeError:
		product_description = default_value

	# Get next td node after element
	try:
		category = book_category
	except AttributeError:
		category = default_value

	# Get child who has "star-rating" class within "product_main" class element
	try:
		star_rating = soup.find(class_='product_main').find(class_='star-rating')
		# Get its second class name which is the number of stars
		number_of_stars = star_rating['class'][1]
		# Use dictionary to get number
		equivalent = {'Zero': 0, 'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
		review_rating = equivalent[number_of_stars]
	except AttributeError:
		review_rating = default_value

	# Get src attribute of first img
	try:
		img_relative_url = soup.img['src']
		# Remove relative elements from path
		img_url_list = img_relative_url.split('/')[2:]
		# Create absolute URL
		image_url = SITE_URL + '/'.join(img_url_list)
	except AttributeError:
		image_url = default_value

	# Info
	print('Product')
	###
	return [
		universal_product_code,
		title, price_including_tax,
		price_excluding_tax,
		number_available,
		product_description,
		category,
		review_rating,
		image_url
	]


def download_image(url, file_name):
	""" Download image and save it locally.

	Parameters:
		url: Image URL
		file_name: To rename the image

	Returns:
		None

	"""
	image_extension = '.' + url.split('.')[-1]
	image = requests.get(url).content

	with open('images/' + file_name + image_extension, 'wb') as file:
		file.write(image)
