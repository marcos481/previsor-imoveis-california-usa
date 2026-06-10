import numpy as np
import pandas as pd
import streamlit as st
import xgboost as xgb

# 1. Configuração visual do site
st.set_page_config(
    page_title="Previsor de Imóveis Brasil", page_icon="🏠", layout="centered"
)
st.title("🏠 Sistema Inteligente de Avaliação de Imóveis (Brasil)")
st.markdown(
    "Insira as características do imóvel para estimar o valor de mercado em Reais."
)

# 2. Simulação e treinamento de dados nacionais na inicialização
@st.cache_resource
def inicializar_ia_brasil():
    np.random.seed(42)
    n_amostras = 2000

    # Simulando características comuns do mercado brasileiro
    area_m2 = np.random.randint(40, 300, n_amostras)
    quartos = np.random.randint(1, 4, n_amostras)
    vagas = np.random.randint(0, 3, n_amostras)

    # Simulando coordenadas da região de SP / Baixada Santista
    latitude = np.random.uniform(-24.0, -23.5, n_amostras)
    longitude = np.random.uniform(-46.6, -46.2, n_amostras)

    # Cálculo matemático simulado para precificação realista (Preço por m² + bônus de vagas/quartos)
    preco_base = area_m2 * np.random.randint(6000, 11000, n_amostras)
    preco_reais = preco_base + (vagas * 45000) + (quartos * 30000)

    # Montando a tabela estruturada
    X = pd.DataFrame(
        {
            "area_m2": area_m2,
            "quartos": quartos,
            "vagas": vagas,
            "latitude": latitude,
            "longitude": longitude,
        }
    )
    y = preco_reais

    # Treinando o modelo XGBoost nacional
    modelo_ia = xgb.XGBRegressor(
        n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42
    )
    modelo_ia.fit(X, y)
    return modelo_ia


# 3. Liga os motores da IA
with st.spinner("Configurando mercado imobiliário brasileiro..."):
    modelo = inicializar_ia_brasil()

# 4. Criação dos controles visuais nacionais na barra lateral
st.sidebar.header("Características do Imóvel")
area_m2 = st.sidebar.slider("Área Privativa (m²)", 40, 300, 75)
quartos = st.sidebar.slider("Quantidade de Quartos", 1, 4, 2)
vagas = st.sidebar.slider("Vagas de Garagem", 0, 3, 1)

st.sidebar.header("Localização Geográfica")
latitude = st.sidebar.slider(
    "Latitude (Região SP/Litoral)", -24.00, -23.50, -23.96, step=0.01
)
longitude = st.sidebar.slider(
    "Longitude (Região SP/Litoral)", -46.60, -46.20, -46.32, step=0.01
)

# 5. Executa a previsão nacional
if st.button("Calcular Preço Estimado"):
    dados_usuario = pd.DataFrame(
        [[area_m2, quartos, vagas, latitude, longitude]],
        columns=["area_m2", "quartos", "vagas", "latitude", "longitude"],
    )

    resultado_ia = modelo.predict(dados_usuario)
    preco_final = float(resultado_ia)

    # Exibição do resultado final formatado na moeda nacional (R$)
    st.success(f"### Valor Estimado do Imóvel: R$ {preco_final:,.2f}")
    st.info(
        "Nota: Modelo calibrado para o padrão de precificação da Grande São Paulo e Litoral."
    )
