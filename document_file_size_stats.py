import gzip
from typing import Dict, Optional, Tuple

import poser

pz3_path = poser.Scene().DocumentPath()
pz3: str
try:
    pz3 = open(pz3_path, 'r', encoding='cp1252').read()
except UnicodeDecodeError:
    pz3 = gzip.open(pz3_path, 'rb').read().decode()
total: int = len(pz3)

MAX_RANK = 3
MIN_SIZE = total / 1000


def collect_objects(rank: int, min_par: int, max_par: int
                    ) -> Optional[Dict[str, Tuple[int, Optional[dict]]]]:
    global pz3
    cur = min_par
    indent = '	' * rank
    res_: Dict[str, Tuple[int, Optional[dict]]] = {}
    duplicates: dict[str, int] = {}

    while True:
        cur = pz3.find('\n' + indent + '{', cur, max_par)
        if cur == -1: break

        title_ = pz3[pz3.rfind('\n', cur - 100, cur):cur].strip()
        if title_ in res_:
            if title_ not in duplicates:
                duplicates[title_] = 0
            duplicates[title_] += 1
            title_ += f'___{duplicates[title_]:02d}'

        cur += rank + 1
        min_obj = cur
        cur = pz3.find('\n' + indent + '}', cur, max_par)
        max_obj = cur
        total_ = max_obj - min_obj

        if rank <= MAX_RANK and total_ >= MIN_SIZE:
            res_[title_] = (total_, collect_objects(rank + 1, min_obj, max_obj))
        else:
            if 'OTHERS' not in res_:
                res_['OTHERS'] = (0, None)
            res_['OTHERS'] = (res_['OTHERS'][0] + total_), res_['OTHERS'][1]

    return res_ if len(res_) > 1 else None


def print_stats(title_: Optional[str], total_: int, items: Optional[Dict], rank: int) -> None:
    global total
    if title_ is not None:
        percent = (total_ / total) * 100.0
        print(('  ' * (rank - 1)) + f'{title_} [{percent:.2f}%]:')
    if items is not None:
        for title__, total_and_subitems in \
                sorted(items.items(), key=lambda item: item[1][0], reverse=True):
            print_stats(title__, total_and_subitems[0], total_and_subitems[1], rank + 1)


print_stats(None, total, collect_objects(1, 0, total), 1)
