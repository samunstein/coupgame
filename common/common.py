from config import DEBUG, PARAM_SPLITTER, COMMAND_END


def debug_print(msg):
    if DEBUG:
        print(msg)

def make_command_params(*values):
    return PARAM_SPLITTER.join([str(v) for v in values]) + COMMAND_END

def read_command_params(raw_data: str):
    commands = raw_data.rstrip(COMMAND_END).split(COMMAND_END)
    return [(cd.split(PARAM_SPLITTER)[0], cd.split(PARAM_SPLITTER)[1:]) for cd in commands]

def get_just_data_from_socket(raw_data: str):
    return raw_data.rstrip(COMMAND_END).split(PARAM_SPLITTER)
