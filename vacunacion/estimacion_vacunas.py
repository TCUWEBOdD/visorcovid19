"""
Limpieza de Datos Vacunas
"""
import pandas as pd


def dosis(vacunas=list, lab=None, r=0.5):
    primera = []
    segunda = []
    reserva = []
    contador = len(vacunas)

    if lab == "Pfizer":
        for t in range(contador + 15):
            if t == 0:

                reserva.append(vacunas[t] * (1 - r))
                segunda.append(0)
                primera.append(vacunas[t] * r)

            elif 0 < t < 3:
                segunda.append(0)

                if t < contador:
                    primera.append(vacunas[t] * r)
                    reserva.append((vacunas[t] * (1 - r)) + reserva[t - 1] - segunda[t])
                else:
                    primera.append(0)
                    reserva.append(reserva[t - 1] - segunda[t])

            elif 3 <= t <= 19:
                segunda.append(vacunas[t - 3] * r)

                if t < contador:
                    primera.append(vacunas[t] * r)
                    reserva.append((vacunas[t] * (1 - r)) + reserva[t - 1] - segunda[t])
                else:
                    primera.append(0)
                    reserva.append(reserva[t - 1] - segunda[t])

            elif 7 < t <= (21 + 12):
                segunda.append(0)

                if t < contador:
                    primera.append(vacunas[t] * r)
                    reserva.append((vacunas[t] * (1 - r)) + reserva[t - 1] - segunda[t])

                else:
                    primera.append(0)
                    reserva.append(reserva[t - 1] - segunda[t])

            elif t > (21 + 12):
                segunda.append(vacunas[t - 15] * r)

                if t < contador:
                    primera.append(vacunas[t] * r)
                    reserva.append((vacunas[t] * (1 - r)) + reserva[t - 1] - segunda[t])

                else:
                    primera.append(0)
                    reserva.append(reserva[t - 1] - segunda[t])

    if lab == "AstraZeneca":
        for t in range(contador + 12):
            if t == 0:

                reserva.append(vacunas[t] * (1 - r))
                segunda.append(0)
                primera.append(vacunas[t] * r)

            elif 0 < t < 12:
                segunda.append(0)

                if t < contador:
                    primera.append(vacunas[t] * r)
                    reserva.append((vacunas[t] * (1 - r)) + reserva[t - 1] - segunda[t])
                else:
                    primera.append(0)
                    reserva.append(reserva[t - 1] - segunda[t])

            elif t >= 12:
                segunda.append(vacunas[t - 12] * r)

                if t < contador:
                    primera.append(vacunas[t] * r)
                    reserva.append((vacunas[t] * (1 - r)) + reserva[t - 1] - segunda[t])
                else:
                    primera.append(0)
                    reserva.append(reserva[t - 1] - segunda[t])
    return primera, segunda, reserva


def set_weeks(DataFrame=None):
    DataFrame["fecha"] = pd.to_datetime(
        DataFrame["fecha"], format="%d/%m/%Y"
    )  # estblecer el formato de la fecha
    DataFrame = DataFrame.sort_values("fecha")
    DataFrame = DataFrame.set_index("fecha")
    return DataFrame


def get_doses(DataFrame=None, lab=None):
    DataFrame = DataFrame.loc[DataFrame["laboratorio"] == lab]
    DataFrame = DataFrame.resample(
        "W", label="left"
    ).sum()  # establece el primer día de la semana
    DataFrame = DataFrame.reset_index()
    return DataFrame


# Datos

df = pd.read_csv("vacunas.csv")  # cargamos el set de datos establecemos los formatos

efect = pd.read_csv(
    "efectivas.csv", index_col=False, header=None
)  # cargamos el set de delfino de vacunas semanales

# Limpieza

df = set_weeks(DataFrame=df)

pfizer = get_doses(DataFrame=df, lab="Pfizer")

cantidad_vacun = pfizer["cantidad"].tolist()

max_primera1, max_segunda1, reservas1 = dosis(vacunas=cantidad_vacun, lab="Pfizer")


total_dosis1 = [i + u for i, u in zip(max_primera1, max_segunda1)]

pfizer["max_primera"] = max_primera1[: len(pfizer)]

pfizer["max_segunda"] = max_segunda1[: len(pfizer)]

pfizer["total"] = total_dosis1[: len(pfizer)]

pfizer["reserva"] = reservas1[: len(pfizer)]

pfizer = pfizer.set_index("fecha")
# Calculo AstraZeneza
astra = get_doses(DataFrame=df, lab="AstraZeneca")

cantidad_vacun = astra["cantidad"].tolist()

max_primera2, max_segunda2, reservas2 = dosis(vacunas=cantidad_vacun, lab="AstraZeneca")

total_dosis2 = [i + u for i, u in zip(max_primera2, max_segunda2)]

astra["max_primera"] = max_primera2[: len(astra)]

astra["max_segunda"] = max_segunda2[: len(astra)]

astra["total"] = total_dosis2[: len(astra)]

astra["reserva"] = reservas2[: len(astra)]

astra = astra.set_index("fecha")

df2 = astra.reindex_like(pfizer).fillna(0) + pfizer
df2 = df2.reset_index()
df2["efect"] = efect

df2["cantidad_acumulado"] = df2.cantidad.cumsum()
df2["efectivas_acumulado"] = df2.efect.cumsum()
df2["reservas_reales"] = df2.cantidad_acumulado - df2.efectivas_acumulado

# export

df2.to_csv("vacunas_v2.csv")
