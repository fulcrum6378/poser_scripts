import os

tmp_path = os.path.join(os.environ['TEMP'], 'buld_clothes_conformer.txt')
if not os.path.isfile(tmp_path):
    open(tmp_path, 'w').write('\n'.join(map(lambda f: f.Name(), poser.Scene().Figures())))
