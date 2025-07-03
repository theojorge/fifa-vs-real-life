import pickle
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.model_selection import RandomizedSearchCV, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from scipy.stats import uniform, randint
from sklearn.preprocessing import LabelEncoder, StandardScaler
import xgboost as xgb

league_mapping = {
    'Liga Profesional de Fútbol': 'LPF',
    '1. Division': 'Unknown',
    '2. Bundesliga': 'Bundesliga 2',
    '3. Liga': '3. Liga',
    'A-League Men': 'A-League',
    'Allsvenskan': 'Allsvenskan',
    'Bundesliga': 'Bundesliga',
    'Categoría Primera A': 'Liga Colombia',
    'Championship': 'EFL Championship',
    'División Profesional': 'Unknown',
    'División de Fútbol Profesional': 'Unknown',
    'Ekstraklasa': 'PKO BP Ekstraklasa',
    'Eliteserien': 'Eliteserien',
    'Eredivisie': 'Eredivisie',
    'Hrvatska nogometna liga': 'Liga Hrvatska',
    'K League 1': 'K League 1',
    'La Liga': 'LALIGA EA SPORTS',
    'La Liga 2': 'LALIGA HYPERMOTION',
    'League One': 'EFL League One',
    'League Two': 'EFL League Two',
    'Liga 1': 'SUPERLIGA',
    'Liga I': 'SUPERLIGA',
    'Ligue 1': 'Ligue 1 Uber Eats',
    'Ligue 2': 'Ligue 2 BKT',
    'Major League Soccer': 'MLS',
    'Nemzeti Bajnokság I': 'Unknown',
    'Premier Division': 'SSE Airtricity PD',
    'Premier League': 'Premier League',
    'Premiership': 'cinch Prem',
    'Premyer Liqa': 'Unknown',
    'Primeira Liga': 'Liga Portugal',
    'Primera Division': 'Unknown',
    'Primera División': 'Unknown',
    'Pro League': '1A Pro League',
    'První liga': 'Česká Liga',
    'Serie A': 'Serie A TIM',
    'Serie B': 'Serie BKT',
    'Super League': 'CSSL',
    'Superliga': '3F Superliga',
    'Série A': 'Libertadores',
    'Süper Lig': 'Trendyol Süper Lig',
    'Veikkausliiga': 'Finnliiga'
}


def load_model_components(filename='fifa_model.pkl'):
    """
    Carga todos los componentes del modelo
    """
    try:
        with open(filename, 'rb') as f:
            components = pickle.load(f)

        print(f"✅ Modelo cargado desde: {filename}")
        print(f"📊 Componentes cargados:")
        print(f"   - Modelo: {components['model_type']}")
        print(f"   - OneHot Encoders: {len(components['onehot_encoders']) if components['onehot_encoders'] else 0}")
        print(f"   - MultiLabel Binarizer: {'Sí' if components['mlb'] else 'No'}")
        print(f"   - Features: {len(components['feature_columns'])}")
        print(f"   - Target: {components['target_col']}")
        if 'top_leagues' in components and components['top_leagues']:
            print(f"   - Top Ligas: {len(components['top_leagues'])}")
        else:
            print(f"   - Top Ligas: No especificadas")
        return components

    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {filename}")
        return None
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        return None

def preprocess_new_data(new_data, model_components):
    """
    Preprocesa nuevos datos usando los encoders guardados
    """
    if model_components is None:
        print("❌ Error: Componentes del modelo no cargados")
        return None

    print("🔄 Preprocesando nuevos datos...")
    data_processed = new_data.copy()

    onehot_encoders = model_components['onehot_encoders']
    mlb = model_components['mlb']
    target_col = model_components['target_col']

    # Identificar columnas categóricas y numéricas
    categorical_cols = data_processed.select_dtypes(include=['object']).columns.tolist()
    numerical_cols = data_processed.select_dtypes(include=['int64', 'float64']).columns.tolist()

    # Remover target si está presente
    if target_col in categorical_cols:
        categorical_cols.remove(target_col)
    if target_col in numerical_cols:
        numerical_cols.remove(target_col)

    # Columnas especiales
    special_multi_col = 'positions'
    binary_col = 'preferred_foot'
    league_col = 'club_league_name'

    for col in [special_multi_col, binary_col, league_col]:
        if col in categorical_cols:
            categorical_cols.remove(col)

    # Manejar valores nulos
    for col in categorical_cols:
        if data_processed[col].isnull().any():
            data_processed[col] = data_processed[col].fillna('Unknown')

    for col in numerical_cols:
        if data_processed[col].isnull().any():
            median_val = data_processed[col].median()
            data_processed[col] = data_processed[col].fillna(median_val)

    # Codificar preferred_foot como binario
    if binary_col in new_data.columns:
        print(f"Codificando '{binary_col}' como binario...")
        data_processed[binary_col] = data_processed[binary_col].fillna('Unknown')
        data_processed[binary_col] = data_processed[binary_col].map({'Left': 0, 'Right': 1}).fillna(-1).astype(int)

    # Codificar club_league_name con top 10 ligas
    if league_col in new_data.columns and league_col in onehot_encoders:
        
        print(f"Codificando '{league_col}' con OneHotEncoder (top 15 ligas)...")
        fifa_to_full_league = {v: k for k, v in league_mapping.items()}

        # Aplicar mapeo a 'league_name'
        data_processed[league_col] = data_processed[league_col].map(fifa_to_full_league).fillna('Unknown')
        
        data_processed[league_col] = data_processed[league_col].fillna('Unknown')

        # Agrupar ligas no vistas como 'Other'
        known_leagues = list(onehot_encoders[league_col].categories_[0])

        data_processed[league_col] = data_processed[league_col].apply(
            lambda x: x if x in known_leagues else 'Other'
        )

        encoded_cols = onehot_encoders[league_col].transform(data_processed[[league_col]])
        col_names = [f"{league_col}_{cat}" for cat in onehot_encoders[league_col].categories_[0][1:]]
        encoded_df = pd.DataFrame(encoded_cols, columns=col_names, index=data_processed.index)
        data_processed = data_processed.drop(columns=[league_col])
        data_processed = pd.concat([data_processed, encoded_df], axis=1)

    # Aplicar OneHotEncoders para otras columnas categóricas
    for col in categorical_cols:
        if col in onehot_encoders:
            data_processed[col] = data_processed[col].fillna('Unknown')
            encoded_cols = onehot_encoders[col].transform(data_processed[[col]])
            col_names = [f"{col}_{cat}" for cat in onehot_encoders[col].categories_[0][1:]]
            encoded_df = pd.DataFrame(encoded_cols, columns=col_names, index=data_processed.index)
            data_processed = data_processed.drop(columns=[col])
            data_processed = pd.concat([data_processed, encoded_df], axis=1)

    # Procesar player_positions si existe
    if special_multi_col in new_data.columns and mlb is not None:
        data_processed[special_multi_col] = data_processed[special_multi_col].fillna('Unknown')
        multilabel_values = data_processed[special_multi_col].str.split(',\s*')
        position_dummies = pd.DataFrame(mlb.transform(multilabel_values),
                                        columns=[f"pos_{cls}" for cls in mlb.classes_],
                                        index=data_processed.index)
        data_processed = pd.concat([data_processed.drop(columns=[special_multi_col]), position_dummies], axis=1)

    # Asegurar que tenemos todas las columnas del modelo entrenado
    expected_features = model_components['feature_columns']
    missing_cols = set(expected_features) - set(data_processed.columns)

    if missing_cols:
        print(f"⚠️  Columnas faltantes: {missing_cols}")
        for col in missing_cols:
            data_processed[col] = 0

    # Ordenar columnas
    data_processed = data_processed[expected_features]

    print(f"✅ Datos preprocesados: {data_processed.shape}")
    data_processed.to_csv('data_processed.csv', index=False)
    return data_processed

def predict_new_data(new_data, model_components):
    """
    Hace predicciones en nuevos datos
    """
    if model_components is None:
        return None

    # Preprocesar datos
    X_new = preprocess_new_data(new_data, model_components)
    if X_new is None:
        return None

    # Hacer predicciones
    model = model_components['model']
    predictions = model.predict(X_new)
    print(f"\n🎯 Predicciones realizadas: {len(predictions)}")
    print(f"📊 Estadísticas de predicciones:")
    print(f"   Media: {predictions.mean():.2f}")
    print(f"   Mediana: {np.median(predictions):.2f}")
    print(f"   Min: {predictions.min():.2f}")
    print(f"   Max: {predictions.max():.2f}")
    new_data['predicted_price'] = predictions
    return new_data

def test_model_on_new_data(new_data_path=None, new_data_df=None):
    """
    Prueba el modelo en nuevos datos
    """
    # Cargar nuevos datos
    if new_data_df is not None:
        new_data = new_data_df.copy()
        print("📊 Usando datos proporcionados")
    elif new_data_path:
        new_data = pd.read_csv(new_data_path)
        print(f"📊 Datos cargados desde: {new_data_path}")
    else:
        print("❌ Error: Proporciona nuevos datos (DataFrame o ruta)")
        return

    print(f"📈 Nuevos datos: {new_data.shape}")

    # Cargar modelo
    components = load_model_components()
    if components is None:
        return

    # Hacer predicciones
    results = predict_new_data(new_data, components)

    if results is None:
        print("❌ Error en las predicciones")
        return

    # Procesar resultados
    if isinstance(results, tuple):  # Clasificador con probabilidades
        predictions, probabilities = results
        print(f"\n🎯 Predicciones realizadas: {len(predictions)}")
        print(f"📊 Distribución de predicciones:")
        unique, counts = np.unique(predictions, return_counts=True)
        for val, count in zip(unique, counts):
            print(f"   Clase {val}: {count} ({count/len(predictions):.1%})")

        # Agregar predicciones al DataFrame
        new_data['predicted_class'] = predictions
        new_data['predicted_probability'] = probabilities.max(axis=1)

    else:  # Regresor
        predictions = results
        print(f"\n🎯 Predicciones realizadas: {len(predictions)}")
        print(f"📊 Estadísticas de predicciones:")
        print(f"   Media: {predictions.mean():.2f}")
        print(f"   Mediana: {np.median(predictions):.2f}")
        print(f"   Min: {predictions.min():.2f}")
        print(f"   Max: {predictions.max():.2f}")
        # Agregar predicciones al DataFrame
        new_data['predicted_price'] = predictions
    return new_data