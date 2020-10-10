''' Script for encoding the text (password)
    Base64 encode method is used to encode the input text
'''
# Created on: Oct 10 2020
# @author: Nagaraj

import base64

input_password = input('Enter the password to encode: ')
encoded_password = base64.b64encode(input_password.encode())
print(f'Your encoded password - {encoded_password}')
