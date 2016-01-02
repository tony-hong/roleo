from selenium import webdriver

browser = webdriver.Firefox()

browser.get('http://localhost:8000/view2D')

assert 'Web-based semantic visualization tool' in browser.title