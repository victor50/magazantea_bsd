def decode32(dato):
    cod32=['0','1','2','3','4','5','6','7','8','9',\
            'B','C','D','F','G','H','J','K','L','M',\
            'N','P','Q','R','S','T','U','V','W','X','Y','Z']
    #
    nonva=False
    try:
        dato=float(dato)
    except:
        try:
            dato=float(int(dato))
        except:
            nonva=True
    decoded=''
    if not nonva:
        for n in[5,4,3,2,1]:
            a=dato // (32**n)
            decoded +=cod32[int(a)]
            dato=dato-a*(32**n)
        decoded +=cod32[int(dato)]
    return decoded
