#!/usr/bin/python

#pour transformer des fichiers en csv :
#import pdal (à installer avec anaconda/miniconda, ne marche pas avec pip)
#pdal translate -i <fichierAImporter> -o <output.csv>

# FICHIERS ISSUS D'UN LIDAR : utiliser importLidarCSV() et pas importCSV()

from vtk import *
import csv
import time
import subprocess
import os
from xvfbwrapper import Xvfb


beginning = time.time()
start = beginning

def initFile():
    file = input("Entrez le nom du fichier (sans l'extension): ")
    format= input("L'extension du fichier ? : ")
    finput=file+'.'+format
    if format=='csv':
        print("Vous utilisez importCSV")
        fichier = importCSV(finput,",",modulo)
    else:
        fileoutput=input("Quel nom voulez vous donnez a votre fichier en sortie: ")
        output=fileoutput+'.csv'
        print("Début de la conversion du fichier")
        subprocess.call(["pdal","translate","-i",finput,"-o",output])
        print("Fin de la conversion du fichier")
        if format=='laz':
            print("Vous utilisez importLidarCSV")
            fichier = importLidarCSV(output,",", modulo)
    return fichier



def importCSV(filename, delimiter, modulo) :
    points = vtkPoints()
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter, quotechar='|')
        print ("Import du fichier")
        i = 0
        j=0
        for row in reader:
            if (i != 0 and i%modulo==0) : #pour ne pas prendre en compte le header
                    points.InsertNextPoint(int(float(row[0])),int(float(row[1])), int(float(row[2])))
                    j=j+1
            i = i+1
    print ("Nombre de points importés  : ",j)
    return points

def importLidarCSV(filename, delimiter,modulo) :
    points = vtkPoints()
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter, quotechar='|')
        print ("Import du fichier")
        i = 0
        j=0
        for row in reader:
            if (i != 0 and row[8]=='2.000' and i%modulo==0) : #row[8] est la catégorie des points, 2.000 correspond au sol
                    points.InsertNextPoint(int(float(row[0])),int(float(row[1])), int(float(row[2])))
                    j=j+1
            i = i+1
    print ("Nombre de points importés  : ",j)
    return points

#triangulation

def delaunay2D(points) :
    profile = vtkPolyData()
    profile.SetPoints(points)
    delny = vtkDelaunay2D()
    delny.SetInputData(profile)
    return delny

def mapping(delny) :
    mapMesh = vtkPolyDataMapper()
    mapMesh.SetInputConnection(delny.GetOutputPort())
    meshActor = vtkActor()
    meshActor.SetMapper(mapMesh)
    meshActor.GetProperty().SetColor(.1, .2, .4)
    return meshActor

#rendering

def rendering(meshActor) :
    ren = vtkRenderer()
    renWin = vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    print("Render en cours")

    # Add the actors to the renderer, set the background and size
    ren.AddActor(meshActor)
    print("add actor")
    ren.SetBackground(1, 1, 1)
    print("Ajout background")
    renWin.SetSize(250, 250)
    print("definition de la taille")
    renWin.Render()
    print("ouverture de la fenetre")
    cam1 = ren.GetActiveCamera()
    print("Ajout des caméra")
    cam1.Zoom(1.5)
    print("Ajout du zoom")
    iren.Initialize()
    print("Initialisation")
    renWin.Render()
    print("Ajout du render")
    # iren.Start()
    # print("iren start")
    return renWin

#export au format OBJ
def exportOBJ(renWin) :
    obj = vtkOBJExporter()
    obj.SetFilePrefix("essai")
    obj.SetRenderWindow(renWin)
    obj.Write()

#La même chose que dans le main de ce fichier mais utilisable ailleurs car dans une fonction avec arguments
def pipeline_VTK(fic,modulo=1):
    beginning = time.time()
    start = beginning
    print("Modulo : ",modulo)
    fichier = importCSV(fic,",",modulo) # a remplacer par importLidarCSV si les données sont issues d'un fichier lidar
    print ("Import : ", time.time() -beginning)
    beginning = time.time()
    delny = delaunay2D(fichier)
    print ("Triangulation de Delaunay : ", time.time() -beginning)
    beginning = time.time()
    mapped = mapping(delny)
    print ("Mapping : ", time.time() -beginning)
    beginning = time.time()
    rendered = rendering(mapped)
    print ("Rendering : ", time.time() -beginning)
    beginning = time.time()
    exportOBJ(rendered)
    print ("Ecriture obj : ", time.time() -beginning)
    print ("Temps total : ",time.time()-start)



if __name__=='__main__':
    vdisplay = Xvfb(width=1280, height=740)
    vdisplay.start()
    modulo = 1000
    print("Modulo : ",modulo)
    fichier=initFile()
    print ("Import : ", time.time() -beginning)
    beginning = time.time()
    delny = delaunay2D(fichier)
    print ("Triangulation de Delaunay : ", time.time() -beginning)
    beginning = time.time()
    mapped = mapping(delny)
    print ("Mapping : ", time.time() -beginning)
    beginning = time.time()
    rendered = rendering(mapped)
    print ("Rendering : ", time.time() -beginning)
    beginning = time.time()
    exportOBJ(rendered)
    print ("Ecriture obj : ", time.time() -beginning)
    beginning = time.time()
    print ("Temps total : ",time.time()-start)
    vdisplay.stop()
