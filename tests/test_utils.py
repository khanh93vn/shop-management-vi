from src.utils import *

def test_int2datestr_datestr2int():
    for m in range(1, 13):
        for d in range(1, 29):
            s = f"{d:02}/{m:02}/2021"
            assert s == int2datestr(datestr2int(s))