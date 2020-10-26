# Numpy, pandas y ploteo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Otros
import os
from tkinter import filedialog, Tk

# Tiempo/fecha
import time as t
from datetime import datetime

# Propias
from autolabel import *

# Constantes
MESES = ('Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic')


def open_file():
	# open file
	Tk().withdraw()
	filename = filedialog.askopenfilename()
	# Chequeo extensión cargo dataframe
	if filename.endswith('csv'):
		separador = input("Ingrese separador:")
		data = pd.read_csv(filename, sep=separador)
	elif filename.endswith('xlsx') or filename.endswith('xls'):
		data = pd.read_excel(filename)
	else:
		print("Error en el tipo de archivo.")
		raise
	return data


class Organizador(object):
	ejercicios = []
	columna_fecha = ""
	columna_valores = ""

	def __init__(self, ejercicios, columna_ejercicios, columna_valores):
		if (len(ejercicios) != 2) or (ejercicios[0] <= ejercicios[1]):
			print("Error, cantidad de ejercicios distinta de 2 o no estan ordenados.")
			raise
		elif len(columna_valores) == 0:
			print("Error, falta campo valores.")
			raise
		elif len(columna_ejercicios) == 0:
			print("Error, falta campo de ejercicios.")
			raise
		else:
			self.ejercicios = ejercicios
			self.columna_fecha = columna_ejercicios
			self.columna_valores = columna_valores


def actualizar_precios(df_main, df_act, campo_unitario: str, campo_temporal: str, meses: list, tipo: str):
	if tipo == 'renglon_y_proveedor':
		# Obtengo los números de renglón y precio correspondiente
		df_main['AUX_MES_PRECIO'] = pd.DatetimeIndex(df_main[campo_temporal]).month
		for cuit in df_main.CUIT.unique():
			for mes in range(meses[0], meses[1] + 1):
				for renglon in df_act[df_act.CUIT == cuit].RENGLON.unique():
					# Genero filtros y fetch precio
					filtro = (df_main.N_RENGLON_PLIEGO == renglon) & \
					         (df_main.AUX_MES_PRECIO == mes) & \
					         (df_main.CUIT == cuit)
					filtro_precios = (df_act.CUIT == cuit) & \
					                 (df_act.RENGLON == renglon)
					precio = float(df_act[filtro_precios][MESES[mes - 1]].to_numpy())
					# Asigno
					df_main.loc[filtro, campo_unitario] = precio
	return df_main


def get_variacion_interanual(df: pd.DataFrame, organizador: Organizador, operacion: str, factor) -> pd.DataFrame:
	df['AUX_MES'] = pd.DatetimeIndex(df[organizador.columna_fecha]).month
	df['AUX_ANIO'] = pd.DatetimeIndex(df[organizador.columna_fecha]).year
	df = df[
		(df.AUX_ANIO == organizador.ejercicios[0]) | (df.AUX_ANIO == organizador.ejercicios[1])]
	df = df.groupby(['AUX_ANIO', 'AUX_MES'])[organizador.columna_valores].sum().reset_index()
	df[organizador.columna_valores] = df[organizador.columna_valores] / factor
	ret = df.pivot(index='AUX_MES', columns='AUX_ANIO', values=organizador.columna_valores)
	ret = ret.rename(columns={'index': 'AUX_MES'})
	ret = ret.reset_index()
	ret['VARIACION'] = ret[organizador.ejercicios[0]] - ret[organizador.ejercicios[1]]
	df_ = pd.DataFrame(columns=["AUX_MES", "VALOR", "CATEGORIA"])
	for columna in ret.columns[-3:]:
		aux = pd.DataFrame(columns=["AUX_MES", "VALOR", "CATEGORIA"])
		aux["AUX_MES"] = ret["AUX_MES"]
		aux["CATEGORIA"] = columna
		aux["VALOR"] = ret[columna]
		df_ = df_.append(aux)
	return df_


def get_variacion_categoria(df, organizador, categoria, columna_categoria):
	df['AUX_MES'] = pd.DatetimeIndex(df[organizador.columna_fecha]).month
	df[categoria] = df[organizador.columna_valores] * (df[columna_categoria] == categoria)
	df = df.groupby('AUX_MES')[[organizador.columna_valores, categoria]].sum().reset_index()
	df['VARIACION'] = (df[categoria] / df[organizador.columna_valores]) * 100
	df[organizador.columna_valores] = df[organizador.columna_valores] / 10 ** 6
	df[categoria] = df[categoria] / 10 ** 6
	return df


def graficar_variaciones2(df: pd.DataFrame, valores_limite: list, xlabels, titulo='', nombre_x='', nombre_y=''):
	sns.set_theme(style="whitegrid")
	df = df[(df["AUX_MES"] >= valores_limite[0]) & (df["AUX_MES"] <= valores_limite[1])]
	plt.figure(figsize=(15, 10))
	g = sns.barplot(
		data=df,
		x="AUX_MES", y="VALOR", hue="CATEGORIA",
		ci="sd", palette="dark", alpha=.8
	)
	g.set(xlabel=nombre_x, ylabel=nombre_y)
	df.sort_values(by=["AUX_MES"])
	for p in g.patches:
		if p.get_height() >= 0:
			va_ = "bottom"
		else:
			va_ = "top"
		padding = np.sign(p.get_height()) * 2
		g.annotate(format(p.get_height(), '.2f'),
		           (p.get_x() + p.get_width() / 2., p.get_height()),
		           ha='center', va=va_,
		           size=15, xytext=(0, padding),
		           textcoords='offset points')
	plt.title(titulo, fontsize=25)
	plt.setp(g.get_xticklabels(), fontsize=20)
	plt.setp(g, xticklabels=xlabels[valores_limite[0] - 1:valores_limite[1]])
	plt.setp(g.get_legend().get_texts(), fontsize='22')  # for legend text
	plt.setp(g.get_legend().get_title(), text='Leyenda', fontsize='32')  # for legend title
	if 'Graficos' not in os.listdir():
		os.mkdir('Graficos')
	plt.savefig(
		'Graficos/{}.png'.format(datetime.fromtimestamp(t.time()).strftime('%Y%m%d%H%M%S')),
		bbox_inches='tight')


def graficar_variaciones(df, organizador: Organizador, valores_limite: list, formato='{:.2f}', width=0.9,
                         xlabels=MESES, modo='completo', titulo=''):
	df = df[(df.AUX_MES >= valores_limite[0]) & (df.AUX_MES <= valores_limite[1])]
	plt.figure(figsize=(10, 10), dpi=200, facecolor='w', edgecolor='k')

	# Colores de cada barra
	colores = ['g', 'r', 'b']
	ax = plt.subplot(111)
	ax.set_title(titulo, fontsize=20)

	cantidad_barras = 0
	labels_list = df['CATEGORIA'].unique()
	labels = []
	pos_leyenda = (1, 1)
	if modo == 'completo':
		cantidad_barras = 3
		organizador.ejercicios.reverse()
		for label in labels_list:
			labels.append(
				'{}: {}'.format(str(label).title(), formato.format(df[df['CATEGORIA'] == label]['VALOR'].sum())))
		pos_leyenda = (0.95, 1.01)
	elif modo == 'variacion':
		cantidad_barras = 1
		colores = [(0.2, 0.4, 0.6, 1)]
		labels = ['Variacion media: {}'.format(formato.format(df[df['CATEGORIA'] == 'VARIACION']['VALOR'].mean()))]
		pos_leyenda = (0.95, 1)
	elif modo == 'comparativo':
		cantidad_barras = 2
		labels = labels_list
		pos_leyenda = (0.95, 1)

	print(df)
	# Genero ejes, barras y etiqueto cada una de ellas
	for i in range(cantidad_barras):
		x = np.arange(valores_limite[1] - valores_limite[0] + 1) + (
				(width / cantidad_barras) * (i - cantidad_barras / 2))
		bar = ax.bar(x, df[df['CATEGORIA'] == labels_list[i]]['VALOR'].to_numpy(), width=width / cantidad_barras,
		             color=colores[i], align='center', label=labels[i])
		if modo in ['completo', 'variacion']:
			autolabel(ax, bar)
		else:
			if i == 0:
				autolabel(ax, bar, mode='custom', labels=df['PrecioBase'], formato='{:.2}M')
			else:
				autolabel(ax, bar, mode='custom',
				          labels=['{:.2f}M\n({:.2f}%)'.format(a, b) for a, b in df[['', 'VALOR']].to_numpy()],
				          formato='{}')

	# Formato leyenda
	ax.legend(loc='best', bbox_to_anchor=pos_leyenda, bbox_transform=plt.gcf().transFigure, fontsize='x-large')

	# Formato del eje Y
	for tick in ax.yaxis.get_major_ticks():
		tick.label.set_fontsize(14)
	ax.set_yscale('linear')
	ax.grid(axis='y', linewidth=0.2)  # Agrego lineas horizontales al grafico

	# Formato del eje X
	ax.ticklabel_format(style='plain', useOffset=False, axis='both')
	plt.setp(ax.get_xticklabels(), fontsize=14)
	plt.setp(ax, xticks=np.arange(valores_limite[1] - valores_limite[0] + 1) - width / (2 * cantidad_barras),
	         xticklabels=xlabels[valores_limite[0] - 1:valores_limite[1]])
	if 'Graficos' not in os.listdir():
		os.mkdir('Graficos')
	plt.savefig(
		'Graficos/{}.png'.format(datetime.fromtimestamp(t.time()).strftime('%Y%m%d%H%M%S')),
		bbox_inches='tight')


def change_width(ax, new_value):
	for patch in ax.patches:
		current_width = patch.get_width()
		diff = current_width - new_value

		# we change the bar width
		patch.set_width(new_value)

		# we recenter the bar
		patch.set_x(patch.get_x() + diff * (1/3))
