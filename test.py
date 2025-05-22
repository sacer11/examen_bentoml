import jwt
print("jwt Modul Pfad:", jwt.__file__)
try:
    print("jwt Version:", jwt.__version__)
except AttributeError:
    print("jwt Modul hat kein __version__ Attribut")