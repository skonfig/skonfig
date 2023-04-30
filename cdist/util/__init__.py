import hashlib


def str_hash(s):
    """Return hash of string s"""
    if isinstance(s, str):
        return hashlib.md5(s.encode('utf-8')).hexdigest()
    else:
        raise Error("Param should be string")
