hMax = 1500 #wysokość max [m]

def monitorHeight( hCurr):
    hDiff = hMax - hCurr

    if hDiff <= 0:
        return 1
    else:
        return 0


