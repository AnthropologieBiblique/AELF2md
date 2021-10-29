import re
import fileinput
import os
import csv
import markdownify

class Bible:
	def __init__(self,name,unbound_name,abbrev,NRSVA_mapping,hebraic):
		self.name = name
		self.unbound_name = unbound_name
		self.abbrev = abbrev
		self.NRSVA_mapping = NRSVA_mapping
		self.hebraic = hebraic
		self.booksNames = {}
		self.booksAbbrev = {}
		self.booksStandardNames = {}
		self.booksStandardAbbrev = {}
		self.booksEnglishNames = {}
		self.hebraicPsTable = {}
		self.lxxPsTable = {}
		self.booksList = []
		self.createBooksNames()
		self.createBooksAbbrev()
		self.createBooksStandardNames()
		self.createBooksStandardAbbrev()
		self.createBooksEnglishNames()
		self.createPsTable()
		if NRSVA_mapping:
			self.readBibleTextMapped()
		else:
			self.readBibleText()
		self.buildMdBible()
	def createBooksNames(self):
		with open('../Source/'+self.unbound_name+'/book_names.txt', mode='r') as tsv_file:
			csv_reader = csv.reader(tsv_file, delimiter='\t')
			for row in csv_reader:
				self.booksNames[row[0]] = row[1]
	def createBooksAbbrev(self):
		with open('../Source/'+self.unbound_name+'/book_abbrev.txt', mode='r') as tsv_file:
			csv_reader = csv.reader(tsv_file, delimiter='\t')
			for row in csv_reader:
				self.booksAbbrev[row[0]] = row[1]
	def createBooksStandardNames(self):
		with open('../Source/'+'book_standard_names.txt', mode='r') as tsv_file:
			csv_reader = csv.reader(tsv_file, delimiter='\t')
			for row in csv_reader:
				self.booksStandardNames[row[0]] = row[1]
	def createBooksStandardAbbrev(self):
		with open('../Source/'+'book_standard_abbrev.txt', mode='r') as tsv_file:
			csv_reader = csv.reader(tsv_file, delimiter='\t')
			for row in csv_reader:
				self.booksStandardAbbrev[row[0]] = row[1]
	def createBooksEnglishNames(self):
		with open('../Source/'+'book_english_names.txt', mode='r') as tsv_file:
			csv_reader = csv.reader(tsv_file, delimiter='\t')
			for row in csv_reader:
				self.booksEnglishNames[row[0]] = row[1]
	def createPsTable(self):
		with open('../Source/'+'PsTable.csv', mode='r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				self.hebraicPsTable[row[0]]=row[1]
				self.lxxPsTable[row[1]]=row[0]
	def addBook(self,book):
		self.booksList.append(book)
	def readBibleTextMapped(self):
		with open('../Source/'+self.unbound_name+'/'+self.unbound_name+'_utf8_mapped_to_NRSVA.txt', mode='r') as tsv_file:
			csv_reader = csv.reader(tsv_file, delimiter='\t')
			bookRef = ''
			chapterRef = ''
			flag = False
			for row in csv_reader:
				if row[0][0] == '#':
					pass
				elif row[8] == '':
					pass
				elif row[3]!=bookRef:
					if flag:
						book.addChapter(chapter)
						self.addBook(book)
					bookRef = row[3]
					bookStandardRef = row[0]
					book = BibleBook(self.booksNames[bookRef],
						self.booksAbbrev[bookRef],
						self.booksStandardNames[bookStandardRef],
						self.booksStandardAbbrev[bookStandardRef],
						self.booksEnglishNames[bookStandardRef])
					chapterRef = row[4]
					chapterStandardRef = row[1]
					chapter = BibleChapter(book.standardAbbrev,
						self.hebraic,self.hebraicPsTable,self.lxxPsTable,
						chapterRef,chapterStandardRef)
					chapter.addVerse(BibleVerse(row[5],row[6],row[8]))
					flag = True
				elif row[4]!=chapterRef:
					book.addChapter(chapter)
					chapterRef = row[4]
					chapterStandardRef = row[1]
					chapter = BibleChapter(book.standardAbbrev,
						self.hebraic,self.hebraicPsTable,self.lxxPsTable,
						chapterRef,chapterStandardRef)
					chapter.addVerse(BibleVerse(row[5],row[6],row[8]))
				else :
					chapter.addVerse(BibleVerse(row[5],row[6],row[8]))
			book.addChapter(chapter)
			self.addBook(book)
	def readBibleText(self):
		with open('../Source/'+self.unbound_name+'/'+self.unbound_name+'_utf8.txt', mode='r') as tsv_file:
			csv_reader = csv.reader(tsv_file, delimiter='\t')
			bookRef = ''
			chapterRef = ''
			flag = False
			for row in csv_reader:
				if row[0][0] == '#':
					pass
				elif row[0]!=bookRef:
					if flag:
						book.addChapter(chapter)
						self.addBook(book)
					bookRef = row[0]
					bookStandardRef = bookRef
					book = BibleBook(self.booksNames[bookRef],
						self.booksAbbrev[bookRef],
						self.booksStandardNames[bookStandardRef],
						self.booksStandardAbbrev[bookStandardRef],
						self.booksEnglishNames[bookStandardRef])
					chapterRef = row[1]
					chapterStandardRef = chapterRef
					chapter = BibleChapter(book.standardAbbrev,
						self.hebraic,self.hebraicPsTable,self.lxxPsTable,
						chapterRef,chapterStandardRef)
					chapter.addVerse(BibleVerse(row[2],row[2],row[3]))
					flag = True
				elif row[1]!=chapterRef:
					book.addChapter(chapter)
					chapterRef = row[1]
					chapterStandardRef = chapterRef
					chapter = BibleChapter(book.standardAbbrev,
						self.hebraic,self.hebraicPsTable,self.lxxPsTable,
						chapterRef,chapterStandardRef)
					chapter.addVerse(BibleVerse(row[2],row[2],row[3]))
				else :
					chapter.addVerse(BibleVerse(row[2],row[2],row[3]))
			book.addChapter(chapter)
			self.addBook(book)

	def buildMdBible(self):
		path = '../Bibles/'+self.abbrev
		print(path)
		try:
			os.mkdir(path)
		except FileExistsError:
			pass
		f = open(path+'/'+self.abbrev+'.md', 'w')
		f.write('# '+self.name+'\n\n')
		f.write('[['+self.abbrev+' Mentions légales]]'+'\n\n')
		for book in self.booksList:
			book.buildMdBible(self.abbrev,path)
			f.write('[['+self.abbrev+' '+book.abbrev+'|'+book.name+']]'+'\n')
		f.close()
		f = open(path+'/Livres/'+self.abbrev+' Mentions légales.md','w')
		g = open('../Source/'+self.unbound_name+'/'+self.unbound_name+'.html',mode='r')
		html = ''
		for line in g:
			html+=line
		markdown = markdownify.markdownify(html,heading_style="ATX")
		f.write(markdown)
		f.close()
		g.close()


class BibleBook:
	def __init__(self,name,abbrev,standardName,standardAbbrev,englishName):
		self.name = name
		self.abbrev = abbrev
		self.standardName = standardName
		self.standardAbbrev = standardAbbrev
		self.englishName = englishName
		self.numberChapters = 0
		self.chapterList = []
	def addChapter(self,chapter):
		self.chapterList.append(chapter)
	def buildMdBible(self,bibleAbbrev,path):
		name = bibleAbbrev+' '+self.standardAbbrev
		path += '/Livres'
		try:
			os.mkdir(path)
		except FileExistsError:
			pass
		f = open(path+'/'+name+'.md', 'w')
		f.write('---'+'\n')
		f.write('aliases : '+'\n')
		f.write('- '+self.name+'\n')
		f.write('- '+self.standardName+'\n')
		f.write('- '+self.standardAbbrev+'\n')
		if self.standardName != self.englishName:
			f.write('- '+self.englishName+'\n')
		f.write('tags : '+'Bible/'+self.standardAbbrev.replace(" ", "")+'\n')
		f.write('---'+'\n\n')
		f.write('# '+self.name+'\n\n')
		path+='/'+self.name
		for chapter in self.chapterList:
			chapter.buildMdBible(bibleAbbrev,self.name,self.abbrev,self.standardName,self.standardAbbrev,self.englishName,path)
			f.write('[['+name+' '+chapter.number+'|'+self.name+' '+chapter.number+']]'+'\n')
		f.close()

class BibleChapter:
	def __init__(self,bookStandardAbbrev,hebraic,hebraicPsTable,lxxPsTable,number,standard_number):
		if bookStandardAbbrev == 'Ps':
			if hebraic:
				if number != hebraicPsTable[number]:
					self.number = number+' ('+hebraicPsTable[number]+')'
					self.standard_number = self.number
				else:
					self.number = number
					self.standard_number = standard_number
			else:
				if number != lxxPsTable[number]:
					self.number = number+' ('+lxxPsTable[number]+')'
					self.standard_number = lxxPsTable[number]+' ('+number+')'
				else:
					self.number = number
					self.standard_number = standard_number
		else:
			self.number = number
			self.standard_number = standard_number
		self.verseList = []
	def cleanTag(self,string):
		string = string.replace(" ","")
		string = string.replace("(","_")
		string = string.replace(")","")
		return(string)
	def addVerse(self,verse):
		self.verseList.append(verse)
	def buildMdBible(self,bibleAbbrev,bookName,bookAbbrev,bookStandardName,bookStandardAbbrev,bookEnglishName,path):
		name = bibleAbbrev +' '+bookAbbrev+' '+self.number
		try:
			os.mkdir(path)
		except FileExistsError:
			pass
		f = open(path+'/'+name+'.md', 'w')
		f.write('---'+'\n')
		f.write('aliases : '+'\n')
		f.write('- '+bookName+' '+self.number+'\n')
		f.write('- '+bookStandardName+' '+self.standard_number+'\n')
		f.write('- '+bookStandardAbbrev+' '+self.standard_number+'\n')
		if bookStandardName != bookEnglishName:
			f.write('- '+bookEnglishName+' '+self.standard_number+'\n')
		f.write('tags : '+'Bible/'+self.cleanTag(bookStandardAbbrev)+'/'+self.cleanTag(self.standard_number)+'\n')
		f.write('---'+'\n\n')
		f.write('# '+bookName+' '+self.number+'\n\n')
		for verse in self.verseList:
			f.write('###### '+verse.number+verse.sub_number+'\n')
			f.write(verse.verseText+'\n')
		f.close()

class BibleVerse:
	def __init__(self,number,sub_number,verseText):
		self.number = number
		self.sub_number = sub_number
		self.verseText = verseText

lsg = Bible("Louis Segond","french_lsg","LSG",False,True)
pes = Bible("Peshitta","peshitta","PST",False,True)
vul = Bible("Vulgata Clementina","latin_vulgata_clementina","VG",True,False)
novVul = Bible("Nova Vulgata","latin_nova_vulgata","NVG",True,True)
hebrew = Bible("Hebrew BHS accents","hebrew_bhs_vowels","BHS",True,True)
lxx = Bible("Septante accentuée","lxx_a_accents","LXX",True,False)
wlc = Bible("Hebrew WLC","wlc","WLC",True,True)
#web = Bible("English WEB","web","WEB",True,True)

