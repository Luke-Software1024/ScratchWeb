def example(arg: str, cmd: str):
    return "Argument: {}\nCommand: {}".format(arg, cmd)

funcs: dict[str, function] = {"example": example}