import math

def floor(val, prec):
    val = round(val, prec+1) #avoid 3.9999999996 
    mult = float(pow(10, prec))
    return math.floor(val*mult)/mult

def floor_1(val):
    return math.floor(val*10.0)/10.0

def floor_4(val):
    return math.floor(val*10000.0)/10000.0

def cmax(arg1, arg2, arg3):
    return max(max(arg1, arg2), arg3)

def cmin(arg1, arg2, arg3):
    return min(min(arg1, arg2), arg3)    