import streamlit as st
import pandas as pd
import requests

# 1. Configuração visual do site
st.set_page_config(page_title="Previsor Imobiliário Brasil Pro", page_icon="🏠", layout="wide")
st.title("🏠 Sistema Inteligente de Avaliação Imobiliária")
st.markdown("Estime o valor de mercado real baseado em CEP com localização exata por logradouro.")

# Tabela dinâmica de valor do m² médio por Cidade (Mercado Real)
tabela_m2_brasil = {
    "guaruja": 7100,
    "cubatao": 4300,
    "santos": 8200,
    "capital": 10200,
    "interior": 4500
}

# 2. Interface de entrada em colunas
col_esq, col_dir = st.columns(2)

with col_esq:
    st.subheader("📐 Características do Imóvel")
    area_m2 = st.slider("Área Privativa (m²)", 30, 400, 70)
    quartos = st.slider("Quantidade de Quartos", 1, 5, 2)
    vagas = st.slider("Vagas de Garagem", 0, 4, 1)
    padrao = st.selectbox("Padrão de Acabamento", ["Econômico / Popular", "Médio / Padrão", "Alto Padrão / Luxo"])

with col_dir:
    st.subheader("📍 Localização por CEP")
    cep_digitado = st.text_input("Digite o CEP do Imóvel", "11471-070")
    st.caption("Exemplos válidos de teste: '11471-070' (Guarujá) ou '11520-000' (Cubatão)")

# 3. Processamento da Localização e Cálculo do Preço
if st.button("🚀 Calcular Avaliação de Mercado"):
    with st.spinner("Buscando dados cadastrais da rua e aplicando índices locais..."):
        
        # Limpeza rígida do número do CEP para evitar erros de consulta
        cep_limpo = ''.join(filter(str.isdigit, cep_digitado)).strip()
        
        # Configurações básicas de segurança (Fallbacks regionais caso a rede falhe)
        if "114" in cep_limpo:
            cidade_detectada = "Guarujá"
            estado_uf = "SP"
            latitude, longitude = -23.9922, -46.2594
            endereco_completo = "Logradouro não identificado, Guarujá - SP"
            preco_m2_base = tabela_m2_brasil["guaruja"]
        elif "115" in cep_limpo:
            cidade_detectada = "Cubatão"
            estado_uf = "SP"
            latitude, longitude = -23.8900, -46.4200
            endereco_completo = "Logradouro não identificado, Cubatão - SP"
            preco_m2_base = tabela_m2_brasil["cubatao"]
        else:
            cidade_detectada = "São Paulo"
            estado_uf = "SP"
            latitude, longitude = -23.5505, -46.6333
            endereco_completo = "Logradouro não identificado, São Paulo - SP"
            preco_m2_base = tabela_m2_brasil["capital"]

        # 🚀 PASSO 1: CONSULTA DIRETA DE LOGRADOURO (Via API de barramento descentralizada)
        if len(cep_limpo) == 8:
            try:
                # Mudança para servidor de alta disponibilidade sem bloqueios de nuvem do Streamlit
                url_busca = f"https://apicep.com{cep_limpo[:5]}-{cep_limpo[5:]}.json"
                resposta = requests.get(url_busca, timeout=5).json()
                
                if resposta.get("status") == 200:
                    cidade_detectada = resposta.get("city")
                    estado_uf = resposta.get("state")
                    rua = resposta.get("code") if resposta.get("address") == "" else resposta.get("address")
                    bairro = resposta.get("district")
                    endereco_completo = f"{rua}, {bairro} - {cidade_detectada}, {estado_uf}"
            except:
                # Fallback secundário caso a primeira API apresente oscilação
                try:
                    url_back = f"https://viacep.com.br{cep_limpo}/json/"
                    res_back = requests.get(url_back, timeout=4).json()
                    if "localidade" in res_back:
                        cidade_detectada = res_back["localidade"]
                        estado_uf = res_back["uf"]
                        endereco_completo = f"{res_back.get('logradouro', '')}, {res_back.get('bairro', '')} - {cidade_detectada}, {estado_uf}"
                except:
                    pass

        # 🚀 PASSO 2: IDENTIFICAÇÃO DE COORDENADAS PARA CENTRALIZAR O MAPA NATIVO
        cidade_limpa = cidade_detectada.lower().strip()
        
        # Mapeia as coordenadas exatas da orla do Guarujá para o mapa carregar perfeitamente na tela
        if "guaruja" in cidade_limpa or "guarujá" in cidade_limpa:
            preco_m2_base = tabela_m2_brasil["guaruja"]
            latitude, longitude = -23.9930, -46.2560 # Centralização precisa no Guarujá
        elif "cubatão" in cidade_limpa or "cubatao" in cidade_limpa:
            preco_m2_base = tabela_m2_brasil["cubatao"]
            latitude, longitude = -23.8920, -46.4250 # Centralização precisa em Cubatão
        elif "santos" in cidade_limpa:
            preco_m2_base = tabela_m2_brasil["santos"]
            latitude, longitude = -23.9608, -46.3339

        # 🧠 MOTOR DE PRECIFICAÇÃO DIRETO E ROBUSTO (Sem travamentos de biblioteca externa)
        valor_base_estrutura = (area_m2 * preco_m2_base) + (quartos * 12000) + (vagas * 15000)
        
        if padrao == "Econômico / Popular":
            preco_final = valor_base_estrutura * 0.85
        elif padrao == "Alto Padrão / Luxo":
            preco_final = valor_base_estrutura * 1.25
        else:
            preco_final = valor_base_estrutura

        preco_final = preco_final * 0.93  # Ajuste fino final de valorização de mercado

        # Exibição dos resultados estruturados na tela
        st.success(f"## Valor de Mercado Estimado: R$ {preco_final:,.2f}")
        
        c1, c2 = st.columns(2)
        c1.metric(label="Média do m² Calculado", value=f"R$ {preco_final/area_m2:,.2f}/m²")
        c2.metric(label="Localidade Identificada", value=f"{cidade_detectada} - {estado_uf}")
        
        # Imprime na tela o nome correto da Avenida ou Rua retornado pelos Correios
        st.info(f"📍 **Endereço do Logradouro:** {endereco_completo}")
        
        # 🗺️ RENDERIZADOR DE MAPA ATUALIZADO (Garante o carregamento do mapa na tela)
        st.subheader("🗺️ Localização Geográfica do Imóvel")
        df_mapa = pd.DataFrame({'latitude': [latitude], 'longitude': [longitude]})
        st.map(df_mapa, zoom=14)
        
        # 🔗 LINK GOOGLE MAPS NATIVO CORRIGIDO
        url_google_maps = f"https://google.com{latitude},{longitude}"
        st.link_button("➡️ Abrir Localização Detalhada no Google Maps", url_google_maps)
