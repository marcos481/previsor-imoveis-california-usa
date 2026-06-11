import streamlit as st
import pandas as pd
import xgboost as xgb
from geopy.geocoders import Nominatim
import io

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Brasil", page_icon="🏠", layout="wide")
st.title("🏠 Sistema Inteligente de Avaliação de Imóveis Nacional")
st.markdown("Estime o valor de mercado real de imóveis em **qualquer município do Brasil** com calibração regional automática.")

# 2. Base de dados base para tendências de tamanho e cômodos
@st.cache_resource
def treinar_ia_nacional():
    # Dataset genérico que ensina ao XGBoost o impacto proporcional de m², quartos e vagas
    texto_dados = """area_m2,quartos,vagas,preco_base_referencia
40,1,0,160000
50,1,1,210000
65,2,1,280000
80,2,1,360000
90,2,2,420000
110,3,2,550000
140,3,2,720000
180,4,3,980000
220,4,3,1300000"""
    
    dados_mercado = pd.read_csv(io.StringIO(texto_dados))
    X = dados_mercado[['area_m2', 'quartos', 'vagas']]
    y = dados_mercado['preco_base_referencia']
    
    modelo_ia = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
    modelo_ia.fit(X, y)
    return modelo_ia

with st.spinner("Analisando mercado e inicializando motores de cálculo nacionais..."):
    modelo = treinar_ia_nacional()

# Tabela dinâmica de valor do m² médio por Estado/Capital (Referência de Mercado)
tabela_m2_brasil = {
    "SP": {"capital": 10200, "interior_no_geral": 5400, "cubatao": 4300},
    "RJ": {"capital": 10100, "interior_no_geral": 4800},
    "DF": {"capital": 8900, "interior_no_geral": 5200},
    "SC": {"capital": 11000, "interior_no_geral": 6500},
    "PR": {"capital": 7800, "interior_no_geral": 4500},
    "MG": {"capital": 7900, "interior_no_geral": 4200},
    "RS": {"capital": 6800, "interior_no_geral": 4100},
    "PE": {"capital": 7400, "interior_no_geral": 3900},
    "BA": {"capital": 6200, "interior_no_geral": 3600},
    "CE": {"capital": 5900, "interior_no_geral": 3500},
    "GO": {"capital": 6500, "interior_no_geral": 3800},
    "PA": {"capital": 5400, "interior_no_geral": 3200},
    "PADRAO": {"capital": 5500, "interior_no_geral": 3500}
}

# 3. Interface em colunas
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📐 Características do Imóvel")
    area_m2 = st.slider("Área Privativa (m²)", 30, 400, 70)
    quartos = st.slider("Quantidade de Quartos", 1, 5, 2)
    vagas = st.slider("Vagas de Garagem", 0, 4, 1)
    padrao = st.selectbox("Padrão de Acabamento", ["Econômico / Popular", "Médio / Padrão", "Alto Padrão / Luxo"])

with col_dir:
    st.subheader("📍 Localização (Escolha uma opção)")
    opcao_busca = st.radio("Como deseja localizar?", ["Por CEP ou Endereço escrito", "Por Coordenadas (Lat/Lon)"])
    
    latitude, longitude = -23.5505, -46.6333 # Padrão: SP Capital
    endereco_digitado = ""
    
    if opcao_busca == "Por CEP ou Endereço escrito":
        endereco_digitado = st.text_input("Digite o CEP, Rua ou Cidade (Ex: Jardim Casqueiro, Cubatão SP)", "Cubatão, SP")
    else:
        latitude = st.number_input("Latitude", value=-23.8900, format="%.4f")
        longitude = st.number_input("Longitude", value=-46.4200, format="%.4f")

# 4. Processamento da Localização e Cálculo do Preço
if st.button("🚀 Calcular Avaliação de Mercado Nacional"):
    with st.spinner("Buscando dados geográficos e aplicando índices locais..."):
        geolocator = Nominatim(user_agent="previsor_imoveis_brasil_v3")
        cidade = ""
        estado_uf = ""
        endereco_completo = ""
        
        # Resolve a localização independente da escolha do usuário
        try:
            if opcao_busca == "Por CEP ou Endereço escrito" and endereco_digitado:
                loc = geolocator.geocode(endereco_digitado, addressdetails=True, timeout=10)
                if loc:
                    latitude, longitude = loc.latitude, loc.longitude
                    endereco_completo = loc.address
                    detalhes = loc.raw.get('address', {})
                    cidade = detalhes.get('city', detalhes.get('town', detalhes.get('municipality', '')))
                    estado_uf = detalhes.get('state_code', '').upper() if detalhes.get('state_code') else ""
                    if not estado_uf and 'state' in detalhes:
                        estado_uf = detalhes.get('state', '')
            else:
                loc = geolocator.reverse(f"{latitude}, {longitude}", addressdetails=True, timeout=10)
                if loc:
                    endereco_completo = loc.address
                    detalhes = loc.raw.get('address', {})
                    cidade = detalhes.get('city', detalhes.get('town', detalhes.get('municipality', '')))
                    estado_uf = detalhes.get('state_code', '').upper() if detalhes.get('state_code') else ""
                    if not estado_uf and 'state' in detalhes:
                        estado_uf = detalhes.get('state', '')
        except:
            st.warning("⚠️ Falha temporária ao conectar ao mapa. Usando aproximação padrão regional.")

        # Limpeza rápida de nomes de cidades e estados
        cidade_limpa = str(cidade).lower().strip() if cidade else ""
        estado_uf = str(estado_uf).upper().strip() if estado_uf else "SP"
        
        # Tratamento de segurança se vir o nome completo do estado por extenso
        if len(estado_uf) > 2:
            if "paulo" in estado_uf.lower(): estado_uf = "SP"
            elif "rio" in estado_uf.lower(): estado_uf = "RJ"
            elif "minas" in estado_uf.lower(): estado_uf = "MG"
            elif "santa" in estado_uf.lower(): estado_uf = "SC"
            elif "paraná" in estado_uf.lower() or "parana" in estado_uf.lower(): estado_uf = "PR"
            else: estado_uf = "SP"

        # 💎 DEFINE O PREÇO DO M² DO MICRO-MERCADO
        dados_uf = tabela_m2_brasil.get(estado_uf, tabela_m2_brasil["PADRAO"])
        
        # Regras de especificidade (Cidade específica -> Capital -> Interior)
        if "cubatão" in cidade_limpa:
            preco_m2_base = dados_uf.get("cubatao", 4300)
        elif cidade_limpa and any(k in cidade_limpa for k in ["são paulo", "rio de janeiro", "curitiba", "belo horizonte", "porto alegre", "recife", "salvador", "fortaleza", "brasília"]):
            preco_m2_base = dados_uf.get("capital", 5500)
        else:
            preco_m2_base = dados_uf.get("interior_no_geral", 3500)

        # 🧠 PREDITOR COMBINADO CORRIGIDO (Extraindo o valor do Array com)
        dados_usuario = pd.DataFrame([[area_m2, quartos, vagas]], columns=['area_m2', 'quartos', 'vagas'])
        resultado_predicao = modelo.predict(dados_usuario)
        proporcao_ia = float(resultado_predicao[0])  # Fix do TypeError garantido
        
        # Preço base estruturado no m² comercial real do município atual
        valor_m2_calculado = area_m2 * preco_m2_base
        
        # Agrega o peso das variáveis físicas tratadas pelo modelo (70% peso do m² real da cidade, 30% comportamento da IA)
        preco_final = (valor_m2_calculado * 0.70) + (proporcao_ia * 0.30)
        
        # Multiplicadores de padrão de acabamento
        if padrao == "Econômico / Popular":
            preco_final *= 0.85
        elif padrao == "Alto Padrão / Luxo":
            preco_final *= 1.30

        # Adiciona valor de mercado por vaga de garagem comercializável
        preco_final += (vagas * 20000)

        # Exibição Analítica dos Resultados na Tela
        st.success(f"## Valor de Mercado Estimado: R$ {preco_final:,.2f}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric(label="Média do m² Calculado", value=f"R$ {preco_final/area_m2:,.2f}/m²")
        c2.metric(label="Cidade / UF Identificada", value=f"{cidade if cidade else 'Região Identificada'} - {estado_uf}")
        c3.metric(label="Coordenadas de Análise", value=f"{latitude:.4f}, {longitude:.4f}")
        
        st.info(f"📍 **Endereço Completo no Mapa:** {endereco_completo if endereco_completo else 'Busca por coordenadas locais.'}")
