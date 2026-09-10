import os
import sys


def examine_group_nodes(min_: int, max_: int, indent: int) -> tuple[bool, int]:
    global pz
    indents = '	' * indent
    removed_chars = 0
    anything_useful = False

    # loop on each group node
    while True:
        # noinspection PyUnboundLocalVariable
        min__ = min_ if 'max_group' not in locals() else max_group
        min_group = pz.find('\n' + indents + '			groupNode ', min__, max_)
        if min_group == -1: break
        max_group = pz.find('\n' + indents + '				}', min_group, max_) + 6 + indent

        # check for subgroups
        anything_useful_1, removed_chars_1 = examine_group_nodes(min_group, max_group, indent + 1)
        removed_chars += removed_chars_1
        max_group -= removed_chars_1
        max_ -= removed_chars_1
        if anything_useful_1:
            anything_useful = True
            continue

        # check for existence of any parameter nodes
        anything_useful_2 = '\n' + indents + '				parmNode' in pz[min_group:max_group]
        if anything_useful_2:
            anything_useful = True

        # self-destruct if nothing is useful here
        removed_chars_2 = 0
        if not anything_useful_1 and not anything_useful_2:
            annihilate(min_group, max_group)
            removed_chars_2 = max_group - min_group
            removed_chars += removed_chars_2
            max_group = min_group
        max_ -= removed_chars_2

    return anything_useful, removed_chars


def annihilate(start: int, end: int):
    global pz
    if start > end: raise ArithmeticError()
    pz = pz[:start] + pz[end:]


request = sys.argv[1] if len(sys.argv) >= 2 else os.getcwd()
pzs: list[str] = []
if os.path.isfile(request):
    pzs.append(request)
elif os.path.isdir(request):
    for dir_path, dir_names, filenames in os.walk(request):
        for filename in filenames:
            if '.' not in filename: continue
            ext = filename.rsplit('.', 1)[1]
            if ext in ['pz3', 'pz2', 'cr2', 'fc2', 'hr2', 'hd2', 'pp2']:
                pzs.append(os.path.join(dir_path, filename))
else:
    print('The address is not available.')
    quit()

for pz_path in pzs:
    if len(pzs) > 0:
        print('Scanning', pz_path.replace(request, ''))
    pz: str = open(pz_path, 'r').read()
    removed = examine_group_nodes(0, len(pz), 0)[1]
    if len(pzs) == 1:
        print(f'{removed:,} characters removed.')
    elif removed > 0:

        print(f'{pz_path.replace(request, "")}:  {removed:,} characters removed.')
    if removed > 0:
        os.rename(pz_path, pz_path + '.BAK')
        open(pz_path, 'w', encoding='cp1252', newline='\n').write(pz)
