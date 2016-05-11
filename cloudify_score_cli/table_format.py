def _short_line(name, size):
    if not name:
        return ""
    if len(name) < size:
        return name
    else:
        return name[:size-3] + "..."


def print_header(colums):
    line = ""
    for (name, size) in colums:
        line += (
            "%" + str(size) + "s|"
        ) %  (_short_line(name, size))
    print line
    line = ""
    for (_, size) in colums:
        line += "-" * size + "+"
    print line


def print_row(data, colums):
    line = ""
    for (name, size) in colums:
        value = data.get(name)
        line += (
            "%" + str(size) + "s|"
        ) %  (_short_line(value, size))
    print line
