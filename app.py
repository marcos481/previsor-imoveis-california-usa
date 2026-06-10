import streamlit as st
import pandas as pd
import xgboost as xgb
from geopy.geocoders import Nominatim
import io

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor de Imóveis Brasil", page_icon="🏠", layout="centered")
st.title("🏠 Sistema Inteligente de Avaliação de Imóveis (Preços Reais)")
st.markdown("Insira as características do imóvel para estimar o valor de mercado real baseado em transações de SP e Litoral.")

# 2. Base de dados expandida e regionalizada para evitar inversão de valores
@st.cache_resource
def treinar_ia_com_dados_reais():
    # Histórico com mais amostras para o modelo entender o peso real da localização
    texto_dados = """area_m2,quartos,vagas,latitude,longitude,preco_reais
45,1,0,-23.54,-46.41,155000
75,2,1,-23.53,-46.25,215000
46,2,1,-23.54,-46.41,134800
64,2,1,-23.53,-46.25,190000
67,1,1,-23.52,-46.29,215000
50,1,0,-23.99,-46.42,160000
65,2,1,-23.98,-46.43,195000
40,1,0,-23.97,-46.25,140000
55,1,0,-23.96,-46.40,170000
80,2,1,-23.96,-46.33,580000
120,3,2,-23.97,-46.31,920000
150,3,2,-23.98,-46.30,1450000
90,2,1,-23.95,-46.26,620000
110,3,2,-23.96,-46.25,850000
220,3,3,-23.95,-46.26,1950000
180,4,3,-23.55,-46.63,1650000
95,3,2,-23.58,-46.67,890000"""
    
    dados_mercado = pd.read_csv(io.StringIO(texto_dados))
    
    X = dados_mercado[['area_m2', 'quartos', 'vagas', 'latitude', 'longitude']]
    y = dados_mercado['preco_reais']
    
    # Treinamos com profundidade ajustada para respeitar as coordenadas
    modelo_ia = xgb.XGBRegressor(n_estimators=150, learning_rate=0.05, max_depth=4, random_state=42)
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
latitude = st.sidebar.slider("Latitude (Região SP/Litoral)", -24.00, -23.45, -23.96, step=0.01)
longitude = st.sidebar.slider("Longitude (Região SP/Litoral)", -46.68, -46.20, -46.32, step=0.01)

# 4. Executa a previsão nacional e busca o endereço real
if st.button("Calcular Preço Estimado"):
    dados_usuario = pd.DataFrame([[area_m2, quartos, vagas, latitude, longitude]], 
                                 columns=['area_m2', 'quartos', 'vagas', 'latitude', 'longitude'])
    
    resultado_ia = modelo.predict(dados_usuario)
    preco_final = float(resultado_ia)
    
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
