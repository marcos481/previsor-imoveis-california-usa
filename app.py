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

with st.spinner("Inicializando motores de cálculo nacionais..."):
    modelo = treinar_ia_nacional()

# Tabela dinâmica de valor do m² médio por Estado/Capital (Referência de Mercado)
# Valores calibrados para a realidade de mercado refletindo variações regionais
tabela_m2_brasil = {
    "SP": {"capital": 10200, "interior_no_geral": 5400, "cubatao": 4300},
    "RJ": {"capital": 10100, "interior_no_geral": 4800},
    "DF": {"capital": 8900, "interior_no_geral": 5200},
    "SC": {"capital": 11000, "interior_no_geral": 6500}, # Balneário Camboriú / Itapema puxam para cima
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
col_esq, col_dir = st.columns([1, 1])

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
        latitude = st.number_input("Latitude", value=-23.890, format="%.4f")
        longitude = st.number_input("Longitude", value=-46.420, format="%.4f")

# 4. Processamento da Localização e Cálculo do Preço
if st.button("🚀 Calcular Avaliação de Mercado Nacional"):
    with st.spinner("Buscando dados geográficos e aplicando índices locais..."):
        geolocator = Nominatim(user_agent="previsor_imoveis_brasil_v1")
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
                    estado_uf = detalhes.get('state_code', '').upper()
                    if not estado_uf and 'state' in detalhes:
                        # Fallback se não vier a sigla direta
                        estado_uf = detalhes.get('state', '')
            else:
                loc = geolocator.reverse(f"{latitude}, {longitude}", addressdetails=True, timeout=10)
                if loc:
                    endereco_completo = loc.address
                    detalhes = loc.raw.get('address', {})
                    cidade = detalhes.get('city', detalhes.get('town', detalhes.get('municipality', '')))
                    estado_uf = detalhes.get('state_code', '').upper()
        except:
            st.warning("⚠️ Falha temporária ao conectar ao mapa. Usando aproximação padrão regional.")

        # Limpeza rápida de nomes de cidades e estados
        cidade_limpa = cidade.lower().strip() if cidade else ""
        
        # Tratamento simplificado de UF se vier o nome completo do estado
        if len(estado_uf) > 2:
            mapeamento_estados = {"são paulo": "SP", "rio de janeiro": "RJ", "minas gerais": "MG"}
            estado_uf = mapeamento_estados.get(estado_uf.lower(), "SP")
        if not estado_uf: 
            estado_uf = "SP" # Fallback prudente

        # 💎 DEFINE O PREÇO DO M² DO MICRO-MERCADO
        dados_uf = tabela_m2_brasil.get(estado_uf, tabela_m2_brasil["PADRAO"])
        
        # Regras de especificidade (Cidade específica -> Capital -> Interior)
        if "cubatão" in cidade_limpa:
            preco_m2_base = dados_uf.get("cubatao", 4300)
        elif cidade_limpa and any(k in cidade_limpa for k in ["são paulo", "rio de janeiro", "curitiba", "belo horizonte", "porto alegre", "recife", "salvador", "fortaleza", "brasília"]):
            preco_m2_base = dados_uf.get("capital")
        else:
            preco_m2_base = dados_uf.get("interior_no_geral")

        # 🧠 PREDITOR COMBINADO
        # XGBoost calcula a proporção do valor pelo tamanho e distribuição de cômodos
        dados_usuario = pd.DataFrame([[area_m2, quartos, vagas]], columns=['area_m2', 'quartos', 'vagas'])
        proporcao_ia = float(modelo.predict(dados_usuario))
        
        # Preço base estruturado no m² comercial real do município atual
        valor_m2_calculado = area_m2 * preco_m2_base
        
        # Agrega o peso das variáveis físicas tratadas pelo modelo
        preco_final = (valor_m2_calculado * 0.70) + (proporcao_ia * 0.30)
        
        # Multiplicadores de padrão de acabamento
        if padrao == "Econômico / Popular":
            preco_final *= 0.85
        elif padrao == "Alto Padrão / Luxo":
            preco_final *= 1.30

        # Adiciona valor de mercado por vaga de garagem extra comercializável
        preco_final += (vagas * 20000)

        # Exibição Analítica dos Resultados na Tela
        st.success(f"## Valor de Mercado Estimado: R$ {preco_final:,.2f}")
        
        c1, c2, c3 = st.columns(3)
        c1.metric(label="Média do m² Calculado", value=f"R$ {preco_final/area_m2:,.2f}/m²")
        c2.metric(label="Cidade / UF Identificada", value=f"{cidade if cidade else 'Região Identificada'} - {estado_uf}")
        c3.metric(label="Coordenadas de Análise", value=f"{latitude:.4f}, {longitude:.4f}")
        
        st.info(f"📍 **Endereço Completo no Mapa:** {endereco_completo if endereco_completo else 'Busca por coordenadas locais.'}")
