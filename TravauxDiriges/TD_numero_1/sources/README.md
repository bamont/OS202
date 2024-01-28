
# TD1

`pandoc -s --toc README.md --css=./github-pandoc.css -o README.html`





## lscpu

```
 CPU family:          6
    Model:               126
    Thread(s) per core:  2
    Core(s) per socket:  4
    Socket(s):           1
    Stepping:            5
    BogoMIPS:            2995.20

    Caches (sum of all):     
  L1d:                   192 KiB (4 instances)
  L1i:                   128 KiB (4 instances)
  L2:                    2 MiB (4 instances)
  L3:                    8 MiB (1 instance)
```

*Des infos utiles s'y trouvent : nb core, taille de cache*



## Produit matrice-matrice

Temps de calcul : 
1023 : 1,4s
1024 : 4,9s
1025 : 1,6s

### Permutation des boucles

*Expliquer comment est compilé le code (ligne de make ou de gcc) : on aura besoin de savoir l'optim, les paramètres, etc. Par exemple :*

`make TestProduct.exe && ./TestProduct.exe 1024`


  ordre           | time    | MFlops  | MFlops(n=2048) 
------------------|---------|---------|----------------
i,j,k (origine)   | 4.64768 | 462.055 |                
j,i,k             | 5.25332 | 408.786 |    
i,k,j             | 7.98851 | 268.821 |    
k,i,j             | 7.626   | 281.6   |    
j,k,i             | 0.731459| 2935.89 |    
k,j,i             | 0.882712| 2432.82 |    


*Discussion des résultats*
La complexité algorithmique est identique entre les différents ordre. Il s'agit ici d'un problème d'accès à la mémoire et de taille de cache. 
Les matrices sont stockées en colonnes. Il faut donc que les indices de colonne varient le moins souvent possible pour ne pas devoir charger trop souvent la mémoire. C'est pour cela que l'ordre j,k,i est optimal.


### OMP sur la meilleure boucle 

`make TestProduct.exe && OMP_NUM_THREADS=8 ./TestProduct.exe 1024`

  OMP_NUM         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
1                 | 2887.47 |
2                 | 5275.63 |
3                 | 6486.73 |
4                 | 8740.2  |
5                 | 10906.6 |
6                 | 12190.2 |
7                 | 13037.4 |
8                 | 13102.7 |


On calcule l'accélération avec le rapport performance séquentielle sur performance parallèle. 
  OMP_NUM         | Accélération  | 
------------------|---------------|
1                 | 1             |
2                 | 0,55          |
3                 | 0,45          |
4                 | 0,33          |
5                 | 0,26          |
6                 | 0,24          |
7                 | 0,22          |
8                 | 0,22          |
L'ajout de thread n'augmente pas l'accélération de manière significative à partir de 5 threads. 

### Produit par blocs

`make TestProduct.exe && ./TestProduct.exe 1024`

  szBlock         | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)
------------------|---------|----------------|----------------|---------------
origine (=max)    | 696.438 |
32                | 3120.91 |
64                | 3326.31 |
128               | 3326.31 |
256               | 3627.19 |
512               | 3921.19 | 
1024              | 2894.99 |

Les performances sont bien meilleures que pour le cas scalaire (2935.89) sauf pour le cas max et 1024.

### Bloc + OMP

  szBlock      | OMP_NUM | MFlops  | MFlops(n=2048) | MFlops(n=512)  | MFlops(n=4096)|
---------------|---------|---------|-------------------------------------------------|
A.nbCols       |  1      | 3754.24 |                |                |               |
512            |  8      | 14112.7 |                |                |               |
---------------|---------|---------|-------------------------------------------------|
Speed-up       |         |         |                |                |               |
---------------|---------|---------|-------------------------------------------------|

On a une accélération de 0,27.


### Comparaison with BLAS
Pour le produit BLAS, on obtient 2824,49 MFlops. La version de produit avec matrices par blocs parait plus efficace.

# Tips 

```
	env 
	OMP_NUM_THREADS=4 ./produitMatriceMatrice.exe
```

```
    $ for i in $(seq 1 4); do elap=$(OMP_NUM_THREADS=$i ./TestProductOmp.exe|grep "Temps CPU"|cut -d " " -f 7); echo -e "$i\t$elap"; done > timers.out
```
