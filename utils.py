import pandas as pd
import os
class Utils:
    
 def filtrar_columnas(self, df, vector):
    """
    Filtra el DataFrame para quedarse únicamente con las columnas indicadas en `vector`.

    Args:
        df (pd.DataFrame): DataFrame original.
        vector (list[str]): Lista de nombres de columnas a conservar.

    Returns:
        pd.DataFrame: Sub-DataFrame con solo las columnas válidas.
    """
    cols_existentes = [c for c in vector if c in df.columns]
    faltantes = [c for c in vector if c not in df.columns]
    if faltantes:
        print(f"Advertencia: estas columnas no existen y se omiten: {faltantes}")
    return df[cols_existentes]

 def agregar_columna_binaria(self, df, columna):
        """
        Agrega al DataFrame una columna binaria que indica si el valor
        en `columna` es NaN (0) o no (1).

        Args:
            df (pd.DataFrame): DataFrame original.
            columna (str): Nombre de la columna a evaluar.

        Returns:
            pd.DataFrame: Copia del DataFrame con la nueva columna `{columna}_binaria`.
        """
        df_out = df.copy()
        nueva = f"{columna}_binaria"
        # .notna() devuelve True si no es NaN; .astype(int) convierte True/False a 1/0
        df_out[nueva] = df_out[columna].notna().astype(int)
        return df_out


 def agregar_dummies(self, df, col):
        """
        Agrega columnas dummy (0/1) para cada categoría de `col`.

        Args:
            df: DataFrame de entrada.
            col: Nombre de la columna categórica.

        Returns:
            DataFrame con las nuevas columnas "{col}_{valor}_dummy" de tipo int.
        """
        if col not in df.columns:
            print(f"Advertencia: '{col}' no existe.")
            return df.copy()
        
        df_out = df.copy()
        # Crear dummies como int directamente
        dummies = pd.get_dummies(df_out[col], prefix=col, dtype=int)
        # Renombrar para añadir sufijo '_dummy'
        dummies.columns = [f"{c}_dummy" for c in dummies.columns]
        # Unir al DataFrame original
        return pd.concat([df_out, dummies], axis=1)
    
 def fusionar_dataframes(self, df1, df2, key1, key2):
        """
        Une df2 a df1 tomando key1 de df1 y key2 de df2,
        agregando todas las columnas de df2 (menos key2)
        y manteniendo únicamente key1.

        Args:
            df1: DataFrame base.
            df2: DataFrame con datos a agregar.
            key1: Nombre de la columna llave en df1.
            key2: Nombre de la columna llave en df2.

        Returns:
            DataFrame resultante de la unión.
        """
        # Renombrar key2 a key1 para poder hacer el merge
        tmp = df2.rename(columns={key2: key1})
        # Seleccionar sólo key1 + las demás columnas de tmp
        cols = [c for c in tmp.columns if c != key1]
        # Hacer left merge y devolver
        return df1.merge(tmp[[key1] + cols], on=key1, how='left')

 def generar_features_fecha(self, df, col):
        """
        A partir de una columna de fecha en formato día/mes/año, agrega al DataFrame:
        - mes: número de mes (1–12)
        - dia: número de día del mes (1–31)
        - mes_anio: texto 'YYYY-MM'
        - dia_del_anio: día ordinal del año (1–365/366)
        - mes_anio_contador: índice de mes contado desde el primer mes del df (1,2,3…)
        - lunes_semana: fecha del lunes correspondiente a la semana de cada fecha

        Args:
            df: pd.DataFrame original.
            col: nombre de la columna que contiene las fechas en 'DD/MM/YYYY'.

        Returns:
            pd.DataFrame con las nuevas columnas.
        """
        df_out = df.copy()
        # Parsear con dayfirst=True para formato DD/MM/YYYY
        df_out[col] = pd.to_datetime(df_out[col], dayfirst=True, errors='coerce')
        # Extraer mes y día
        df_out['mes'] = df_out[col].dt.month
        df_out['dia'] = df_out[col].dt.day
        # YYYY-MM
        df_out['mes_anio'] = df_out[col].dt.strftime('%Y-%m')
        # Día del año
        df_out['dia_del_anio'] = df_out[col].dt.dayofyear
        # Índice de mes-año relativo
        periods = df_out[col].dt.to_period('M')
        primera = periods.min()
        df_out['mes_anio_contador'] = periods.apply(
            lambda p: (p.year - primera.year) * 12 + (p.month - primera.month) + 1
        )
        # Fecha del lunes de cada semana
        df_out['lunes_semana'] = df_out[col] - pd.to_timedelta(df_out[col].dt.weekday, unit='D')
        return df_out

 def asignar_grupos(self, df, col):
        """
        Agrega al DataFrame una columna 'grupo' donde:
        - 1 si el valor de `col` (Revisor) está en el grupo 1
        - 2 en caso contrario

        Grupo 1: Jeniffer Caballero, Cristian Gil, Valentina Bernal (insensible a mayúsculas/minúsculas).

        Args:
            df: pd.DataFrame de entrada.
            col: nombre de la columna que contiene al revisor.

        Returns:
            pd.DataFrame con la nueva columna 'grupo'.
        """
        df_out = df.copy()
        # Lista de revisores del grupo 1 en minúsculas
        grupo1 = {'jeniffer caballero', 'cristian gil', 'valentina bernal'}
        # Normalizar texto y asignar grupo
        df_out['grupo'] = (
            df_out[col]
            .astype(str)
            .str.strip()
            .str.lower()
            .apply(lambda x: 1 if x in grupo1 else 2)
        )
        return df_out

