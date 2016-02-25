# coding: shift-jis
class Music():
	def __init__(self):
		self._title = ''
		self._artist = ''
		self._keys = None
		self._chords = []
		self._lyrics = []
		self._dat = []
		self._emo4 = []
	
	def get_title(self):
		return self._title
	def set_title(self, val):
		self._title = val
	def del_title(self):
		del self._title	
	title = property(get_title, set_title, del_title)
	
	def get_artist(self):
		return self._artist
	def set_artist(self, val):
		self._artist = val
	def del_artist(self):
		del self._artist
	artist = property(get_artist, set_artist, del_artist)
	
	def get_keys(self):
		return self._keys
	def set_keys(self, val):
		self._keys = val
	def del_keys(self):
		del self._keys
	play_key = property(get_keys, set_keys, del_keys)

	def get_chords(self):
		return self._chords
	def set_chords(self, val):
		self._chords = val
	def del_chords(self):
		del self._chords
	chords = property(get_chords, set_chords, del_chords)
	
	def get_lyrics(self):
		return self._lyrics
	def set_lyrics(self, val):
		self._lyrics = val
	def del_lyrics(self):
		del self._lyrics
	lyrics = property(get_lyrics, set_lyrics, del_lyrics)
	
	def get_dat(self):
		return self._dat
	def set_dat(self, val):
		self._dat = val
	def del_dat(self):
		del self._dat
	dat = property(get_dat, set_dat, del_dat)
	
	def get_emo4(self):
		return self._emo4
	def set_emo4(self, val):
		self._emo4 = val
	def del_emo4(self):
		del self._emo4
	emo4 = property(get_emo4, set_emo4, del_emo4)
	



