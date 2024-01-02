CC = clang
CFLAGS = -Wall -std=c99 -pedantic 

all: _molecule.so

clean:
	rm -f *.o *.so  _molecule.so molecule_wrap.c molecule_wrap.o  molecule.py

libmol.so: mol.o
	$(CC) $(CFLAGS) mol.o -shared -o libmol.so

mol.o: mol.c mol.h
	$(CC) $(CFLAGS) -c mol.c -fPIC -o mol.o

molecule_wrap.c: molecule.i mol.h
	swig3.0 -python molecule.i

molecule_wrap.o: molecule_wrap.c
	$(CC) $(CFLAGS) -c molecule_wrap.c -fPIC -I/usr/include/python3.7m -o molecule_wrap.o

_molecule.so: molecule_wrap.o libmol.so
	$(CC) $(CFLAGS) molecule_wrap.o -shared -L. -lmol -L/usr/lib/python3.7/config-3.7m-x86_64-linux-gnu -dynamiclib -lpython3.7m -o _molecule.so