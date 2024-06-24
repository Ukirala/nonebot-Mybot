# transform value
def convert_value(val: str | int | bool):
    # int
    if val.isdigit():
        return int(val)
    # bool
    if val.lower() in ['true', 'false']:
        return val.lower() == 'true'
    # keep str
    return val