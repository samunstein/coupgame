from config import DEBUG, PARAM_SPLITTER, COMMAND_END


def debug_print(msg):
    if DEBUG:
        print(msg)

def commands_params(raw_data: str):
    commands = raw_data.rstrip(COMMAND_END).split(COMMAND_END)
    return [(cd.split(PARAM_SPLITTER)[0], cd.split(PARAM_SPLITTER)[1:]) for cd in commands]
