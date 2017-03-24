# -*- coding: utf-8 -*-

from twisted.internet import defer
import logging
from collections import OrderedDict

from le2mUtile import le2mUtileTools

import dictateurEmotionsParametres as parametres
import dictateurEmotionsTextes as textes
from dictateurEmotionsPartie import PartieDE

logger = logging.getLogger("le2m.{}".format(__name__))
    

class Serveur(object):
    def __init__(self, main_serveur):
        self._main_serveur = main_serveur
        self._main_serveur.gestionnaire_experience.ajouter_to_remote_parties(
            "dictateurEmotions", "RemoteDE"
        )

        # création du menu de la partie dans le menu expérience du serveur
        actions = OrderedDict()
        actions[u"Configurer"] = self._configurer
        actions[u"Afficher les paramètres"] = \
            lambda _: self._main_serveur.gestionnaire_graphique. \
            afficher_information2(
                le2mUtileTools.get_module_info(parametres), u"Paramètres"
            )
        actions[u"Démarrer"] = lambda _: self._demarrer()
        actions[u"Afficher les gains"] = \
            lambda _: self._main_serveur.gestionnaire_experience.\
            afficher_ecran_gains_partie("dictateurEmotions")
        self._main_serveur.gestionnaire_graphique.ajouter_to_menu_experience(
            u"Dictateur special émotion", actions)

    def _configurer(self):
        """
        Pour configurer la partie (traitement ...)
        :return:
        """
        pass

    @defer.inlineCallbacks
    def _demarrer(self):
        """
        Lancement de la partie. Définit tout le déroulement
        :return:
        """
        confirmation = self._main_serveur.gestionnaire_graphique.\
            afficher_question(u"Démarrer dictateurEmotions?")
        if not confirmation:
            return
        
        # initialisation de la partie ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self._main_serveur.gestionnaire_experience.initialiser_partie(
            "dictateurEmotions", parametres
        )
        
        # formation des groupes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # ATTENTION ICI IL FAUT RECUPERER LES GROUPES DEJA FORMES PAR indictionEmotion
        # ET IL FAUT TIRER 2 JOUEURS A DANS CHACUN DE CES GROUPES
#        for g in range(self._main_serveur.gestionnaire_groupes.get_nombre_groupes):
#            membres = self._main_serveur.gestionnaire_groupes.get_composition_groupe
#            setattr(membres[0],  "role",  parametres.Joueur_A)
#            setattr(membres[1],  "role",  parametres.Joueur_B)

#        if parametres.TAILLE_GROUPES > 0:
#            try:
#                self._main_serveur.gestionnaire_groupes.former_groupes(
#                    self._main_serveur.gestionnaire_joueurs.get_liste_joueurs(),
#                    parametres.TAILLE_GROUPES, forcer_nouveaux=True
#                )
#            except ValueError as e:
#                self._main_serveur.gestionnaire_graphique.afficher_erreur(
#                    e.message)
#                return 

        # creation de la partie chez chq joueur ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        for j in self._main_serveur.gestionnaire_joueurs.get_liste_joueurs():
            if not j.get_partie(PartieDE):
                yield (
                    j.ajouter_partie(PartieDE(
                        self._main_serveur, j)
                    )
                )
        self._tous = self._main_serveur.gestionnaire_joueurs.get_liste_joueurs(
            'dictateurEmotions')

        # pour configurer les clients et les remotes ~~~~~~~~~~~~~~~~~~~~~~~~~~~
        yield (self._main_serveur.gestionnaire_experience.run_func(
            self._tous, "configurer")
        )

        # On remplit la variable groupe_joueur dans la base
        for j in self._tous:
            j.DE_groupe_joueur = j.joueur.groupe
            j.DE_place_joueur_dans_groupe = self._main_serveur.gestionnaire_groupes.get_place_joueur_dans_groupe(j.joueur)
            
        # début de la partie ===================================================
        # en mettant la période à 0 les écrans n'afficheront pas période ...
        yield (self._main_serveur.gestionnaire_experience.run_func(
            self._tous, "nouvelle_periode", 0)
        )
        
        # Affichage ecran role seulement si TYPE_DICT = 0
        if parametres.TYPE_DICT == 0:
            yield (self._main_serveur.gestionnaire_experience.run_step(
                u"Role", self._tous, "afficher_ecran_role")
            )
        
        # décision ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        yield (self._main_serveur.gestionnaire_experience.run_step(
            u"Decision", self._tous, "afficher_ecran_decision")
        )
        
        # On enregistre les decision des joueurs A dans DE_recu des joueurs B 
        # Dans le cas TYPE_DICT = 0
        # le joueur 0 est associe avec le 2, le 1 avec le 3
        if parametres.TYPE_DICT == 0:
            for g, m in self._main_serveur.gestionnaire_groupes. \
            get_groupes("dictateurEmotions").iteritems():
                decision_joueurA1 = 0
                decision_joueurA2 = 0
                for j in m:
                    if j.DE_place_joueur_dans_groupe == 0:
                        decision_joueurA1 = j.DE_decision
                    if j.DE_place_joueur_dans_groupe == 1:
                        decision_joueurA2 = j.DE_decision
                for k in m:
                    if k.DE_place_joueur_dans_groupe == 2:
                        k.DE_recu = decision_joueurA1
                    if k.DE_place_joueur_dans_groupe == 3:
                        k.DE_recu = decision_joueurA2                    
      
        
        # calcul des gains de la période ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self._main_serveur.gestionnaire_experience.calculer_gains_periode(
            "dictateurEmotions")
    
        # affichage du récapitulatif ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        yield (self._main_serveur.gestionnaire_experience.run_step(
            u"Récapitulatif", self._tous, "afficher_ecran_recapitulatif")
        )
        
        # FIN DE LA PARTIE =====================================================
        self._main_serveur.gestionnaire_experience.finaliser_partie(
            "dictateurEmotions")
