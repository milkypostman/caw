all: genconst
	./genconst

genconst: genconst.c
	gcc -o genconst -lxcb -lxcb-atom -lxcb-icccm genconst.c
