# coding: shift-jis
# wn.py
# WordNet に基づき感情語辞書を構築する
# (注)
# 実際に構築を行なった結果がすでに別ファイルとして存在しています

import nltk
from nltk.corpus import wordnet as wn
from nltk.corpus import sentiwordnet as swn
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import *
from xml.dom import minidom
import numpy as np
import MeCab

a_words = [
	'ecstasy', 'joy', 'serenity',
	'love',
	'admiration', 'trust', 'acceptance',
	'submission',
	'terror', 'fear', 'apprehension',
	'awe',
	'amazement', 'surprise', 'distraction',
	'disapproval',
	'grief', 'sadness', 'pensiveness',
	'remorse',
	'loathing', 'disgust', 'boredom',
	'contempt',
	'rage', 'anger', 'annoyance',
	'aggressiveness',
	'vigilance', 'anticipation', 'interest',
	'optimism'
]

a_dict = { a_word:[] for a_word in a_words }

for a_word in a_words:
	a_synsets = wn.synsets(a_word)
	for a_synset in a_synsets:
		a_dict[a_word].append(a_synset)
		hypos = a_synset.hyponyms()
		for hypo in hypos:
			a_dict[a_word].append(hypo)
		sims = a_synset.similar_tos()
		for sim in sims:
			a_dict[a_word].append(sim)
		vgs = a_synset.hyponyms()
		for vg in vgs:
			a_dict[a_word].append(vg)
		ents = a_synset.entailments()
		for ent in ents:
			a_dict[a_word].append(ent)
		for lemma in a_synset.lemmas():
			pts = lemma.pertainyms()
			for pt in pts:
				a_dict[a_word].append(pt.synset())
			derivs = lemma.derivationally_related_forms()
			for deriv in derivs:
				a_dict[a_word].append(deriv.synset())

fout = open('affective_dict.xml', 'w')
root = Element('affective-words')

for key, val in a_dict.items():
	categ = key
	for synset in list(set(val)):
		word = synset.name().split('.')[0]
		pos_node = SubElement(root, 'a-word', { 'word':word, 'categ':categ })
		jpn_lemmas = synset.lemmas('jpn')
		for jpn_lemma in jpn_lemmas:
			jpn_word = jpn_lemma.name()
			word_node = SubElement(pos_node, 'jpn-word', { 'lemma':jpn_word })

words = []
dic = {}
for node in root.findall('a-word'):
	word = node.attrib['word']
	categ = node.attrib['categ']
	words.append(word)
	dic[word] = categ

new_root = Element('affective-words')

words = list(set(words))
for word in words:
	categ = dic[word]
	pos_node = SubElement(new_root, 'a-word', { 'word':word, 'categ':categ })
	jpn_words = []
	for node in root.findall('a-word'):
		if node.attrib['word'] == word:
			for child in node:
				jpn_word = child.attrib['lemma']
				if not jpn_word in jpn_words: jpn_words.append(jpn_word)
	for jpn_word in jpn_words:
		tagger = MeCab.Tagger('mecabrc')
		res = tagger.parseToNode(jpn_word.encode('shift-jis'))
		while res:
			org = res.feature.split(',')[6]
			if org.decode('shift-jis') == jpn_word:
				word_node = SubElement(pos_node, 'jpn-word', { 'lemma':jpn_word })
				break
			res = res.next

fout.write(minidom.parseString(tostring(new_root)).toprettyxml(encoding='shift-jis'))
fout.close()
