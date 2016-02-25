# coding: shift-jis
# parse_lyrics.py
# 歌詞からの感情分析を行う

import CaboCha
import re
from lxml import etree
import numpy as np

# 感情語辞書を読み込む
dictfile = 'resources/result.xml'

parser = etree.XMLParser(encoding='shift-jis')
tree = etree.parse(dictfile, parser)
root = tree.getroot()

a_dict = {}

nodes = root.findall('.//a-word')

for node in nodes:
	categ = node.attrib['categ']
	word = node.attrib['word']
	a_dict[word] = categ
	for child in node:
		lemma = child.attrib['lemma']
		#print lemma
		a_dict[lemma] = categ

# 否定表現
neg_words = [
	u'ない', u'無い', u'ぬ', u'ず',
]

# 品詞
pos_words = [ 
	'名詞', '動詞', '形容詞', '副詞', '感動詞', '連体詞', 
]

# txt が ASCII 文字だけかどうかを判定する
def isASCII(txt):
	return re.search(r'^[0-9A-Za-z]+$', txt)

# 感情語辞書に単語があればそれを持ってくる
def isexist_and_get_data(data, key):
	return data[key] if key in data else None

# 感情語を抽出する
def get_affective_words(lyrics):
	c = CaboCha.Parser('')
	a_words = []

	for lyric in lyrics:
		l = lyric.split()
		for st in l:
			tree = c.parse(st)
			chunk_size = tree.chunk_size()
			for i in xrange(chunk_size):
				chunk = tree.chunk(i)
				token_pos = chunk.token_pos
				token_size = chunk.token_size
				chunk_words = []
				for ix in xrange(token_pos, token_pos + token_size):
					surface = tree.token(ix).surface
					feature = tree.token(ix).feature.split(',')
					asc = isASCII(surface)
					pos = feature[0]
					if asc is not None:
						origin = surface.lower().decode('shift-jis')
					else:
						origin = feature[6].decode('shift-jis')
					if origin in neg_words:
						chunk_words = []
						break
					if pos in pos_words:
						categ = isexist_and_get_data(a_dict, origin)
						if categ is not None:
							chunk_words.append(origin)
				a_words.extend(chunk_words)
	return a_words

# 感情スコアを算出する
def calc_score(collection, terms, doc):
	joy          = np.array([0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
	trust        = np.array([0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
	fear         = np.array([0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0])
	surprise     = np.array([0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0])
	sadness      = np.array([0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0, 0.0])
	disgust      = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0, 0.0])
	anger        = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5, 0.0])
	anticipation = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.5])
	
	score_dict = {
		'ecstasy':2*joy,            'joy':joy,                  'serenity':0.5*joy,
		'love':joy + trust,
		'admiration':2*trust,       'trust':trust,              'acceptance':0.5*trust,
		'submission':trust + fear,
		'terror':2*fear,            'fear':fear,                'apprehension':0.5*fear,
		'awe':fear + surprise,
		'amazement':2*surprise,     'surprise':surprise,        'distraction':0.5*surprise,
		'disapproval':surprise + sadness,
		'grief':2*sadness,          'sadness':sadness,           'pensiveness':0.5*sadness,
		'remorse':sadness + disgust,
		'loathing':2*disgust,       'disgust':disgust,           'boredom':0.5*disgust,
		'contempt':disgust + anger,
		'rage':2*anger,             'anger':anger,               'annoyance':0.5*anger,
		'aggressiveness':anger + anticipation,
		'vigilance':2*anticipation, 'anticipation':anticipation, 'interest':0.5*anticipation,
		'optimism':anticipation + joy,
	}
	
	a_scores = np.zeros(8)
	
	for term in terms:
		tfidf = collection.tf_idf(term, doc)
		if tfidf != 0.0:
			categ = a_dict[term]
			score = score_dict[categ] * tfidf
			a_scores += score

	return a_scores

# 感情スコアから4つの主感情を抽出する (使用はしていない)
def calc_4emotions(a_scores):
	joy = 0.25 * a_scores[7] + 0.5 * a_scores[0] + 0.25 * a_scores[1]
	fear = 0.25 * a_scores[1] + 0.5 * a_scores[2] + 0.25 * a_scores[3]
	sadness = 0.25 * a_scores[3] + 0.5 * a_scores[4] + 0.25 * a_scores[5]
	anger = 0.25 * a_scores[5] + 0.5 * a_scores[6] + 0.25 * a_scores[7]
	return np.array([joy, fear, sadness, anger])
