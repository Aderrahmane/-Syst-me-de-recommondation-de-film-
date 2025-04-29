import pandas as pd
from annoy import AnnoyIndex
import numpy as np

#on initialise les données dans la table de donnée structuré de panda "TableDonnees"
DirectoryFichier = "spotusers.csv"
TableDonnees = pd.read_csv(DirectoryFichier, header=None, names=["utilisateur", "film"])

ListeToutFilms = list(TableDonnees["film"].unique())
DicoFilmsIndex = {film: i for i, film in enumerate(ListeToutFilms)}

#on crée un vecteur pour les utilisateurs
NbrFilms = len(ListeToutFilms)
#on groupe les films vus par chaque utilisateurs
GroupeUtilFilm = TableDonnees.groupby("utilisateur")["film"].apply(list).to_dict()
VecteursUtilisateur = {}
for utilisateur, films in GroupeUtilFilm.items():
    vecteur = np.zeros(NbrFilms)
    for film in films:
        vecteur[DicoFilmsIndex[film]] = 1
    VecteursUtilisateur[utilisateur] = vecteur

#NbrFilms est le nombre de dimensions et "angular" et la méthode de calcul entre les points
IndexAnnoy = AnnoyIndex(NbrFilms, "angular")

#on ajoute les vecteurs à l'arbre d'annoy
for i, (utilisateur, vecteur) in enumerate(VecteursUtilisateur.items()):
    IndexAnnoy.add_item(i, vecteur)

#on choisit le nombre d'arbres à générer
NbrArbre = 100
IndexAnnoy.build(NbrArbre)
IndexAnnoy.save("Annoy"+str(NbrArbre)+"Arbres.ann")
#trié en fonction de l'ajout à l'index annoy
ListeUtilisateurTriée = list(VecteursUtilisateur.keys())
CatalogueUtilisateur = {utilisateur: i for i, utilisateur in enumerate(ListeUtilisateurTriée)}

#cherche les k voisins plus proches pour recommander les films
def SuggestionDeFilms(target, k):
    PositionTarget = CatalogueUtilisateur[target]
    PositionVoisin = IndexAnnoy.get_nns_by_item(PositionTarget, k + 1)[1:] #except lui meme

    #on cherche enfin les films recommandés
    FilmsRecommandés = set()
    for IndexVoisin in PositionVoisin:
        FilmsVoisins = set(GroupeUtilFilm[ListeUtilisateurTriée[IndexVoisin]])
        FilmsRecommandés.update(FilmsVoisins)

    FilmsVus = set(GroupeUtilFilm[target])
    RecommendationsFinales = FilmsRecommandés - FilmsVus
    return list(RecommendationsFinales)

#on demande à l'utilisateur d'entrer le numéro de l'utilisateur
continer = "y"
while continer=="y":
    try:
        target = int(input("Veuillez entrer le numéro d'utilisateur: "))
        k = int(input("Veuillez entrer le nombre de voisins désirés(k): "))
        recommendations = SuggestionDeFilms(target, k)
        print("Films recommandés pour l'utilisateur", target, "pour", k,"voisins sont :", recommendations)
    except:
        print("Veuillez entrer un id d'utilisateur et un nombre de voisins(k) valide")
    continer = input("Voulez vous continuer?(y/n)")