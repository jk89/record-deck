import time

def temporalTimeout(ns, func, *args):
    cont = True
    tNow = time.time_ns()
    while cont:
        tThen = time.time_ns()
        dt = tThen - tNow
        if (dt) > ns:
            func(dt, ns)
            cont = False
# dt = 0.00228571428 / (10**-9) # [ns]

#def callback(dt, ns):
#    print("hi", dt, ns)

#temporalTimeout(dt, callback, "ok")