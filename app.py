import streamlit as st
from streamlit_folium import folium_static
import folium
import pandas as pd
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
import seaborn as sns

icon = 'data/flag.png'

st.set_page_config(page_title='Pirámides', page_icon = icon)

st.title("Pirámides de población por localidad 🇺🇾")
st.markdown("Aplicación para comparar pirámides de población de dos localidades "
            "de Uruguay según datos del Censo INE 2011. "
            "*Desarrollada por Guillermo D'Angelo.*")

@st.cache(persist=True)
def load_data(url):
    data = pd.read_csv(url)
    return data

deptos = load_data('data/deptos.csv')
locs = load_data('data/locs.csv')
data_group = load_data('data/data_group.csv')
data_tramos = load_data('data/data_tramos_edad.csv')
coords = load_data('data/coords.csv')


#### sidebars #####
st.sidebar.title('Selección de departamento y localidad 👇')

# sidebar 1
st.sidebar.subheader("Localidad 1")
nom_depto = list(deptos.DEPTO)

nom_depto1 = st.sidebar.selectbox("Departamento", nom_depto, key=1, index=3)
depto1 = list(deptos.loc[deptos.DEPTO == nom_depto1, 'COD'])[0]

nom_loc = list(locs.loc[locs.DPTO==depto1, 'NOMBLOC'])
nom_loc1 = st.sidebar.selectbox("Localidad", nom_loc, key=2)
loc1 = list(locs.loc[(locs.NOMBLOC == nom_loc1) & (locs.DPTO==depto1), 'LOCALIDAD'])[0]

codloc1 = int(str(depto1) + str(loc1).zfill(3))

# sidebar 2
st.sidebar.subheader("Localidad 2")

nom_depto2 = st.sidebar.selectbox("Departamento", nom_depto, key=3, index=9)
depto2 = list(deptos.loc[deptos.DEPTO == nom_depto2, 'COD'])[0]

nom_loc = list(locs.loc[locs.DPTO==depto2, 'NOMBLOC'])
nom_loc2 = st.sidebar.selectbox("Localidad", nom_loc, key=4)
loc2 = list(locs.loc[(locs.NOMBLOC == nom_loc2) & (locs.DPTO==depto2), 'LOCALIDAD'])[0]

codloc2 = int(str(depto2) + str(loc2).zfill(3))

# extrae datos en objetos
c1 = data_group.loc[data_group.CODLOC==codloc1]
c2 = data_group.loc[data_group.CODLOC==codloc2]




# mapita de folium
centroide = [-32.706, -56.0284]

m = folium.Map(location=centroide, zoom_start=6, tiles='OpenStreetMap',
               width='100%', height='100%', left='0%', top='0%')

coords_1 = list(coords.loc[coords.CODLOC==codloc1, ['Y', 'X']].values[0])
coords_2 = list(coords.loc[coords.CODLOC==codloc2, ['Y', 'X']].values[0])

# add marker for Liberty Bell
folium.Marker(coords_1, popup=nom_loc1, tooltip=nom_loc1).add_to(m)
folium.Marker(coords_2, popup=nom_loc2, tooltip=nom_loc2).add_to(m)

# call to render Folium map in Streamlit
folium_static(m)

# texto
def get_round_values(df):
    val1 = df.poblacion.values[0]
    val2 = df.dep_edad.values[0].round(2)
    val3 = df.ind_masc.values[0].round(2)
    return val1, val2, val3

pob_c1, dep_c1, masc_c1 = get_round_values(c1)
pob_c2, dep_c2, masc_c2 = get_round_values(c2)

# textos
data1 = f"""**{nom_loc1}** tiene **{pob_c1}** habitantes, una tasa de dependencia 
            por edades de **{dep_c1}** y un índice de masculinidad de **{masc_c1}** hombres por cada 100 mujeres."""
               
st.markdown(data1)

data2 = f"""**{nom_loc2}** tiene **{pob_c1}** habitantes, una tasa de dependencia 
            por edades de **{dep_c2}** y un índice de masculinidad de **{masc_c2}** hombres por cada 100 mujeres."""
               
st.markdown(data2)


def calc_props(df):
    df['porc_pers'] = (df.personas / df.personas.sum())*100
    df['personas'] = np.where(df['sexo'] ==1, -df['personas'], df['personas'])
    df['porc_pers'] = np.where(df['sexo'] ==1, -df['porc_pers'], df['porc_pers'])
    return df

ciudad_1_gr = calc_props(data_tramos.loc[data_tramos.CODLOC == codloc1])
ciudad_2_gr = calc_props(data_tramos.loc[data_tramos.CODLOC == codloc2])

# pirmides de poblacin
fig, (ax1, ax2)  = plt.subplots(1,2, figsize= ( 10, 6 ), sharex= True, sharey='row')

bins = [0 if i==-1 else i for i in range(-1,95,5)]
bins.append(120)
l1 = [str(i) if i==0 else str(i+1) for i in bins][:19]
l2 = [str(i) for i in bins][1:]
labels = ['-'.join([l1[i], l2[i]]) for i in range(19)]
labels.append('+95')
    
# plot
group_col = 'sexo_label'
order_of_bars = labels[::-1]
colors = ['skyblue', 'seagreen']
label=['sexo', 'sasa']

array_sexo = ciudad_1_gr[group_col].unique()

for c, group in zip(colors, array_sexo):
    sns.barplot(x='porc_pers', y='tramo_label', data=ciudad_1_gr.loc[ciudad_1_gr[group_col]==group, :],
                order = order_of_bars, color=c, label=group, ax=ax1)

for c, group in zip(colors, array_sexo):
    sns.barplot(x='porc_pers', y='tramo_label', data=ciudad_2_gr.loc[ciudad_2_gr[group_col]==group, :],
                order = order_of_bars, color=c, label=group, ax=ax2)

ax1.set_title(nom_loc1, pad=20)
ax2.set_title(nom_loc2, pad=20)

labels = ['8%', '6%','4%','2%','0','2%','4%','6%']

for i in [ax1, ax2]:
    i.set_axisbelow(True)
    i.set_ylabel(None)
    i.set_xlabel(None)
    i.set_xlim([-7.5, 7.5])
    i.axvline(linewidth=1, color='black')
    i.set_xticklabels(labels)
    _ =[s.set_visible(False) for s in i.spines.values()]
    _ =[t.set_visible(False) for t in i.get_yticklines()]

ax1.text(-3, 0.5, 'Varones',
        horizontalalignment='left',
        color='cadetblue', fontsize=10)

ax1.text(3, 0.5, 'Mujeres',
        horizontalalignment='right',
        color='green', fontsize=10)

st.pyplot(fig)