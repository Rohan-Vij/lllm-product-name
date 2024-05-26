import requests
import time
import unittest

class TestContentGenerationAPI(unittest.TestCase):
    
    base_url = "http://127.0.0.1:5555"
    
    def test_generate_content(self):
        prompt = "What is the meaning of life?"
        response = requests.post(f"{self.base_url}/", data={'prompt': prompt})
        
        self.assertEqual(response.status_code, 202)
        response_data = response.json()
        self.assertIn('command_id', response_data)
        self.assertIn('status_url', response_data)
        
        command_id = response_data['command_id']
        status_url = response_data['status_url']
        
        while True:
            status_response = requests.get(f"{self.base_url}{status_url}")
            status_data = status_response.json()
            self.assertIn('status', status_data)
            
            if status_data['status'] in ['done', 'error', 'failed']:
                break
            
            time.sleep(1)
        
        self.assertIn('status', status_data)
        if status_data['status'] == 'done':
            self.assertIn('result', status_data)
            print(status_data['candidates'][0]['content']['parts'][0]['text'])
        elif status_data['status'] in ['error', 'failed']:
            self.assertIn('result', status_data)
            self.assertIsInstance(status_data['result'], str)

if __name__ == '__main__':
    unittest.main()
