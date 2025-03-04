import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import pathlib
import datetime
import math

st.set_page_config(
    page_title="Perú: indicadores económicos",
    layout="wide")
st.sidebar.title("Perú: indicadores económicos")

def BCRPseries(SeriesDict, inicio=1970, fin=2022):
    if type(SeriesDict) != dict:
        print("Las serie(s) no tiene(n) la forma de un diccionario")
    else:
        SeriesDict = {k: v for k, v in sorted(SeriesDict.items(), key=lambda item: item[1])}
        # Encadena las series a ser consultadas
        series = ''
        for i,key in enumerate(SeriesDict):
            if i == 0:
                series = str(SeriesDict[key])
            else:
                series = series + '-' + str(SeriesDict[key])
        # Encadena la dirección, las series y las fechas de consulta
        string1 = 'https://estadisticas.bcrp.gob.pe/estadisticas/series/api/'
        string2 = '/txt/'
        inicio = str(inicio)
        fin = str(fin)
        stringfinal = string1+series+string2+inicio+'/'+fin
        # Renombra las series
        names = [n for n in SeriesDict.keys()]
        names.insert(0, 'Período')
        # returns a dataframe
        return pd.read_csv(stringfinal, sep='\t', skiprows=[0], names=names)

def growth(data, serie):
    #return np.round((data[serie][len(data)-1]/data[serie][0])**(1/(len(data)-1))-1, 4) * 100
    return "{:.2f}".format(((data[serie][len(data)-1]/data[serie][0])**(1/(len(data)-1))-1) * 100)

def promedio(data, serie):
    return np.round(np.average(data[serie]), 1)

st.sidebar.markdown('Seleccione el período de visualización')
# Rango de series estadísticas
año_inicial = 2000
año_final = datetime.datetime.now().year - 1
inicio = st.sidebar.slider('Año de inicio', año_inicial, año_final-1, value=año_inicial)
fin = st.sidebar.slider('Año de finalización', año_inicial, año_final, value=año_final)

st.sidebar.subheader('Categorías')
choice = st.sidebar.radio('', ('Producto', 'Precios', 'Coyuntura', 'Comercio Exterior'))

col = st.columns((6,6), gap='medium')

if choice == 'Producto':
    serie_anual = {'PBI en US$': 'PM05373BA'
                }
    # Serie anual a precios constantes de 2007
    serie_PBI_anual = {'PBI Soles 2007': 'PM04935AA',
                    'Inversión Privada Soles 2007': 'PM04930AA',
                    'Inversión Pública Soles 2007': 'PM04931AA',
                    'Consumo Privado Soles 2007':'PM04926AA',
                    'Consumo Publico Soles 2007':'PM04927AA',
                    'Variacion Inventarios Soles 2007':'PM04932AA',
                    'Exportaciones Soles 2007':'PM04933AA',
                    'Importaciones Soles 2007':'PM04934AA'
                }
    serie_trimestral = {'PBI Variación Real Trimestral': 'PN02517AQ',
                        'Inversión Privada Variación Real Trimestral':'PN02522AQ',
                        'Inversión Pública Variación Real Trimestral':'PN02523AQ',
                        }
    data1 = BCRPseries(serie_anual, inicio, fin)
    data2 = BCRPseries(serie_trimestral, inicio, fin)
    data_PBI = BCRPseries(serie_PBI_anual, inicio, fin)
    data_PBI['Inversión Privada'] = data_PBI['Inversión Privada Soles 2007']/(data_PBI['Inversión Privada Soles 2007']+data_PBI['Inversión Pública Soles 2007'])*100
    data_PBI['Inversión Pública'] = data_PBI['Inversión Pública Soles 2007']/(data_PBI['Inversión Privada Soles 2007']+data_PBI['Inversión Pública Soles 2007'])*100
    PBI_modified = pd.DataFrame()
    PBI_modified['Inversión Privada'] = data_PBI['Inversión Privada Soles 2007']/(data_PBI['PBI Soles 2007']+data_PBI['Importaciones Soles 2007']-data_PBI['Variacion Inventarios Soles 2007'])
    PBI_modified['Inversión Pública'] = data_PBI['Inversión Pública Soles 2007']/(data_PBI['PBI Soles 2007']+data_PBI['Importaciones Soles 2007']-data_PBI['Variacion Inventarios Soles 2007'])
    PBI_modified['Consumo Privado'] = data_PBI['Consumo Privado Soles 2007']/(data_PBI['PBI Soles 2007']+data_PBI['Importaciones Soles 2007']-data_PBI['Variacion Inventarios Soles 2007'])
    PBI_modified['Consumo Publico'] = data_PBI['Consumo Publico Soles 2007']/(data_PBI['PBI Soles 2007']+data_PBI['Importaciones Soles 2007']-data_PBI['Variacion Inventarios Soles 2007'])
    PBI_modified['Exportaciones'] = data_PBI['Exportaciones Soles 2007']/(data_PBI['PBI Soles 2007']+data_PBI['Importaciones Soles 2007']-data_PBI['Variacion Inventarios Soles 2007'])
    with col[0]:
        st.header(choice)
        st.divider()
        fig11 = px.bar(data1, x='Período', y='PBI en US$', title='PBI en US$', 
                       labels={'PBI en US$':"miles de millones", "Período":" "}, height=400)
        st.plotly_chart(fig11, key=11)
        st.write(f"<center>Tasa de crecimiento anualizada {growth(data1, 'PBI en US$')}%</center>", unsafe_allow_html=True)
        fig12 = px.pie(PBI_modified, list(PBI_modified.iloc[0:].columns), PBI_modified.iloc[0:].values[0], title=f'PBI por tipo de gasto<br>{data_PBI["Período"].values[0]}')
        st.plotly_chart(fig12, key=12)
        fig13 = px.bar(data_PBI, x='Período', y=[data_PBI['Inversión Privada'], data_PBI['Inversión Pública']], title='Inversión Bruta Fija', 
                       labels={"value":"Porcentajes", "Período":" "}, height=400)
        fig13.update_layout(legend=dict(yanchor="bottom", y=0.02, xanchor="left", x=0.01), legend_title="",)
        st.plotly_chart(fig13)
        st.write(f"<center>Promedio Inversión: Privada {promedio(data_PBI, 'Inversión Privada')}% - Pública {promedio(data_PBI, 'Inversión Pública')}%</center>", unsafe_allow_html=True)

    with col[1]:
        st.header("")
        st.divider()
        fig21 = px.bar(data2, x='Período', y='PBI Variación Real Trimestral', title='PBI (variación trimestral-anualizada)', 
                       labels={'PBI Variación Real Trimestral':"porcentajes", "Período":" "}, height=400)
        fig21.update_traces(marker_color='orange')
        st.plotly_chart(fig21, key=21)
        st.write("")
        fig22 = px.pie(PBI_modified, list(PBI_modified.iloc[-1:].columns), PBI_modified.iloc[-1:].values[0], title=f'PBI por tipo de gasto<br>{data_PBI["Período"].values[-1]}')
        st.plotly_chart(fig22, key=22)


    # with col[1]:
    #     fig2 = plt.figure(figsize=(3,2))
    #     plt.plot(data['Período'], data['IPC - variacion anual'])
    #     plt.title('Índice de Precios al Consumidor')
    #     st.pyplot(fig2)

if choice == 'Precios':
    serie_anual = {'IPC - variacion anual':'PM05197PA'
                }
    serie_mensual = {'Tarifa Eléctrica Residencial':'PN01444PM',
                     'Cobre ¢US$/Libra':'PN38784BM',
                     'Harina de Pescado US$/Tonelada':'PN38766BM'
                    }
    data1 = BCRPseries(serie_anual, inicio, fin)
    data3 = BCRPseries(serie_mensual, inicio, fin)
    with col[0]:
        st.header(choice)
        st.divider()
        fig31 = px.bar(data1, x='Período', y='IPC - variacion anual', title='Índice de Precios al Consumidor', 
                       labels={'IPC - variacion anual':'variacion anual', "Período":" "}, height=400)
        st.plotly_chart(fig31, key=31)
        fig21 = px.line(data3, x='Período', y='Cobre ¢US$/Libra', title='Precio del Cobre', 
                        labels={"Cobre ¢US$/Libra":"US$/100/Libra", "Período":" "}, height=400)
        fig21.update_traces(line_color='red')
        st.plotly_chart(fig21)
    with col[1]:
        st.header("")
        st.divider()
        fig32 = px.line(data3, x='Período', y='Tarifa Eléctrica Residencial', title='Tarifa Eléctrica - Residencial', 
                        labels={'Tarifa Eléctrica Residencial':'2010 = 100', "Período":" "}, height=400)
        fig32.update_traces(line_color='red')
        st.plotly_chart(fig32, key=32)
        fig22 = px.line(data3, x='Período', y='Harina de Pescado US$/Tonelada', title='Precio de la Harina de Pescado', 
                       labels={'Harina de Pescado US$/Tonelada':'US$/Tonelada', "Período":" "}, height=400)
        st.plotly_chart(fig22)


if choice == 'Coyuntura':
    serie_mensual = {'Electricidad':'PD37965AM',
                    'Consumo de Cemento':'PD37967GM',
                    'Inversión Minera':'PD37982GM',
                    'Colocaciones de Pollo BB':'PD39796PM'
                    }
    data3 = BCRPseries(serie_mensual, inicio, fin)
    with col[0]:
        st.header(choice)
        st.divider()
        fig11 = px.bar(data3, x='Período', y='Electricidad', title='Electricidad', 
                       labels={'Electricidad':'variación % 12 meses', "Período":" "}, height=400)
        fig11.update_traces(marker_color='orange')
        st.plotly_chart(fig11)
        fig21 = px.bar(data3, x='Período', y='Inversión Minera', title='Inversión Minera', 
                       labels={'Inversión Minera':'variación % 12 meses', "Período":" "}, height=400)
        st.plotly_chart(fig21)
    with col[1]:
        st.header("")
        st.divider()
        fig12 = px.line(data3, x='Período', y='Consumo de Cemento', title='Consumo de Cemento', 
                        labels={'Consumo de Cemento':'variación % 12 meses', "Período":" "}, height=400)
        fig12.update_layout(yaxis_range=[-30,30])
        st.plotly_chart(fig12)
        fig22 = px.line(data3, x='Período', y='Colocaciones de Pollo BB', title='Colocaciones de Pollo', 
                        labels={'Colocaciones de Pollo BB':'variación % 12 meses', "Período":" "}, height=400)
        fig22.update_traces(line_color='orange')
        st.plotly_chart(fig22)

if choice == 'Comercio Exterior':
    serie_anual = {'Exportaciones Totales': 'PM05374BA',
                    'Exportaciones Tradicionales':'PM05375BA',
                    'Exportaciones No Tradicionales':'PM05376BA',
                    'Importaciones':'PM05378BA',
                    'Cobre':'PM05435BA'
                    }
    data1 = BCRPseries(serie_anual, inicio, fin)
    data1['Exp'] = data1['Exportaciones Tradicionales'] + data1['Exportaciones No Tradicionales']
    data1['Tradicionales'] = data1['Exportaciones Tradicionales']/data1['Exp'] * 100
    data1['No Tradicionales'] = data1['Exportaciones No Tradicionales']/data1['Exp'] * 100
    with col[0]:
        st.header(choice)
        st.divider()
        fig11 = px.bar(data1, x='Período', y='Exportaciones Totales', title='Exportaciones Totales', 
                       labels={'Exportaciones Totales':"miles de millones de US$", "Período":" "}, height=400)
        fig11.update_traces(marker_color='orange')
        st.plotly_chart(fig11)
        st.write(f"<center>Tasa de crecimiento anualizada {growth(data1, 'Exportaciones Totales')}%</center>", unsafe_allow_html=True)
        fig21 = px.bar(data1, x='Período', y=[data1['Exportaciones Totales']-data1['Importaciones']], title='Balanza Comercial: exportaciones - importaciones', 
                       labels={"value":"miles de millones de US$", "Período":" "}, height=400)
        fig21.update_layout(showlegend=False)
        st.plotly_chart(fig21)
    with col[1]:
        st.header("")
        st.divider()
        fig12 = px.bar(data1, x='Período', y=[data1['Tradicionales'], data1['No Tradicionales']], title='Exportaciones', 
                       labels={"value":"Porcentajes", "Período":" "}, height=400)
        fig12.update_layout(legend=dict(yanchor="bottom", y=0.02, xanchor="left", x=0.01), legend_title="")
        st.plotly_chart(fig12)
        st.write(f"<center>Promedio: Tradicionales {promedio(data1, 'Tradicionales')}% - No Tradicionales {promedio(data1, 'No Tradicionales')}%</center>", unsafe_allow_html=True)
        fig22 = px.bar(data1, x='Período', y='Cobre', title='Exportaciones de Cobre', 
                       labels={'Cobre':"miles de millones de US$", "Período":" "}, height=400)
        fig22.update_traces(marker_color='orange')
        st.plotly_chart(fig22)
        st.write(f"<center>Tasa de crecimiento anualizada {growth(data1, 'Cobre')}%</center>", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.markdown('###### Datos: Banco Central de Reservas del Perú. Cálculos propios.')
st.sidebar.markdown('###### Elaborado por ricardo.campins@gmail.com')