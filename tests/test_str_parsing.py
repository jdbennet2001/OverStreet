

def test_str():
    str1 = "Adventure Comics #423 (1972-09-01).cbz"
    str2 = "Adventure Comics"
    strtkn1 = str1.split(' ')
    strtkn2 = str2.split(' ')
    overlap = set(strtkn1) & set(strtkn2)
    assert len(overlap) > 0
