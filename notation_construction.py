from config import *

n_to_step = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

base_note_vals = [
	[6, 4], # treble
	[1, 3], # bass
	[0, 4]  # alto
]

staffline_height = 2.6
staffspace_height = 20.625
staff_rows = [[80, 81], [100, 101, 102], [121, 122, 123], [142, 143], [162, 163, 164]]
symbols = [
	[2, 428, 130, 1],
	[2, 740, 130, 0],
	[2, 1176, 130, 0],
	[2, 1788, 130, 1],
	[2, 2028, 130, 2],
	[2, 2132, 130, 1],
	[2, 2200, 130, 1],
	[2, 2264, 130, 2],
	[2, 492, 134, 0],
	[2, 580, 134, 1],
	[2, 644, 134, 0],
	[2, 932, 134, 0],
	[2, 1020, 134, 1],
	[2, 1084, 134, 0],
	[2, 1300, 134, 1],
	[2, 1364, 134, 0],
	[2, 1524, 134, 0],
	[2, 1612, 134, 0],
	[2, 1740, 134, 2],
	[2, 1852, 134, 1],
	[2, 1916, 134, 1],
	[2, 1980, 134, 2],
	[2, 2068, 134, 1],
	[4, 1880, 70],
	[4, 2148, 70],
	[6, 863, 130],
	[6, 1455, 130],
	[14, 335, 113]
]

symbols.sort(key=lambda x: x[1])

staff_middle = sum(staff_rows[2])/len(staff_rows[2])
semitone_dist = (staffspace_height + staffline_height)/2

f = open("output.musicxml", "w")

f.write('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE score-partwise PUBLIC
	"-//Recordare//DTD MusicXML 4.0 Partwise//EN"
	"http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="4.0">
	<part-list>
		<score-part id="P1">
			<part-name>Staff</part-name>
		</score-part>
	</part-list>
	<part id="P1">
		<measure number="1">
			<attributes>
				<divisions>8</divisions>
				<key>
					<fifths>0</fifths>
				</key>
				<time>
					<beats>4</beats>
					<beat-type>4</beat-type>
				</time>''')

base_step, base_oct = base_note_vals[0] # default to treble clef

for s in symbols:
	if s[0] == Symbols.clef_treble.value:
		f.write('''
				<clef>
					<sign>G</sign>
					<line>2</line>
				</clef>''')
		base_step, base_oct = base_note_vals[0]
		break
	if s[0] == Symbols.clef_bass.value:
		f.write('''
				<clef>
					<sign>F</sign>
					<line>4</line>
				</clef>''')
		base_step, base_oct = base_note_vals[1]
		break
	if s[0] == Symbols.clef_alto.value:
		f.write('''
				<clef>
					<sign>C</sign>
					<line>3</line>
				</clef>''')
		base_step, base_oct = base_note_vals[2]
		break

f.write('''
			</attributes>''')

measure_timer = 32
measure_n = 1

for s in symbols:

	if s[0] == Symbols.notehead_full.value or s[0] == Symbols.notehead_empty.value:

		# writing note

		if s[0] == Symbols.notehead_empty.value:
			duration = 32
		else:
			duration = 16

		for i in range(s[3]+1):
			duration = int(duration/2)
		if duration < 1:
			duration = 1

		step = base_step
		octave = base_oct

		dist = round((s[2] - staff_middle) / semitone_dist)
		step = step - dist

		while step > 6:
			step = step - 7
			octave = octave + 1

		while step < 0:
			step = step + 7
			octave = octave - 1

		f.write(f'''
			<note>
				<pitch>
					<step>{n_to_step[step]}</step>
					<octave>{str(octave)}</octave>
				</pitch>
				<duration>{str(duration)}</duration>
			</note>''')

		measure_timer = measure_timer - duration

	if s[0] == Symbols.rest_wholehalf.value and len(s) == 4:
		duration = 32 if s[3] == 0 else 16
		f.write(f'''
			<note>
				<rest/>
				<duration>{duration}</duration>
			</note>''')
		measure_timer = measure_timer - duration

	if s[0] == Symbols.rest_quarter.value:
		f.write('''
			<note>
				<rest/>
				<duration>8</duration>
			</note>''')
		measure_timer = measure_timer - 8

	if s[0] == Symbols.rest_eighth.value:
		f.write('''
			<note>
				<rest/>
				<duration>4</duration>
			</note>''')
		measure_timer = measure_timer - 4

	if s[0] == Symbols.rest_sixteenth.value:
		f.write('''
			<note>
				<rest/>
				<duration>2</duration>
			</note>''')
		measure_timer = measure_timer - 2

	if s[0] == Symbols.rest_thirtysecond.value:
		f.write('''
			<note>
				<rest/>
				<duration>1</duration>
			</note>''')
		measure_timer = measure_timer - 1

	if measure_timer <= 0:
		measure_timer = 32
		measure_n = measure_n + 1
		f.write(f'''
		</measure>
		<measure number="{measure_n}">''')

f.write('''
		</measure>
	</part>
</score-partwise>
	''')

f.close()