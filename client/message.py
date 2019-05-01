import sys

def msg_server_err(message):
    print(message, file=sys.stderr, flush=True)

def msg_server_action(message):
    print(message, file=sys.stdout, flush=True)

def msg_server_comment(message):
    msg_server_action("#{}".format(message))

