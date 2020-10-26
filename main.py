from auxiliares import *
'''
df_1 = open_file(data=pd.DataFrame())
df_2 = open_file(data=pd.DataFrame())
df = df_1.append(df_2)
'''
df = open_file()

i=0

for i, columna in zip(range(len(df.columns)), df.columns):
    print(str(i)+". "+columna)

columna_fecha = df.columns[int(input('Seleccione la columna de fecha: '))]

columna_valor = ""
mes_base = int(input("Ingrese mes base: "))
mes_tope = int(input("Ingrese mes tope: "))

if input('Calcular el monto? (y/n)').lower() == 'y':
    columna_cantidad = int(input('Seleccione la columna de cantidad: '))
    columna_unitario = int(input('Seleccione la columna de valor unitario: '))
    if input('Actualizar unita rio? (y/n)').lower() == 'y':
        df_precios = open_file()
        df = actualizar_precios(df, df_precios, columna_fecha, df.columns[columna_unitario], [mes_base, mes_tope],
                                'renglon_y_proveedor')
    df['MONTO_TOTAL'] = df[df.columns[columna_cantidad]] * df[df.columns[columna_unitario]]
    columna_valor = 'MONTO_TOTAL'
else:
    columna_valor = df.columns[int(input('Seleccione la columna de valor: '))]

organizador = Organizador([2020, 2019], columna_fecha, columna_valor)
# df.loc[df.Linea_Status == 'Bonificado COVID-19', 'Copias'] = 0
variaciones = get_variacion_interanual(df, organizador, operacion='diferencia', factor=10**6)
print(variaciones)
# variaciones = get_variacion_categoria(df, organizador, 'Bonificado COVID-19', 'Linea_Status')
graficar_variaciones2(variaciones, [mes_base, mes_tope], MESES, titulo='Ahorro mensual en aguas')

#graficar_variaciones(variaciones, organizador, valores_limite=[mes_base, mes_tope], formato='{:.2f}M', modo='completo',
 #                    titulo='Ahorro mensual en aguas')
