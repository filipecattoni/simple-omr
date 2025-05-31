def segment_staves(img, grouped_staff_rows):

	# deve retornar uma lista de pares com os valores de inicio e fim de cada pentagrama

	staves_n = int(len(grouped_staff_rows)/5)
	staffspace_height = grouped_staff_rows[1][0] - grouped_staff_rows[0][0]

	bounds = []

	for i in range(staves_n):
		upper = grouped_staff_rows[i*5][0] - staffspace_height*4
		if upper < 0:
			upper = 0
		lower = grouped_staff_rows[i*5+4][-1] + staffspace_height*4
		if lower > len(img):
			lower = len(img)
		bounds.append([upper, lower])

	return bounds