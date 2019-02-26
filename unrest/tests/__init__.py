def idsorted(it, key='id'):
    return sorted(it, key=lambda x: x[key])
