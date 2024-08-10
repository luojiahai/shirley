from shirley.utils.pickleablegenerator import PickleableGenerator

import os
import re
from PIL import Image


def getpath(filepath: str) -> str:
    return os.path.abspath(os.path.expanduser(filepath))


def isimage(filepath: str) -> bool:
    try:
        with Image.open(filepath) as img:
            img.verify()
            return True
    except (IOError, SyntaxError):
        return False


def parse(text: str, remove_image_tags: bool = False) -> str:
    lines = text.split('\n')
    lines = [line for line in lines if line != '']
    count = 0
    for i, line in enumerate(lines):
        if '```' in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class=\'language-{items[-1]}\'>'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace('`', r'\`')
                    line = line.replace('<', '&lt;')
                    line = line.replace('>', '&gt;')
                    line = line.replace(' ', '&nbsp;')
                    line = line.replace('*', '&ast;')
                    line = line.replace('_', '&lowbar;')
                    line = line.replace('-', '&#45;')
                    line = line.replace('.', '&#46;')
                    line = line.replace('!', '&#33;')
                    line = line.replace('(', '&#40;')
                    line = line.replace(')', '&#41;')
                    line = line.replace('$', '&#36;')
                lines[i] = '<br>' + line

    text = ''.join(lines)
    if remove_image_tags:
        text = text.replace('<ref>', '').replace('</ref>', '')
        text = re.sub(r'<box>.*?(</box>|$)', '', text)
    return text
