# -*- coding: utf-8 -*-
"""
Ce module contient les boites de dialogue du programme.
"""

from PyQt4 import QtGui, QtCore
import logging
import random

from le2mClient.le2mClientGui.le2mClientGuiDialogs import GuiHistorique
import le2mClient.le2mClientTextes as textes_main

import dictateurEmotionsParametres as parametres
import dictateurEmotionsTextes as textes
from dictateurEmotionsGuiSrc import dictateurEmotionsGuiSrcDecision
from dictateurEmotionsGuiSrc import dictateurEmotionsGuiSrcRole

logger = logging.getLogger("le2m.{}".format(__name__))

class GuiRole(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, periode, historique, le_role):
        super(GuiRole, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique
        self._historique = GuiHistorique(self, historique)
        self.le_role = le_role

        # création gui
        self.ui = dictateurEmotionsGuiSrcRole.Ui_Dialog()
        self.ui.setupUi(self)

        # periode et historique
#        if periode:
#            self.ui.label_periode.setText(textes_main.PERIODE_label(periode))
#            self.ui.pushButton_historique.setText(textes_main.HISTORIQUE_bouton)
#            self.ui.pushButton_historique.clicked.connect(
#                self._historique.show
#            )
#        else:
#            self.ui.label_periode.setVisible(False)
#            self.ui.pushButton_historique.setVisible(False)
        self.ui.label_periode.setVisible(False)
        self.ui.pushButton_historique.setVisible(False)
        
        # Explication
        if le_role == 0:
            self.ui.textEdit_role.setText(textes.ROLE_JOUEUR_A)
            self.ui.textEdit_role.setReadOnly(True)
            self.ui.textEdit_role.setFixedSize(400, 80)
        else:
            self.ui.textEdit_role.setText(textes.ROLE_JOUEUR_B)
            self.ui.textEdit_role.setReadOnly(True)
            self.ui.textEdit_role.setFixedSize(400, 80)
            
        # bouton box
        self.ui.buttonBox.accepted.connect(self._accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setVisible(False)

        # titre et taille
#        self.setWindowTitle(textes.DECISION_titre)
        self.setFixedSize(520, 320)

        # automatique
        if self._automatique:
            self._timer_automatique = QtCore.QTimer()
            self._timer_automatique.timeout.connect(self._accept)
            self._timer_automatique.start(7000)
                
    def reject(self):
        pass
    
    def _accept(self):
        try:
            self._timer_automatique.stop()
        except AttributeError:
            pass
#        if not self._automatique:
#            confirmation = QtGui.QMessageBox.question(
#                self, textes.DECISION_confirmation.titre,
#                textes.DECISION_confirmation.message,
#                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes
#            )
#            if confirmation != QtGui.QMessageBox.Yes: 
#                return
        role = self.le_role
        self._defered.callback(role)
        self.accept()

class GuiDecision(QtGui.QDialog):
    def __init__(self, defered, automatique, parent, periode, historique):
        super(GuiDecision, self).__init__(parent)

        # variables
        self._defered = defered
        self._automatique = automatique
        self._historique = GuiHistorique(self, historique)

        # création gui
        self.ui = dictateurEmotionsGuiSrcDecision.Ui_Dialog()
        self.ui.setupUi(self)

        # periode et historique
#        if periode:
#            self.ui.label_periode.setText(textes_main.PERIODE_label(periode))
#            self.ui.pushButton_historique.setText(textes_main.HISTORIQUE_bouton)
#            self.ui.pushButton_historique.clicked.connect(
#                self._historique.show
#            )
#        else:
#            self.ui.label_periode.setVisible(False)
#            self.ui.pushButton_historique.setVisible(False)
        self.ui.label_periode.setVisible(False)
        self.ui.pushButton_historique.setVisible(False)

        # Explication
        if parametres.TYPE_DICT == 0:
            self.ui.textEdit_explication.setText(textes.DECISION_explication)
        else:
            self.ui.textEdit_explication.setText(textes.DECISION_explication_assoc)
        self.ui.textEdit_explication.setReadOnly(True)
        self.ui.textEdit_explication.setFixedSize(400, 80)

        # Décision
        self.ui.label_decision.setText(textes.DECISION_label)
        self.ui.spinBox_decision.setMinimum(parametres.DECISION_MIN)
        self.ui.spinBox_decision.setMaximum(parametres.DECISION_MAX)
        self.ui.spinBox_decision.setSingleStep(parametres.DECISION_STEP)
        self.ui.spinBox_decision.setValue(self.ui.spinBox_decision.minimum())

        # bouton box
        self.ui.buttonBox.accepted.connect(self._accept)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setVisible(False)

        # titre et taille
        self.setWindowTitle(textes.DECISION_titre)
        self.setFixedSize(520, 320)

        # automatique
        if self._automatique:
            self.ui.spinBox_decision.setValue(random.randrange(0, parametres.DOTATION))
            self._timer_automatique = QtCore.QTimer()
            self._timer_automatique.timeout.connect(self._accept)
            self._timer_automatique.start(7000)
                
    def reject(self):
        pass
    
    def _accept(self):
        try:
            self._timer_automatique.stop()
        except AttributeError:
            pass
        decision = self.ui.spinBox_decision.value()
        if not self._automatique:
            confirmation = QtGui.QMessageBox.question(
                self, textes.DECISION_confirmation.titre,
                textes.DECISION_confirmation.message,
                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes
            )
            if confirmation != QtGui.QMessageBox.Yes: 
                return
        self._defered.callback(decision)
        self.accept()
