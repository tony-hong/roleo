from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
import time

class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    # TODO: fill in the name of the use case
    def test_nameOfUC(self):
        # Open the browser and visit the tool
        self.browser.get('http://localhost:8000/view2D')
        # Wait for 3 secs
        self.browser.implicitly_wait(3)
        
        # TODO: write the statements and exceptions in the use case here
        self.assertIn('Web-based semantic visualization tool', self.browser.title)
        

        # The value of the placeholder on the noun inputbox is "e.g. apple"
        inputbox_noun = self.browser.find_element_by_id('input_noun')
        self.assertEqual(
                inputbox_noun.get_attribute('placeholder'),
                'e.g. apple'
        )

        # The value of the placeholder on the noun inputbox is "e.g. eat"
        inputbox_verb = self.browser.find_element_by_id('input_verb')
        self.assertEqual(
                inputbox_verb.get_attribute('placeholder'),
                'e.g. eat'
        )

        # The default value on the noun inputbox is "apple"
        self.assertEqual(
                inputbox_noun.get_attribute('value'),
                'apple'
        )

        # The default value on the verb inputbox is "eat"
        self.assertEqual(
                inputbox_verb.get_attribute('value'),
                'eat'
        )


        

        

    #self.fail('Finish the test!')
    # TODO: define more tests
    # 

    def tearDown(self):
        self.browser.quit()



class TravelAround(unittest.TestCase):
    
    def setUp(self):
        self.browser = webdriver.Firefox()

    def test_travel_around_and_then_go_back_to_the_homepage(self):
        # Open the browser and visit the tool
        self.browser.get('http://localhost:8000/view2D')
        # Wait for 3 secs
        self.browser.implicitly_wait(3)

        #get the input boxes
        inputbox_noun = self.browser.find_element_by_id('input_noun')
        inputbox_verb = self.browser.find_element_by_id('input_verb')

        # The user inputs a noun "book"
        inputbox_noun.clear()
        inputbox_noun.send_keys('book')
        
        
        # The user inputs a verb "read"
        inputbox_verb.clear()
        inputbox_verb.send_keys('read')
        


        # The user clicks the submit button

        print("************************************************************")
       
        
        time.sleep(1)

        self.browser.find_element_by_id("submitBtn").click()

        # The user waits 5 seconds for the results
        time.sleep(5)
        
        # The user goes to the help page
        help_page = self.browser.find_element_by_id('help_page')
        help_page.click()
        
        current_url = self.browser.current_url
        self.assertEqual(current_url, 'http://localhost:8000/view2D/help/')

        # The user goes to the contact page
        contact_page = self.browser.find_element_by_id('contact_page')
        contact_page.click()

        current_url = self.browser.current_url
        self.assertEqual(current_url, 'http://localhost:8000/view2D/contact/')

        # The user goes to the impressum page
        impressum_page = self.browser.find_element_by_id('impressum_page')
        impressum_page.click()

        current_url = self.browser.current_url
        self.assertEqual(current_url, 'http://localhost:8000/view2D/impressum/')

        # The user goes back to the home_page
        home_page = self.browser.find_element_by_id('query_page')
        home_page.click()

        current_url = self.browser.current_url
        self.assertEqual(current_url, 'http://localhost:8000/view2D/')

        # Since the user has input the noun "book", the inputbox_nound should has the value book
        inputbox_noun = self.browser.find_element_by_id('input_noun')
        self.assertEqual(
                inputbox_noun.get_attribute('value'),
                'book'
        )

        #Since the user has input the verb "read", the inputbox_nound should has the value read
        inputbox_verb = self.browser.find_element_by_id('input_verb')
        self.assertEqual(
                inputbox_verb.get_attribute('value'),
                'read'
        )
        

    def tearDown(self):
        self.browser.quit()




if __name__ == '__main__':
    unittest.main()