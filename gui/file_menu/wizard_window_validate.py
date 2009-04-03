from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *

import sys, os, re
import newproject
from database.createDBConnection import createDBC
from intro_page import IntroPage
from resolution_page import ResolutionPage
from sample_page import SampleDataPage
from control_page import ControlDataPage
from dbconnection_page import DBConnectionPage
from summary_page import SummaryPage
from misc.errors import *
from misc.widgets import *
import results_menu.dbf as dbf



class Wizard(QWizard):
    def __init__(self, parent=None):
        super(Wizard, self).__init__(parent)
        self.project = newproject.NewProject()
        self.setFixedSize(QSize(800,500))
        self.setWizardStyle(QWizard.ClassicStyle)

        self.selectedCounties = None
        self.page1 = IntroPage()
        self.addPage(self.page1)
        self.page2 = ResolutionPage()
        self.addPage(self.page2)
        self.page3 = SampleDataPage()
        self.addPage(self.page3)
        self.page4 = ControlDataPage()
        self.addPage(self.page4)
        self.page5 = DBConnectionPage()
        self.addPage(self.page5)
        self.page6 = SummaryPage()
        self.addPage(self.page6)

        self.setWindowTitle("New Project Wizard")

        self.connect(self.button(QWizard.CancelButton), SIGNAL("pressed()"), self.reject)
        self.connect(self, SIGNAL("currentIdChanged(int)"), self.update)
        

    def reject(self):
        reply = QMessageBox.question(None, "PopSim: New Project Wizard",
                                     QString("Do you wish to continue?"),
                                     QMessageBox.Yes| QMessageBox.No)
        if reply == QMessageBox.Yes:
            QWizard.reject(self)


    def update(self, id):
        
        if id == 5:
            geocorrLocation = self.page2.geocorrLocationComboBox.currentText()
            geocorrUserProv = newproject.Geocorr(self.page2.geocorrUserProvRadio.isChecked(),
                                                 geocorrLocation)
            
            sampleHHLocation = self.page3.sampleHHLocationComboBox.currentText()
            sampleGQLocation = self.page3.sampleGQLocationComboBox.currentText()
            samplePersonLocation = self.page3.samplePersonLocationComboBox.currentText()
            sampleUserProv = newproject.Sample(self.page3.sampleUserProvRadio.isChecked(),
                                               sampleHHLocation,
                                               sampleGQLocation,
                                               samplePersonLocation)

            controlHHLocation = self.page4.controlHHLocationComboBox.currentText()
            controlGQLocation = self.page4.controlGQLocationComboBox.currentText()
            controlPersonLocation = self.page4.controlPersonLocationComboBox.currentText()
            controlUserProv = newproject.Control(self.page4.controlUserProvRadio.isChecked(),
                                                 controlHHLocation,
                                                 controlGQLocation,
                                                 controlPersonLocation)
            
            db = newproject.DBInfo(self.page5.hostnameLineEdit.text(),
                                   self.page5.usernameLineEdit.text(),
                                   self.page5.passwordLineEdit.text(),
                                   "QMYSQL")


            self.project = newproject.NewProject(self.page1.nameLineEdit.text(),
                                                 self.page1.locationComboBox.currentText(),
                                                 self.page1.descTextEdit.toPlainText(),
                                                 self.page1.selectedCounties,
                                                 self.page2.resolutionComboBox.currentText(),
                                                 geocorrUserProv,
                                                 sampleUserProv,
                                                 controlUserProv,
                                                 db)

            region = {}
            if self.project.region is not None:
                for i in self.project.region:
                    region[i.text(0)] = i.parent().text(0)

            self.project.region = region
            self.page6.fillPage(self.project)



            self.page6.checkProjectLocation(self.project.location, self.project.name)
            self.page6.checkProjectDatabase(self.project.db, self.project.name)



    def accept(self):
        self.project.save()
        QWizard.accept(self)



def main():
    app = QApplication(sys.argv)
    QgsApplication.setPrefixPath(qgis_prefix, True)
    QgsApplication.initQgis()
    wiz = Wizard()
    wiz.show()
    app.exec_()
    QgsApplication.exitQgis()


if __name__ == "__main__":
    main()

