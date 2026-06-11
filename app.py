import streamlit as st
import pandas as pd
import xgboost as xgb
import io
import requests

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Brasil Pro", page_icon="🏠", layout="wide")
st.title("🏠 Sistema de Avaliação Imobiliária com Localização Exata")
st.markdown("Estime o valor de mercado baseado em CEP ou endereço real cruzado com inteligência artificial.")

# 2. Base de dados base para tendências de tamanho e cômodos
@st.cache_resource
def treinar_ia_nacional():
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

with st.spinner("Inicializando motores de cálculo..."):
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
    st.subheader("📍 Localização por CEP ou Endereço")
    endereco_digitado = st.text_input("Digite o CEP ou Endereço Completo", "11520-000")
    st.caption("Exemplos válidos: '11520-000' ou 'Av. Brasil, Jardim Casqueiro, Cubatão SP'")

# 4. Processamento da Localização e Cálculo do Preço
if st.button("🚀 Calcular Avaliação de Mercado Nacional"):
    with st.spinner("Buscando coordenadas exatas e aplicando índices locais..."):
        # Coordenadas padrão de fallback (Cubatão Centro)
        latitude, longitude = -23.8900, -46.4200  
        cidade_detectada = "Cubatão"
        estado_uf = "SP"
        endereco_completo = endereco_digitado

        # Passo 1: Limpeza rápida e verificação se é um CEP
        texto_limpo = endereco_digitado.replace('-', '').replace(' ', '').strip()
        
        if texto_limpo.isdigit() and len(texto_limpo) == 8:
            try:
                url_cep = f"https://viacep.com.br{texto_limpo}/json/"
                res_cep = requests.get(url_cep, timeout=5).json()
                if "localidade" in res_cep:
                    cidade_detectada = res_cep["localidade"]
                    estado_uf = res_cep["uf"]
                    endereco_completo = f"{res_cep.get('logradouro', '')}, {res_cep.get('bairro', '')} - {cidade_detectada}, {estado_uf}"
            except:
                pass

        # Passo 2: Motor Geocodificador de Alta Precisão (Transforma texto do endereço em Latitude/Longitude reais)
        try:
            url_geo = f"https://maps.co{endereco_completo}, Brasil"
            res_geo = requests.get(url_geo, timeout=5).json()
            if isinstance(res_geo, list) and len(res_geo) > 0:
                latitude = float(res_geo[0]['lat'])
                longitude = float(res_geo[0]['lon'])
        except:
            try:
                url_nominatim = f"https://openstreetmap.org{endereco_completo}, Brasil"
                headers = {'User-Agent': 'previsor_imobiliario_marcos_v8'}
                res_nom = requests.get(url_nominatim, headers=headers, timeout=5).json()
                if len(res_nom) > 0:
                    latitude = float(res_nom[0]['lat'])
                    longitude = float(res_nom[0]['lon'])
            except:
                st.warning("⚠️ Coordenadas aproximadas pela região comercial.")

        # Limpeza das variáveis de texto para o cálculo do m²
        cidade_limpa = cidade_detectada.lower().strip()
        estado_uf = estado_uf.upper().strip()

        # 💎 DEFINE O PREÇO DO M² DO MICRO-MERCADO
        dados_uf = tabela_m2_brasil.get(estado_uf, tabela_m2_brasil["PADRAO"])
        
        if "cubatão" in cidade_limpa or "cubatao" in cidade_limpa:
            preco_m2_base = dados_uf.get("cubatao", 4300)
        elif any(k in cidade_limpa for k in ["são paulo", "rio", "curitiba", "belo horizonte", "porto alegre"]):
            preco_m2_base = dados_uf.get("capital", 5500)
        else:
            preco_m2_base = dados_uf.get("interior_no_geral", 3500)

        # 🧠 PREDITOR COMBINADO CORRIGIDO CONTRA TYPEERROR (Utilizando)
        dados_usuario = pd.DataFrame([[area_m2, quartos, vagas]], columns=['area_m2', 'quartos', 'vagas'])
        resultado_predicao = modelo.predict(dados_usuario)
        proporcao_ia = float(resultado_predicao[0])  # <--- SOLUÇÃO DEFINITIVA DO TYPEERROR
        
        valor_m2_calculado = area_m2 * preco_m2_base
        preco_final = (valor_m2_calculado * 0.70) + (proporcao_ia * 0.30)
        
        if padrao == "Econômico / Popular": preco_final *= 0.85
        elif padrao == "Alto Padrão / Luxo": preco_final *= 1.30
        preco_final += (vagas * 20000)

        # Exibição dos resultados na interface
        st.success(f"## Valor de Mercado Estimado: R$ {preco_final:,.2f}")
        
        c1, c2 = st.columns(2)
        c1.metric(label="Média do m² Calculado", value=f"R$ {preco_final/area_m2:,.2f}/m²")
        c2.metric(label="Localidade Identificada", value=f"{cidade_detectada} - {estado_uf}")
        
        st.info(f"📍 **Endereço Formatado Localizado:** {endereco_completo}")
        
        # 🗺️ RENDERIZADOR DE MAPA ATUALIZADO
        st.subheader("🗺️ Localização Geográfica do Imóvel")
        df_mapa = pd.DataFrame({'latitude': [latitude], 'longitude': [longitude]})
        st.map(df_mapa, zoom=15)
        
        # Cria um link dinâmico para abrir direto no app do Google Maps se o usuário quiser
        url_google_maps = f"https://google.com{latitude},{longitude}"
        st.markdown(f"[🔗 Clique aqui para abrir este imóvel direto no app do Google Maps]({url_google_maps})")
