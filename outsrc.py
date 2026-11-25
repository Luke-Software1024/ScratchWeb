def example(arg: str, cmd: str):
    return "Argument: {}\nCommand: {}".format(arg, cmd)

funcs: dict[str, tuple[function, int]] = {"example": (example, 0)}
