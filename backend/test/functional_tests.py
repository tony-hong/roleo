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


        # The user inputs a noun "book"
        inputbox_noun.clear()
        inputbox_noun.send_keys('book')
        
        
        # The user inputs a verb "read"
        inputbox_verb.clear()
        inputbox_verb.send_keys('read')
        


        # The user clicks the submit button
        self.browser.find_element_by_id("submitBtn").click()
        time.sleep(30)


        self.fail('Finish the test!')
    # TODO: define more tests
    # 


    def tearDown(self):
        self.browser.quit()

if __name__ == '__main__':
    unittest.main()