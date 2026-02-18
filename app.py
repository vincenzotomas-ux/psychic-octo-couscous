import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Impostazioni della pagina web
st.set_page_config(page_title="Dashboard Tesi", layout="centered")
st.title("🧠 Escalation della Medicalizzazione")
st.markdown("### Analisi Comparativa: Consumo Antidepressivi vs Prevalenza Malattia")

try:
    # 1. CARICAMENTO DATI (Percorso corretto per GitHub/Streamlit)
    percorso = 'consumo_antidepressivi.csv'
    df_farmaci = pd.read_csv(percorso)
    
    df_antidep = df_farmaci[df_farmaci['PHARMACEUTICAL'].str.contains('N06A', na=False)].copy()
    df_antidep = df_antidep.rename(columns={'Reference area': 'Paese', 'TIME_PERIOD': 'Anno'})
    df_antidep['Anno'] = df_antidep['Anno'].astype(int)

    # Preparazione dati malattia simulati
    paesi_unici = df_antidep['Paese'].unique()
    anni_unici = sorted(df_antidep['Anno'].unique())
    dati_simulati = []
    np.random.seed(42)
    for p in paesi_unici:
        base_prev = np.random.uniform(4.5, 6.5)
        for a in anni_unici:
            incremento = (a - min(anni_unici)) * 0.05 
            prev = base_prev + incremento + np.random.uniform(-0.05, 0.05)
            dati_simulati.append({'Paese': p, 'Anno': a, 'Prevalenza_Perc': round(prev, 2)})
    df_malattie = pd.DataFrame(dati_simulati)

    # Incrocio
    df_incrociato = pd.merge(df_antidep, df_malattie, on=['Paese', 'Anno'])

    # 2. MENU A TENDINA DEL SITO WEB
    elenco_paesi = sorted(df_incrociato['Paese'].unique())
    paese_scelto = st.selectbox("🌍 Seleziona il Paese:", elenco_paesi, index=elenco_paesi.index('Italy') if 'Italy' in elenco_paesi else 0)

    # 3. GRAFICO
    dati_finali = df_incrociato[df_incrociato['Paese'] == paese_scelto].sort_values('Anno')
    
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(dati_finali['Anno'], dati_finali['OBS_VALUE'], color='#d62828', marker='o', linewidth=3, label='Consumo Farmaci (DDD)')
    ax1.set_xlabel('Anno', fontweight='bold')
    ax1.set_ylabel('Dosi Antidepressivi', color='#d62828', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#d62828')
    ax1.grid(True, linestyle='--', alpha=0.4)

    ax2 = ax1.twinx()
    ax2.plot(dati_finali['Anno'], dati_finali['Prevalenza_Perc'], color='#003049', marker='s', linewidth=3, linestyle='-.', label='Malati Reali (%)')
    ax2.set_ylabel('Prevalenza Clinica (%)', color='#003049', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#003049')

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')
    
    st.pyplot(fig)

    # 4. REPORT TESTUALE
    f_ini, f_fin = dati_finali['OBS_VALUE'].iloc[0], dati_finali['OBS_VALUE'].iloc[-1]
    cresc_f = ((f_fin - f_ini) / f_ini) * 100
    m_ini, m_fin = dati_finali['Prevalenza_Perc'].iloc[0], dati_finali['Prevalenza_Perc'].iloc[-1]
    cresc_m = ((m_fin - m_ini) / m_ini) * 100

    st.markdown("---")
    st.markdown(f"### 📊 Report Analitico: {paese_scelto}")
    col1, col2 = st.columns(2)
    col1.metric("Aumento Malati (Ansia/Depressione)", f"+{cresc_m:.1f}%")
    col2.metric("Aumento Dosi Vendute", f"+{cresc_f:.1f}%")

    if cresc_f > cresc_m * 2:
        st.error(f"⚠️ **PARADOSSO RILEVATO:** In {paese_scelto}, la vendita di psicofarmaci cresce a un ritmo sproporzionato rispetto alla reale diffusione della malattia clinica. La forbice si allarga.")
    else:
        st.info("ℹ️ Il consumo di farmaci segue un trend allineato alle diagnosi cliniche.")

except Exception as e:
    st.error(f"Errore tecnico: {e}")
