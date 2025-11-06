import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Cargar archivo
df = pd.read_csv("../Datos/Enf_USA.csv", encoding="utf-8")

# Filtrar registros del tema Oral Health con preguntas que contengan "teeth"
df_oral = df[df["Topic"] == "Oral Health"].copy()
df_teeth = df_oral[df_oral["Question"].str.contains("teeth", case=False, na=False)].copy()

# Seleccionar columnas útiles
cols = ["LocationDesc", "Question", "Response", "Stratification1", "DataValue"]
df_teeth = df_teeth[cols].copy()
df_teeth["Categoria"] = df_teeth["Response"].fillna(df_teeth["Stratification1"])
df_teeth = df_teeth.dropna(subset=["DataValue", "Categoria"]).copy()
df_teeth["DataValue"] = pd.to_numeric(df_teeth["DataValue"], errors="coerce")
df_teeth = df_teeth.dropna(subset=["DataValue"])
df_teeth = df_teeth[~df_teeth["Categoria"].isin(["", " ", "Unknown", "Data not available"])]

# Indicadores de Oral Health
indicadores = [
    "All teeth lost among adults aged 65 years and older",
    "Six or more teeth lost among adults aged 65 years and older",
    "No teeth lost among adults aged 18-64 years"
]

df_alllost = df_teeth[df_teeth["Question"] == indicadores[0]].copy()
df_sixplus = df_teeth[df_teeth["Question"] == indicadores[1]].copy()
df_noteeth = df_teeth[df_teeth["Question"] == indicadores[2]].copy()

# Razas de interés
raciales = ["Hispanic", "White, non-Hispanic", "Black, non-Hispanic"]
df_race = df_teeth[df_teeth["Categoria"].isin(raciales)].copy()


#  1) PAIRPLOT: Relación entre indicadores dentales
# Crear tabla de correlación base
df_corr_data = df_teeth[df_teeth["Question"].isin(indicadores)].copy()
tabla_corr = df_corr_data.pivot_table(values="DataValue", index="LocationDesc", columns="Question", aggfunc="mean")

# Renombrar columnas para simplificar
cols_map = {col: ("All lost (65+)" if "All teeth lost" in col else
                  "6+ lost (65+)" if "Six or more" in col else
                  "No lost (18–64)") for col in tabla_corr.columns}
tabla_corr = tabla_corr.rename(columns=cols_map)

# Asegurar que no haya NaN y reordenar columnas
tabla_corr = tabla_corr.dropna()
cols_order = ["All lost (65+)", "6+ lost (65+)", "No lost (18–64)"]
tabla_corr = tabla_corr[cols_order]

# Crear pairplot
sns.set_style("white")
g = sns.pairplot(
    tabla_corr,
    diag_kind="kde",
    kind="reg",  # líneas de regresión
    corner=False,
    height=3,
    plot_kws={"scatter_kws": {"s": 50, "alpha": 0.6}, "line_kws": {"color": "black", "lw": 1}},
    diag_kws={"fill": True}
)
g.fig.suptitle("1) Relaciones entre indicadores de pérdida dental", y=1.03)
plt.tight_layout()
plt.show()


# 2) Boxplot por sexo (All teeth lost, ≥65)
df_gender = df_alllost[df_alllost["Categoria"].isin(["Male", "Female"])].copy()
if not df_gender.empty:
    plt.figure(figsize=(7, 5))
    sns.boxplot(x="Categoria", y="DataValue", hue="Categoria", data=df_gender, palette="Set2")
    plt.title("2) Pérdida total de dientes (≥65) por sexo")
    plt.xlabel("Sexo")
    plt.ylabel("Porcentaje (%)")
    plt.tight_layout()
    plt.show()
else:
    print("No hay datos de sexo para 'All teeth lost'.")


# 3) Heatmap: Indicadores dentales promedio por estado
# Combinar promedios por estado para los tres indicadores
df_all_mean = df_alllost.groupby("LocationDesc")["DataValue"].mean()
df_six_mean = df_sixplus.groupby("LocationDesc")["DataValue"].mean()
df_no_mean = df_noteeth.groupby("LocationDesc")["DataValue"].mean()

df_heat = pd.concat([df_all_mean, df_six_mean, df_no_mean], axis=1)
df_heat.columns = ["All lost (65+)", "6+ lost (65+)", "No lost (18–64)"]
df_heat = df_heat.dropna()

if not df_heat.empty:
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        df_heat,
        cmap="coolwarm_r",  # _r invierte los colores (más pérdida = más rojo)
        linewidths=0.4,
        annot=False,
        cbar_kws={"label": "Porcentaje promedio (%)"}
    )
    plt.title("3) Indicadores dentales promedio por estado")
    plt.xlabel("Indicadores")
    plt.ylabel("Estado")
    plt.tight_layout()
    plt.show()
else:
    print("No hay datos suficientes para el gráfico 3.")



# 4) Gráficos de barras agrupadas: indicadores por raza
df_ind = df_race[df_race["Question"].isin(indicadores)].copy()
if not df_ind.empty:
    df_ind["Indicador"] = df_ind["Question"].replace({
        indicadores[0]: "All lost",
        indicadores[1]: "6+ lost",
        indicadores[2]: "No lost"
    })
    plt.figure(figsize=(9, 6))
    sns.barplot(x="Indicador", y="DataValue", hue="Categoria", data=df_ind,
                estimator="mean", errorbar="sd", palette="coolwarm")
    plt.title("4) Indicadores dentales por raza")
    plt.xlabel("Indicador")
    plt.ylabel("Porcentaje (%)")
    plt.legend(title="Raza")
    plt.tight_layout()
    plt.show()
else:
    print("No hay datos raciales suficientes para el gráfico 4.")


# 5) KDE bivariado: pérdida dental vs deterioro cognitivo
df_cog = df[df["Topic"].str.contains("Cognitive Health", case=False, na=False)].copy()
df_decline = df_cog[df_cog["Question"] == "Subjective cognitive decline among adults aged 45 years and older"].copy()

if not df_decline.empty:
    df_cog_mean = df_decline.groupby("LocationDesc")["DataValue"].mean().reset_index().rename(columns={"DataValue": "Cognitive_mean"})
    df_teeth_mean = df_alllost.groupby("LocationDesc")["DataValue"].mean().reset_index().rename(columns={"DataValue": "Teeth_mean"})
    df_merge = pd.merge(df_teeth_mean, df_cog_mean, on="LocationDesc", how="inner")

    if not df_merge.empty:
        plt.figure(figsize=(7, 6))
        sns.kdeplot(
            data=df_merge,
            x="Teeth_mean",
            y="Cognitive_mean",
            fill=True,  # ya actualizado (antes era shade)
            cmap="mako",
            thresh=0.05,
            levels=15
        )
        sns.scatterplot(
            data=df_merge,
            x="Teeth_mean",
            y="Cognitive_mean",
            color="black",
            alpha=0.6,
            s=40
        )
        plt.title("5) Pérdida dental vs deterioro cognitivo")
        plt.xlabel("Pérdida dental promedio (%)")
        plt.ylabel("Declive cognitivo promedio (%)")
        plt.tight_layout()
        plt.show()

        corr5 = df_merge[["Teeth_mean", "Cognitive_mean"]].corr().iloc[0, 1]
        print(f"Correlación pérdida dental vs declive cognitivo: r={corr5:.3f}")
    else:
        print("No hay estados comunes entre pérdida dental y cognición.")
else:
    print("No se encontró información de salud cognitiva.")
