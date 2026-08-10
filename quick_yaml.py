def load(text: str):
    global _yml
    _yml = text.split('\n')
    return _parse_model(0)[0]


def _parse_model(line: int):
    global _yml

    # determine the indentation of the current model
    this_indent = _count_indent(line)

    # create an initial model
    if _yml[line][this_indent:this_indent + 2] == '- ':
        model = list()
    else:
        model = dict()

    # loop on each line
    while line != len(_yml):

        # if the model is finished:
        if _count_indent(line) < this_indent:
            break

        # focus on the usable data of this line
        l = _yml[line][this_indent:]
        if ' #' in l: l = l.split(' #', 1)[0]
        l = l.strip()
        if l == '' or l.startswith('#'):
            line += 1
            continue

        # if it is a single value:
        if not l.endswith(':'):
            if isinstance(model, list):
                model.append(l.split('- ', 1)[1].strip())
            else:
                model[l] = None
            line += 1

        # if it is a key:
        else:
            if isinstance(model, list):
                old_model: List = model.copy()
                model = dict()
                for item in old_model:
                    model[item] = None
            key = l[:-1]
            if key.startswith('- '):
                key = key[2:].strip()
            model[key], line = _parse_model(line + 1)

    return model, line


def _count_indent(line: int) -> int:
    global _yml
    count = 0
    for ch in _yml[line]:
        if ch == ' ':
            count += 1
        else:
            break
    return count
