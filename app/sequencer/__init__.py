from nanoid import generate as nanoid_generate

# This alphabet does not have letters that look alike.
ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
DEFAULT_SIZE = 21


def generate() -> str:
    return nanoid_generate(ALPHABET, DEFAULT_SIZE)
