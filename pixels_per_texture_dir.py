import os
from typing import Dict

import poser
from PIL import Image

from collect_required_content import collect_pz3_required_paths

# initial parameters
required_paths = collect_pz3_required_paths(poser.Scene().DocumentPath())[0]

# count pixels
pixels_per_dir_1: Dict[str, int] = {}
for file_path in required_paths:
    fpl = file_path.lower()
    if not fpl.endswith('.jpg') and not fpl.endswith('.png'): continue
    k: str = os.path.dirname(file_path)
    if k not in pixels_per_dir_1:
        pixels_per_dir_1[k] = 0
    with Image.open(file_path) as img:
        pixels_per_dir_1[k] += img.width * img.height
del required_paths

# shorten paths and index maximum lengths of paths of each directory for pretty printing
max_chars = 0
total = 0
pixels_per_dir_2: Dict[str, int] = {}
for k, v in pixels_per_dir_1.items():
    tx_dir = k
    for content_path in poser.Libraries():
        if k.startswith(content_path):
            tx_dir = k[len(content_path):]
            break
    tx_dir = tx_dir.replace('\\', ':')
    if tx_dir.lower().startswith(':runtime:textures'):
        tx_dir = tx_dir[18:]
    pixels_per_dir_2[tx_dir] = pixels_per_dir_1[k]
    if len(tx_dir) > max_chars:
        max_chars = len(tx_dir)
    total += v
pixels_per_dir_2 = dict(sorted(pixels_per_dir_2.items(), key=lambda item: item[1], reverse=True))
pixels_per_dir_2['TOTAL'] = total
del pixels_per_dir_1

# print the results
for k, v in pixels_per_dir_2.items():
    print(k + ((max_chars - len(k)) * ' ') + '  ' + f'{v:,d}')
