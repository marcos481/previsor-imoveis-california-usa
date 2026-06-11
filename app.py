import streamlit as st
import pandas as pd
import xgboost as xgb
import io
import requests

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Brasil Pro", page_icon="🏠", layout="wide")
st.title("🏠 Sistema de Avaliação Imobiliária com Google Maps")
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
    st.subheader("📍 Localização por Google Maps / CEP")
    endereco_digitado = st.text_input("Digite o CEP ou Endereço Completo", "11520-000, Cubatão, SP")
    
    # Campo opcional para colocar a chave da API caso queira usar em produção com o mapa do satélite
    google_key = st.text_input("Chave API do Google Maps (Opcional)", type="password", help="Deixe em branco para usar o buscador nativo otimizado")

# 4. Processamento da Localização e Cálculo do Preço
if st.button("🚀 Calcular Avaliação de Mercado Nacional"):
    with st.spinner("Conectando aos servidores de mapas..."):
        latitude, longitude = -23.8900, -46.4200  # Padrão Cubatão
        cidade_detectada = "Cubatão"
        estado_uf = "SP"
        endereco_completo = endereco_digitado

        # Se o usuário tiver uma chave Google Maps, usamos a API oficial de Geocoding
        if google_key:
            try:
                url = f"https://googleapis.com{endereco_digitado}&key={google_key}"
                response = requests.get(url).json()
                if response['status'] == 'OK':
                    resultado = response['results'][0]
                    latitude = resultado['geometry']['location']['lat']
                    longitude = resultado['geometry']['location']['lng']
                    endereco_completo = resultado['formatted_address']
                    
                    for comp in resultado['address_components']:
                        if "administrative_area_level_2" in comp['types']:
                            cidade_detectada = comp['long_name']
                        if "administrative_area_level_1" in comp['types']:
                            estado_uf = comp['short_name']
            except:
                st.error("Erro ao validar chave do Google Maps. Usando contingência.")
        else:
            # Sistema de geocodificação pública alternativa via API do OpenStreetMap otimizada para CEPs estruturados
            try:
                url_cep = f"https://viacep.com.br{endereco_digitado.replace('-', '').replace(' ', '')}/json/"
                res_cep = requests.get(url_cep).json()
                if "localidade" in res_cep:
                    cidade_detectada = res_cep["localidade"]
                    estado_uf = res_cep["uf"]
                    endereco_completo = f"{res_cep['logradouro']}, {res_cep['bairro']} - {cidade_detectada}, {estado_uf}"
            except:
                pass # Mantém o padrão Cubatão se falhar

        # Limpeza das variáveis de texto
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
        proporcao_ia = float(resultado_predicao[0])  # <--- CORREÇÃO CIRÚRGICA AQUI
        
        valor_m2_calculado = area_m2 * preco_m2_base
        preco_final = (valor_m2_calculado * 0.70) + (proporcao_ia * 0.30)
        
        if padrao == "Econômico / Popular": preco_final *= 0.85
        elif padrao == "Alto Padrão / Luxo": preco_final *= 1.30
        preco_final += (vagas * 20000)

        # Exibição dos resultados
        st.success(f"## Valor de Mercado Estimado: R$ {preco_final:,.2f}")
        
        c1, c2 = st.columns(2)
        c1.metric(label="Média do m² Calculado", value=f"R$ {preco_final/area_m2:,.2f}/m²")
        c2.metric(label="Localidade Identificada", value=f"{cidade_detectada} - {estado_uf}")
        
        st.info(f"📍 **Endereço Formatado:** {endereco_completo}")
        
        # 🗺️ RENDERIZADOR DE MAPA CORRIGIDO (Nome exato das colunas 'latitude' e 'longitude')
        st.subheader("🗺️ Visualização Geográfica")
        df_mapa = pd.DataFrame({'latitude': [latitude], 'longitude': [longitude]})
        st.map(df_mapa, zoom=15)
        
        # Cria um link dinâmico para abrir direto no app do Google Maps se o usuário quiser
        url_google_maps = f"https://google.com{latitude},{longitude}"
        st.markdown(f"[🔗 Clique aqui para abrir este imóvel direto no app do Google Maps]({url_google_maps})")
