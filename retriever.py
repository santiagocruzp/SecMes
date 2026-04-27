import json

import pyperclip
import os

basedir = os.path.dirname(__file__)
file = os.path.join(basedir,"keys.json")

with open(file, "r") as f:
    keys_data = json.load(f)

name = input("Whose public key do you need?")

desired_key = keys_data[name]['pubKey'][1]

pyperclip.copy(desired_key)