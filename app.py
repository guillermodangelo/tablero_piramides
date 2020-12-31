import streamlit as st
import pandas as pd
import numpy as np
import pylab as pl
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Pirámides de población por localidad 🇺🇾")
st.markdown("Aplicación para comparar pirámides de población de dos localidades "
            "de Uruguay según datos del Censo INE 2011. "
            "*Desarrollada por Guillermo D'Angelo.*")

@st.cache(persist=True)
def load_data(url):
    data = pd.read_csv(url)
    return data

censo = load_data('data/personas_censo_2011_piramides.csv')
deptos = load_data('data/deptos.csv')
locs = load_data('data/locs.csv')

#### sidebars #####
st.sidebar.title('Selección de departamento y localidad')

# sidebar 1
st.sidebar.subheader("Localidad 1")
nom_depto = list(deptos.DEPTO)

nom_depto1 = st.sidebar.selectbox("Departamento", nom_depto, key=1, index=3)
depto1 = list(deptos.loc[deptos.DEPTO == nom_depto1, 'COD'])[0]

nom_loc = list(locs.loc[locs.DPTO==depto1, 'NOMBLOC'])
nom_loc1 = st.sidebar.selectbox("Localidad", nom_loc, key=2)
loc1 = list(locs.loc[(locs.NOMBLOC == nom_loc1) & (locs.DPTO==depto1), 'LOCALIDAD'])[0]


# sidebar 2
st.sidebar.subheader("Localidad 2")

nom_depto2 = st.sidebar.selectbox("Depto.", nom_depto, key=3, index=9)
depto2 = list(deptos.loc[deptos.DEPTO == nom_depto2, 'COD'])[0]

nom_loc = list(locs.loc[locs.DPTO==depto2, 'NOMBLOC'])
nom_loc2 = st.sidebar.selectbox("Loc.", nom_loc, key=4)
loc2 = list(locs.loc[(locs.NOMBLOC == nom_loc2) & (locs.DPTO==depto2), 'LOCALIDAD'])[0]

# ciudades
ciudad_1 = censo.loc[(censo.DPTO==depto1) & (censo.LOC==loc1)].copy()
ciudad_2 = censo.loc[(censo.DPTO==depto2) & (censo.LOC==loc2)].copy()

# dependencia por edad
def dependencia_edad(df):
    pob_dep = df.loc[(df.PERNA01 < 15) | (df.PERNA01 > 64)].count()[0]
    pob_no_dep = df.loc[(df.PERNA01 >= 15) & (df.PERNA01 <= 64)].count()[0]
    return (pob_dep / pob_no_dep)*100

dep_c1 = round(dependencia_edad(ciudad_1), 2)
dep_c2 = round(dependencia_edad(ciudad_2), 2)

# masculinidad
def masculinidad(df, redondeo=2):
    varones = df.loc[df.PERPH02==1].count()[0]
    mujeres = df.loc[df.PERPH02==2].count()[0]
    ind_masc = (varones/mujeres)*100
    return round(ind_masc, redondeo)

masc_c1 =  masculinidad(ciudad_1)
masc_c2 =  masculinidad(ciudad_2)

# textos
data1 = f"""**{nom_loc1}** tiene **{ciudad_1.shape[0]:,}** habitantes, una tasa de dependencia 
            por edades de **{dep_c1}** y un índice de masculinidad de **{masc_c1}** hombres por cada 100 mujeres."""
               
st.markdown(data1)

data2 = f"""**{nom_loc2}** tiene **{ciudad_2.shape[0]:,}** habitantes, una tasa de dependencia 
            por edades de **{dep_c2}** y un índice de masculinidad de **{masc_c2}** hombres por cada 100 mujeres."""
               
st.markdown(data2)


# tramos de edad
def tramos_edad(df):
    import pandas as pd
    import numpy as np
    # genera lista con cortes, para reclasificar el dataframe
    bins = [0 if i==-1 else i for i in range(-1,95,5)]
    bins.append(120)
    # labels
    l1 = [str(i) if i==0 else str(i+1) for i in bins][:19]
    l2 = [str(i) for i in bins][1:]
    labels = ['-'.join([l1[i], l2[i]]) for i in range(19)]
    labels.append('+95')
    # calcula tramos de edad
    df.loc[:, 'tramo'] = pd.cut(df['PERNA01'],
                                bins= bins,
                                include_lowest=True,
                                ordered=True,
                                labels=labels)    
    return df

 # calcula tramos de edad
ciudad_1 = tramos_edad(ciudad_1)
ciudad_2 = tramos_edad(ciudad_2)



# define función para agrupar por tramos y edad
def agrupar_df(df, col_tramo, col_sexo):
    df_group = df.groupby([col_sexo, col_tramo]).size().reset_index()
    df_group.rename(columns={col_sexo: 'sexo', 0:'personas'}, inplace=True)
    df_group['porc_pers'] = (df_group.personas / df_group.personas.sum())*100
    df_group['personas'] = np.where(df_group['sexo'] ==1, -df_group['personas'], df_group['personas'])
    df_group['porc_pers'] = np.where(df_group['sexo'] ==1, -df_group['porc_pers'], df_group['porc_pers'])
    df_group['sexo_label'] = np.where(df_group['sexo'] ==1, 'varones', 'mujeres')
    df_group['tramo_label'] = df_group.tramo.astype(str)
    return df_group

ciudad_1_gr = agrupar_df(ciudad_1,'tramo', 'PERPH02')
ciudad_2_gr = agrupar_df(ciudad_2,'tramo', 'PERPH02')

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

ax1.set_title(nom_loc1)
ax2.set_title(nom_loc2)

for i in [ax1, ax2]:
    i.set_axisbelow(True)
    i.set_ylabel(None)
    i.set_xlabel(None)
    i.axvline(linewidth=1, color='black')
    _ =[s.set_visible(False) for s in i.spines.values()]
    _ =[t.set_visible(False) for t in i.get_yticklines()]

ax1.text(-3, 0.5, 'Varones',
        horizontalalignment='left',
        color='cadetblue', fontsize=10)

ax1.text(3, 0.5, 'Mujeres',
        horizontalalignment='right',
        color='green', fontsize=10)

st.pyplot(fig)