import streamlit as st
import pandas as pd
import xgboost as xgb
import numpy as np
from geopy.geocoders import Nominatim # Biblioteca para descobrir o endereço pelas coordenadas

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor de Imóveis Brasil", page_icon="🏠", layout="centered")
st.title("🏠 Sistema Inteligente de Avaliação de Imóveis (Brasil)")
st.markdown("Insira as características do imóvel para estimar o valor de mercado e localizar o endereço.")

# 2. Treinamento inteligente de dados nacionais na inicialização
@st.cache_resource
def inicializar_ia_brasil():
    np.random.seed(42)
    n_amostras = 2000
    
    area_m2 = np.random.randint(40, 300, n_amostras)
    quartos = np.random.randint(1, 4, n_amostras)
    vagas = np.random.randint(0, 3, n_amostras)
    
    # Coordenadas cobrindo Baixada Santista (Guarujá/Santos) e capital de SP
    latitude = np.random.uniform(-24.00, -23.50, n_amostras)
    longitude = np.random.uniform(-46.60, -46.20, n_amostras)
    
    preco_base = area_m2 * np.random.randint(6000, 11000, n_amostras)
    preco_reais = preco_base + (vagas * 45000) + (quartos * 30000)
    
    X = pd.DataFrame({"area_m2": area_m2, "quartos": quartos, "vagas": vagas, "latitude": latitude, "longitude": longitude})
    y = preco_reais
    
    modelo_ia = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    modelo_ia.fit(X, y)
    return modelo_ia

with st.spinner("Configurando mercado imobiliário brasileiro..."):
    modelo = inicializar_ia_brasil()

# 3. Criação dos controles visuais na barra lateral
st.sidebar.header("Características do Imóvel")
area_m2 = st.sidebar.slider("Área Privativa (m²)", 40, 300, 75)
quartos = st.sidebar.slider("Quantidade de Quartos", 1, 4, 2)
vagas = st.sidebar.slider("Vagas de Garagem", 0, 3, 1)

st.sidebar.header("Localização Geográfica")
# Valores iniciais calibrados próximos ao Guarujá/Santos
latitude = st.sidebar.slider("Latitude (Região SP/Litoral)", -24.00, -23.50, -23.99, step=0.01)
longitude = st.sidebar.slider("Longitude (Região SP/Litoral)", -46.60, -46.20, -46.31, step=0.01)

# 4. Executa a previsão nacional e busca o endereço
if st.button("Calcular Preço Estimado"):
    # Organiza os dados para a IA
    dados_usuario = pd.DataFrame([[area_m2, quartos, vagas, latitude, longitude]], 
                                 columns=['area_m2', 'quartos', 'vagas', 'latitude', 'longitude'])
    
    resultado_ia = modelo.predict(dados_usuario)
    preco_final = float(resultado_ia[0])  # <--- ADICIONE O [0] AQUI PARA EXTRAIR O NÚMERO

    
    # 🌍 MÁGICA GEOGRÁFICA: Buscando a rua e a cidade real pelas coordenadas
    try:
        geolocator = Nominatim(user_agent="previsor_imoveis_marcos")
        localizacao = geolocator.reverse(f"{latitude}, {longitude}", timeout=10)
        endereco_completo = localizacao.address
    except:
        endereco_completo = "Endereço localizado em área marítima ou limite de coordenadas."

    # Exibição dos resultados estruturados na tela
    st.success(f"### Valor Estimado do Imóvel: R$ {preco_final:,.2f}")
    
    st.subheader("📍 Localização Identificada pelo Sistema:")
    st.info(f"**Endereço Completo:** {endereco_completo}")
    
    st.markdown(f"**Coordenadas Selecionadas:** Lat {latitude} | Long {longitude}")
