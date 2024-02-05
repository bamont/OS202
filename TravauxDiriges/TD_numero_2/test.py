import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
import matplotlib.cm
from mpi4py import MPI

#mpirun -n 4 ./test.py pour run avec 4 processus

globCom = MPI.COMM_WORLD.Dup()
nbp     = globCom.size
rank    = globCom.rank
name    = MPI.Get_processor_name()

print(f"Je suis le processus {rank} sur {nbp} processus")
print(f"Je m'execute sur l'ordinateur {name}")

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nbp = comm.Get_size()
print(nbp)

if rank == 0:
    data = {'a': 7, 'b': 3.14}
    comm.send(data, dest=1)
elif rank == 1:
    data = comm.recv(source=0)
    print('On process 1, data is ',data)