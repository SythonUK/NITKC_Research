# coding: shift-jis
# parse_html.py:
# html ファイルを解析して必要な情報を抽出する

import bs4
from bs4 import BeautifulSoup
from music import Music
from itertools import chain
import re
import sys
import os

# シンボル (コード, 記号) かどうかを判定する
def isSymbols(text):
	chords = [ 
		'C', 'C#', 'D', 'D#', 'E', 'F',
		'F#', 'G', 'G#', 'A', 'A#', 'B',
		'D♭', 'E♭', 'G♭', 'A♭', 'B♭'
	]
	symbols = [
		'N.C.', '(9)', '(11)', '+5', 'Capo', 'M9',
	]
	for chord in chords:
		if text == 'on' + chord: return True
	for symbol in symbols:
		if symbol in text: return True
	return False

# ASCII 文字だけで text が構成されているかを判定する
def is_only_ascii(text):
	regexp = re.compile(r'\A[\x00-\x7f]*\Z')
	return isinstance(text, str) and regexp.match(text)

# フラット (♭) をシャープに変換する
def flat2sharp(chord):
	conv_dict = {'G':'F', 'E':'D', 'D':'C', 'B':'A', 'A':'G'}
	tmp = chord.split(u'♭'.encode('shift-jis'))
	suffix = tmp[1]
	conv = conv_dict[tmp[0]]
	return conv + '#' + suffix

# html からヘッダー情報 (曲名, アーティスト名) を抽出する
def getHeader(soup):
	text = soup.find("title").text.encode('shift-jis')
	text = text.replace('\n', '')
	text = text.strip()
	text = text.split(u'（'.encode('shift-jis'))
	title = text[0]
	artist = text[1].split(u'）'.encode('shift-jis'))[0]
	return title, artist

# html から楽曲のキーの情報を抽出する
def getKeys(soup):
	nodes = soup.find(text=re.compile("Original Key")).encode('shift-jis')
	text = nodes.split('/')
	org_key = text[0].split(u'：'.encode('shift-jis'))[1].strip()
	if u'♭'.encode('shift-jis') in org_key:
		org_key = flat2sharp(org_key)
	capo = text[1].split(u'：'.encode('shift-jis'))[1].strip()
	play_key = text[2].split(u'：'.encode('shift-jis'))[1].replace('\n', '').strip()
	play_key = play_key.split(u'　'.encode('shift-jis'))[0]
	if u'♭'.encode('shift-jis') in play_key:
		play_key = flat2sharp(play_key)
	keys = (org_key, capo, play_key)
	return keys

# html から歌詞情報を抽出する
def getLyrics(soup):
	lyrics = []

	nodes = soup.find("tt")
	for node in nodes:
		if isinstance(node, bs4.element.NavigableString) and not isinstance(node, bs4.element.Comment):
			text = node.encode('shift-jis')
			text = text.replace('\n', '')
			text = text.replace(u'　'.encode('shift-jis'), ' ')
			text = text.replace('  ', ' ')
			text = text.replace('/', '')
			text = text.replace(u'→'.encode('shift-jis'), '')
			text = text.rstrip()
			text = text.lstrip()
			if len(text) == 0 or isSymbols(text): continue
			words = ''
			for s in text.split():
				word = s
				if is_only_ascii(s) is not None:
					word = ' ' + word + ' '
				words += word
			words = words.replace('  ', ' ')
			lyrics.append(words)
	return lyrics

# html からコード進行の情報を抽出する
def getChords(soup):
	chords = []
	tmp = []

	nodes = soup.find("tt")

	new_nodes = []
	for node in nodes:
		if isinstance(node, bs4.element.Tag):
			new_nodes.append(node)

	count_br = 0
	for node in new_nodes:
		name = node.name
		if name == 'a':
			count_br = 0
			chord = node.text.replace('\n', '')
			chord = chord.strip()
			if u'♭'.encode('shift-jis') in chord.encode('shift-jis'):
				chord = flat2sharp(chord.encode('shift-jis'))
			tmp.append(chord.encode('shift-jis'))
		if name == 'br':
			count_br += 1
			if count_br == 3:
				while '' in tmp:
					tmp.remove('')
				if len(tmp) < 3:
					tmp = []
					continue
					if len(tmp) == 0: continue
					if len(chords) == 0:
						tmp = []
						continue
					chords[-1].extend(tmp)
				else:
					if len(tmp) < 3:
						print tmp
					chords.append(tmp)
				tmp = []

	if len(tmp) > 0:
		while '' in tmp:
			tmp.remove('')
		if len(tmp) < 3:
			if len(tmp) != 0: 
				chords[-1].extend(tmp)
		else:
			chords.append(tmp)
	
	while [] in chords:
		chords.remove([])
	
	return chords

# fname で指定した html ファイルを解析する
def parse(fname):
	soup = BeautifulSoup(open(fname), 'lxml')
	soup = BeautifulSoup(soup.prettify('shift-jis'), 'lxml')
	music = Music()

	title, artist = getHeader(soup)
	keys = getKeys(soup)
	lyrics = getLyrics(soup)
	chords = getChords(soup)

	music.title = title
	music.artist = artist
	music.keys = keys
	music.lyrics = lyrics
	music.chords = chords

	return music
