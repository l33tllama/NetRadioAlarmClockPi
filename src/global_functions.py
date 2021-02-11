def StringToBytes(val):
    ret_val = []
    for c in val:
        ret_val.append(ord(c))
        #print(c)

    ret_val.append(0)
    return ret_val