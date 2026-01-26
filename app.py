import streamlit as st
import pdfplumber
import pandas as pd
from utils import is_searchable_pdf, parse_page_selection
from extractor import extract_tables_from_buffer, convert_to_excel

st.set_page_config(page_title="PDF Table Extractor", layout="wide")

st.title("📄 PDF Table Extractor")
st.markdown("""
Este aplicativo extrai tabelas de arquivos PDF e as converte para Excel.
**Nota:** Este aplicativo não suporta arquivos digitalizados (imagens). O PDF deve conter texto selecionável.
""")

uploaded_file = st.file_uploader("Carregue seu arquivo PDF", type="pdf")

if uploaded_file is not None:
    # 1. Validation: Check if it's not just an image
    # Note: is_searchable_pdf consumes the buffer, so we need to reset it or handle it carefully.
    # pdfplumber.open can take the file-like object directly.
    # But if we read it once, we might need to seek(0).
    
    if not is_searchable_pdf(uploaded_file):
        st.error("⚠️ O arquivo carregado parece ser uma imagem ou digitalização. Este aplicativo requer PDFs com texto selecionável (sem OCR).")
    else:
        st.success("✅ Arquivo válido detectado.")
        
        # Reset pointer after check if needed, though pdfplumber usually handles it if passed correctly or refreshed.
        uploaded_file.seek(0)
        
        # Get total pages for UI
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                total_pages = len(pdf.pages)
        except Exception as e:
            st.error(f"Erro ao ler o PDF: {e}")
            st.stop()
            
        st.info(f"O documento possui {total_pages} páginas.")
        
        # 2. Page Selection
        extraction_mode = st.radio(
            "Selecione as páginas para extração:",
            ("Documento Inteiro", "Selecionar Páginas/Intervalo")
        )
        
        pages_to_extract = None # None implies all pages
        
        if extraction_mode == "Selecionar Páginas/Intervalo":
            page_input = st.text_input(
                f"Digite os números das páginas (ex: 1, 3-5, 10). Máximo: {total_pages}",
                placeholder="Ex: 1-5, 8"
            )
            if page_input:
                pages_to_extract = parse_page_selection(page_input, total_pages)
                if not pages_to_extract:
                    st.warning("Nenhuma página válida selecionada.")
                else:
                    st.write(f"Páginas selecionadas: {', '.join([str(p+1) for p in pages_to_extract])}")
            else:
                st.info("Digite o intervalo acima.")
        
        # Button to trigger extraction
        if st.button("Extrair Tabelas"):
            uploaded_file.seek(0) # Reset again before extraction
            
            with st.spinner("Extraindo tabelas..."):
                try:
                    # Logic to extract
                    tables_dict = extract_tables_from_buffer(uploaded_file, pages_to_extract)
                    
                    if not tables_dict:
                        st.warning("Nenhuma tabela foi encontrada nas páginas selecionadas.")
                    else:
                        st.success(f"Sucesso! Encontramos {len(tables_dict)} tabelas.")
                        
                        # Preview
                        with st.expander("Pré-visualizar Tabelas Extraídas"):
                            for key, df in tables_dict.items():
                                st.subheader(key)
                                st.dataframe(df)
                        
                        # Convert to Excel
                        excel_data = convert_to_excel(tables_dict)
                        
                        st.download_button(
                            label="📥 Baixar Excel (.xlsx)",
                            data=excel_data,
                            file_name=f"{uploaded_file.name.split('.')[0]}_tabelas.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                        
                except Exception as e:
                    st.error(f"Ocorreu um erro durante a extração: {e}")

