import random
import string


def random_str(n: int):
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase) for _ in range(n))