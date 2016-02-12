from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
import time


class simultaneousTest(unittest.TestCase):

    drivers = []
    nouns = ['people','person','he']
    verbs = ['read','cook','dirve']

    def setUp(self):
        for i in range(0, 10):
            self.drivers.append(webdriver.Firefox())
            self.drivers[i].get('http://localhost:8000/view2D')

            

    # TODO: fill in the name of the use case
    def test_simultaneous_requests(self):

        for i in range(0, 10):
            
            
            #get the input boxes
            inputbox_noun = self.drivers[i].find_element_by_id('input_noun')
            inputbox_verb = self.drivers[i].find_element_by_id('input_verb')

            # The user inputs a noun 
            inputbox_noun.clear()
            inputbox_noun.send_keys("apple")
        
        
            # The user inputs a verb
            inputbox_verb.clear()
            inputbox_verb.send_keys("eat")
            time.sleep(0.2)
            self.drivers[i].find_element_by_id("submitBtn").click()
            

        time.sleep(10)
        
        


    def tearDown(self):
        for i in range(0, 10):
            self.drivers[i].quit()












if __name__ == '__main__':
    unittest.main()