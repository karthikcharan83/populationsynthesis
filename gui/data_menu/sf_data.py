import urllib
import os

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
from database.createDBConnection import createDBC
from misc.errors import FileError
from misc.utils import UnzipFile
from import_data import ImportUserProvData, FileProperties

from global_vars import *


class UserImportControlData():
    def __init__(self, project):
        self.project = project
        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()
        self.query = QSqlQuery(self.projectDBC.dbc)


    def createHhldTable(self):
        hhldTableQuery = self.mysqlQueries('hhld_marginals', self.project.controlUserProv.hhLocation)

        if not self.query.exec_(hhldTableQuery.query1):
            raise FileError, self.query.lastError().text()

        if not self.query.exec_(hhldTableQuery.query2):
            raise FileError, self.query.lastError().text()

    def createGQTable(self):
        gqLocLen = len(self.project.controlUserProv.gqLocation)
        
        if gqLocLen > 1:
            gqTableQuery = self.mysqlQueries('gq_marginals', self.project.controlUserProv.gqLocation)

            if not self.query.exec_(gqTableQuery.query1):
                raise FileError, self.query.lastError().text()
            
            if not self.query.exec_(gqTableQuery.query2):
                raise FileError, self.query.lastError().text()

    def createPersonTable(self):
        personTableQuery = self.mysqlQueries('person_marginals', self.project.controlUserProv.personLocation)

        if not self.query.exec_(personTableQuery.query1):
            raise FileError, self.query.lastError().text()

        if not self.query.exec_(personTableQuery.query2):
            raise FileError, self.query.lastError().text()


    def mysqlQueries(self, name, filePath):
        # Generate the mysql queries to import the tables
        fileProp = FileProperties(filePath)
        fileQuery = ImportUserProvData(name, 
                                       filePath, 
                                       fileProp.varNames,
                                       fileProp.varTypes,
                                       fileProp.varNamesDummy, 
                                       fileProp.varTypesDummy)
        return fileQuery

class AutoImportSFData():
    def __init__(self, project):
        self.project = project
        self.state = self.project.state
        self.stateAbb = self.project.stateAbb
        self.stateCode = self.project.stateCode

        self.loc = DATA_DOWNLOAD_LOCATION + os.path.sep + self.state + os.path.sep + 'SF'
        self.loc = os.path.realpath(self.loc)
        
        self.countiesSelected = self.project.region.keys()

        self.projectDBC = createDBC(self.project.db, self.project.name)
        self.projectDBC.dbc.open()

        self.query = QSqlQuery(self.projectDBC.dbc)


        #self.rawSF = ['geo_uf3.zip',
        #              '00001_uf3.zip',
        #              '00004_uf3.zip',
        #              '00006_uf3.zip']
        self.rawSF = RAW_SUMMARY_FILES
        
        #self.rawSFNamesNoExt = ['geo',
        #                        '00001',
        #                        '00004',
        #                        '00006']
        self.rawSFNamesNoExt = RAW_SUMMARY_FILES_NOEXT

        self.downloadSFData()
        self.createRawSFTable()
        self.createMasterSFTable()


    def downloadSFData(self):
        try:
            os.makedirs(self.loc)
            self.retrieveAndStoreSF(self.state)
        except WindowsError, e:
            reply = QMessageBox.question(None, "PopSim: Processing Data",
                                         QString("""Windows Error: %s.\n\n"""
                                                 """Do you wish to keep existing files?"""
                                                 """\nPress No if you wish to download the files again."""%e),
                                         QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.No:
                confirm = QMessageBox.question(None, "PopSim: Processing Data",
                                               QString("""Are you sure you want to continue?"""),
                                               QMessageBox.Yes|QMessageBox.No)
                if confirm == QMessageBox.Yes:
                    self.retrieveAndStoreSF(self.state)
            #self.extractSF(self.state)


    def retrieveAndStoreSF(self, state):
        web_state = '%s' %state
        web_state = web_state.replace(' ', '_')
        for i in self.rawSF:
            sf_loc = self.loc + os.path.sep + '%s%s' %(self.stateAbb[state], i)
            urllib.urlretrieve("""http://www2.census.gov/census_2000/"""
                               """datasets/Summary_File_3/%s/%s%s""" %(web_state, self.stateAbb[state], i),
                               sf_loc)

    def extractSF(self, state):
        for i in self.rawSF:
            file = UnzipFile(self.loc, "%s%s" %(self.stateAbb[state],i))
            file.unzip()


    def createRawSFTable(self):
        # Create raw SF tables which can then be used to create the required summary file tables for use
        # population synthesis

        # First create the state geo table
        if not self.query.exec_("""create table %sgeo (raw text, sumlev int, sfgeoid int, """
                                """state text, county text, tract text, bg text, logrecno text)""" 
                                %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        geo_loc = self.loc + os.path.sep + '%sgeo.uf3' %(self.stateAbb[self.state])
        geo_loc = geo_loc.replace("\\", "/")
        if not self.query.exec_("""load data local infile '%s'"""
                                """ into table %sgeo (raw)""" %(geo_loc, self.stateAbb[self.state])):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""update %sgeo set sumlev = mid(raw, 9, 3)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""update %sgeo set sfgeoid = mid(raw, 19, 7)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""update %sgeo set state = mid(raw, 30, 2)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""update %sgeo set county = mid(raw, 32, 3)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""update %sgeo set tract = mid(raw, 56, 6)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""update %sgeo set bg = mid(raw, 62, 1)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""update %sgeo set logrecno = mid(raw, 19, 7)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""alter table %sgeo modify logrecno int""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_("""alter table %sgeo add primary key (logrecno)""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()

        # Load the other necessary tables
        sf3FilesTablesCorrTable = ImportUserProvData("sf3filestablescorr",
                                                     "./data/sf3filestablescorr.csv",
                                                     [], [], True, True)
        if not self.query.exec_(sf3FilesTablesCorrTable.query1):
            raise FileError, self.query.lastError().text()
        if not self.query.exec_(sf3FilesTablesCorrTable.query2):
            raise FileError, self.query.lastError().text()


        for j in self.rawSFNamesNoExt[1:]:
            variables, variabletypes = self.variableNames(j)
            filename = "%s%s" %(self.stateAbb[self.state], j)
            sf_loc = self.loc + os.path.sep + '%s.uf3' %(filename)
            sffile = ImportUserProvData(filename,
                                        sf_loc,
                                        variables, variabletypes, False, False)
            if not self.query.exec_(sffile.query1):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_(sffile.query2):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("alter table %s add primary key (logrecno)" %filename):
                raise FileError, self.query.lastError().text()


    def variableNames(self, filenumber = None, tablenumber = None):
        import copy
        variables = copy.deepcopy(RAW_SUMMARY_FILES_COMMON_VARS)
        variabletypes = copy.deepcopy(RAW_SUMMARY_FILES_COMMON_VARS_TYPE)

        filenumber = str(filenumber).rjust(5, '0')

        if tablenumber is None and filenumber is not None:
            if not self.query.exec_("""select tablenumber, numcat from sf3filestablescorr"""
                                    """ where filenumber = %s order by tablenumber""" %filenumber):
                raise FileError, self.query.lastError().text()
        if tablenumber is not None:
            if not self.query.exec_("""select tablenumber, numcat from sf3filestablescorr"""
                                    """ where tablenumber = %s""" %tablenumber):
                raise FIleError, self.query.lastError().text()
        if filenumber is None and tablenumber is None:
            raise FileError, "Insufficient parameters supplied"


        while self.query.next():
            tablenumber = str(self.query.value(0).toInt()[0]).rjust(3, '0')
            numcat = self.query.value(1).toInt()[0]
            for i in range(numcat):
                colname = 'P'+ tablenumber + str(i+1).rjust(3, '0')
                variables.append(colname)
                variabletypes.append('int')
                #print colname

        return variables, variabletypes


    def createMasterSFTable(self):
        import copy
        var1 = copy.deepcopy(MASTER_SUMMARY_FILE_VARS)
        var1string = self.createVariableString(var1)

        var1.remove('logrecno')
        var1.append('temp1.logrecno')
        
        if not self.query.exec_("""create table temp1 select %s from %sgeo""" 
                                %(var1string, self.stateAbb[self.state])):
            raise FileError, self.query.lastError().text()
        for j in self.rawSFNamesNoExt[1:]:
            var2, var2types = self.variableNames('%s' %j)
            var1 = var1 + var2[5:]
            var1string = self.createVariableString(var1)
            
            tablename = '%s%s' %(self.stateAbb[self.state], j)


            if not self.query.exec_("""create table temp2 select %s from temp1, %s"""
                                    """ where temp1.logrecno = %s.logrecno""" %(var1string, tablename, tablename)):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""drop table temp1"""):
                raise FileError, self.query.lastError().text()
            if not self.query.exec_("""alter table temp2 rename to temp1"""):
                raise FileError, self.query.lastError().text()
            
        if not self.query.exec_("""alter table temp1 rename to mastersftable_%s""" %self.stateAbb[self.state]):
            raise FileError, self.query.lastError().text()

    def createVariableString(self, variableList):
        variableString = ""
        for i in variableList:
            variableString = variableString + i + ", "
        return variableString[:-2]


    def createHousingSFTable(self):
        #HousingTables = [9, 10, 14, 52]
        HousingTables = HOUSING_SUMMARY_TABLES

        import copy
        var = copy.deepcopy(MASTER_SUMMARY_FILE_VARS)

        for i in HousingTables:
            var1, var1types = self.variableNames(tablenumber = i)
            var = var + var1[5:]

        varstring = self.createVariableString(var)

        if not self.query.exec_("""create table housing_marginals_%s select %s from mastersftable_%s"""
                                %(self.stateAbb[self.state], varstring, self.stateAbb[self.state])):
            raise FileError, self.query.lastError().text()

    def createPersonSFTable(self):
        #PersonTables = [6, 8, 43]
        PersonTables = PERSON_SUMMARY_TABLES
        
        import copy
        var = copy.deepcopy(MASTER_SUMMARY_FILE_VARS)
        #var = ['state', 'county', 'tract', 'bg', 'sumlev', 'logrecno']

        for i in PersonTables:
            var1, var1types = self.variableNames(tablenumber = i)
            var = var + var1[5:]

        varstring = self.createVariableString(var)

        if not self.query.exec_("""create table person_marginals_%s select %s from mastersftable_%s"""
                                %(self.stateAbb[self.state], varstring, self.stateAbb[self.state])):
            raise FileError, self.query.lastError().text()