# La banane pixélisée

La banane pixélisée est un site de vidéothèque open-source qui peut être hébergé n'importe où et facilement.

## Description

La banane pixélisée est destinée à être disponible pour plusieurs amis qui souhaiteraient partager leur vidéothèque ensemble aisément. Il y a même 3 rôles : User, Trusted et Admin.

## Pour commencer

### Dépendance

* Docker

### Installation

* Allez dans le dossier souhaité, clonez le projet.
* Copiez le .env.example, puis configurez-le ! Un jeu de données est fourni et automatiquement importé dans /data/init.sql.
* Une fois fait, faites :
```bash
docker compose up -d --build
```
* Vous pouvez maintenant aller sur le site soit avec localhost, soit avec l'IP. L'accès se fait avec nginx sur le port externe dans le .env.

## Aide

* Si besoin, l'accès à la base de données se fait avec la commande :
```bash
docker exec -it <NOM_CONTENEUR> psql -U <NOM_UTILISATEUR> -d <NOM_BASE>
```
* Pour rappel, le listage des tables se fait avec :
```bash
\dt
```

## Auteurs

* Mathis OGER  
* [@Lyghht - Simon ROGER](https://github.com/Lyghht)

## Licence

* Aucune