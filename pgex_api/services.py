from os import urandom
from datetime import datetime

def random_code():
    return f"{urandom(10).hex()}{datetime.now().strftime('%d%m%y%H%M%S')}"