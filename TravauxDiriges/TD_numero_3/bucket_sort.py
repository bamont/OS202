from mpi4py import MPI
import numpy as np

comm = MPI.COMM_WORLD
nbp = comm.Get_size()
rank = comm.Get_rank()

def tri_rapide(Tab):
    if len(Tab)==0:
        return []
    elif len(Tab)==1:
        return Tab
    else :
        pivot=Tab[0]
        Tab_inf,Tab_sup=[],[]
        for i in range(1,len(Tab)):
            if Tab[i]<pivot:
                Tab_inf.append(Tab[i])
            else :
                Tab_sup.append(Tab[i])
        return tri_rapide(Tab_inf)+[pivot]+tri_rapide(Tab_sup)
    
def bucket_sort(Tab):
    # Nombre de seaux
    nb_buckets = nbp
    
    # Création des seaux locaux
    bucket_local = [[] for i in range(nb_buckets)]
    
    # Détermination des bornes de Tab
    min_Tab = min(Tab)
    max_Tab = max(Tab)
    taille_seau = (max_Tab - min_Tab) / nb_buckets
    
    # Distribution des éléments dans les seaux locaux
    for x in Tab:
        for i in range(nb_buckets):
            if rank == i:
                if x >= min_Tab + i * taille_seau and x < min_Tab + (i + 1) * taille_seau:
                    bucket_local[i].append(x)

    
    # Tri local du seau rank par le processus rank
    bucket_local[rank] = tri_rapide(bucket_local[rank])
    
    # Envoi des parties triées aux processus 0
    Tab_trié = comm.gather(bucket_local[rank], root=0)
    
    # Concaténation des buckets triés
    if rank == 0:
        Tab_final = []
        for part in Tab_trié:
            Tab_final.extend(part)
        return Tab_final
    else:
        return None

if rank == 0:
    # Génération du tableau de nombres arbitraires
    Tab = np.random.randint(0, 1000, 50)
    print("Tableau non trié :", Tab)
else:
    Tab = None

# Distribution du tableau à tous les processus
Tab = comm.bcast(Tab, root=0)

# Tri par bucket
Tab_ = bucket_sort(Tab)

# Affichage du tableau trié sur le processus 0
if rank == 0:
    print("Tableau trié :", Tab_)