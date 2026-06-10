import streamlit as st
import pandas as pd
import xgboost as xgb
from sklearn.datasets import fetch_california_housing # Base de dados nativa interna

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor de Imóveis", page_icon="🏠", layout="centered")
st.title("🏠 Sistema Inteligente de Avaliação de Imóveis")
st.markdown("Insira os dados da região da Califórnia para estimar o valor médio das casas.")

# 2. Inicialização do modelo usando a base interna (Sem downloads externos)
@st.cache_resource
def inicializar_inteligencia_artificial():
    # Carrega os dados nativos da biblioteca
    california = fetch_california_housing(as_frame=True)
    dados = california.frame
    
    # Mapeia os nomes exatos das colunas da biblioteca
    # MedInc = Renda Média, HouseAge = Idade, AveRooms = Total Quartos
    X = dados[["Longitude", "Latitude", "AveRooms", "HouseAge", "MedInc"]]
    X.columns = ["longitude", "latitude", "total_rooms", "housing_median_age", "median_income"]
    y = dados["MedHouseVal"] * 100000 # Ajusta a escala do preço para valores reais
    
    # Treina o cérebro da IA
    modelo_ia = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, n_jobs=-1)
    modelo_ia.fit(X, y)
    return modelo_ia

# 3. Liga os motores da IA
with st.spinner("Inicializando os motores da Inteligência Artificial..."):
    modelo = inicializar_inteligencia_artificial()

# 4. Criação dos controles visuais do usuário na barra lateral
st.sidebar.header("Parâmetros do Imóvel")
longitude = st.sidebar.slider("Longitude", -124.3, -114.3, -118.0, step=0.1)
latitude = st.sidebar.slider("Latitude", 32.5, 41.9, 34.0, step=0.1)
total_rooms = st.sidebar.number_input("Total de Quartos no Bloco", min_value=1, max_value=40000, value=1000)
housing_median_age = st.sidebar.slider("Idade Média da Casa", 1, 52, 28)
median_income = st.sidebar.number_input("Renda Média do Bairro (em dezenas de milhares)", min_value=0.5, max_value=15.0, value=4.0, step=0.1)

# 5. Executa a previsão quando o botão for clicado
if st.button("Calcular Preço Estimado"):
    dados_usuario = pd.DataFrame([[longitude, latitude, total_rooms, housing_median_age, median_income]], 
                                 columns=['longitude', 'latitude', 'total_rooms', 'housing_median_age', 'median_income'])
    
    resultado_ia = modelo.predict(dados_usuario)
    preco_final = float(resultado_ia)
    
    st.success(f"### Valor Estimado do Imóvel: R$ {preco_final:,.2f}")
    st.info("Nota: Modelo operando com estabilidade via carregamento local.")
