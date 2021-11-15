import os
import csv
import markdownify
from bs4 import BeautifulSoup
import urllib.parse
import urllib.request
import re
import fileinput

class Bible:
	def __init__(self,name,abbrev,hebraic,language):
		self.name = name
		self.abbrev = abbrev
		self.hebraic = hebraic
		self.language = language
		self.booksNames = {}
		self.booksAbbrev = {}
		self.booksStandardNames = {}
		self.booksStandardAbbrev = {}
		self.booksEnglishNames = {}
		self.hebraicPsTable = {}
		self.lxxPsTable = {}
		self.indicePsTable = {}
		self.booksList = []
		self.createBooksNames()
		self.createBooksAbbrev()
		self.createBooksStandardNames()
		self.createBooksStandardAbbrev()
		self.createBooksEnglishNames()
		self.createPsTable()
		self.createIndicePsTable()
		self.readBibleText()
		self.buildMdBible()
	def createBooksNames(self):
		with open('../Source/'+'book_names.txt', mode='r') as tsv_file:
			csv_reader = csv.reader(tsv_file, delimiter='\t')
			for row in csv_reader:
				self.booksNames[row[0]] = row[1]
	def createBooksAbbrev(self):
		with open('../Source/'+'book_abbrev.txt', mode='r') as tsv_file:
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
	def createIndicePsTable(self):
		with open('../Source/'+'PsIndice.csv', mode='r') as csv_file:
			csv_reader = csv.reader(csv_file, delimiter=',')
			for row in csv_reader:
				self.indicePsTable[row[0]]=row[1]
	def addBook(self,book):
		self.booksList.append(book)
	def readBibleText(self):
		with open('../Source/book_target.txt', mode='r') as tsv_file:
			csv_reader = csv.reader(tsv_file, delimiter='\t')
			for row in csv_reader:
				print(row)
				bookRef = row[0]
				bookStandardRef = bookRef
				book = BibleBook(self.booksNames[bookRef],
					self.booksAbbrev[bookRef],
					self.booksStandardNames[bookStandardRef],
					self.booksStandardAbbrev[bookStandardRef],
					self.booksEnglishNames[bookStandardRef],
					self.language)
				for i in range(int(row[2]),int(row[3])+1):
					print(i)
					chapterRef = str(i)
					chapterStandardRef = chapterRef
					chapter = BibleChapter(row[1],self.indicePsTable, book.standardAbbrev,
						self.hebraic,self.hebraicPsTable,self.lxxPsTable,
						chapterRef,chapterStandardRef,self.language)
					book.addChapter(chapter)
				self.addBook(book)

	def buildMdBible(self):
		path = '../Bibles/'+self.abbrev
		print(path)
		try:
			os.mkdir(path)
		except FileExistsError:
			pass
		f = open(path+'/'+'Ref.md', 'w')
		f.write('---'+'\n')
		f.write('tags : '+'Bible'+', '+self.language+'\n')
		f.write('cssclass : '+self.language+'\n')
		f.write('---'+'\n')
		f.write('# '+self.name+'\n\n')
		for book in self.booksList:
			book.buildMdBible(self.abbrev,path)
			f.write('[['+book.abbrev+'|'+book.name+']]'+'\n')
		f.close()

class BibleBook:
	def __init__(self,name,abbrev,standardName,standardAbbrev,englishName,language):
		self.name = name
		self.abbrev = abbrev
		self.standardName = standardName
		self.standardAbbrev = standardAbbrev
		self.englishName = englishName
		self.language = language
		self.numberChapters = 0
		self.chapterList = []
	def addChapter(self,chapter):
		self.chapterList.append(chapter)
	def buildMdBible(self,bibleAbbrev,path):
		name = self.standardAbbrev
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
		f.write('tags : '+'\n')
		f.write('- '+'Bible/'+self.standardAbbrev.replace(" ", "")+'\n')
		f.write('- '+self.language+'\n')
		f.write('cssclass : '+self.language+'\n')
		f.write('---'+'\n\n')
		f.write('# '+self.name+'\n\n')
		path+='/'+self.name
		for chapter in self.chapterList:
			chapter.buildMdBible(bibleAbbrev,self.name,self.abbrev,self.standardName,self.standardAbbrev,self.englishName,path)
			f.write('[['+name+' '+chapter.number+'|'+self.name+' '+chapter.number+']]'+'\n')
		f.close()

class BibleChapter:
	def __init__(self,bookTarget,indicePsTable,bookStandardAbbrev,hebraic,hebraicPsTable,lxxPsTable,number,standard_number,language):
		if bookStandardAbbrev == 'Ps':
			self.indice = indicePsTable[number]
			number = hebraicPsTable[number]
			print(number)
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
			self.indice = number
			self.standard_number = standard_number
		self.bookTarget = bookTarget
		self.language = language
		self.verseList = []
		self.readVerses()
	def readVerses(self):
		path = '../Source/html/'+self.bookTarget
		try:
			os.mkdir(path)
		except FileExistsError:
			pass		
		if os.path.isfile(path+'/'+self.indice+'.html'):
			pass
		else:
			try:
			    url = "https://www.aelf.org/bible/"+self.bookTarget+"/"+self.indice
			    headers = {}
			    headers['User-Agent'] = "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"
			    req = urllib.request.Request(url, headers = headers)
			    resp = urllib.request.urlopen(req)
			    respData = resp.read().decode('utf-8')
			    saveFile = open(path+'/'+self.indice+'.html','w')
			    saveFile.write(str(respData))
			    saveFile.close()
			except Exception as e:
	   			print(str(e))
		file = open(path+'/'+self.indice+'.html', 'r')
		contents = file.read()
		soup = BeautifulSoup(contents, 'html.parser')
		
		for data in soup.find_all():
			if data.name == "p":
				if data.attrs == {}:
					verse = BibleVerse(data.contents[0].getText(),'',data.contents[1].strip())
					self.addVerse(verse)

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
		f = open(path+'/'+name.strip()+'.md', 'w')
		f.write('---'+'\n')
		f.write('aliases : '+'\n')
		#f.write('- '+bookName+' '+self.number+'\n')
		f.write('- '+bookStandardName+' '+self.standard_number+'\n')
		f.write('- '+bookStandardAbbrev+' '+self.standard_number+'\n')
		if bookStandardName != bookEnglishName:
			f.write('- '+bookEnglishName+' '+self.standard_number+'\n')
		f.write('tags : '+'\n')
		f.write('- '+'Bible/'+self.cleanTag(bookStandardAbbrev)+'/'+self.cleanTag(self.standard_number)+'\n')
		f.write('- '+self.language+'\n')
		f.write('cssclass : '+self.language+'\n')
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

#aelf = Bible("Bible AELF","AELF",False,"français")
ref = Bible("Bible AELF","",False,"français")


