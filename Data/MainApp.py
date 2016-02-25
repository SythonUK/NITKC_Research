# coding: shift-jis
# MainApp.py:
# メインアプリケーションのGUI

import parse_html, parse_lyrics
import conv2cof
import scipy
from sklearn import manifold
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
import nltk
from hmm import HMM
import sys
import os
import glob
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
from PyQt4.QtWebKit import QWebView
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.path as path
import matplotlib.patches as patches

inf = float('inf')
np.random.seed(100)
RS = 1

reload(sys)
sys.setdefaultencoding('shift-jis')

# files から楽曲データ情報を抽出する
def load_data(files):
	musics = []
	for idx, f in enumerate(files):
		music = parse_html.parse(f)
		chords = music.chords
		keys = music.keys
		dat = []
		for chord in chords:
			new_chords = conv2cof.to_cof(chord, keys)
			x = []
			y = []
			for chord in new_chords:
				x.append(chord[0]) 
				y.append(chord[1])
			if len(x) < 3:
				print x
			dat.append([x, y])
		music.dat = dat
		musics.append(music)
	return musics

# 歌詞情報のみを用いた楽曲分類を行う
def clustering_by_lyrics(musics, k):
	scores = []
	emo4s = []
	docs = []
	for music in musics:
		a_words = parse_lyrics.get_affective_words(music.lyrics)
		music.a_words = a_words
		docs.append(a_words)
	collection = nltk.TextCollection(docs)
	terms = list(set(collection))
	for idx, doc in enumerate(docs):
		if len(doc) == 0:
			score = np.zeros(8)
			emo4 = np.zeros(4)
		else:
			score = parse_lyrics.calc_score(collection, terms, doc)
			sum_score = np.sum(score)
			emo4 = parse_lyrics.calc_4emotions(score)
		musics[idx].score = score
		musics[idx].emo4 = emo4
		scores.append(score)
		emo4s.append(emo4)
	scores = np.array(scores)
	emo4s = np.array(emo4s)

	scores = np.array(scores)
	max_scores = scores.max(axis=0)
	min_scores = scores.min(axis=0)
	diff = max_scores - min_scores
	scores = (scores - min_scores) / diff
	for music in musics:
		music.score = (music.score - min_scores) / diff

	kmeans_model = KMeans(n_clusters = k, random_state=RS).fit(scores)
	labels = kmeans_model.labels_
	return labels, scores

# コード進行の情報のみを用いて楽曲の分類を行う
def clustering_by_chords(musics, k, num_states=3):
	N = len(musics)
	ns = 2
	nc = 12
	n = num_states + num_states**2 + nc * num_states

	feature_vectors = []

	for idx, music in enumerate(musics):
		suffix = []
		chord = []
		for dat in music.dat:
			suffix.extend(dat[0])
			chord.append(dat[1])
		f = []

		hmm_c = HMM(nc, num_states=num_states)
		hmm_c.learning(chord)
		
		Pic = hmm_c.Pi
		a_sort = Pic.argsort()[-1::-1]
		Pic = Pic[a_sort]
		Ac = hmm_c.A[:, a_sort]
		Bc = hmm_c.B[:, a_sort]

		f.extend(list(Pic.flatten()))
		f.extend(list(Ac.flatten()))
		f.extend(list(Bc.flatten()))
		
		f = np.array(f)
		if any(np.isnan(f)): 
			print idx, music.title, music.keys[0]
		feature_vectors.append(f)
	
	feature_vectors = np.array(feature_vectors)
	kmeans_model = KMeans(n_clusters=k, random_state=RS).fit(feature_vectors)
	labels = kmeans_model.labels_

	return labels, feature_vectors

# コード進行と歌詞情報の両方を用いた楽曲の分類を行う
def clustering_by_chords_and_lyrics(musics, k, num_states=3):
	N = len(musics)
	nc = 12
	n = num_states + num_states**2 + nc * num_states
	
	feature_vectors = []

	for idx, music in enumerate(musics):
		suffix = []
		chord = []
		for dat in music.dat:
			suffix.append(dat[0])
			chord.append(dat[1])
		f = []

		hmm_c = HMM(nc, num_states=num_states)
		hmm_c.learning(chord)
		
		Pic = hmm_c.Pi
		a_sort = Pic.argsort()[-1::-1]
		Pic = Pic[a_sort]
		Ac = hmm_c.A[:, a_sort]
		Bc = hmm_c.B[:, a_sort]

		f.extend(list(Pic.flatten()))
		f.extend(list(Ac.flatten()))
		f.extend(list(Bc.flatten()))
		f = np.array(f)
		if any(np.isnan(f)): 
			print idx, music
		feature_vectors.append(f)

	Scores = []
	docs = []
	for music in musics:
		a_words = parse_lyrics.get_affective_words(music.lyrics)
		music.a_words = a_words
		docs.append(a_words)
	collection = nltk.TextCollection(docs)
	terms = list(set(collection))
	for idx, doc in enumerate(docs):
		score = parse_lyrics.calc_score(collection, terms, doc)
		Scores.append(score)
		emo4 = parse_lyrics.calc_4emotions(score)
		musics[idx].score = score
		musics[idx].emo4 = emo4

	Scores = np.array(Scores)
	max_scores = Scores.max(axis=0)
	min_scores = Scores.min(axis=0)
	diff = max_scores - min_scores
	Scores = (Scores - min_scores) / diff
	for music in musics:
		music.score = (music.score - min_scores) / diff

	for idx, f in enumerate(feature_vectors):
		np.append(f, Scores[idx])
	
	feature_vectors = np.array(feature_vectors)
	kmeans_model = KMeans(n_clusters=k, random_state=RS).fit(feature_vectors)
	labels = kmeans_model.labels_

	return labels, feature_vectors

# GUI のメインウィンドウ
class MainWindow(QtGui.QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.musics = None
		self.t_end = 0
		self.dat_idx = None
		self.selected_clusters = None
		self.mainLayout = QtGui.QHBoxLayout()

		self.open_folder_button = QtGui.QPushButton('open folder')
		self.open_folder_button.setFixedWidth(100)
		self.connect(self.open_folder_button, QtCore.SIGNAL('clicked()'), self.open_folder)
	
		self.statusBar().showMessage('Welcome')

		self.num_of_clusters = QtGui.QLineEdit()
		self.num_of_clusters.setFixedWidth(20)
		self.num_of_clusters.setText('12')
		self.num_of_clusters.setAlignment(QtCore.Qt.AlignLeft)

		self.mode_select = QtGui.QButtonGroup()
		lyrics = QtGui.QRadioButton('only lyrics')
		chords = QtGui.QRadioButton('only chords')
		both = QtGui.QRadioButton('both')
		both.setChecked(True)
		self.mode_select.addButton(lyrics, 0)
		self.mode_select.addButton(chords, 1)
		self.mode_select.addButton(both, 2)
	
		self.start_button = QtGui.QPushButton('start')
		self.start_button.setFixedWidth(100)
		self.connect(self.start_button, QtCore.SIGNAL('clicked()'), self.main)

		self.cluster_select = QtGui.QComboBox()
		self.cluster_select.setEditable(False)
		self.cluster_select.activated[str].connect(self.select_cluster)

		font = QtGui.QFont()
		font.setPointSize(12)
		self.results = QtGui.QTreeView()
		self.results.header().setFont(font)
		self.stdItemModel = QtGui.QStandardItemModel(0, 3)
		self.stdItemModel.setHeaderData(0, QtCore.Qt.Horizontal, 'Title')
		self.stdItemModel.setHeaderData(1, QtCore.Qt.Horizontal, 'Artist')
		self.stdItemModel.setHeaderData(2, QtCore.Qt.Horizontal, 'Original Key')
		self.results.setModel(self.stdItemModel)
		self.results.clicked.connect(self.plot_a_score)

		self.draw_frame = QtGui.QWidget()
		self.dpi = 100
		self.fig = Figure((5.0, 5.0), dpi=self.dpi)
		self.canvas = FigureCanvas(self.fig)
		self.canvas.setParent(self.draw_frame)
		self.axes = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
		
		self.mpl_toolbar = NavigationToolbar(self.canvas, self.draw_frame)

		leftLayout = QtGui.QVBoxLayout()
		label1 = QtGui.QLabel('properties')
		label1.setAlignment(QtCore.Qt.AlignTop)
		properties = QtGui.QHBoxLayout()
		pl = QtGui.QVBoxLayout()
		op = QtGui.QHBoxLayout()
		op.addWidget(self.open_folder_button)
		self.label2 = QtGui.QLabel('opened folder:')
		op.addWidget(self.label2)
		pl.addLayout(op)
		cl = QtGui.QHBoxLayout()
		label3 = QtGui.QLabel('number of clusters:')
		cl.addWidget(label3)
		cl.addWidget(self.num_of_clusters)
		cl.addStretch(1)
		pl.addLayout(cl)
		pr = QtGui.QVBoxLayout()
		pr.addWidget(lyrics)
		pr.addWidget(chords)
		pr.addWidget(both)
		properties.addLayout(pl)
		properties.addLayout(pr)
		label4 = QtGui.QLabel('results')
		leftLayout.addWidget(label1)
		leftLayout.addLayout(properties)
		leftLayout.addWidget(self.start_button)
		leftLayout.addWidget(label4)
		leftLayout.addWidget(self.cluster_select)
		leftLayout.addWidget(self.results)

		self.mainLayout.addLayout(leftLayout)

		rightLayout = QtGui.QVBoxLayout()
		rightLayout.addWidget(self.canvas)
		rightLayout.addWidget(self.mpl_toolbar)
		self.mainLayout.addLayout(rightLayout)

		self.main_widget = QtGui.QWidget()
		self.main_widget.setLayout(self.mainLayout)
		self.setCentralWidget(self.main_widget)
		self.setWindowTitle('Main App')
		self.setMinimumSize(1200, 700)
		self.files = None
	
	# ファイルをロードするためのメソッド
	def open_folder(self):
		fname = QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', os.path.expanduser('~' + '/research/Musics'))
		files = glob.glob(str(fname) + '/*')
		self.fname = fname
		self.files = files
		musics = load_data(files)
		self.musics = musics
		self.label2.setText('opened folder: ' + fname)
		self.statusBar().showMessage('opened ' + fname + ' successfully')

	# 多次元尺度構成法 (MDS) によるプロットを行うメソッド
	def plot_mds(self, labels, data):
		leds = [ 'cluster ' + str(i) for i in xrange(self.k) ]
		pt = ['o', '+', 'x', '4']

		mds = manifold.MDS(n_components=2, dissimilarity='euclidean')
		y = mds.fit_transform(data)
		self.fig.delaxes(self.fig.axes[0])
		self.axes = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
		for i in xrange(self.k):
			dat = y[np.where(labels==i)]
			self.axes.plot(dat[:, 0], dat[:, 1], pt[i/6], label=leds[i])
		self.axes.set_xlim(np.min(y[:, 0]) - 0.5, np.max(y[:, 0]) + 1.5)
		self.axes.set_ylim(np.min(y[:, 1]) - 0.5, np.max(y[:, 1]) + 1.5)
		self.axes.set_title('MDS Scatter Plots')
		self.axes.legend(loc='upper right', fontsize='x-small')
		self.canvas.draw()
	
	# 感情スコアをプロットするメソッド
	@QtCore.pyqtSlot(QtCore.QModelIndex)
	def plot_a_score(self, index):
		checked = self.mode_select.checkedId()
		if checked == 1: return
		
		props = [
			'ecstasy', 'admiration', 'terror', 'amazement',
			'grief', 'loathing', 'rage', 'vigilance',
		]

		self.fig.delaxes(self.fig.axes[0])
		self.axes = self.fig.add_axes([0.1, 0.05, 0.8, 0.8], polar=True)
		cols = [ 
			'yellow', 'lime', 'darkgreen', 'cyan',
			'blue', 'magenta', 'red', 'orange',
			]
		theta = np.pi/2 - np.arange(0.0, 2*np.pi, 2*np.pi/8) - np.pi/16
		score = self.clusters[self.selected_cluster][index.row()].score
		width = np.pi/8 * np.ones(8)

		bars = self.axes.bar(theta, score, width=width, bottom=0.0)

		idx = 0
		for r, bar in zip(score, bars):
			bar.set_facecolor(cols[idx])
			idx += 1

		t = np.arange(0, 2*np.pi, 2*np.pi/8)
		self.axes.set_xticks(t, [])
		self.axes.set_xticklabels([])
		self.axes.set_yticks(np.linspace(0, 1.0, 11))
		yticklabels = ['0.0', '', '', '', '', '0.5', '', '', '', '', '1.0']
		self.axes.set_yticklabels(yticklabels)
		self.axes.set_ylim(0, 1.0)

		for i in xrange(8):
			ang_rad = np.pi/2 -i / 8.0 * 2 * np.pi
			ang_deg = -i / 8.0 * 360
			ha = 'right'
			if ang_rad < np.pi/2 or ang_rad > 3*np.pi/2: ha = 'left'
			self.axes.text(ang_rad, 1.1, props[i], size=20,
				rotation=ang_deg,
				horizontalalignment='center',
				verticalalignment='center'
			)
		self.canvas.draw()

	# 分類結果として確認するクラスタを変更するメソッド
	def select_cluster(self):
		font = QtGui.QFont()
		self.stdItemModel = QtGui.QStandardItemModel(0, 3)
		self.stdItemModel.setHeaderData(0, QtCore.Qt.Horizontal, 'Title')
		self.stdItemModel.setHeaderData(1, QtCore.Qt.Horizontal, 'Artist')
		self.stdItemModel.setHeaderData(2, QtCore.Qt.Horizontal, 'Original Key')
		self.results.setModel(self.stdItemModel)
		self.dat_idx = 0
		selected = int(str(self.cluster_select.currentText()).split()[1])
		self.selected_cluster = selected

		font = QtGui.QFont()
		font.setPointSize(12)
		for music in self.clusters[selected]:
			title = QtGui.QStandardItem(QtCore.QString.fromLocal8Bit(music.title))
			title.setFont(font)
			artist = QtGui.QStandardItem(QtCore.QString.fromLocal8Bit(music.artist))
			artist.setFont(font)
			org = QtGui.QStandardItem(QtCore.QString.fromLocal8Bit(music.keys[0]))
			org.setFont(font)
			self.stdItemModel.setItem(self.dat_idx, 0, title)
			self.stdItemModel.setItem(self.dat_idx, 1, artist)
			self.stdItemModel.setItem(self.dat_idx, 2, org)
			self.dat_idx += 1
		self.results.resizeColumnToContents(0)
		self.results.resizeColumnToContents(1)
		self.results.resizeColumnToContents(2)

	# メインメソッド
	def main(self):
		if self.musics is None:
			qm = QtGui.QMessageBox.critical(self, 'ExectionError', 'No directory is selected!', QtGui.QMessageBox.Ok)
			return
		try:
			k = int(self.num_of_clusters.text())
		except ValueError:
			qm = QtGui.QMessageBox.critical(self, 'ValueError', 'Invalid type for number of clusters!', QtGui.QMessageBox.Ok)
			return
		if k <= 0:
			qm = QtGui.QMessageBox.critical(self, 'ValueError', 'Number of clusters must be a positive integer!', QtGui.QMessageBox.Ok)
			return
		self.stdItemModel.clear()
		self.stdItemModel = QtGui.QStandardItemModel(0, 3)
		self.stdItemModel.setHeaderData(0, QtCore.Qt.Horizontal, 'Title')
		self.stdItemModel.setHeaderData(1, QtCore.Qt.Horizontal, 'Artist')
		self.stdItemModel.setHeaderData(2, QtCore.Qt.Horizontal, 'Original Key')
		self.results.setModel(self.stdItemModel)
		self.k = k
		self.cluster_select.clear()
		for i in xrange(k):
			self.cluster_select.addItem('cluster ' + str(i))
		self.selected_cluster = 0
		
		checked = self.mode_select.checkedId()
		labels = None
		data = None
		if checked == 0:
			labels, data = clustering_by_lyrics(self.musics, k)
		elif checked == 1:
			labels, data = clustering_by_chords(self.musics, k)
		elif checked == 2:
			labels, data = clustering_by_chords_and_lyrics(self.musics, k)
		self.statusBar().showMessage('Finish')
		
		self.plot_mds(labels, data)
		
		self.dat_idx = 0
		clusters = { i:[] for i in xrange(k) }
		for idx, label in enumerate(labels):
			clusters[label].append(self.musics[idx])
		self.clusters = clusters
		
		font = QtGui.QFont()
		font.setPointSize(12)
		for music in clusters[0]:
			title = QtGui.QStandardItem(QtCore.QString.fromLocal8Bit(music.title))
			title.setFont(font)
			artist = QtGui.QStandardItem(QtCore.QString.fromLocal8Bit(music.artist))
			artist.setFont(font)
			org = QtGui.QStandardItem(QtCore.QString.fromLocal8Bit(music.keys[0]))
			org.setFont(font)
			self.stdItemModel.setItem(self.dat_idx, 0, title)
			self.stdItemModel.setItem(self.dat_idx, 1, artist)
			self.stdItemModel.setItem(self.dat_idx, 2, org)
			self.dat_idx += 1
		self.results.resizeColumnToContents(0)
		self.results.resizeColumnToContents(1)
		self.results.resizeColumnToContents(2)

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)
	QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForLocale())
	md = MainWindow()
	md.show()
	app.exec_()
