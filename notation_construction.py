from config import *

n_to_step = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

base_note_vals = [
	[6, 4], # treble
	[1, 3], # bass
	[0, 4]  # alto
]

max_measure_timer = 32

def output_xml(symbols, staff_rows, staffspace_height, staffline_height, scale, beats, beat_type):

	symbols.sort(key=lambda x: x[1])

	staff_middle = (sum(staff_rows[2])/len(staff_rows[2]))*scale
	semitone_dist = ((staffspace_height + staffline_height)/2.0)*scale

	divisions = int(32/beat_type)
	max_measure_timer = int(divisions*beats)

	f = open("output.musicxml", "w")

	f.write(f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
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
				<divisions>{divisions}</divisions>
				<time>
					<beats>{beats}</beats>
					<beat-type>{beat_type}</beat-type>
				</time>''')

	base_step, base_oct = base_note_vals[0] # default to treble clef
	attributes_open = True

	measure_timer = max_measure_timer
	measure_n = 1
	flat_notes = []
	sharp_notes = []

	for s in symbols:

		if s[0] == Symbols.clef_treble.value or s[0] == Symbols.clef_bass.value or s[0] == Symbols.clef_alto.value:

			if not attributes_open:

				if measure_timer < max_measure_timer:
					measure_timer = max_measure_timer
					measure_n = measure_n+1
					f.write(f'''
		</measure>
		<measure number="{measure_n}">''')

				attributes_open = True
				f.write('''
			<attributes>''')

			if s[0] == Symbols.clef_treble.value:
				f.write('''
				<clef>
					<sign>G</sign>
					<line>2</line>
				</clef>''')
				base_step, base_oct = base_note_vals[0]

			if s[0] == Symbols.clef_bass.value:
				f.write('''
				<clef>
					<sign>F</sign>
					<line>4</line>
				</clef>''')
				base_step, base_oct = base_note_vals[1]

			if s[0] == Symbols.clef_alto.value:
				f.write('''
				<clef>
					<sign>C</sign>
					<line>3</line>
				</clef>''')
				base_step, base_oct = base_note_vals[2]

		if attributes_open and s[0] >= Symbols.notehead_full.value and s[0] <= Symbols.rest_thirtysecond.value:
			f.write('''
			</attributes>''')
			attributes_open = False

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
					<step>{n_to_step[step]}</step>''')

			note = n_to_step[step] + str(octave)

			if note in flat_notes:
				f.write('''
					<alter>-1</alter>''')

			if note in sharp_notes:
				f.write('''
					<alter>1</alter>''')

			f.write(f'''
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

		if s[0] == Symbols.accidental_flat.value or s[0] == Symbols.accidental_sharp.value or s[0] == Symbols.accidental_natural.value:

			if s[0] == Symbols.accidental_flat.value:
				y = s[2] + int(0.20*symbol_sizes[Symbols.accidental_flat.value][1])
			else:
				y = s[2]

			step = base_step
			octave = base_oct

			dist = round((y - staff_middle) / semitone_dist)
			step = step - dist

			while step > 6:
				step = step - 7
				octave = octave + 1

			while step < 0:
				step = step + 7
				octave = octave - 1

			note = n_to_step[step] + str(octave)

			if s[0] == Symbols.accidental_flat.value:
				flat_notes.append(note)
			if s[0] == Symbols.accidental_sharp.value:
				sharp_notes.append(note)
			if s[0] == Symbols.accidental_natural.value:
				try:
					flat_notes.remove(note)
				except:
					pass
				try:
					sharp_notes.remove(note)
				except:
					pass

		if measure_timer <= 0:
			measure_timer = max_measure_timer
			measure_n = measure_n + 1
			f.write(f'''
		</measure>
		<measure number="{measure_n}">''')
			flat_notes.clear()
			sharp_notes.clear()

	f.write('''
		</measure>
	</part>
</score-partwise>
	''')

	f.close()