from selenium import webdriver
import unittest

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
        self.fail('Finish the test!')

    # TODO: define more tests
    # ...

    def tearDown(self):
        self.browser.quit()

if __name__ == '__main__':
    unittest.main()