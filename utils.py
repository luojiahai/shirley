def print_begin_end(name: str, func, *args, **kwargs):
    print(f'BEGIN {name.upper()}')
    ret = func(*args, **kwargs)
    print(f'END {name.upper()}')
    print()
    return ret

def initialization(func):
    def decorated(*args, **kwargs):
        return print_begin_end('initialization', func, *args, **kwargs)
    return decorated

def generation(func):
    def decorated(*args, **kwargs):
        return print_begin_end('generation', func, *args, **kwargs)
    return decorated
