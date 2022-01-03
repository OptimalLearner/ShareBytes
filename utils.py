import string
import random

def get_random_string(str_size = 10):
    allowed_chars = string.ascii_letters + string.punctuation
    return ''.join(random.choice(allowed_chars) for _ in range(str_size))

def get_pass_code(str_size = 10):
    allowed_chars = string.ascii_letters + string.digits
    return ''.join(random.choice(allowed_chars) for _ in range(str_size))