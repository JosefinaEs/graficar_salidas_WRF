# Script que grafica la variable T2 de una salida de WRF en NetCDF
# El script recibe los siguientes par'ametros:
# 1 (obligatorio): Archivo NetCDF a graficar

# Los dem'as parametros  son opcionales y se pasan como banderas
# --lat_n	latitud norte del subdominio a graficar
# --lat_s	latitud sur del subdominio a graficar
# --long_e	longitud este del subdominio a graficar
# --long_o	longitud oeste del subdominio a graficar
# --barra 	archivo de la barra de color a utilizar
# --rango_i		
# --rango_s
# --proc	numero de procesadores para graficado en paralelo

import sys
import getopt
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.colors as colors

from netCDF4 import Dataset
from matplotlib import cm

# Funcion que realiza una grafica de una variable escalar
def graficar_temparatura(i, tmp2m, levels, cmap1, long_o, long_e, lat_s, lat_n, Fechas):
        fig=plt.figure()

        # Convertir la temperatura a grados Celcius
        aux=tmp2m-273.15

        # Formato de las etiquetas de los ejes (ticks)
        plt.rc('font', weight='bold', size=8)

        # Hora de salida
        fecha=Fechas.astype('|S1').tostring().decode('utf-8')

        # data es el atributo que tiene los datos dentro del formato netcdf
        plt.contourf(long,lat,aux.data,levels,cmap=cm.get_cmap(cmap1))
        plt.plot(data[:,0],data[:,1],'k',linewidth=0.5)
        plt.title('Temperatura en superficie [°C] \n ' + str(fecha) +'UTC', fontdict=font)
        plt.xlabel('Longitud', fontdict=font)
        plt.ylabel('Latitud', fontdict=font)
        #plt.colorbar(ticks=np.arange(-10,50,5), fraction=0.046, pad=0.04)
        plt.colorbar(ticks=np.arange(-10,50,5), orientation="horizontal", pad=0.15, fraction=0.056)
        plt.axis('scaled')

        # Coordenadas del dominio
        plt.axis([float(long_o), float(long_e), float(lat_s), float(lat_n)])

        # Crear y guardar la figura
        nombre='Temperatura_2m_' + str(i) +'.png'
        plt.savefig(nombre,bbox_inches="tight", dpi=200)

        #Que no muestre la ventana por cada imagen
        plt.show(block=False)
        plt.close(fig)


# Cargar la divisi'on pol'itica de M'exico
data=np.loadtxt('/home/comun/scripts/python/division_mexico.dat')

# Formato del texto de la gr'afica
font={'family': 'sans-serif','color': 'black','weight': 'bold','size': 10,}

# Cargar el archivo NetCDF
dataset=Dataset(sys.argv[1])

# Cargar individualmente las variables de latitud, longitud, temparatura y tiempo
lat=dataset.variables['XLAT']
long=dataset.variables['XLONG']
T2=dataset.variables['T2']
Tiempo=len(dataset.variables['Times'])
Fechas=dataset.variables['Times']

# Guardar 'unicamente la latitud y la longitud
lat=lat[1,:,1]
long=long[1,1,:]

# Valores por defecto, tomados del NetCDF de entrada
lat_n=lat[len(lat)-1]		# Latitud norte
lat_s=lat[0]			# Latitud sur
long_e=long[len(long)-1]	# Longitud este
long_o=long[0]			# Longitud oeste
file="/home/comun/scripts/python/barra_temperatura.txt"
rango_i=-14
rango_s=51
numproc=1

# Obtener los parametros si es que el usuario ha definido algunos
argv=sys.argv[2:]
try:
    opts, args=getopt.getopt(argv,"b:n:s:e:o:i:u:p:",["barra=","lat_n=","lat_s=","long_e=","long_o=","rango_i=","rango_s=","numproc="])
except getopt.GetoptError as err:
    print(err)
    opts=[]

for opt, arg in opts:
    if opt in ['-n','--lat_n']:
        lat_n=arg
    elif opt in ['-b','--barra']:
        file=arg
    elif opt in ['-s','--lat_s']:
        lat_s=arg
    elif opt in ['-e','--long_e']:
        long_e=arg
    elif opt in ['-o','--long_o']:
        long_o=arg
    elif opt in ['-i','--rango_i']:
        rango_i=int(arg)
    elif opt in ['-u','--rango_s']:
        rango_s=int(arg)+1
    elif opt in ['-p','--numproc']:
        numproc=arg

# Cargar el archivo con la barra de color
cmap=np.loadtxt(file)
cmap1=colors.ListedColormap(cmap)

# Rango de la grafica
levels=range(rango_i,rango_s,1)

# Ciclo que realiza una grafica para cada uno de los tiempos encontrados en el archivo NetCDF
if numproc==1:
	# Lo corremos en serie
	for i in range(1,Tiempo,1):
		graficar_temparatura(i, T2[i,:,:], levels, cmap1, long_o, long_e, lat_s, lat_n, Fechas[i])
else:
	# Lo corremos en paralelo
	pool = mp.Pool(int(numproc))
	results=pool.starmap_async(graficar_temparatura, [(i, T2[i,:,:], levels, cmap1, long_o, long_e, lat_s, lat_n, Fechas[i]) for i in range(1,Tiempo,1)]).get()
	pool.close()
