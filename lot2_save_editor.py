# -*- coding: utf-8 -*-

'''
東方記偽器　～　Artificial Record
By Doctus (kirikayuumura.noir@gmail.com)

	A LoT2 save editor.

    東方記偽器　～　Artificial Record is free software: you can
    redistribute it and/or modify it under the terms of the GNU General
    Public License as published by the Free Software Foundation, either
    version 3 of the License, or (at your option) any later version.

    RandomGameGenerator is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty
    of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with 東方記偽器　～　Artificial Record.  If not, see
    <http://www.gnu.org/licenses/>.
'''

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import os

EDITOR_TITLE = u"東方記偽器　～　Artificial Record v1.00"

CHARACTER_NAMES = ["Reimu", "Marisa", "Rinnosuke", "Keine",
					"Momiji", "Youmu", "Kogasa", "Rumia",
					"Cirno", "Minoriko", "Komachi", "Chen",
					"Nitori", "Parsee", "Wriggle", "Kaguya",
					"Mokou", "Aya", "Mystia", "Kasen",
					"Nazrin", "Hina", "Rin", "Okuu",
					"Satori", "Yuugi", "Meiling", "Alice",
					"Patchouli", "Eirin", "Reisen", "Sanae",
					"Iku", "Suika", "Ran", "Remilia",
					"Sakuya", "Kanako", "Suwako", "Tenshi",
					"Flandre", "Yuyuko", "Yuuka", "Yukari",
					"Byakuren", "Eiki", "Renko", "Maribel"]

SUBCLASSES = ["Guardian", "Monk", "Warrior", "Sorcerer",
				"Healer", "Enhancer", "Hexer", "Toxicologist",
				"Magician", "Herbalist", "Strategist",
				"Gambler", "Diva", "Transcendant"]

STAT_ORDER = ["LEVEL", "EXPERIENCE", "SKILLPOINTS",
				"LEVELPOINTS", "BATTLEPOINTS"]
LEVEL_BONUS_ORDER = ["HP", "ATTACK", "DEFENSE",
						"MAGIC", "MIND", "SPEED"]
LIBRARY_STAT_ORDER = ["HP", "ATTACK", "DEFENSE", "MAGIC",
						"MIND", "SPEED", "FIRE", "COLD",
						"WIND", "NATURE", "MYSTIC", "SPIRIT",
						"DARK", "PHYSICAL"]
GENERAL_STUFF_ORDER = ["TIME", "MONEY", "BATTLES"]

GENERAL_MEM_STRUCT = {"TIME": [4, 2],
						"MONEY": [13, 3],
						"BATTLES": [17, 1]}

CHAR_MEM_STRUCT = {"LEVEL": 3,
					"EXPERIENCE": 11,
					"LIBRARY":
						{"HP": 15,
						"ATTACK": 19,
						"DEFENSE": 23,
						"MAGIC": 27,
						"MIND": 31,
						"SPEED": 35,
						"FIRE": 39,
						"COLD": 43,
						"WIND": 47,
						"NATURE": 51,
						"MYSTIC": 55,
						"SPIRIT": 59,
						"DARK": 63,
						"PHYSICAL": 67},
					"LEVELUP":
						{"HP": 71,
						"ATTACK": 75,
						"DEFENSE": 79,
						"MAGIC": 83,
						"MIND": 87,
						"SPEED": 91},
					"SUBCLASS":95,
					#"SKILLS": 0x60 ~ 0xEA
					"SKILLPOINTS": 238,
					"LEVELPOINTS": 243,
					"BATTLEPOINTS": 264
					}

class HexDataContainer(object):

	def __init__(self, hexData):
		self._hexData = [byte for byte in hexData]

	@property
	def hexData(self):
		return "".join(["%c" % byte for byte in self._hexData])

	def _value(self, address, limit):
		return sum([self._hexData[address-i] * (0x100**i) for i in range(limit)])

	def bigValue(self, address):
		return self._value(address, 6)

	def value(self, address, limit=4):
		return self._value(address, limit)

	def singleValue(self, address):
		return self._hexData[address]

	def bigPoke(self, address, newValue):
		if newValue <= 0xFFFFFFFFFFFF:
			self._hexData[address] = "%c" % (newValue % 0x100)
			if newValue > 0xFF:
				self._hexData[address-1] = "%c" % ((newValue / 0x100) % 0x100)
			if newValue > 0xFFFF:
				self._hexData[address-2] = "%c" % ((newValue / 0x10000) % 0x100)
			if newValue > 0xFFFFFF:
				self._hexData[address-3] = "%c" % ((newValue / 0x1000000) % 0x100)
			if newValue > 0xFFFFFFFF:
				self._hexData[address-4] = "%c" % ((newValue / 0x100000000) % 0x100)
			if newValue > 0xFFFFFFFFFF:
				self._hexData[address-5] = "%c" % (newValue / 0x10000000000)
		else:
			self.errorDialog = QErrorMessage(self)
			self.errorDialog.showMessage("Value too large!", "overflow")

	def poke(self, address, newValue, limit=3):
		if newValue <= 0xFF:
			self._hexData[address] = "%c" % newValue
		elif newValue <= 0xFFFFFFFF:
			self._hexData[address] = "%c" % (newValue % 0x100)
			if newValue > 0xFF and limit >= 1:
				self._hexData[address-1] = "%c" % ((newValue / 0x100) % 0x100)
			if newValue > 0xFFFF and limit >= 2:
				self._hexData[address-2] = "%c" % ((newValue / 0x10000) % 0x100)
			if newValue > 0xFFFFFF and limit >= 3:
				self._hexData[address-3] = "%c" % (newValue / 0x1000000)
		else:
			self.errorDialog = QErrorMessage(self)
			self.errorDialog.showMessage("Value too large!", "overflow")

class SubclassPicker(QComboBox):

	def __init__(self, *args, **kwargs):
		super(SubclassPicker, self).__init__(*args, **kwargs)
		self.addItem("(None)")
		for subclass in SUBCLASSES:
			self.addItem(subclass)

	def setValue(self, value):
		if value > 0:
			self.setCurrentIndex(value-99)
		else:
			self.setCurrentIndex(0)

class CharacterEditWidget(QWidget):

	def __init__(self, characterName, characterData, recruited, *args, **kwargs):
		super(CharacterEditWidget, self).__init__(*args, **kwargs)
		self.data = characterData
		self.layout = QGridLayout()
		recruitedLabel = QCheckBox("Recruited")
		recruitedLabel.setChecked(recruited)
		recruitedLabel.setEnabled(False)
		charNameLabel = QLabel(characterName)
		self.layout.addWidget(charNameLabel, 0, 0, 1, 3)
		self.layout.addWidget(recruitedLabel, 0, 3)
		bigFont = QFont()
		bigFont.setPointSize(16)
		bigFont.setBold(True)
		underlineFont = QFont()
		underlineFont.setUnderline(True)
		charNameLabel.setFont(bigFont)
		baseLabel = QLabel("Base")
		libraryLabel = QLabel("Library")
		levelupLabel = QLabel("Level Bonus")
		baseLabel.setFont(underlineFont)
		libraryLabel.setFont(underlineFont)
		levelupLabel.setFont(underlineFont)
		self.layout.addWidget(baseLabel, 1, 0, 1, 2)
		self.layout.addWidget(libraryLabel, 1, 2, 1, 2)
		self.layout.addWidget(levelupLabel, 1, 4, 1, 2)
		for i, stat in enumerate(STAT_ORDER):
			self.layout.addWidget(QLabel(stat + ":"), i+2, 0)
			spinbox = QSpinBox()
			spinbox.setMaximum(2147483647)
			if stat != "EXPERIENCE":
				spinbox.setValue(self.data.value(CHAR_MEM_STRUCT[stat]))
				spinbox.valueChanged.connect(self.pokeValue(self.data, CHAR_MEM_STRUCT[stat]))
			else:
				spinbox.setValue(self.data.bigValue(CHAR_MEM_STRUCT[stat]))
				spinbox.valueChanged.connect(self.pokeValue(self.data, CHAR_MEM_STRUCT[stat], True))
			self.layout.addWidget(spinbox, i+2, 1)
		self.layout.addWidget(QLabel("SUBCLASS:"), len(STAT_ORDER)+2, 0)
		subclass = SubclassPicker()
		subclass.setValue(self.data.value(CHAR_MEM_STRUCT["SUBCLASS"]))
		subclass.currentIndexChanged.connect(self.pokeSubclass)
		self.layout.addWidget(subclass, len(STAT_ORDER)+2, 1)
		for i, libraryUp in enumerate(LIBRARY_STAT_ORDER):
			self.layout.addWidget(QLabel(libraryUp + ":"), i+2, 2)
			spinbox = QSpinBox()
			spinbox.setMaximum(2147483647)
			spinbox.setValue(self.data.value(CHAR_MEM_STRUCT["LIBRARY"][libraryUp]))
			spinbox.valueChanged.connect(self.pokeValue(self.data, CHAR_MEM_STRUCT["LIBRARY"][libraryUp]))
			self.layout.addWidget(spinbox, i+2, 3)
		for i, stat in enumerate(LEVEL_BONUS_ORDER):
			self.layout.addWidget(QLabel(stat + ":"), i+2, 4)
			spinbox = QSpinBox()
			spinbox.setMaximum(2147483647)
			spinbox.setValue(self.data.value(CHAR_MEM_STRUCT["LEVELUP"][stat]))
			spinbox.valueChanged.connect(self.pokeValue(self.data, CHAR_MEM_STRUCT["LEVELUP"][stat]))
			self.layout.addWidget(spinbox, i+2, 5)
		self.setLayout(self.layout)

	def pokeSubclass(self, value):
		if value > 0:
			value = value + 99
		self.data.poke(CHAR_MEM_STRUCT["SUBCLASS"], value)

	def pokeValue(self, dataContainer, address, big=False):
		if not big:
			def pokeValueFunc(value):
				dataContainer.poke(address, value)
			return pokeValueFunc
		else:
			def pokeValueFunc(value):
				dataContainer.bigPoke(address, value)
			return pokeValueFunc

	@property
	def hexData(self):
		return self.data.hexData

class CharacterDataTab(QWidget):

	def __init__(self, basePath, *args, **kwargs):
		super(CharacterDataTab, self).__init__(*args, **kwargs)
		self.basePath = basePath
		self.characterData = {}
		self.layout = QGridLayout()
		self.layout.setColumnStretch(2, 10)
		self.liste = QListWidget()
		self.stack = QStackedWidget()
		recruitmentData = self.loadRecruitmentData(basePath)
		for index, charName in enumerate(CHARACTER_NAMES):
			data = self.loadCharacterData(index+1, charName, basePath)
			if data is not None:
				self.liste.addItem(charName)
				self.stack.addWidget(CharacterEditWidget(charName, data, recruitmentData.singleValue(index+1)))
		self.layout.addWidget(self.liste, 0, 0, 2, 1)
		self.layout.addWidget(self.stack, 0, 1)
		self.stack.setSizePolicy(QSizePolicy())
		self.setLayout(self.layout)
		self.liste.currentRowChanged.connect(self.stack.setCurrentIndex)

	def loadRecruitmentData(self, basePath):
		try:
			with open(os.path.join(basePath, "PCF01.ngd"), "rb") as f:
				data = f.read()
		except:
			self.errorDialog = QErrorMessage(self)
			self.errorDialog.showMessage("Error reading character recruitment file. SAVING NOT RECOMMENDED. YOUR SAVE MAY BE (FURTHER) CORRUPTED.", "recruitmentFileRead")
		else:
			return HexDataContainer(data)

	def loadCharacterData(self, index, characterName, basePath):
		try:
			with open(os.path.join(basePath, "C%02i.ngd" % index), "rb") as f:
				data = f.read()
		except:
			self.errorDialog = QErrorMessage(self)
			self.errorDialog.showMessage("Error reading character file: %s. SAVING NOT RECOMMENDED. YOUR SAVE MAY BE (FURTHER) CORRUPTED." % characterName, "charFileRead")
		else:
			return HexDataContainer(data)

	def _saveCharacterData(self, index, data, basePath):
		with open(os.path.join(basePath, "C%02i.ngd" % index), "wb") as f:
			f.write(data)

	def saveCharacterData(self):
		for index, charName in enumerate(CHARACTER_NAMES):
			self._saveCharacterData(index+1, self.stack.widget(index).hexData, self.basePath)

class MiscDataTab(QWidget):

	def __init__(self, basePath, *args, **kwargs):
		super(MiscDataTab, self).__init__(*args, **kwargs)
		self.basePath = basePath
		self.data = self.loadGeneralData(basePath)
		self.layout = QGridLayout()
		self.layout.setColumnStretch(2, 10)
		self.layout.setRowStretch(len(GENERAL_STUFF_ORDER), 10)
		for i, stat in enumerate(GENERAL_STUFF_ORDER):
			self.layout.addWidget(QLabel(stat + ":"), i, 0)
			spinbox = QSpinBox()
			spinbox.setMaximum(2147483647)
			memdata = GENERAL_MEM_STRUCT[stat]
			spinbox.setValue(self.data.value(memdata[0], memdata[1]+1))
			spinbox.valueChanged.connect(self.pokeValue(self.data, *memdata))
			self.layout.addWidget(spinbox, i, 1)
		self.setLayout(self.layout)

	def pokeValue(self, dataContainer, address, limit):
		def pokeValueFunc(value):
			dataContainer.poke(address, value, limit)
		return pokeValueFunc

	def loadGeneralData(self, basePath):
		try:
			with open(os.path.join(basePath, "SHD01.ngd"), "rb") as f:
				data = f.read()
		except:
			self.errorDialog = QErrorMessage(self)
			self.errorDialog.showMessage("Error reading general data file. SAVING NOT RECOMMENDED. YOUR SAVE MAY BE (FURTHER) CORRUPTED.", "recruitmentFileRead")
		else:
			return HexDataContainer(data)

	def saveGeneralData(self):
		with open(os.path.join(self.basePath, "SHD01.ngd"), "wb") as f:
			f.write(self.data.hexData)

class MainWidget(QWidget):

	def __init__(self, *args, **kwargs):
		super(MainWidget, self).__init__(*args, **kwargs)
		self.tabWidget = QTabWidget()
		self.characterTab = CharacterDataTab(basePath="save1")
		self.miscTab = MiscDataTab(basePath="save1")
		self.tabWidget.addTab(self.characterTab, "Characters")
		#self.tabWidget.addTab(QLabel("Inventory!"), "Inventory")
		self.tabWidget.addTab(self.miscTab, "Misc")
		self.tabWidget.addTab(QTextEdit("Fields currently limited to 2147483647 due to a Qt limitation I'm too lazy to circumvent. (Experience points above that limit won't be lost as long as you don't touch that character's experience field.)<br><br>Many addresses taken from Wymar's research after I noticed it existed. Thanks for the saved time and effort."), "About")
		bigFont = QFont()
		bigFont.setPointSize(16)
		self.saveButton = QPushButton("Save All Changes")
		self.saveButton.setFont(bigFont)
		self.saveButton.pressed.connect(self.saveEverything)
		self.layout = QGridLayout()
		self.layout.addWidget(self.tabWidget, 0, 0)
		self.layout.addWidget(self.saveButton, 1, 0)
		self.setLayout(self.layout)

	def saveEverything(self):
		self.characterTab.saveCharacterData()
		self.miscTab.saveGeneralData()

class MainWindow(QMainWindow):

	def __init__(self):
		QMainWindow.__init__(self)

		self.setObjectName("MainWindow")
		self.setWindowIcon(QIcon("logo.png"))
		self.setWindowTitle(EDITOR_TITLE)
		if os.path.exists("save1"):
			self.mainWidget = MainWidget()
			self.setCentralWidget(self.mainWidget)
		else:
			QMessageBox.critical(self, "ERROR: No save folder", "You must copy your chosen save folder (the folder, not just its contents) to this directory as 'save1'. After editing, delete the original folder and replace it with the edited one. Be sure to keep backups!")
			import sys
			sys.exit()

app = QApplication([EDITOR_TITLE])
main = MainWindow()
main.show()
app.exec_()
