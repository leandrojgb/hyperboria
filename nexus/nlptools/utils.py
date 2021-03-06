import re
import struct
import unicodedata

from .regex import (
    ALNUMWHITESPACE_REGEX,
    EMAIL_REGEX,
    EMOJI_REGEX,
    HASHTAG_REGEX,
    MULTIWHITESPACE_REGEX,
    TELEGRAM_LINK_REGEX,
    URL_REGEX,
)


def add_surrogate(text):
    return ''.join(
        # SMP -> Surrogate Pairs (Telegram offsets are calculated with these).
        # See https://en.wikipedia.org/wiki/Plane_(Unicode)#Overview for more.
        ''.join(chr(y) for y in struct.unpack('<HH', x.encode('utf-16le')))
        if (0x10000 <= ord(x) <= 0x10FFFF) else x for x in text
    )


def cast_string_to_single_string(s):
    processed = MULTIWHITESPACE_REGEX.sub(' ', ALNUMWHITESPACE_REGEX.sub(' ', s))
    processed = processed.strip().replace(' ', '-')
    return processed


def clean_text(text):
    text = remove_markdown(remove_emoji(text))
    text = remove_url(text)
    text = despace_smart(text)
    return text.strip()


def despace(text):
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n[ \t]+', '\n', text)
    return text


def despace_full(text):
    return re.sub(r'\s+', ' ', text).strip()


def despace_smart(text):
    text = re.sub(r'\n\s*[-•]+\s*', r'\n', text)
    text = re.sub(r'\n{2,}', r'\n', text).strip()
    text = re.sub(r'\.?(\s+)?\n', r'. ', text)
    text = re.sub(r'\s+', ' ', text)
    return text


def escape_format(text):
    text = text.replace("__", "_").replace("**", "*").replace("`", "'")
    text = text.replace('[', r'`[`').replace(']', r'`]`')
    return text


def remove_markdown(text):
    text = re.sub('[*_~]{2,}', '', text)
    text = re.sub('[`]+', '', text)
    text = re.sub(r'\[\s*(.*?)(\s*)\]\(.*?\)', r'\g<1>\g<2>', text, flags=re.MULTILINE)
    return text


def normalize_string(string):
    string = re.sub('[^a-zA-Z0-9_\\-]+', '', string.lower().strip().replace(' ', '-'))
    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').decode('utf-8')


def remove_emails(text):
    return re.sub(EMAIL_REGEX, '', text)


def remove_emoji(text):
    text = re.sub(EMOJI_REGEX, '', text)
    text = re.sub(u'\ufe0f', '', text)
    return text


def remove_hashtags(text):
    return re.sub(HASHTAG_REGEX, '', text)


def remove_url(text):
    return re.sub(URL_REGEX, '', text)


def replace_telegram_link(text):
    return re.sub(TELEGRAM_LINK_REGEX, r'@\1', text)


def split_at(s, pos):
    if len(s) < pos:
        return s
    pos -= 10
    pos = max(0, pos)
    for p in range(pos, min(pos + 20, len(s) - 1)):
        if s[p] in [' ', '\n', '.', ',', ':', ';', '-']:
            return s[:p] + '...'
    return s[:pos] + '...'


def unwind_hashtags(text):
    return re.sub(HASHTAG_REGEX, r'\2', text)
