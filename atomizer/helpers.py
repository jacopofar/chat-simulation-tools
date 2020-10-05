
from functools import lru_cache
import re
from typing import List

DIGITS = re.compile(r'[0-9]+')
URL = re.compile(r'http(s)*://')

@lru_cache
def text_to_features(text: str) -> List[str]:
    text = text.lower()
    # replace relevant punctuation and stuff with tokens
    text = text.replace(':)', ' token_smileface ')
    text = text.replace(':(', ' token_sadface ')
    text = text.replace(':/', ' token_mehface ')

    text = text.replace('?', ' token_questionmark ')
    text = text.replace('!', ' token_exclamationnmark ')
    text = text.replace('\'', ' token_singlequote ')
    text = text.replace('"', ' token_doublequote ')
    text = text.replace(':', ' token_colon ')
    text = text.replace('...', ' token_ellipsis ')

    # TODO maybe nice to also keep the original number and URL
    # also, generate token for domain name
    text = DIGITS.sub('token_digits ', text)
    text = URL.sub('token_url ', text)

    # replace everything else with spaces, then remove them
    # NOTE: isalpha works with non-english characters too
    text = ''.join(l for l in text if l.isalpha() or l in ' _')
    text = re.sub(' +', ' ', text)
    return [x for x in text.split(' ') if len(x) > 0]
