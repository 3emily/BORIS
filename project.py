#!/usr/bin/env python3

"""
BORIS
Behavioral Observation Research Interactive Software
Copyright 2012-2016 Olivier Friard

This file is part of BORIS.

  BORIS is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 3 of the License, or
  any later version.

  BORIS is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not see <http://www.gnu.org/licenses/>.

"""

import logging
try:
    from PyQt5.QtGui import *
    from PyQt5.QtCore import *
    from PyQt5.QtWidgets import *
except:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *

import json

from config import *
from add_modifier import *
import dialog

if QT_VERSION_STR[0] == "4":
    from project_ui import Ui_dlgProject
else:
    from project_ui5 import Ui_dlgProject


class ExclusionMatrix(QDialog):

    def __init__(self):
        super(ExclusionMatrix, self).__init__()

        self.label = QLabel()
        self.label.setText("Check behaviors excluded by")

        self.twExclusions = QTableWidget()

        hbox = QVBoxLayout(self)

        hbox.addWidget(self.label)
        hbox.addWidget(self.twExclusions)

        self.pbOK = QPushButton("OK")
        self.pbOK.clicked.connect(self.pbOK_clicked)
        self.pbCancel = QPushButton("Cancel")
        self.pbCancel.clicked.connect(self.pbCancel_clicked)

        hbox2 = QHBoxLayout(self)

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hbox2.addItem(spacerItem)

        hbox2.addWidget(self.pbCancel)
        hbox2.addWidget(self.pbOK)

        hbox.addLayout(hbox2)

        self.setLayout(hbox)

        self.setWindowTitle("Behaviors exclusion matrix")

    def pbOK_clicked(self):
        self.accept()

    def pbCancel_clicked(self):
        self.reject()


class projectDialog(QDialog, Ui_dlgProject):

    def __init__(self, log_level, parent=None):

        super(projectDialog, self).__init__(parent)
        logging.basicConfig(level=log_level)

        self.setupUi(self)

        self.lbObservationsState.setText("")
        self.lbSubjectsState.setText("")

        # ethogram tab
        self.pbAddBehavior.clicked.connect(self.pbAddBehavior_clicked)
        self.pbCloneBehavior.clicked.connect(self.pb_clone_behavior_clicked)

        self.pbRemoveBehavior.clicked.connect(self.pbRemoveBehavior_clicked)
        self.pbRemoveAllBehaviors.clicked.connect(self.pbRemoveAllBehaviors_clicked)

        self.pbExclusionMatrix.clicked.connect(self.pbExclusionMatrix_clicked)

        self.pbImportBehaviorsFromProject.clicked.connect(self.pbImportBehaviorsFromProject_clicked)

        self.pbImportFromJWatcher.clicked.connect(self.pbImportFromJWatcher_clicked)
        self.pbImportFromTextFile.clicked.connect(self.pbImportFromTextFile_clicked)

        self.twBehaviors.cellChanged[int, int].connect(self.twBehaviors_cellChanged)
        self.twBehaviors.cellDoubleClicked[int, int].connect(self.twBehaviors_cellDoubleClicked)

        # left align table header
        for i in range(self.twBehaviors.columnCount()):
            self.twBehaviors.horizontalHeaderItem(i).setTextAlignment(Qt.AlignLeft)

        # subjects
        self.pbAddSubject.clicked.connect(self.pbAddSubject_clicked)
        self.pbRemoveSubject.clicked.connect(self.pbRemoveSubject_clicked)
        self.twSubjects.cellChanged[int, int].connect(self.twSubjects_cellChanged)

        self.pbImportSubjectsFromProject.clicked.connect(self.pbImportSubjectsFromProject_clicked)

        # independent variables tab
        self.pbAddVariable.clicked.connect(self.pbAddVariable_clicked)
        self.pbRemoveVariable.clicked.connect(self.pbRemoveVariable_clicked)
        self.twVariables.cellChanged[int, int].connect(self.twVariables_cellChanged)
        self.twVariables.cellDoubleClicked[int, int].connect(self.twVariables_cellDoubleClicked)

        self.pbImportVarFromProject.clicked.connect(self.pbImportVarFromProject_clicked)

        # observations
        self.pbRemoveObservation.clicked.connect(self.pbRemoveObservation_clicked)

        self.pbOK.clicked.connect(self.pbOK_clicked)
        self.pbCancel.clicked.connect(self.reject)


    def twBehaviors_cellDoubleClicked(self, row, column):

        # check if double click on coding map
        if column == behavioursFields["coding map"]:
            self.comboBoxChanged(row)

        if column == behavioursFields["modifiers"]:
            # check if behavior has coding map
            if self.twBehaviors.item(row, behavioursFields["coding map"]).text():
                QMessageBox.warning(self, programName, "Use the coding map to set/modify the areas")
            else:
                addModifierWindow = addModifierDialog(self.twBehaviors.item(row, column).text())
                addModifierWindow.setWindowTitle("""Set modifiers for "{}" behavior""".format(self.twBehaviors.item(row, 2).text()))
                if addModifierWindow.exec_():
                    self.twBehaviors.item(row, column).setText(addModifierWindow.getModifiers())


    def check_variable_default_value(self, txt, varType):
        """
        check if variable default value is compatible with variable type
        """
        # check for numeric type
        if varType == 0:  # numeric
            try:
                if txt:
                    float(txt)
                return True
            except:
                return False

        return True


    def variableTypeChanged(self, row):
        """
        variable type combobox changed
        """

        print("variable changed")
        print(self.twVariables.cellWidget(row, tw_indVarFields.index("type")).currentIndex())

        if self.twVariables.cellWidget(row, tw_indVarFields.index("type")).currentIndex() == SET_OF_VALUES_idx:
            if not self.twVariables.item(row, tw_indVarFields.index("possible values")).text():
                self.twVariables.item(row, tw_indVarFields.index("possible values")).setText("Double-click to add values")
                self.twVariables.item(row, tw_indVarFields.index("possible values")).setBackground(Qt.red)

        else:
            # check if set of values defined
            if self.twVariables.item(row, tw_indVarFields.index("possible values")).text():
                if dialog.MessageDialog(programName, "Erase the set of values?", [YES, CANCEL]) == CANCEL:
                    self.twVariables.cellWidget(row, tw_indVarFields.index("type")).setCurrentIndex(SET_OF_VALUES_idx)
                    return
                else:
                    self.twVariables.item(row, tw_indVarFields.index("possible values")).setText("")

            # check compatibility between variable type and default value
            if not self.check_variable_default_value(self.twVariables.item(row, tw_indVarFields.index("default value")).text(),
                                                   self.twVariables.cellWidget(row, tw_indVarFields.index("type")).currentIndex()):
                QMessageBox.warning(self, programName + " - Independent variables error", "The default value ({0}) of variable <b>{1}</b> is not compatible with variable type".format(
                                    self.twVariables.item(row, tw_indVarFields.index("default value")).text(),
                                    self.twVariables.item(row, tw_indVarFields.index("label")).text()))


    def pbAddVariable_clicked(self):
        """
        add an independent variable
        """
        logging.debug("add an independent variable")

        self.twVariables.setRowCount(self.twVariables.rowCount() + 1)
        signalMapper = QSignalMapper(self)
        for idx, field in enumerate(tw_indVarFields):

            if field == "type":
                # add type combobox
                comboBox = QComboBox()
                comboBox.addItems([NUMERIC, TEXT, SET_OF_VALUES])
                comboBox.setCurrentIndex(NUMERIC_idx)
                self.twVariables.setCellWidget(self.twVariables.rowCount() - 1, idx, comboBox)
                signalMapper.setMapping(comboBox, self.twVariables.rowCount() - 1)
                comboBox.currentIndexChanged["int"].connect(signalMapper.map)
                signalMapper.mapped["int"].connect(self.variableTypeChanged)
            else:
                item = QTableWidgetItem("")
                self.twVariables.setItem(self.twVariables.rowCount() - 1, idx, item)
                if field == "possible values":
                    item.setFlags(Qt.ItemIsEnabled)



    def twVariables_cellDoubleClicked(self, row, column):

        # check if double click on coding map

        if column == tw_indVarFields.index("possible values"):
            if self.twVariables.cellWidget(row, tw_indVarFields.index("type")).currentIndex() == 2: # variable type: set of values
                text = self.twVariables.item(row, column).text()
                if text == "Double-click to add values":
                    text = ""
                newText, ok = QInputDialog.getText(self, "Independent variable", "Possible values: (comma separated)", QLineEdit.Normal, text)
                if ok:
                    if newText:
                        newText = ",".join([x.strip() for x in newText.split(",")])
                        self.twVariables.item(row, column).setText(newText)
                        self.twVariables.item(row, column).setBackground(self.twVariables.item(row, column - 1).background())
                    else:
                        self.twVariables.item(row, column).setText("Double-click to add values")
                        self.twVariables.item(row, column).setBackground(Qt.red)



    def pbRemoveVariable_clicked(self):
        """
        remove the selected independent variable
        """
        logging.debug("remove selected independent variable")

        if not self.twVariables.selectedIndexes():
            QMessageBox.warning(self, programName, "First select a variable to remove")
        else:
            if dialog.MessageDialog(programName, "Remove the selected variable?", [YES, CANCEL]) == YES:
                self.twVariables.removeRow(self.twVariables.selectedIndexes()[0].row())

    def pbImportVarFromProject_clicked(self):
        """
        import independent variables from another project
        """

        if QT_VERSION_STR[0] == "4":
            fileName = QFileDialog(self).getOpenFileName(self, "Import independent variables from project file", "", "Project files (*.boris);;All files (*)")
        else:
            fileName, _ = QFileDialog(self).getOpenFileName(self, "Import independent variables from project file", "", "Project files (*.boris);;All files (*)")
        if fileName:

            with open(fileName, "r") as infile:
                s = infile.read()

            try:
                project = json.loads(s)
            except:
                QMessageBox.warning(None, programName, "Error while reading independent variables from selected file", QMessageBox.Ok | QMessageBox.Default, QMessageBox.NoButton)
                return

            # independent variables
            if project[INDEPENDENT_VARIABLES]:

                # check if variables are already present
                if self.twVariables.rowCount():

                    response = dialog.MessageDialog(programName, "There are independent variables already configured. Do you want to append independent variables or replace them?", ['Append', 'Replace', CANCEL])

                    if response == 'Replace':
                        self.twVariables.setRowCount(0)

                    if response == CANCEL:
                        return

                for i in sorted(project[INDEPENDENT_VARIABLES].keys()):

                    self.twVariables.setRowCount(self.twVariables.rowCount() + 1)

                    for idx, field in enumerate(tw_indVarFields):

                        item = QTableWidgetItem()

                        if field == 'type':

                            comboBox = QComboBox()
                            comboBox.addItem(NUMERIC)
                            comboBox.addItem(TEXT)
                            if project[INDEPENDENT_VARIABLES][i][field] == NUMERIC:
                                comboBox.setCurrentIndex(0)
                            if project[INDEPENDENT_VARIABLES][i][field] == TEXT:
                                comboBox.setCurrentIndex(1)

                            self.twVariables.setCellWidget(self.twVariables.rowCount() - 1, idx, comboBox)

                        else:
                            item.setText(project[INDEPENDENT_VARIABLES][i][field])

                            self.twVariables.setItem(self.twVariables.rowCount() - 1, idx, item)

                self.twVariables.resizeColumnsToContents()

            else:
                QMessageBox.warning(self, programName, "No independent variables found in project")

    def pbImportSubjectsFromProject_clicked(self):
        """
        import subjects from another project
        """
        if QT_VERSION_STR[0] == "4":
            fileName = QFileDialog(self).getOpenFileName(self, "Import subjects from project file", "", "Project files (*.boris);;All files (*)")
        else:
            fileName, _ = QFileDialog(self).getOpenFileName(self, "Import subjects from project file", "", "Project files (*.boris);;All files (*)")

        if fileName:

            with open(fileName, "r") as infile:
                s = infile.read()

            try:
                project = json.loads(s)
            except:
                QMessageBox.warning(None, programName, "Error while reading subjects from selected file", QMessageBox.Ok | QMessageBox.Default, QMessageBox.NoButton)
                return

            # configuration of behaviours
            if project[SUBJECTS]:

                if self.twSubjects.rowCount():

                    response = dialog.MessageDialog(programName, 'There are subjects already configured. Do you want to append subjects or replace them?', ['Append', 'Replace', 'Cancel'])

                    if response == 'Replace':
                        self.twSubjects.setRowCount(0)

                    if response == CANCEL:
                        return

                for idx in sorted(project[SUBJECTS].keys()):

                    self.twSubjects.setRowCount(self.twSubjects.rowCount() + 1)

                    for idx2, sbjField in enumerate(subjectsFields):

                        if sbjField in project[SUBJECTS][idx]:
                            self.twSubjects.setItem(self.twSubjects.rowCount() - 1, idx2, QTableWidgetItem(project[SUBJECTS][idx][sbjField]))
                        else:
                            self.twSubjects.setItem(self.twSubjects.rowCount() - 1, idx2, QTableWidgetItem(''))

                self.twSubjects.resizeColumnsToContents()
            else:
                QMessageBox.warning(self, programName, 'No subjects configuration found in project')

    def pbImportBehaviorsFromProject_clicked(self):
        """
        import behaviors from another project
        """

        if QT_VERSION_STR[0] == "4":
            fileName = QFileDialog(self).getOpenFileName(self, 'Import behaviors from project file', '', 'Project files (*.boris);;All files (*)')
        else:
            fileName, _ = QFileDialog(self).getOpenFileName(self, 'Import behaviors from project file', '', 'Project files (*.boris);;All files (*)')
        if fileName:

            with open(fileName, 'r') as infile:
                s = infile.read()

            try:
                project = json.loads(s)
            except:
                QMessageBox.warning(None, programName, 'Error while reading behaviors from selected file', QMessageBox.Ok | QMessageBox.Default, QMessageBox.NoButton)
                return

            # configuration of behaviours
            if project[ETHOGRAM]:

                if self.twBehaviors.rowCount():

                    response = dialog.MessageDialog(programName, 'There are behaviors already configured. Do you want to append behaviors or replace them?', ['Append', 'Replace', CANCEL])

                    if response == 'Replace':
                        self.twBehaviors.setRowCount(0)

                    if response == CANCEL:
                        return

                for i in sorted(project[ETHOGRAM].keys()):

                    self.twBehaviors.setRowCount(self.twBehaviors.rowCount() + 1)

                    for field in project[ETHOGRAM][i]:

                        item = QTableWidgetItem()

                        if field == 'type':

                            comboBox = QComboBox()
                            comboBox.addItems(observation_types)
                            comboBox.setCurrentIndex(observation_types.index(project[ETHOGRAM][i][field]))

                            self.twBehaviors.setCellWidget(self.twBehaviors.rowCount() - 1, fields[field], comboBox)

                        else:
                            item.setText(project[ETHOGRAM][i][field])

                            if field in ['excluded', 'coding map']:
                                item.setFlags(Qt.ItemIsEnabled)

                            self.twBehaviors.setItem(self.twBehaviors.rowCount() - 1, fields[field], item)

                self.twBehaviors.resizeColumnsToContents()

            else:
                QMessageBox.warning(self, programName, 'No behaviors configuration found in project')

    def pbExclusionMatrix_clicked(self):
        """
        activate exclusion matrix window
        """

        if not self.twBehaviors.rowCount():
            QMessageBox.warning(None, programName, "Behaviors list is empty!", QMessageBox.Ok | QMessageBox.Default, QMessageBox.NoButton)
            return

        ex = ExclusionMatrix()

        stateBehaviors, allBehaviors, excl, new_excl  = [], [], {}, {}

        includePointEvents = dialog.MessageDialog(programName, "Do you want to include point events?", [YES, NO])

        for r in range(0, self.twBehaviors.rowCount()):

            combobox = self.twBehaviors.cellWidget(r, 0)

            if self.twBehaviors.item(r, fields['code']):

                if includePointEvents == YES or (includePointEvents == NO and 'State' in observation_types[combobox.currentIndex()]):
                    allBehaviors.append(self.twBehaviors.item(r, fields['code']).text())

                excl[self.twBehaviors.item(r, fields['code']).text()] = self.twBehaviors.item(r, fields['excluded']).text().split(',')
                new_excl[self.twBehaviors.item(r, fields['code']).text()] = []

                if 'State' in observation_types[combobox.currentIndex()]:
                    stateBehaviors.append(self.twBehaviors.item(r, fields['code']).text())

        logging.debug('all behaviors: {}'.format(allBehaviors))
        logging.debug('stateBehaviors: {}'.format(stateBehaviors))

        if not stateBehaviors:
            QMessageBox.warning(None, programName, 'State events not found in behaviors list!', QMessageBox.Ok | QMessageBox.Default, QMessageBox.NoButton)
            return

        logging.debug('exclusion matrix {0}'.format(excl))

        # columns contain state events
        ex.twExclusions.setColumnCount(len(stateBehaviors))
        ex.twExclusions.setHorizontalHeaderLabels(stateBehaviors)

        # rows contains all events
        ex.twExclusions.setRowCount(len(allBehaviors))
        ex.twExclusions.setVerticalHeaderLabels(allBehaviors)

        for r in range(0, len(allBehaviors)):
            for c in range(0, len(stateBehaviors)):

                if stateBehaviors[c] != allBehaviors[r]:

                    checkBox = QCheckBox()

                    if stateBehaviors[c] in excl[allBehaviors[r]]:  # or headers[ r ] in excl[ headers[c] ]:

                        checkBox.setChecked(True)

                    ex.twExclusions.setCellWidget(r, c, checkBox)

        if ex.exec_():

            for r in range(0, len(allBehaviors)):
                for c in range(0, len(stateBehaviors)):

                    if stateBehaviors[c] != allBehaviors[r]:
                        checkBox = ex.twExclusions.cellWidget(r, c)
                        if checkBox.isChecked():

                            s1 = stateBehaviors[c]
                            s2 = allBehaviors[r]
                            '''
                            if not s2 in new_excl[s1]:
                                new_excl[s1].append(s2)

                            '''
                            if s1 not in new_excl[s2]:
                                new_excl[s2].append(s1)

            logging.debug('new exclusion matrix {0}'.format(new_excl))

            # update excluded field
            for r in range(0, self.twBehaviors.rowCount()):
                if includePointEvents == YES or (includePointEvents == NO and 'State' in observation_types[self.twBehaviors.cellWidget(r, 0).currentIndex()]):
                    for e in excl:
                        if e == self.twBehaviors.item(r, fields['code']).text():
                            item = QTableWidgetItem(','.join(new_excl[e]))
                            item.setFlags(Qt.ItemIsEnabled)
                            self.twBehaviors.setItem(r, fields['excluded'], item)

    def pbRemoveAllBehaviors_clicked(self):

        if self.twBehaviors.rowCount():

            response = dialog.MessageDialog(programName, "Remove all behaviors?", [YES, CANCEL])

            if response == YES:

                # extract all codes to delete
                codesToDelete = []
                row_mem = {}
                for r in range(self.twBehaviors.rowCount()-1, -1, -1):
                    if self.twBehaviors.item(r, 2).text():
                        codesToDelete.append(self.twBehaviors.item(r, 2).text())
                        row_mem[self.twBehaviors.item(r, 2).text()] = r

                # extract all codes used in observations
                codesInObs = []
                for obs in self.pj['observations']:
                    events = self.pj['observations'][obs]['events']
                    for event in events:
                        codesInObs.append(event[2])

                for codeToDelete in codesToDelete:
                    # if code to delete used in obs ask confirmation
                    if codeToDelete in codesInObs:
                        response = dialog.MessageDialog(programName, 'The code <b>{}</b> is used in observations!'.format(codeToDelete), ['Remove', CANCEL])
                        if response == 'Remove':
                            self.twBehaviors.removeRow(row_mem[codeToDelete])
                    else:   # remove without asking
                        self.twBehaviors.removeRow(row_mem[codeToDelete])

    def pbImportFromJWatcher_clicked(self):
        """
        import behaviors configuration from JWatcher (GDL file)
        """
        if self.twBehaviors.rowCount():
            response = dialog.MessageDialog(programName, "There are behaviors already configured. Do you want to append behaviors or replace them?", ['Append', 'Replace', CANCEL])
            if response == CANCEL:
                return

        if QT_VERSION_STR[0] == "4":
            fileName = QFileDialog(self).getOpenFileName(self, "Import behaviors from JWatcher", "", "Global Definition File (*.gdf);;All files (*)")
        else:
            fileName, _ = QFileDialog(self).getOpenFileName(self, "Import behaviors from JWatcher", "", "Global Definition File (*.gdf);;All files (*)")
        if fileName:

            if self.twBehaviors.rowCount() and response == 'Replace':
                self.twBehaviors.setRowCount(0)

            with open(fileName, 'r') as f:
                rows = f.readlines()

            for idx, row in enumerate(rows):
                if row and row[0] == '#':
                    continue

                if "Behavior.name." in row and "=" in row:
                    key, code = row.split('=')
                    key = key.replace("Behavior.name.", "")
                    # read description
                    if idx < len(rows) and "Behavior.description." in rows[idx+1]:
                        description = rows[idx+1].split('=')[-1]

                    behavior = {'key': key, 'code': code, 'description': description, 'modifiers': '', 'excluded': '', 'coding map': ''}

                    self.twBehaviors.setRowCount(self.twBehaviors.rowCount() + 1)

                    signalMapper = QSignalMapper(self)

                    for field_type in behavioursFields:
                        if field_type == TYPE:
                            # add type combobox
                            comboBox = QComboBox()
                            comboBox.addItems(observation_types)
                            comboBox.setCurrentIndex(0)   # event type from jwatcher not known
                            signalMapper.setMapping(comboBox, self.twBehaviors.rowCount() - 1)
                            comboBox.currentIndexChanged['int'].connect(signalMapper.map)
                            self.twBehaviors.setCellWidget(self.twBehaviors.rowCount() - 1, behavioursFields[field_type], comboBox)
                        else:
                            item = QTableWidgetItem(behavior[field_type])
                            if field_type in ["excluded", "coding map", "modifiers"]:
                                item.setFlags(Qt.ItemIsEnabled)
                            self.twBehaviors.setItem(self.twBehaviors.rowCount() - 1, behavioursFields[field_type], item)

                    signalMapper.mapped['int'].connect(self.comboBoxChanged)

    def check_text_file_type(self, rows):
        """
        check text file
        returns separator and number of fields (if unique)
        """
        separators = "\t,;"
        for separator in separators:
            cs = []
            for row in rows:
                cs.append(row.count(separator))
            if len(set(cs)) == 1:
                return separator, cs[0] + 1
        return None, None


    def pbImportFromTextFile_clicked(self):
        """
        import ethogram from text file
        ethogram must be organized like:
        typeOfBehavior separator key separator behaviorCode [separator description]

        """

        if self.twBehaviors.rowCount():
            response = dialog.MessageDialog(programName, "There are behaviors already configured. Do you want to append behaviors or replace them?", ['Append', 'Replace', CANCEL])
            if response == CANCEL:
                return

        if QT_VERSION_STR[0] == "4":
            fileName = QFileDialog(self).getOpenFileName(self, "Import behaviors from text file", "", "Text files (*.txt *.tsv *.csv);;All files (*)")
        else:
            fileName, _ = QFileDialog(self).getOpenFileName(self, "Import behaviors from text file", "", "Text files (*.txt *.tsv *.csv);;All files (*)")

        if fileName:

            if self.twBehaviors.rowCount() and response == 'Replace':
                self.twBehaviors.setRowCount(0)

            with open(fileName, "r") as f:
                rows = [r.strip() for r in f.readlines()]

            fieldSeparator, fieldsNumber = self.check_text_file_type(rows)

            logging.debug("fields separator: {}  fields number: {}".format(fieldSeparator, fieldsNumber))

            if fieldSeparator is None:
                QMessageBox.critical(self, programName, "Separator character not found! Use plain text file and TAB or comma as value separator")
            else:

                for row in rows:

                    type_, key, code, description = "", "", "", ""

                    if fieldsNumber == 3:  # fields: type, key, code
                        type_, key, code = row.split(fieldSeparator)
                        description = ""
                    if fieldsNumber == 4:  # fields:  type, key, code, description
                        type_, key, code, description = row.split(fieldSeparator)

                    if fieldsNumber > 4:
                        type_, key, code, description = row.split(fieldSeparator)[:4]

                    behavior = {"key": key, "code": code, "description": description, "modifiers": "", "excluded": "", "coding map": ""}

                    self.twBehaviors.setRowCount(self.twBehaviors.rowCount() + 1)

                    signalMapper = QSignalMapper(self)

                    for field_type in behavioursFields:
                        if field_type == TYPE:
                            # add type combobox
                            comboBox = QComboBox()
                            comboBox.addItems(observation_types)

                            if POINT in type_.upper():
                                comboBox.setCurrentIndex(0)
                            if STATE in type_.upper():
                                comboBox.setCurrentIndex(1)

                            signalMapper.setMapping(comboBox, self.twBehaviors.rowCount() - 1)
                            comboBox.currentIndexChanged["int"].connect(signalMapper.map)
                            self.twBehaviors.setCellWidget(self.twBehaviors.rowCount() - 1, behavioursFields[field_type], comboBox)
                        else:
                            item = QTableWidgetItem(behavior[field_type])
                            if field_type in ["excluded", "coding map", "modifiers"]:
                                item.setFlags(Qt.ItemIsEnabled)
                            self.twBehaviors.setItem(self.twBehaviors.rowCount() - 1, behavioursFields[field_type], item)

                    signalMapper.mapped['int'].connect(self.comboBoxChanged)



    def twBehaviors_cellChanged(self, row, column):

        keys, codes = [], []
        self.lbObservationsState.setText("")

        for r in range(0, self.twBehaviors.rowCount()):

            # check key
            if self.twBehaviors.item(r, fields["key"]):
                # check key length
                if self.twBehaviors.item(r, fields["key"]).text().upper() not in ['F' + str(i) for i in range(1, 13)] \
                   and len(self.twBehaviors.item(r, fields["key"]).text()) > 1:
                    self.lbObservationsState.setText("""<font color="red">Key length &gt; 1</font>""")
                    return

                keys.append(self.twBehaviors.item(r, fields["key"]).text())

                # convert to upper text
                self.twBehaviors.item(r, fields["key"]).setText(self.twBehaviors.item(r, fields["key"]).text().upper())

            # check code
            if self.twBehaviors.item(r, fields["code"]):
                if self.twBehaviors.item(r, fields["code"]).text() in codes:
                    self.lbObservationsState.setText("""<font color="red">Code duplicated at line {} </font>""".format(r + 1))
                else:
                    if self.twBehaviors.item(r, fields["code"]).text():
                        codes.append(self.twBehaviors.item(r, fields["code"]).text())

        # check subjects for key duplication
        '''
        for r in range(0, self.twSubjects.rowCount()):
            if self.twSubjects.item(r, fields["key"]):
                if self.twSubjects.item(r, fields["key"]).text() in keys:
                    self.lbObservationsState.setText("""<font color="red">Key found in subjects list at line {} </font>""".format(r + 1))
        '''


    def pb_clone_behavior_clicked(self):
        """
        clone the selected configuration
        """
        if not self.twBehaviors.selectedIndexes():
            QMessageBox.about(self, programName, "First select a behavior")
        else:
            self.twBehaviors.setRowCount(self.twBehaviors.rowCount() + 1)

            row = self.twBehaviors.selectedIndexes()[0].row()
            for field in fields:

                if field == "type":
                    item = QTableWidgetItem()
                    combobox = self.twBehaviors.cellWidget(row, 0)
                    index = combobox.currentIndex()

                    newComboBox = QComboBox()
                    newComboBox.addItems(observation_types)
                    newComboBox.setCurrentIndex(index)

                    self.twBehaviors.setCellWidget(self.twBehaviors.rowCount() - 1, 0, newComboBox)

                else:
                    item = QTableWidgetItem(self.twBehaviors.item(row, fields[field]))
                    self.twBehaviors.setItem(self.twBehaviors.rowCount() - 1, fields[field], item)

    def pbRemoveBehavior_clicked(self):
        """
        remove behavior
        """

        if not self.twBehaviors.selectedIndexes():
            QMessageBox.warning(self, programName, "First select a behaviour to remove")
        else:
            if dialog.MessageDialog(programName, "Remove the selected behavior?", [YES, CANCEL]) == YES:

                # check if behavior already used in observations

                codeToDelete = self.twBehaviors.item(self.twBehaviors.selectedIndexes()[0].row(), 2).text()

                codesInObs = []
                for obs in self.pj[OBSERVATIONS]:
                    events = self.pj[OBSERVATIONS][obs]['events']
                    for event in events:
                        codesInObs.append(event[2])

                if codeToDelete in codesInObs:
                    if dialog.MessageDialog(programName, 'The code to remove is used in observations!', [REMOVE, CANCEL]) == REMOVE:
                        self.twBehaviors.removeRow(self.twBehaviors.selectedIndexes()[0].row())

                else:
                    # code not used
                    self.twBehaviors.removeRow(self.twBehaviors.selectedIndexes()[0].row())

                self.twBehaviors_cellChanged(0, 0)


    def pbAddBehavior_clicked(self):
        """
        add a behavior
        """

        response = "Point event"

        # Add behavior to table
        self.twBehaviors.setRowCount(self.twBehaviors.rowCount() + 1)

        signalMapper = QSignalMapper(self)

        for field_type in fields:
            item = QTableWidgetItem()
            if field_type == TYPE:
                # add type combobox
                comboBox = QComboBox()
                comboBox.addItems(observation_types)
                comboBox.setCurrentIndex(observation_types.index(response))

                signalMapper.setMapping(comboBox, self.twBehaviors.rowCount() - 1)
                comboBox.currentIndexChanged['int'].connect(signalMapper.map)

                self.twBehaviors.setCellWidget(self.twBehaviors.rowCount() - 1, fields[field_type], comboBox)
            else:

                if field_type in ['excluded', 'coding map', 'modifiers']:
                    item.setFlags(Qt.ItemIsEnabled)

                self.twBehaviors.setItem(self.twBehaviors.rowCount() - 1, fields[field_type], item)

        signalMapper.mapped['int'].connect(self.comboBoxChanged)


    def comboBoxChanged(self, row):
        """
        event type combobox changed
        """

        combobox = self.twBehaviors.cellWidget(row, fields["type"])
        if "with coding map" in observation_types[combobox.currentIndex()]:
            # let user select a coding maop
            fd = QFileDialog(self)
            if QT_VERSION_STR[0] == "4":
                fileName = fd.getOpenFileName(self, 'Select a coding map for %s behavior' % self.twBehaviors.item(row, behavioursFields['code']).text(), '', 'BORIS map files (*.boris_map);;All files (*)')
            else:
                fileName, _ = fd.getOpenFileName(self, 'Select a coding map for %s behavior' % self.twBehaviors.item(row, behavioursFields['code']).text(), '', 'BORIS map files (*.boris_map);;All files (*)')

            if fileName:
                import json
                new_map = json.loads(open(fileName, 'r').read())
                self.pj['coding_map'][new_map['name']] = new_map

                # add modifiers from coding map codes
                modifStr = '|'.join(sorted(new_map['areas'].keys()))
                self.twBehaviors.item(row, behavioursFields['modifiers']).setText(modifStr)
                self.twBehaviors.item(row, behavioursFields['coding map']).setText(new_map['name'])

            else:
                # if coding map already exists do not reset the behavior type if no filename selected
                if not self.twBehaviors.item(row, behavioursFields['coding map']).text():
                    QMessageBox.critical(self, programName, 'No coding map was selected.\nEvent type will be reset to "Point event"')
                    self.twBehaviors.cellWidget(row, fields['type']).setCurrentIndex(0)
        else:
            self.twBehaviors.item(row, behavioursFields['modifiers']).setText('')
            self.twBehaviors.item(row, behavioursFields['coding map']).setText('')

    def pbAddSubject_clicked(self):
        """
        add a subject
        """

        self.twSubjects.setRowCount(self.twSubjects.rowCount() + 1)
        for col in range(0, len(subjectsFields)):
            item = QTableWidgetItem("")
            self.twSubjects.setItem(self.twSubjects.rowCount() - 1, col, item)

    def pbRemoveSubject_clicked(self):
        """
        remove selected subject from subjects list
        control before if subject used in observations
        """
        if not self.twSubjects.selectedIndexes():
            QMessageBox.warning(self, programName, "First select a subject to remove")
        else:

            if dialog.MessageDialog(programName, "Remove the selected subject?", [YES, CANCEL]) == YES:

                flagDel = False
                if self.twSubjects.item(self.twSubjects.selectedIndexes()[0].row(), 1):
                    subjectToDelete = self.twSubjects.item(self.twSubjects.selectedIndexes()[0].row(), 1).text()  # 1: subject name

                    subjectsInObs = []
                    for obs in self.pj['observations']:
                        events = self.pj['observations'][obs]['events']
                        for event in events:
                            subjectsInObs.append(event[1])  # 1: subject name
                    if subjectToDelete in subjectsInObs:
                        if dialog.MessageDialog(programName, "The subject to remove is used in observations!", [REMOVE, CANCEL]) == REMOVE:
                            flagDel = True
                    else:
                        # code not used
                        flagDel = True

                else:
                    flagDel = True

                if flagDel:
                    self.twSubjects.removeRow(self.twSubjects.selectedIndexes()[0].row())

                self.twSubjects_cellChanged(0,0)


    def twSubjects_cellChanged(self, row, column):
        """
        check if subject not unique
        """

        subjects, keys = [], []
        self.lbSubjectsState.setText("")

        for r in range(self.twSubjects.rowCount()):

            # check key
            if self.twSubjects.item(r, 0):

                # check key length
                if self.twSubjects.item(r, 0).text().upper() not in ["F" + str(i) for i in range(1, 13)] \
                   and len(self.twSubjects.item(r, 0).text()) > 1:
                    self.lbSubjectsState.setText("""<font color="red">Error on key {} for subject!</font> The key is too long (keys must be of one character except for function keys _F1, F2..._)""".format(self.twSubjects.item(r, 0).text()))
                    return

                if self.twSubjects.item(r, 0).text() in keys:
                    self.lbSubjectsState.setText("""<font color="red">Key duplicated at line # {}</font>""".format(r + 1))
                else:
                    if self.twSubjects.item(r, 0).text():
                        keys.append(self.twSubjects.item(r, 0).text())

                # convert to upper text
                self.twSubjects.item(r, 0).setText(self.twSubjects.item(r, 0).text().upper())

            # check subject
            if self.twSubjects.item(r, 1):
                if self.twSubjects.item(r, 1).text() in subjects:
                    self.lbSubjectsState.setText("""<font color="red">Subject duplicated at line # {}</font>""".format(r + 1))
                else:
                    if self.twSubjects.item(r, 1).text():
                        subjects.append(self.twSubjects.item(r, 1).text())

        # check behaviours keys
        '''
        for r in range(0, self.twBehaviors.rowCount()):
            # check key
            if self.twBehaviors.item(r, fields['key']):
                if self.twBehaviors.item(r, fields['key']).text() in keys:
                    self.lbSubjectsState.setText("""<font color="red">Key found in behaviours configuration ({}) at line # {} </font>""".format(self.twBehaviors.item(r, fields['key']).text(), r + 1))
        '''


    def twVariables_cellChanged(self, row, column):
        """
        check if variable default values are compatible with variable type
        """
        flagOK = True
        for r in range(self.twVariables.rowCount()):
            try:
                if not self.check_variable_default_value(self.twVariables.item(r, tw_indVarFields.index("default value")).text(),
                       self.twVariables.cellWidget(r, tw_indVarFields.index("type")).currentIndex()):
                    QMessageBox.warning(self, programName + " - Independent variables error", "The default value ({0}) of variable <b>{1}</b> is not compatible with variable type".format(self.twVariables.item(r, tw_indVarFields.index('default value')).text(), self.twVariables.item(r, tw_indVarFields.index('label')).text()))
                    flagOK = False
                    break
            except:
                pass

            try:
                if (self.twVariables.item(r, tw_indVarFields.index("default value")).text()
                and self.twVariables.item(r, tw_indVarFields.index("possible values")).text()
                and self.twVariables.item(r, tw_indVarFields.index("possible values")).text() != "Double-click to add values"):
                    if self.twVariables.item(r, tw_indVarFields.index("default value")).text() not in self.twVariables.item(r, tw_indVarFields.index("possible values")).text().split(","):
                        QMessageBox.warning(self, programName + " - Independent variables error", "The default value (<b>{0}</b>) of variable <b>{1}</b> is not in the set of accepted values".format(
                                            self.twVariables.item(r, tw_indVarFields.index("default value")).text(),
                                            self.twVariables.item(r, tw_indVarFields.index("label")).text()))
                        flagOK = False
                        break
            except:
                pass

        return flagOK

    def pbRemoveObservation_clicked(self):
        """
        remove first selected observation
        """

        if not self.twObservations.selectedIndexes():
            QMessageBox.warning(self, programName, 'First select an observation to remove')
        else:

            response = dialog.MessageDialog(programName, 'Are you sure to remove the selected observation?', [YES, CANCEL])

            if response == YES:

                obs_id = self.twObservations.item(self.twObservations.selectedIndexes()[0].row(), 0).text()

                del self.pj['observations'][obs_id]
                self.twObservations.removeRow(self.twObservations.selectedIndexes()[0].row())

    def pbOK_clicked(self):
        """
        verify behaviours and subjects configuration
        """

        if self.lbObservationsState.text():
            QMessageBox.warning(self, programName, self.lbObservationsState.text())
            return

        if self.lbSubjectsState.text():
            QMessageBox.warning(self, programName, self.lbSubjectsState.text())
            return

        # store subjects
        self.subjects_conf = {}

        for row in range(0, self.twSubjects.rowCount()):

            # check key
            if self.twSubjects.item(row, 0):
                key = self.twSubjects.item(row, 0).text()
            else:
                key = ""

            # check subject name
            if self.twSubjects.item(row, 1):
                subjectName = self.twSubjects.item(row, 1).text()
                if "|" in subjectName:
                    QMessageBox.warning(self, programName, "The pipe (|) character is not allowed in subject name <b>{}</b>".format(subjectName))
                    return

            else:
                QMessageBox.warning(self, programName, "Missing subject name in subjects configuration at row {}".format(row))
                return

            # description
            if self.twSubjects.item(row, 2):
                subjectDescription = self.twSubjects.item(row, 2).text()
            else:
                subjectDescription = ""

            self.subjects_conf[str(len(self.subjects_conf))] = {"key": key, "name": subjectName, "description": subjectDescription}

        # store behaviors
        missing_data = []

        self.obs = {}

        # coding maps in ethogram
        codingMapsList = []

        for r in range(0, self.twBehaviors.rowCount()):

            row = {}
            for field in fields:
                if field == 'type':
                    combobox = self.twBehaviors.cellWidget(r, fields['type'])
                    row[field] = observation_types[combobox.currentIndex()]
                else:
                    if self.twBehaviors.item(r, behavioursFields[field]):
                        # check for | char in code
                        if field == 'code' and '|' in self.twBehaviors.item(r, fields[field]).text():
                            QMessageBox.warning(self, programName, "The pipe (|) character is not allowed in code <b>%s</b> !" % self.twBehaviors.item(r, fields[field]).text())
                            return

                        row[field] = self.twBehaviors.item(r, fields[field]).text()
                    else:
                        row[field] = ''

            if (row['type']) and (row['key']) and (row['code']):

                self.obs[str(len(self.obs))] = row

            else:

                missing_data.append(str(r + 1))

            if self.twBehaviors.item(r, behavioursFields['coding map']).text():
                codingMapsList.append(self.twBehaviors.item(r, behavioursFields['coding map']).text())

        # remove coding map from project if not in ethogram
        cmToDelete = []
        for cm in self.pj['coding_map']:
            if cm not in codingMapsList:
                cmToDelete.append(cm)

        for cm in cmToDelete:
            del self.pj['coding_map'][cm]

        if missing_data:
            QMessageBox.warning(self, programName, "Missing data in behaviors configuration at row{} !".format(",".join(missing_data)))
            return

        # delete coding maps loaded in pj and not cited in ethogram
        '''
        for loadedCodingMap in loadedCodingMaps:
            del self.pj['coding_map'][ loadedCodingMap ]
        '''

        # independent variables

        # check if type compatible with predefined value
        if not self.twVariables_cellChanged(0, 0):
            return

        self.indVar = {}
        for r in range(self.twVariables.rowCount()):
            row = {}
            for idx, field in enumerate(tw_indVarFields):

                if field == "type":
                    combobox = self.twVariables.cellWidget(r, idx)
                    if combobox.currentIndex() == NUMERIC_idx:
                        row[field] = NUMERIC

                    if combobox.currentIndex() == TEXT_idx:
                        row[field] = TEXT

                    if combobox.currentIndex() == SET_OF_VALUES_idx:
                        row[field] = SET_OF_VALUES
                        if (not self.twVariables.item(r, tw_indVarFields.index("possible values")).text()
                             or self.twVariables.item(r, tw_indVarFields.index("possible values")).text() == "Double-click to add values"):
                            QMessageBox.warning(self, programName, "The set of values is not defined for variable <b>{}</b>!".format(self.twVariables.item(r, tw_indVarFields.index("label")).text()))
                            return

                else:
                    if self.twVariables.item(r, idx):
                        if field == "possible values":
                            if self.twVariables.cellWidget(r, tw_indVarFields.index("type")).currentIndex() == SET_OF_VALUES_idx:
                                row[field] = self.twVariables.item(r, idx).text()
                        else:
                            row[field] = self.twVariables.item(r, idx).text()
                    else:
                        row[field] = ""

            self.indVar[str(len(self.indVar))] = row

        self.accept()



