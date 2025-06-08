from enum import Enum

class Symbols(Enum):
	empty                = 0
	unknown              = 1
	notehead_full        = 2
	notehead_empty       = 3
	rest_wholehalf       = 4
	rest_quarter         = 5
	rest_eighth          = 6
	rest_sixteenth       = 7
	rest_thirtysecond    = 8
	accidental_flat      = 9
	accidental_natural   = 10
	accidental_sharp     = 11
	clef_alto            = 12
	clef_bass            = 13
	clef_treble          = 14

paths = [
	'empty',
	'unknown',
	'noteheads/full',
	'noteheads/empty',
	'rests/wholehalf',
	'rests/quarter',
	'rests/eighth',
	'rests/sixteenth',
	'rests/thirtysecond',
	'accidentals/flat',
	'accidentals/natural',
	'accidentals/sharp',
	'clefs/alto',
	'clefs/bass',
	'clefs/treble'
]

symbol_names = [
	'',
	'',
	'full noteheads',
	'empty noteheads',
	'whole/half rests',
	'quarter rests',
	'eighth rests',
	'sixteenth rests',
	'thirty-second rests',
	'flats',
	'naturals',
	'sharps',
	'alto clefs',
	'bass clefs',
	'treble clefs'
]

symbol_sizes = [
	[0, 0],
	[0, 0],
	[40, 35],
	[40, 35],
	[40, 90],
	[40, 70],
	[30, 50],
	[30, 70],
	[30, 90],
	[30, 70],
	[25, 50],
	[30, 70],
	[70, 160],
	[70, 160],
	[70, 160]
]

vis_symbol_colors = [
	(0,0,0),
	(0,0,0),
	(0,0,255),
	(0,0,255),
	(0,255,0),
	(0,255,0),
	(0,255,0),
	(0,255,0),
	(0,255,0),
	(255,0,0),
	(255,0,0),
	(255,0,0),
	(225,52,235),
	(225,52,235),
	(225,52,235)
]

flags_to_dur = [
	"1",
	"2",
	"4",
	"8",
	"16",
	"32"
]

hog_or = 9
hog_ppc = [4, 4]
hog_cpb = [2, 2]