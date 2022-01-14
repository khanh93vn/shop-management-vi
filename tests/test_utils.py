import pytest
from itertools import product

from src.utils import *

def test_date2ts():
    assert date2ts("26/11/1993") == 8730

date_test_data2 = [*product(range(1, 13), range(1, 29))]
@pytest.mark.parametrize("month,day", date_test_data2)
def test_ts2date_date2ts(month, day):
    s = f"{day:02}/{month:02}/2021"
    assert s == ts2date(date2ts(s))

def test_currency_format():
    assert currency_format(1000000) == "1.000.000,00 đồng"
