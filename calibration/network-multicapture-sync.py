# read args
# 1st 8132 [port]


import sys
len_argv = len(sys.argv)

if len_argv == 2:
    network_sync_port = sys.argv[1]
    print((network_sync_port))
else:
    print(str(len_argv - 1) + " arguments provided. Expected 1 [tty source, stdout redirect, host, port]")
