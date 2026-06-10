import streamlit as st
import pandas as pd
import xgboost as xgb # Trocamos joblib por xgboost nativo

# 1. Carrega o modelo de forma nativa e ultra compatível (.json)
modelo = xgb.XGBRegressor()
modelo.load_model("modelo_final_xgboost.json")

# 2. Configuração visual do site
st.set_page_config(page_title="Previsor de Imóveis", page_icon="🏠", layout="centered")
st.title("🏠 Sistema Inteligente de Avaliação de Imóveis")
st.markdown("Insira os dados da região da Califórnia para estimar o valor médio das casas.")

st.sidebar.header("Parâmetros do Imóvel")

# 3. Controles do usuário
longitude = st.sidebar.slider("Longitude", -124.3, -114.3, -118.0, step=0.1)
latitude = st.sidebar.slider("Latitude", 32.5, 41.9, 34.0, step=0.1)
total_rooms = st.sidebar.number_input("Total de Quartos no Bloco", min_value=1, max_value=40000, value=1000)
housing_median_age = st.sidebar.slider("Idade Média da Casa", 1, 52, 28)
median_income = st.sidebar.number_input("Renda Média do Bairro (em dezenas de milhares)", min_value=0.5, max_value=15.0, value=4.0, step=0.1)

# 4. Executa a previsão quando o botão for clicado
if st.button("Calcular Preço Estimado"):
    dados_usuario = pd.DataFrame([[longitude, latitude, total_rooms, housing_median_age, median_income]], 
                                 columns=['longitude', 'latitude', 'total_rooms', 'housing_median_age', 'median_income'])
    
    resultado_ia = modelo.predict(dados_usuario)
    preco_final = float(resultado_ia[0])
    
    st.success(f"### Valor Estimado do Imóvel: R$ {preco_final:,.2f}")
    st.info("Nota: Modelo operando com margem de precisão de 15.5%.")
