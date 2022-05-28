import time

def temporalTimeout(ns, func, *args):
    def tick():
        tNow = time.time_ns()
        while True:
            tThen = time.time_ns()
            dt = tThen - tNow
            if (dt) > ns:
                func(dt, ns)
                tNow = tThen    
    return tick()

# dt = 0.00228571428 / (10**-9) # [ns]

#def callback(dt, ns):
#    print("hi", dt, ns)

#temporalTimeout(dt, callback, "ok")