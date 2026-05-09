### Virtual devices
Ce dossier contient des versions simulées des devices afin de mocker les vrais capteurs/équipements

Pour rouler un asset virtuel, il faut d'abord build l'image avec : `docker build -f Dockerfile.[nom_asset] -t virtual-ivac .`

Ensuite, faire docker compose up.