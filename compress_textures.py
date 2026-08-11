import os
import shutil
from typing import Dict, Set

import poser
from PIL import Image

from collect_required_content import collect_pz3_required_paths

scene = poser.Scene()
revert: bool = False
rules_path = scene.DocumentPath()[:-4] + '.txt'
rules: Dict[str, float] = {}
continuum = True

if scene.Changed() == 1 and not poser.DialogSimple.YesNo('Unsaved document. Continue?'):
    continuum = False

if continuum:
    revert = not poser.DialogSimple.YesNo('Do you wish to compress textures? (No to revert original textures)')
    if not revert:
        if not os.path.isfile(rules_path):
            poser.DialogSimple.MessageBox(
                f'You haven\'t defined compression rules in `{os.path.basename(rules_path)}`.')
            continuum = False
        else:
            try:
                with open(rules_path, 'r') as rules_file:
                    for line in rules_file:
                        rule = line.strip()
                        if len(rule) > 0 and not rule.startswith('#'):
                            spl = rule.rsplit(' ', 1)
                            rules[spl[0]] = float(spl[1])
                if len(rules) == 0:
                    poser.DialogSimple.MessageBox(f'{os.path.basename(rules_path)} is empty.')
                    continuum = False
            except:
                poser.DialogSimple.MessageBox(f'{os.path.basename(rules_path)} has an invalid structure.')
                continuum = False

if continuum:
    required_paths: Set[str] = collect_pz3_required_paths(scene.DocumentPath())[0]

    if not revert:
        compressed_count = 0
        copied_count = 0

        #
        # list files to be compressed
        compress_files: Dict[str, float] = {}
        for file in required_paths:
            fpl = file.lower()
            if not fpl.endswith('.jpg') and not fpl.endswith('.png'): continue
            for pattern, compression in rules.items():
                if pattern in file:
                    if compression < 1.0:
                        compress_files[file] = compression
                    elif file in compress_files:
                        compress_files.pop(file)

        # exclude directories which include those files
        compress_dirs: Set[str] = set()
        for file in compress_files.keys():
            compress_dirs.add(os.path.dirname(file))

        # main work
        for compress_dir in compress_dirs:

            # prepare directories
            original_dir = compress_dir + ' (1.0)'
            if not os.path.isdir(original_dir):
                os.rename(compress_dir, original_dir)
            if not os.path.isdir(compress_dir):
                os.mkdir(compress_dir)

            for original in os.listdir(original_dir):
                orig = os.path.join(original_dir, original)
                dest = os.path.join(compress_dir, original)

                # bring all the files into the new directory, compressed or not
                if dest in compress_files:
                    factor = compress_files[dest]
                    with Image.open(orig) as img:
                        do_resize = True
                        desired_scale = (int(img.width * factor), int(img.height * factor))
                        if os.path.isfile(dest):
                            try:
                                with Image.open(dest) as old_img:
                                    if (old_img.width, old_img.height) == desired_scale:
                                        do_resize = False
                            except:
                                pass
                        if do_resize:
                            img.resize(desired_scale, Image.LANCZOS) \
                                .save(dest, quality=100, optimize=True)
                        compressed_count += 1
                elif not os.path.isfile(dest) or os.path.getsize(orig) != os.path.getsize(dest):
                    shutil.copy2(orig, dest)
                    copied_count += 1

        # report
        poser.DialogSimple.MessageBox(
            f'{compressed_count} files were compressed.\n'
            f'{copied_count} files were merely copied.')

    else:
        reverted_count = 0

        # index texture directories
        texture_dirs: Set[str] = set()
        for file in required_paths:
            texture_dirs.add(os.path.dirname(file))

        # revert changes
        for texture_dir in texture_dirs:
            original_dir = texture_dir + ' (1.0)'
            if os.path.isdir(original_dir):
                shutil.rmtree(texture_dir)
                os.rename(original_dir, texture_dir)
                reverted_count += 1

        # report
        poser.DialogSimple.MessageBox(
            f'{reverted_count} directories were reverted.')
