from mpi4py import MPI

# Produit matrice-vecteur v = A.u
import numpy as np

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nbp = comm.Get_size()

# Dimension du problème (peut-être changé)
dim = 12
# Initialisation de la matrice
A = np.array([[(i+j) % dim+1. for i in range(dim)] for j in range(dim)])

# Initialisation du vecteur u
u = np.array([i+1. for i in range(dim)])

# Produit matrice-vecteur
v = A.dot(u)

#pour le produit matrice vecteur par colonne
N_loc=dim//nbp
V = np.zeros(dim)

for i in range(dim):
    for j in range(rank*N_loc,(rank+1)*N_loc):
        V[i]+=A[i][j]*u[j]

for i in range(nbp):
    if i!=rank:
        comm.send(V,dest=i)

for i in range(nbp-1):
    Status=MPI.Status()
    V_bis=comm.recv(source=MPI.ANY_SOURCE,status=Status)#reçoit de n'importe quelle source
    V+=V_bis

#affiche le résultat pour un processus
if rank==0:
    print("A.u = ",np.array(V))

#vérifie que tous les processus ont le même résultat:
print("v et V sont identiques :",(v==V).all(),"pour le processus : ",rank)

#Pour le produit matrice vecteur par ligne
N_loc=dim//nbp
V = np.zeros(dim)

for i in range(rank*N_loc,(rank+1)*N_loc):
    for j in range(dim):
        V[i]+=A[i][j]*u[j]

for i in range(nbp):
    if i!=rank:
        comm.send(V,dest=i)

for i in range(nbp-1):
    Status=MPI.Status()
    V_bis=comm.recv(source=MPI.ANY_SOURCE,status=Status)#reçoit de n'importe quelle source
    V+=V_bis

#affiche le résultat pour un processus
if rank==0:
    print("A.u = ",np.array(V))

#vérifie que tous les processus ont le même résultat:
print("v et V sont identiques :",(v==V).all(),"pour le processus : ",rank)