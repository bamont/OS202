# Calcul de l'ensemble de Mandelbrot en python
import numpy as np
from dataclasses import dataclass
from PIL import Image
from math import log
from time import time
from mpi4py import MPI
import matplotlib.cm

@dataclass
class MandelbrotSet:
    max_iterations: int
    escape_radius:  float = 2.0

    def __contains__(self, c: complex) -> bool:
        return self.stability(c) == 1

    def convergence(self, c: complex, smooth=False, clamp=True) -> float:
        value = self.count_iterations(c, smooth)/self.max_iterations
        return max(0.0, min(value, 1.0)) if clamp else value

    def count_iterations(self, c: complex,  smooth=False) -> int | float:
        z:    complex
        iter: int

        # On vérifie dans un premier temps si le complexe
        # n'appartient pas à une zone de convergence connue :
        #   1. Appartenance aux disques  C0{(0,0),1/4} et C1{(-1,0),1/4}
        if c.real*c.real+c.imag*c.imag < 0.0625:
            return self.max_iterations
        if (c.real+1)*(c.real+1)+c.imag*c.imag < 0.0625:
            return self.max_iterations
        #  2.  Appartenance à la cardioïde {(1/4,0),1/2(1-cos(theta))}
        if (c.real > -0.75) and (c.real < 0.5):
            ct = c.real-0.25 + 1.j * c.imag
            ctnrm2 = abs(ct)
            if ctnrm2 < 0.5*(1-ct.real/max(ctnrm2, 1.E-14)):
                return self.max_iterations
        # Sinon on itère
        z = 0
        for iter in range(self.max_iterations):
            z = z*z + c
            if abs(z) > self.escape_radius:
                if smooth:
                    return iter + 1 - log(log(abs(z)))/log(2)
                return iter
        return self.max_iterations

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nbp = comm.Get_size()

# On peut changer les paramètres des deux prochaines lignes
mandelbrot_set = MandelbrotSet(max_iterations=50, escape_radius=10)
width, height = 1024, 1024

scaleX = 3./width
scaleY = 2.25/height

# #Cas répartition égale des lignes :
# delta=height//nbp
# if rank == 0:
#     convergence = np.empty((width, height), dtype=np.double)
#     deb = time()
#     #le thread 0 calcule les premières lignes : 
#     for y in range(delta):
#         for x in range(width):
#             c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
#             convergence[x, y] = mandelbrot_set.convergence(c, smooth=True)

#     fin = time()
#     print("Temps du calcul de l'ensemble de Mandelbrot : ",fin-deb," pour le rank ",rank)

#     #puis il s'occupe de récupérer les valeurs calculées par les autres threads
#     deb = time()
#     for i in range(1,nbp):
#         Conv=comm.recv(source=i)
#         for y in range(Conv[1],Conv[2]):
#             for x in range(width):
#                 convergence[x,y]=Conv[0][x,y-Conv[1]]

#     # Constitution de l'image résultante :
#     image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T)*255))
#     fin = time()
#     print("Temps de constitution de l'image : ",fin-deb)
#     image.save("nouvelle_image.png")
# else :
#     #calcule des indices entre lequels le processus rank doit travailler
#     if rank!=nbp:
#         ymin, ymax = (rank)*delta,(rank+1)*delta
#     else :
#         ymin, ymax = (rank+1)*delta,height
    
#     #initialisation d'une liste vide et la remplit 
#     deb=time()

#     convergence_bis= np.empty((width, ymax-ymin), dtype=np.double)
#     for y in range(ymin,ymax):
#         for x in range(width):
#             c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
#             convergence_bis[x, y-ymin] = mandelbrot_set.convergence(c, smooth=True)
#     fin=time()
#     print("Temps du calcul de l'ensemble de Mandelbrot : ",fin-deb," pour le rank ",rank)

#     #renvoie les données calculées vers le thread 0
#     comm.send([convergence_bis,ymin,ymax], dest=0)


#Cas maître esclave : 
if rank == 0:
    convergence = np.empty((width, height), dtype=np.double)

    #le maitre envoie npb - 1 lignes aux esclaves : 
    for i in range(1,nbp):
        comm.send(i-1,dest=i)
    
    y_row=nbp-1#dernière ligne à avoir été traitée
    while y_row<height-1:
        Status=MPI.Status()
        Conv=comm.recv(source=MPI.ANY_SOURCE,status=Status)#reçoit de n'importe quelle source

        for x in range(width):
            convergence[x,Conv[1]]=Conv[0][x]

        #on renvoie une nouvelle ligne à calculer à cette source
        comm.send(y_row, dest=Status.Get_source())
        y_row+=1
    #pour arrêter tous les autres processus:
    for i in range(nbp-1):
        Status=MPI.Status()
        Conv=comm.recv(source=MPI.ANY_SOURCE,status=Status)#reçoit de n'importe quelle source
        
        #récupère les dernières lignes d'information
        for x in range(width):
            convergence[x,Conv[1]]=Conv[0][x]
        
        #renvoie None pour arrêter le processus
        comm.send(None, dest=Status.Get_source())

    # Constitution de l'image résultante :
    image = Image.fromarray(np.uint8(matplotlib.cm.plasma(convergence.T)*255))
    image.save("nouvelle_image.png")
else : 
    deb=time()
    while True:
        #reçoit la ligne à calculer
        y = comm.recv(source=0)

        #cas d'arrêt du processus
        if y==None:
            fin=time()
            print("Temps du calcul de l'ensemble de Mandelbrot : ",fin-deb," pour le rank ",rank)
            break
        
        convergence_bis= np.empty(width, dtype=np.double)
        #calcule les différentes valeurs sur la ligne
        for x in range(width):
            c = complex(-2. + scaleX*x, -1.125 + scaleY * y)
            convergence_bis[x] = mandelbrot_set.convergence(c, smooth=True)
        
        #renvoie les résultats au processus 0
        comm.send([convergence_bis,y],dest=0)