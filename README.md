# Guide d'Utilisation de l'Application de Gestion des Séances de Formation

Bienvenue dans l'application de gestion des séances de formation. Ce logiciel vous permet de gérer vos formations, le personnel concerné, les séances de formation ainsi que de générer des rapports au format PDF. Grâce à une interface graphique intuitive, vous pourrez :

- **Ajouter et modifier des formations** (modules).
- **Gérer le personnel** (moniteurs et participants).
- **Planifier et gérer les séances de formation**.
- **Rechercher des séances par différents critères** (date, personnel, module).
- **Générer des tableaux de suivi** sous forme de PDF.

---

## Table des Matières

1. [Prérequis et Installation](#prérequis-et-installation)
2. [Lancement de l'Application](#lancement-de-lapplication)
3. [Navigation et Interface](#navigation-et-interface)
   - [Menu Principal](#menu-principal)
   - [Ajout d'une Nouvelle Séance](#ajout-dune-nouvelle-séance)
   - [Recherche de Séances](#recherche-de-séances)
   - [Gestion du Personnel et des Formations (Admin)](#gestion-du-personnel-et-des-formations-admin)
   - [Tableau Croisé et Génération PDF](#tableau-croisé-et-génération-pdf)
4. [Conseils d’Utilisation et Astuces](#conseils-dutilisation-et-astuces)
5. [Gestion des Erreurs et Aide](#gestion-des-erreurs-et-aide)

---

## 1. Prérequis et Installation

### Prérequis

Avant de lancer l’application, assurez-vous d’avoir installé :
- **Python 3.6** (ou une version ultérieure) sur votre machine.
- Les bibliothèques Python suivantes :
  - **ttkbootstrap** (pour une interface graphique moderne)
  - **Pillow** (pour la gestion des images, notamment le logo)
  - **ReportLab** (pour la génération des documents PDF)
  - **sqlite3** (intégré par défaut dans Python pour la base de données)

### Installation des Dépendances

Vous pouvez installer les bibliothèques nécessaires via `pip`. Par exemple, dans une invite de commande, saisissez :

```bash
pip install ttkbootstrap pillow reportlab
```

---

## 2. Lancement de l'Application

L'application se compose de plusieurs fichiers Python (notamment `main.py`, `controller.py`, `view.py` et `model.py`) qui ensemble assurent le bon fonctionnement de l'interface et de la gestion de la base de données.

Pour démarrer l’application, il vous suffit de lancer le fichier principal :

```bash
python main.py
```

Une fenêtre s’ouvrira alors, affichant l’interface graphique principale.

---

## 3. Navigation et Interface

L’interface a été conçue pour être intuitive et facile d’utilisation. Voici un aperçu des principales sections et fonctionnalités.

### Menu Principal

Dès l’ouverture, vous accédez au **Menu Principal** qui vous présente trois options principales :

- **Nouvelle séance** : Pour planifier une nouvelle session de formation.
- **Recherche** : Pour effectuer des recherches sur les séances (par date, personnel ou module).
- **Admin** : Pour gérer les formations et le personnel.

*Astuce :* Un bouton « Retour » est disponible sur la plupart des pages pour revenir au menu précédent.

---

### Ajout d'une Nouvelle Séance

En sélectionnant **Nouvelle séance**, vous accédez à la page d’ajout d’une séance.

#### Fonctionnalités de la page :

- **Date de la séance**  
  - Un champ pré-rempli avec la date du jour (format `jj/mm/aaaa`). Vous pouvez le modifier si nécessaire.

- **Module**  
  - Une liste déroulante affichant les formations disponibles sous la forme « Code - Nom ». Sélectionnez le module souhaité.

- **Moniteur de séance**  
  - Une liste déroulante des membres du personnel (généralement le formateur ou le moniteur) est proposée. Choisissez le responsable de la séance.

- **Sélection des participants**  
  - Une liste vous permet de sélectionner un ou plusieurs participants à partir du personnel.  
  - Pour sélectionner plusieurs personnes, utilisez le clic avec la touche Ctrl (ou Maj selon votre système).

- **Bouton « Ajouter la séance »**  
  - Une fois tous les champs remplis et les sélections effectuées, cliquez sur ce bouton pour enregistrer la séance.  
  - Un message de confirmation s’affichera en cas de succès, sinon une alerte signalera une erreur ou un oubli.

---

### Recherche de Séances

La fonctionnalité de recherche se décline en trois options accessibles depuis le menu **Recherche** :

#### 1. Recherche par Date

- **Saisie de la date**  
  - Indiquez la date (format `jj/mm/aaaa`) dans le champ prévu à cet effet.
- **Affichage des séances**  
  - Une liste affiche les séances programmées à la date saisie.
- **Détails et Suppression**  
  - En sélectionnant une séance dans la liste, ses détails (formation, formateur, participants) apparaissent.
  - Un bouton « Supprimer la séance » permet de retirer la séance ainsi que les liens associés.

#### 2. Recherche par Personnel

- **Liste du Personnel**  
  - Une liste affiche l’ensemble des membres du personnel. Sélectionnez-en un.
- **Affichage des séances liées**  
  - Les séances auxquelles le personnel a participé s’affichent dans une liste.
- **Détails**  
  - En sélectionnant une séance, ses informations détaillées (formation, date, formateur) sont affichées.
- **Suppression de lien**  
  - Vous pouvez supprimer l’association entre le personnel et une séance si nécessaire.

#### 3. Recherche par Module

- **Sélection du module**  
  - Choisissez dans une liste déroulante le module concerné.
- **Affichage des séances**  
  - Les séances associées au module sélectionné s’affichent.
- **Détails**  
  - Sélectionnez une séance pour obtenir des informations complètes, y compris la liste des participants.

---

### Gestion du Personnel et des Formations (Admin)

En accédant au menu **Admin**, vous avez la possibilité de gérer les formations et le personnel.

#### Fonctionnalités disponibles :

- **Ajouter un personnel**  
  - Remplissez les champs « Nom du personnel » et « Identification » pour enregistrer un nouveau membre.
  
- **Voir le personnel**  
  - Une liste affiche tous les membres enregistrés. Vous pouvez :
    - Visualiser les détails.
    - Modifier les informations.
    - Supprimer un membre (ainsi que les liens associés aux séances).

- **Ajouter une formation**  
  - Saisissez le nom, le code, la description et la durée d’une formation pour l’ajouter à la base de données.

- **Voir les formations**  
  - Affichez la liste des formations existantes.
  - Sélectionnez une formation pour en voir les détails.
  - Vous pouvez ensuite modifier ou supprimer une formation.

---

### Tableau Croisé et Génération PDF

L’application intègre une fonctionnalité de **tableau croisé formations/personnel** accessible depuis le menu **Recherche**.

#### Comment procéder :

1. **Sélection des Personnels**  
   - Une liste permet de sélectionner un ou plusieurs membres du personnel (la sélection multiple est possible).

2. **Génération du Tableau**  
   - Cliquez sur le bouton « Générer le PDF ».
   - Le logiciel récupère les séances effectuées par les personnels sélectionnés, regroupées par formation.

3. **Création du PDF**  
   - Un document PDF est généré et enregistré (le nom du fichier inclut la date et l’heure de génération).
   - Un message de confirmation vous indique le nom et l’emplacement du fichier.

*Conseil :* Vérifiez que vous disposez des droits d’écriture dans le répertoire courant pour que le PDF puisse être enregistré.

---

## 4. Conseils d’Utilisation et Astuces

- **Validation des Champs** :  
  Assurez-vous de remplir tous les champs requis dans chaque formulaire. L’application vérifie que toutes les informations nécessaires sont saisies et vous avertit en cas d’oubli.

- **Navigation** :  
  Utilisez le bouton « Retour » présent sur plusieurs pages pour naviguer facilement entre les menus et revenir à l’écran précédent.

- **Mises à jour** :  
  Vous pouvez modifier les informations des formations et du personnel à tout moment depuis les pages correspondantes. Cela permet de corriger ou d’actualiser les informations sans avoir à recréer de nouvelles entrées.

- **Sauvegarde de la Base de Données** :  
  Le logiciel utilise une base de données SQLite (`bdd_formations.db`). Pensez à sauvegarder ce fichier régulièrement pour éviter toute perte de données.

---

## 5. Gestion des Erreurs et Aide

- **Messages d’Alerte** :  
  L’application affiche des boîtes de dialogue pour confirmer les actions (ajout, suppression, modification) ou signaler une erreur (champs manquants, échec d’ajout, etc.). Lisez attentivement ces messages pour corriger le cas échéant.

- **Journalisation** :  
  Des messages de log (visible dans la console) indiquent le déroulement des opérations et les éventuelles erreurs. Ces informations peuvent être utiles pour diagnostiquer un problème en cas de dysfonctionnement.

- **Assistance** :  
  Si vous rencontrez des difficultés ou si vous avez des questions concernant l’utilisation du logiciel, n’hésitez pas à consulter cette documentation ou à contacter le support technique.

---

## Conclusion

Cette application a été conçue pour faciliter la gestion des formations et des séances associées. Que vous soyez responsable de la formation ou membre du personnel, l’interface intuitive et les nombreuses fonctionnalités (recherche, ajout, modification, suppression et génération de rapports) vous permettent de garder un suivi précis et organisé de vos activités.

Nous vous souhaitons une excellente utilisation de ce logiciel et restons à votre écoute pour toute suggestion ou amélioration !

---