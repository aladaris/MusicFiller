#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

"""
   La idea es crear un script que rellene un mp3 portatil (o cualquier
   reproductor) con ficheros aleatorios de musica.
   
   By aladaris 17-03-2011
"""

import os
import random
import sys
import shutil
import sqlite3

#musicDir = "/media/Terasync/Música"
musicDir = "../Música"
outPutDir = "../Out"
#outPutDir = "/tmp/Música"
#outPutDir = "/media/6662-3261/Audio/My Music"
#dirs = os.popen("ls -RQ "+ musicDir +" | grep /").readlines() # Todos los subdirectorios de la carpeta "musicDir" (incluido el directorio "musicDir")
#totalSize = 0 # Tamaño en bytes que se ha copiado ya
#totalSizeTemp = 0
fichNum = 0 # Numero de ficheros copiados


random.seed(os.urandom(512))
rdm = (random.randint(1,random.randint(1000,10000))*random.randint(1,3000))%2046 + 1 # "+1" evita division entre cero "0"
def isAcepted(thr):
#   thr = 3
#   j = 0
#   for i in range(1,30000):

#   rdm = (random.randint(1,random.randint(1000,10000))*random.randint(1,3000))%2046 + 1 # "+1" evita division entre cero "0"
   if random.randint(1,3000)%(rdm*500) < thr:
      return 1
#         j += 1
#         print "["+str(j)+"]"+str(rdm)
   return 0

"""
   Calculo de la posicion de la progressBar
         maxSize ---> 100%
            x    --->  1%
         x = maxSize/100
         Luego el porcentaje ocupado por el valor de totalSize (y) es:
            y = totalSize / x
"""
def updateProgressBar():
   subDiv = 5 # Porcentaje representado por cada "#" en la ProgressBar
   percent = totalSize / (maxSize/100)
   for i in range(0, int(percent/subDiv)):
      sys.stdout.write("#")
   print str(int(percent))+" % ["+str(fichNum)+" files]."






def populateDataBase():
   dirs = os.popen("ls -RQ "+ musicDir +" | grep /").readlines() # Todos los subdirectorios de la carpeta "musicDir" (incluido el directorio "musicDir")
   conn = sqlite3.connect("./musicFiller.db")
   crsr = conn.cursor()
   for d in dirs:
      d = d.replace(":","") # Quitamos los ":"
      d = d.rstrip('\n') # Quitamos los \n
      consult = "INSERT INTO directories (path) VALUES ("+str(d)+")"
      crsr.execute(consult)
      crsr.execute("SELECT dID FROM directories ORDER BY dID DESC LIMIT 1") # Obtenemos el campo dID de la ultima fila
      for row in crsr: # Obtenemos el valor dID devuelto por la consulta
         dirIndex = row[0]
      files = os.popen("ls "+ d +" | grep .mp3").readlines() # Ficheros mp3 del directorio "d"
      for f in files:
         f = f.replace("/","")
         f = f.rstrip('\n') # Quitamos los \n
         #size = os.path.getsize(d.replace("\"","") + "/" + f)
         size = 1573 # DEBUG
         consult = "INSERT INTO files (fileName, size, dirID) VALUES (\""+str(f)+"\", "+str(int(size))+", "+str(dirIndex)+")"
         crsr.execute(consult)

   conn.commit() # Persistimos los cambios
   

# TODO: Marcar como "copiado/no copiado", para evitar copiar el mismo fichero mas de una vez
def selectFiles(maxSize): # "maxSize" = Maximo espacio disponible (en Megabytes)
   conn = sqlite3.connect("./musicFiller.db")
   crsr = conn.cursor()
   totalSize = 0

   consult = "SELECT * FROM directories WHERE dID >= 0" # Selecciona todas las filas de la tabla "directories"
   #directorios = conn.cursor()
   crsr.execute(consult)
   directorios = list(crsr)
   dirRowsCount = len(directorios)
   # "directorios" contiene ahora todas las filas de la tabla "directories"
#   print "  DEBUG: dirRowCount = "+ str(dirRowsCount)
#   print "  DEBUG: "+ str(directorios[245][0])
   #print "  DEBUG: directorios PRE = "+ str(list(directorios)[0])
   if dirRowsCount > 0:
      while totalSize < maxSize:
         randDirNum = random.randint(0,dirRowsCount - 1)
         #print "  DEBUG: directorios = "+ str(directorios)
         #print "  DEBUG: num = "+ str(int(num))
         dID = int(directorios[randDirNum][0])
#         print "  DEBUG: dID = "+ str(dID)
         consult = "SELECT * FROM files WHERE dirID = " + str(dID) # Selecciona todas las filas de la tabla "files" cuyo
                                                                   # valor "dirID = dID" (es decir: Todos los ficheros
                                                                   # contenidos en el directorio "dID").
         crsr.execute(consult)
         files = list(crsr)
         filesRowsCount = len(files)
         if filesRowsCount > 0:
#            print "  DEBUG: files = "+str(files)
            fileRow = files[random.randint(0,filesRowsCount - 1)] # Selecciona un fichero aleatorio contenido en el directorio "dID"
#            print "  DEBUG: fileRow = "+str(fileRow)
            totalSize += int(fileRow[2])
#            print totalSize
#            print "  DEBUG: fID = "+str(fileRow[0])
            print "Copiando: \"" + directorios[randDirNum][1]+"/"+str(fileRow[1])+"\""
#      print "  DEBUG: totalSize = "+str(totalSize)

selectFiles(13000)
#populateDataBase()



"""
# V: 0.1
for d in dirs:
   d = d.replace(":","") # Quitamos los ":"
   d = d.rstrip('\n') # Quitamos los \n
   files = os.popen("ls "+ d +" | grep .mp3").readlines() # Ficheros mp3 del directorio "d"
#   print "  DEBUG: Dir = "+str(d)
   for f in files:
      f = f.replace("/","")
      f = f.rstrip('\n') # Quitamos los \n
#      print "  DEBUG: File = "+f
      fich = d.replace("\"","") + "/" + f # Ruta absoluta al fichero mp3 "f"
#      print "  DEBUG: Path = "+fich
      size = os.path.getsize(fich)
      if isAcepted(maxSize/26): # TODO: poner 26, como uhna variable. Su mision es ajustar el ratio de aceptadas en funcion de maxSize (a menor valor, mas aceptadas)
         totalSizeTemp += size/float(1024*1024)
         if totalSizeTemp < maxSize:
            totalSize = totalSizeTemp
            #print "  Copiando: "+fich+" ["+str(size/float(1024*1024))+"Mb]" # Ruta [tamaño en Mb]
            fichNum += 1
            shutil.copy(fich, outPutDir)
            updateProgressBar()
         else:
            print "[LIMITE] Total: "+str(totalSize)+"Mb"
            sys.exit()

print "Total: "+str(totalSize)+"Mb"
"""

