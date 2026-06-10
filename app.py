import streamlit as st
import pandas as pd
import xgboost as xgb
from geopy.geocoders import Nominatim

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor de Imóveis Brasil", page_icon="🏠", layout="centered")
st.title("🏠 Sistema Inteligente de Avaliação de Imóveis (Preços Reais)")
st.markdown("Insira as características do imóvel para estimar o valor de mercado real baseado em transações de SP e Litoral.")

# 2. Carregamento e Treinamento Dinâmico da Tabela Real
@st.cache_resource
def treinar_ia_com_dados_reais():
    # O Pandas lê o arquivo .csv real que você acabou de criar na pasta do repositório
    dados_mercado = pd.read_csv("imoveis_reais.csv")
    
    # Separamos as variáveis preditoras (X) da variável alvo de preço (y)
    X = dados_mercado[['area_m2', 'quartos', 'vagas', 'latitude', 'longitude']]
    y = dados_mercado['preco_reais']
    
    # Treinamos a IA para aprender os padrões e preços autênticos da tabela
    modelo_ia = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    modelo_ia.fit(X, y)
    return modelo_ia

with st.spinner("Calibrando preços com o histórico do mercado real..."):
    modelo = treinar_ia_com_dados_reais()

# 3. Criação dos controles visuais na barra lateral
st.sidebar.header("Características do Imóvel")
area_m2 = st.sidebar.slider("Área Privativa (m²)", 40, 250, 70)
quartos = st.sidebar.slider("Quantidade de Quartos", 1, 4, 2)
vagas = st.sidebar.slider("Vagas de Garagem", 0, 3, 1)

st.sidebar.header("Localização Geográfica")
latitude = st.sidebar.slider("Latitude (Região SP/Litoral)", -24.00, -23.45, -23.54, step=0.01)
longitude = st.sidebar.slider("Longitude (Região SP/Litoral)", -46.68, -46.20, -46.41, step=0.01)

# 4. Executa a previsão nacional e busca o endereço real
if st.button("Calcular Preço Estimado"):
    dados_usuario = pd.DataFrame([[area_m2, quartos, vagas, latitude, longitude]], 
                                 columns=['area_m2', 'quartos', 'vagas', 'latitude', 'longitude'])
    
    resultado_ia = modelo.predict(dados_usuario)
    preco_final = float(resultado_ia[0]) # Extração do número do array de forma segura
    
    try:
        geolocator = Nominatim(user_agent="previsor_imoveis_marcos")
        localizacao = geolocator.reverse(f"{latitude}, {longitude}", timeout=10)
        endereco_completo = localizacao.address
    except:
        endereco_completo = "Endereço localizado na Região Metropolitana ou Litoral de SP."

    # Exibição dos resultados estruturados na tela
    st.success(f"### Valor de Mercado Estimado: R$ {preco_final:,.2f}")
    
    st.subheader("📍 Localização do Imóvel:")
    st.info(f"**Endereço:** {endereco_completo}")
