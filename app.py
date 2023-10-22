import warnings
import pandas as pd
import streamlit as st

class App():

    def __init__(self):
        self.pageConfig = st.set_page_config(page_title='Simulador Método Bazin', page_icon=None, layout="centered", initial_sidebar_state="collapsed", menu_items=None)
        self.pageConfig = st.title('Simulador Método Bazin', help = 'O Método de Décio Bazin é uma forma majoritariamente quantitativa e matemática para escolher ações. Assim, ela dá prioridade a múltiplos de investimento e dados na hora de fazer suas filtragens. Portanto, esse simulador tem a função de realizar um filtro naquelas empresas que atendem os requisitos desse método para encontrar as melhores opções de ativos disponíveis no mercado')
        self.filtroPerenidade = ['Utilidade Pública', 'Bens Industriais', 'Financeiro', 'Materiais Básicos', 'Consumo não Cíclico']
        self.colunasRetornoRent = ['1 Mês Atrás', '3 Mêses Atrás', 'Último 1 Ano', 'Último 2 Anos', 'Último 5 Anos', 'Últimos 10 Anos']
        self.colunasRetornoDG = ['DY', 'Liquidez Média Diaria', 'Dívida Líquida/Ebitda', 'Dívida Líquida/Patrimônio', 'Setor']
        self.colunasRetornoRentReal = ['rent_real_mes', 'rent_real_3_meses', 'rent_real_1_ano', 'rent_real_2_anos', 'rent_real_5_anos', 'rent_real_10_anos']
        self.compAtivos = ['DY', 'Liquidez Média Diaria', 'Dívida Líquida/Ebitda', 'Dívida Líquida/Patrimônio', 'P/L', 'P/VP', 'EV/EBITDA', 'EV/EBIT', 'P/EBITDA', 'P/EBIT', 'Margem Líquida', 'Margem Bruta', 'Margem Ebit', 'Margem Ebitda', 'Dívida Líquida/Ebit', 'Dívida Bruta/Patrimônio', 'ROE', 'ROIC', 'ROA', 'CAGR Receita 5 Anos', 'CAGR Lucro 5 Anos', 'Valor Mercado']

    def datasetRead(self):
        self.dataset = pd.read_csv("./data/companies_treated.csv", delimiter = ';').rename(columns={'empresa' : 'Empresa', 'cotacao' : 'Cotação', 'dividend yield' : 'DY', 'liquidez media diaria' : 'Liquidez Média Diaria', 'dívida líquida/ebitda' : 'Dívida Líquida/Ebitda', 'dívida líquida/patrimônio' : 'Dívida Líquida/Patrimônio', 'setor': 'Setor', 'rent_mes' : '1 Mês Atrás', 'rent_3_meses' : '3 Mêses Atrás', 'rent_1_ano' : 'Último 1 Ano', 'rent_2_anos' : 'Último 2 Anos', 'rent_5_anos' : 'Último 5 Anos', 'rent_10_anos' : 'Últimos 10 Anos', 'p/l' : 'P/L', 'p/vp' : 'P/VP', 'ev/ebitda' : 'EV/EBITDA', 'ev/ebit' : 'EV/EBIT', 'p/ebitda' : 'P/EBITDA', 'p/ebit' : 'P/EBIT', 'margem liquida' : 'Margem Líquida', 'margem bruta' : 'Margem Bruta', 'margem ebit' : 'Margem Ebit', 'margem ebitda' : 'Margem Ebitda', 'dívida líquida/ebit' : 'Dívida Líquida/Ebit', 'dívida bruta/patrimônio' : 'Dívida Bruta/Patrimônio', 'roe' : 'ROE', 'roic' : 'ROIC', 'roa' : 'ROA', 'cagr receitas 5 anos' : 'CAGR Receita 5 Anos', 'cagr lucros 5 anos' : 'CAGR Lucro 5 Anos', 'valor mercado' : 'Valor Mercado'})
    
    def datasetView(self):
        self.sideBar()
        self.initializeSession()
        with st.form(key='my_form'):
            self.dataset = self.dataset.set_index('Empresa')
            self.listSelect = self.dataset['codigo'].tolist()
            self.listSelect.insert(0, 'Todos os Ativos')
            self.listAtivos = st.multiselect('Selecione os ativos', self.listSelect, placeholder = 'Ex: TAEE4, BBAS3, SULA11', help = "A opção 'Todos os Ativos' tende a demorar devido a quantidade de ativos disponíveis, logo, escolha ativos de forma personalizada")
            if "Todos os Ativos" in self.listAtivos:
                self.listAtivos = self.dataset['codigo'].tolist()
            self.listAtivos.append('Comparação Entre Ativos')
            if st.form_submit_button('Confirmar') == True:
                st.session_state['botaoConfirma'] = 'Sim'

        if st.session_state['botaoConfirma']:
            self.guias = st.tabs(self.listAtivos)
            self.ativosGuias = [self.dataset.loc[(self.dataset.codigo == x)] for x in self.listAtivos]
            for cont, guia in enumerate(self.guias):
                with guia:
                    if cont == len(self.guias)-1:
                        st.write('**Indicadores Adicionais**')
                        self.teste = [self.ativosGuias[x].loc[:,self.compAtivos].T for x in range(cont)]
                        self.teste2 = pd.concat(self.teste, axis=1)
                        st.write(self.teste2)

                        st.write('**Comparação da Rentabildidade**')
                        self.rentAtivos = [self.ativosGuias[x].loc[:,self.colunasRetornoRent].T for x in range(cont)]
                        self.resultRents = pd.concat(self.rentAtivos, axis=1)
                        st.line_chart(self.resultRents)
                        
                    else:
                        st.subheader(self.listAtivos[cont])
                        st.write(self.ativosGuias[cont]['sobre'][0])
                        self.filtroPerene(cont)
                        self.filtroBazin()

                        with st.expander(f'INFORMAÇÕES PRINCIPAIS DA {self.listAtivos[cont]}'):
                            st.write('**Indicadores Principais**') 
                            self.retornoDG = self.ativosGuias[cont].loc[:,self.colunasRetornoDG]
                            st.write(self.retornoDG)

                            st.write('**Rentabilidade x Rentabilidade Real**')
                            self.concatDF = pd.concat([self.ativosGuias[cont].loc[:,self.colunasRetornoRent], self.ativosGuias[cont].loc[:,self.colunasRetornoRentReal].rename(columns={'rent_real_mes' : '1 Mês Atrás', 'rent_real_3_meses' : '3 Mêses Atrás', 'rent_real_1_ano' : 'Último 1 Ano', 'rent_real_2_anos' : 'Último 2 Anos', 'rent_real_5_anos' : 'Último 5 Anos', 'rent_real_10_anos' : 'Últimos 10 Anos'})], axis=0)
                            self.resetIndexDF = self.concatDF.reset_index(drop=True).T
                            self.renameIndexDF = self.resetIndexDF.rename(columns={0 : "Rentabilidade", 1 : "Rentabilidade Real"})
                            st.line_chart(self.renameIndexDF)
                            
                            self.precoTeto = round(16.67*((self.retornoDG['DY']/100)*self.ativosGuias[cont]['Cotação']), 2)
                            if not self.statusFiltro:
                                st.write(f"**Recomendação de Compra** ❌")
                                st.write("A situação de compra é não recomendada devido ao ativo não atender os requisitos do método")
                            else:
                                if float(self.ativosGuias[cont]['Cotação']) <= self.precoTeto[0]:
                                    st.write(f"**Recomendação de Compra** ✅")
                                    st.write(f"De acordo com Bazin o preço máximo atual é de {self.precoTeto[0]} para {self.listAtivos[cont]}") 
                                    st.write(f"Logo, a situação de compra é recomendada devido ao preço mais recente ser de {str(self.ativosGuias[cont]['Cotação'][0])} e por atender os requisitos do método") 
                                else:
                                    st.write(f"**Recomendação de Compra** ❌")
                                    st.write(f"De acordo com Bazin o preço máximo atual é de {self.precoTeto[0]} para {self.listAtivos[cont]}") 
                                    st.write(f"Logo, o ativo está considerado caro devido o ser preço mais recente ser de {self.ativosGuias[cont]['Cotação'][0]}")

                        with st.expander('INFORMAÇÕES COMPLEMENTARES'):
                            st.write(self.ativosGuias[cont]['informacoes_complementares'][0])

    def filtroPerene(self, cont):
        if st.session_state['Perene'] == 'Sim':
            self.statusFiltro = float(self.ativosGuias[cont]['Liquidez Média Diaria']/100000) >= float(st.session_state['Liquidez']) and float(self.ativosGuias[cont]['DY']) >= float(st.session_state['Dividend Yield']) and float(self.ativosGuias[cont]['Dívida Líquida/Ebitda']) <= float(st.session_state['Dívida Líquida/EBITDA']) and float(self.ativosGuias[cont]['Dívida Líquida/Patrimônio']) <= float(st.session_state['Dívida Líquida/Patrimônio Líquido']) and str(self.ativosGuias[cont]['Setor'].iloc[0]) in self.filtroPerenidade
        else:
            self.statusFiltro = float(self.ativosGuias[cont]['Liquidez Média Diaria']/100000) >= float(st.session_state['Liquidez']) and float(self.ativosGuias[cont]['dividend yield']) >= float(st.session_state['Dividend Yield']) and float(self.ativosGuias[cont]['Dívida Líquida/Ebitda']) <= float(st.session_state['Dívida Líquida/EBITDA']) and float(self.ativosGuias[cont]['Dívida Líquida/Patrimônio']) <= float(st.session_state['Dívida Líquida/Patrimônio Líquido'])
    
    def filtroBazin(self):
        if self.statusFiltro:
            st.write('**Status:** Aprovada no método Décio Bazin ✅') 
        else:
            st.write('**Status:** Reprovada no método Décio Bazin ❌')

    def sideBar(self):
        st.sidebar.write('**Indicadores Fundamentais Bazin:**')
        st.session_state['Liquidez'] = st.sidebar.slider('Liquidez', 0, 100, 5, help='Indica a possibilidade de transformar um ativo financeiro em dinheiro no mesmo dia em que o investidor solicita o resgate. Recomendado acima de 5')
        st.session_state['Dividend Yield'] = st.sidebar.slider('Dividend Yield', 1, 100, 6, help="Indicador utilizado para relacionar os proventos pagos por uma empresa e o preço atual de suas ações. Recomendado acima de 6")
        st.session_state['Dívida Líquida/EBITDA'] = st.sidebar.slider('Dívida Líquida/EBITDA', 0, 100, 3, help='Indica quanto tempo seria necessário para pagar a dívida líquida da empresa considerada o EBITDA atual. Indica também o grau de envividamento da empresa. Recomendado abaixo de 3')
        st.session_state['Dívida Líquida/Patrimônio Líquido'] = st.sidebar.slider('Dívida Líquida/Patrimônio Líquido', 0, 100, 1, help='Indica quanto de dívida uma empresa está usasndo para financiar os seus ativos em relação ao patrimônio dos acionistas. Recomendado abaixo de 1')
        st.session_state['Perene'] = st.sidebar.radio('Setores Perenes:', ['Sim','Não'], help = 'Os setores perenes são aqueles que são considerados estáveis e duradouros ao longo do tempo, com uma demanda constante e uma tendência a sobreviver a flutuações econômicas')

    def initializeSession(self):
        if 'botaoConfirma' not in st.session_state: 
            st.session_state['botaoConfirma'] = None

if __name__ == "__main__":

    warnings.simplefilter(action='ignore', category=FutureWarning)

    app = App()
    app.datasetRead()
    app.datasetView()
