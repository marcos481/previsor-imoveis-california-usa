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

# Tabela dinâmica de valor do m² médio por Estado/Capital/Cidade (Mercado Real)
tabela_m2_brasil = {
    "SP": {"capital": 10200, "interior_no_geral": 5400, "cubatao": 4300, "guaruja": 7100, "santos": 8200},
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
    endereco_digitado = st.text_input("Digite o CEP ou Endereço Completo", "11400-000")
    st.caption("Exemplos válidos: '11421-000', 'Guarujá, SP' ou 'Av. Brasil, Cubatão SP'")

# 4. Processamento da Localização e Cálculo do Preço
if st.button("🚀 Calcular Avaliação de Mercado Nacional"):
    with st.spinner("Buscando coordenadas exatas e aplicando índices locais..."):
        
        # Inteligência preventiva: Define fallbacks baseados no que o usuário digitou
        texto_limpo = ''.join(filter(str.isdigit, endereco_digitado)).strip()
        
        if "114" in texto_limpo or "guaruja" in endereco_digitado.lower() or "guarujá" in endereco_digitado.lower():
            cidade_detectada, estado_uf = "Guarujá", "SP"
            latitude, longitude = -23.9922, -46.2594
        else:
            cidade_detectada, estado_uf = "Cubatão", "SP"
            latitude, longitude = -23.8900, -46.4200
            
        endereco_completo = endereco_digitado

        # Passo 1: Busca via API de CEP (ViaCEP) se for formato numérico
        if len(texto_limpo) == 8:
            try:
                url_cep = f"https://viacep.com.br{texto_limpo}/json/"
                res_cep = requests.get(url_cep, timeout=6).json()
                if "localidade" in res_cep:
                    cidade_detectada = res_cep["localidade"]
                    estado_uf = res_cep["uf"]
                    endereco_completo = f"{res_cep.get('logradouro', '')}, {res_cep.get('bairro', '')} - {cidade_detectada}, {estado_uf}"
            except:
                pass

        # Passo 2: Tradutor Geográfico de Alta Precisão (Obtém Lat/Lon reais da rua do imóvel)
        try:
            url_geo = f"https://maps.co{endereco_completo}, Brasil"
            res_geo = requests.get(url_geo, timeout=6).json()
            if isinstance(res_geo, list) and len(res_geo) > 0:
                latitude = float(res_geo['lat'])
                longitude = float(res_geo['lon'])
        except:
            try:
                url_nominatim = f"https://openstreetmap.org{endereco_completo}, Brasil"
                headers = {'User-Agent': 'previsor_imobiliario_marcos_v13'}
                res_nom = requests.get(url_nominatim, headers=headers, timeout=6).json()
                if len(res_nom) > 0:
                    latitude = float(res_nom['lat'])
                    longitude = float(res_nom['lon'])
            except:
                pass

        # Ajuste de caixa das variáveis de texto
        cidade_limpa = cidade_detectada.lower().strip()
        estado_uf = estado_uf.upper().strip()

        # 💎 DEFINE O PREÇO DO M² DO MICRO-MERCADO
        dados_uf = tabela_m2_brasil.get(estado_uf, tabela_m2_brasil["PADRAO"])
        
        if "guaruja" in cidade_limpa or "guarujá" in cidade_limpa:
            preco_m2_base = dados_uf.get("guaruja", 7100)
        elif "cubatão" in cidade_limpa or "cubatao" in cidade_limpa:
            preco_m2_base = dados_uf.get("cubatao", 4300)
        elif "santos" in cidade_limpa:
            preco_m2_base = dados_uf.get("santos", 8200)
        elif any(k in cidade_limpa for k in ["são paulo", "rio", "curitiba", "belo horizonte", "porto alegre"]):
            preco_m2_base = dados_uf.get("capital", 5500)
        else:
            preco_m2_base = dados_uf.get("interior_no_geral", 3500)

        # 🧠 PREDITOR COMBINADO CORRIGIDO CONTRA TYPEERROR
        dados_usuario = pd.DataFrame([[area_m2, quartos, vagas]], columns=['area_m2', 'quartos', 'vagas'])
        resultado_predicao = modelo.predict(dados_usuario)
        proporcao_ia = float(resultado_predicao)  # Correção definitiva de array
        
        valor_m2_calculado = area_m2 * preco_m2_base
        preco_final = (valor_m2_calculado * 0.70) + (proporcao_ia * 0.30)
        
        if padrao == "Econômico / Popular": preco_final *= 0.85
        elif padrao == "Alto Padrão / Luxo": preco_final *= 1.30
        
        # Calibração de adicionais suavizada
        preco_final += (vagas * 15000)
        preco_final = preco_final * 0.93  

        # Exibição dos resultados na interface
        st.success(f"## Valor de Mercado Estimado: R$ {preco_final:,.2f}")
        
        c1, c2 = st.columns(2)
        c1.metric(label="Média do m² Calculado", value=f"R$ {preco_final/area_m2:,.2f}/m²")
        c2.metric(label="Localidade Identificada", value=f"{cidade_detectada} - {estado_uf}")
        
        st.info(f"📍 **Endereço Formatado Localizado:** {endereco_completo}")
        
        # 🗺️ RENDERIZADOR DE MAPA ATUALIZADO
        st.subheader("🗺️ Localização Geográfica do Imóvel")
        df_mapa = pd.DataFrame({'latitude': [latitude], 'longitude': [longitude]})
        st.map(df_mapa, zoom=14)
        
        # 🔗 LINK GOOGLE MAPS CORRIGIDO: Formato de busca por coordenadas isoladas com a barra '/' correta
        url_google_maps = f"https://google.com{latitude},{longitude}"
        st.markdown(f"[🔗 Clique aqui para abrir este endereço direto no app do Google Maps]({url_google_maps})")
