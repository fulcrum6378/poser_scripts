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

        # convert into dict if necessary
        if isinstance(model, list) and (l.endswith(':') or ': ' in l):
            old_model = model.copy()
            model = dict()
            for item in old_model:
                model[item] = None

        # if it is a single value:
        if not l.endswith(':'):
            if isinstance(model, list):
                model.append(l.split('- ', 1)[1].strip())
            elif ': ' in l:
                spl = l.split(': ', 1)
                if spl[0].startswith('- '):
                    spl[0] = spl[0][2:]
                model[spl[0]] = spl[1]
            else:
                if l.startswith('- '):
                    l = l[2:]
                model[l] = None
            line += 1

        # if it is a key:
        else:
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
