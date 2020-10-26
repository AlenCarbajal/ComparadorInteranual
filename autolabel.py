from matplotlib import axes


def autolabel(ax, rects, size=14, formato='{:.2f}', mode='normal', labels=[]):
	"""
	Función que añade las etiquetas de datos correspondientes a los bar-charts de matplotlib
	:param rects: array de rectangulos
	:param size: tamaño de la fuente
	:param formato: cómo deberían mostrarse los datos. Por defecto se asume float con 2 decimales.
	"""
	if mode == 'normal':
		for rect in rects:
			height = rect.get_height()
			if height >= 0:
				va_ = "bottom"
			else:
				va_ = "top"
			ax.text(x=rect.get_x() + rect.get_width() / 2, y=height, s=formato.format(height),
			        ha='center', va=va_, fontsize=size)
	elif mode == 'custom':
		for rect, label in zip(rects, labels):
			height = rect.get_height()
			if height >= 0:
				va_ = "bottom"
			else:
				va_ = "top"
			type(label)
			if label is tuple:
				print(label)
				ax.text(x=rect.get_x() + rect.get_width() / 2, y=height, s=formato.format(label),
				        ha='center', va=va_, fontsize=size)
			else:
				ax.text(x=rect.get_x() + rect.get_width() / 2, y=height, s=formato.format(label),
				        ha='center', va=va_, fontsize=size)
