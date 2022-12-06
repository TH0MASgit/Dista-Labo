 # Calibration stéréoscopique d'une nouvelle caméra
 La calibration d'un caméra (ou paire de caméra) permet de corriger les distortions liées aux composants optique et electorniques d'une caméra.
 Par exemple :
  - les lentilles provoque des distortions d'images en "sphérisant" l'image produite
  - les capteurs sont parfois ex-centrés de la lentille décalnt le centre focal
  - le traitement electronique de l'image  peut aussi influer sur la qualité de la capture
  
Pour corriger tout ces défauts et obtenir des images de la plus grande précision possible


Un autre aspect de la calibration est le calcul du **_baseline_**. Le baseline est la distance qui sépare les deux capteurs optiques a l'intérieur des caméras.
Cette distance sera necessaire pour le calcul des cartes de disparité (carte de profondeur en 3D)

## Damier de calibration
Pour calibrer toute caméra, il faut une référence "physique" sur lequel le calcul peut se baser.
Un damier noir et blanc est parfait pour cela car on sait que tout ses angles sont droit, et que les formes (les carrés) sont très précises et facilement identifiables.

Grâce au damier, la calibration peut connaitre la "réalité" et corriger l'image perçue par le capteur.

Une image du damier à imprimer est disponible [ici](https://github.com/doorjuice/dista/blob/master/calibration/damier.png)
  
### Ajuster la taille des carreaux 
- Mesurez précisément la taille physique(en cm) des carreaux de votre damier imprimé
- Ouvrir le fichier **_calibration/calibration_stereo.py_**
 - A la `Ligne 104` du fichier `calibration_stereo.py`, indiquez la bonne taille des carreaux : 
```python
    # Taille des carreaux sur le damier en cm 
    squaresize = 3.629 
```
  
## Calibration d'une caméra stéréo (1 seul connecteur USB)  
La calibration est l'étape la plus délicate. Vous allez devoir prendre successivement des photos du damier dans différentes configuration afin que l'algorithme de correction des images soit le mieux "renseigné" concernant les déformations des capteurs.

On ne sait pas encore la meilleur technique pour prendre les photos mais le damier doit toujours être entièrement visible sur les images que vous prendrez.

Il semblerait que prendre des images avec le damiers dans de nombreuses positions et emplacement ( surtout dans les coins) soit une bonne technique.

### I. Selection des caméras
- Ouvrir le fichier **_calibration/capture_single_usb.py_** 
- `Ligne 20`, changer le numéro de la caméra : 
```python
    cap = cv2.VideoCapture(1) 
```
- Changez le `1` Avec par exemple 0,1,2 en fonction du numero assigné à votre caméra 

### II. Changement de la résolution de capture
- `Ligne 29-30`, changer la resolution de la caméra
(changer les chiffres de largeur et de hauteurs) :
```python
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280) 
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480) 
```
**Note :** les caméra stéréoscopique on une résolution double en largeur, car elles captures les deux images dans le même flux.
Donc pour une résolution par caméra de 640px de largeur, on a 640 *2 = 1280px pour la largeur de l'image produite.
 
### III. Caméra inversé (optionnel)
Si la caméra est inversé verticalement ( ex: fixée à l’envers) :
- Dé-commenter les `lignes 49-50` : 
```python
    #left_frame_flip=cv2.flip(left_frame_color, 0) 
    #right_frame_flip=cv2.flip(right_frame_color, 0) 
```
 
### IV. Lancer la capture des images
Lancer le calcul de la configuration : 
```
    $ python capture_single_usb.py 
```


### V. Lancer la calibration  

Pour lancer la calibration, dans le terminal : 
 
```
    $ python calibration_stereo.py 
```
 
Recupérez le fichier config et le renommer avec un nom `"SNxxxxx.conf"`, où `xxxxx` est le numero que vous aurz attribué à votre caméra

 

 