"""
Macro Financial Report - Vista Frontend
Genera e visualizza report macro-finanziari dinamici
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import time


def render():
    st.markdown('<h1 style="color:#FFFFFF !important;font-size:2.5rem;font-weight:800;margin-bottom:20px;">🌍 Macro Financial Report</h1>', unsafe_allow_html=True)

    # Info box
    st.markdown("""
    <div class="fin-card" style="background:#2F5F7F;border-left:4px solid #D4AF37;padding:14px 18px;color:#FFFFFF !important;">
        <b style="color:#FFFFFF !important;">🤖 Report AI Automatico:</b> <span style="color:#FFFFFF !important;">
        Questo report analizza in tempo reale i mercati globali su <b>8 macro-aree geografiche</b>,
        rileva correlazioni anomale, divergenze tra asset e genera alert intelligenti.</span>
        <br><br>
        <span style="color:#FFFFFF !important;">📊 <b>Copertura:</b> America del Nord, America del Sud, Europa, Nord Africa,
        Medio Oriente, Sudafrica, Asia & Oceania (50+ indici, valute, commodities)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════
    # SCHEDULER CONFIGURATION
    # ══════════════════════════════════════════════════════════════════

    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.5rem;font-weight:700;margin:20px 0;">⏰ Configurazione Generazione Automatica</h2>', unsafe_allow_html=True)

    with st.expander("⚙️ Impostazioni Scheduler", expanded=True):
        from backend.schedulers.macro_scheduler import get_scheduler_info, REPORT_CONFIG

        info = get_scheduler_info()

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("""
            <div style="background:#2F5F7F;padding:16px;border-radius:8px;">
                <div style="color:#9CA3AF;font-size:0.85rem;margin-bottom:8px;">🎯 Orario Pubblicazione Target</div>
                <div style="color:#FFFFFF;font-size:1.8rem;font-weight:800;">{}</div>
                <div style="color:#E5E7EB;font-size:0.8rem;margin-top:8px;">Quando vuoi ricevere il report</div>
            </div>
            """.format(info["target_publish_time"]), unsafe_allow_html=True)

        with col_b:
            st.markdown("""
            <div style="background:#2F5F7F;padding:16px;border-radius:8px;">
                <div style="color:#9CA3AF;font-size:0.85rem;margin-bottom:8px;">🕐 Orario Generazione</div>
                <div style="color:#FFFFFF;font-size:1.8rem;font-weight:800;">{}</div>
                <div style="color:#E5E7EB;font-size:0.8rem;margin-top:8px;">1h 30min prima (anticipo {}min)</div>
            </div>
            """.format(info["calculated_generation_time"], info["generation_advance_minutes"]), unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Info dettagliate
        col_c, col_d, col_e = st.columns(3)

        with col_c:
            st.metric("📅 Prossima Generazione", info["next_run"])

        with col_d:
            days_str = ", ".join(["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"][d-1] for d in info["active_days"])
            st.metric("📆 Giorni Attivi", days_str)

        with col_e:
            st.metric("📊 Report Salvati", f"{info['reports_stored']}/{info['keep_last_n']}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Note
        st.info("""
        **ℹ️ Come Funziona:**

        Il sistema genera automaticamente il report **1 ora e 30 minuti prima** dell'orario di pubblicazione desiderato.

        - **Orario pubblicazione**: 08:15 (esempio)
        - **Orario generazione**: 06:45 (automatico)
        - **Report salvato in**: `/reports/macro/`
        - **Giorni attivi**: Lun-Ven (personalizzabile)

        I report vengono salvati automaticamente e sono pronti per essere inviati via Telegram, WhatsApp o Email.
        """)

        # Modifica configurazione
        st.markdown("**🔧 Modifica Orari:**", unsafe_allow_html=True)

        col_mod1, col_mod2 = st.columns(2)

        with col_mod1:
            new_publish_time = st.time_input(
                "Orario Pubblicazione",
                value=datetime.strptime(REPORT_CONFIG["target_publish_time"], "%H:%M").time(),
                help="Quando vuoi ricevere il report pronto"
            )

        with col_mod2:
            new_advance = st.number_input(
                "Anticipo (minuti)",
                min_value=30,
                max_value=180,
                value=REPORT_CONFIG["generation_advance_minutes"],
                step=15,
                help="Quanto tempo prima generare il report"
            )

        if st.button("💾 Salva Configurazione", type="secondary"):
            # Aggiorna configurazione
            REPORT_CONFIG["target_publish_time"] = new_publish_time.strftime("%H:%M")
            REPORT_CONFIG["generation_advance_minutes"] = new_advance

            # Salva su file (opzionale - persistenza)
            st.success("✅ Configurazione aggiornata! Riavvia lo scheduler per applicare le modifiche.")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Bottoni azione
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

    with col1:
        if st.button("📊 Genera Report Adesso", type="primary", use_container_width=True):
            st.session_state["generate_report"] = True

    with col2:
        if st.button("💾 Salva Report in TXT", type="secondary", use_container_width=True):
            if "last_report" in st.session_state:
                st.download_button(
                    label="⬇️ Download Report",
                    data=st.session_state["last_report"],
                    file_name=f"macro_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ Genera prima un report")

    with col3:
        if st.button("📱 Esporta per Telegram", type="secondary", use_container_width=True):
            if "last_report" in st.session_state:
                from backend.schedulers.macro_scheduler import export_for_messaging
                # Salva per export
                telegram_text = st.session_state["last_report"]
                st.download_button(
                    label="⬇️ Download Telegram",
                    data=telegram_text,
                    file_name=f"telegram_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.warning("⚠️ Genera prima un report")

    with col4:
        auto_refresh = st.checkbox("🔄 Auto", help="Aggiorna automaticamente ogni 5 minuti")

    st.markdown("<br>", unsafe_allow_html=True)

    # Genera report
    if st.session_state.get("generate_report", False) or auto_refresh:
        with st.spinner("⏳ Generazione report in corso... (scaricamento dati da 50+ mercati globali)"):
            try:
                from backend.analyzers.macro_report import generate_macro_report

                report_text = generate_macro_report()
                st.session_state["last_report"] = report_text
                st.session_state["last_report_time"] = datetime.now()

                # Reset flag
                st.session_state["generate_report"] = False

            except Exception as e:
                st.error(f"❌ Errore nella generazione del report: {e}")
                st.exception(e)
                return

    # Mostra report
    if "last_report" in st.session_state:
        # Timestamp ultimo aggiornamento
        last_update = st.session_state.get("last_report_time", datetime.now())
        st.caption(f"🕐 Ultimo aggiornamento: {last_update.strftime('%d/%m/%Y %H:%M:%S')}")

        # Report in box con scroll
        st.markdown("""
        <style>
        .macro-report-box {
            background: #1E293B;
            border: 2px solid #D4AF37;
            border-radius: 12px;
            padding: 24px;
            color: #FFFFFF;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            white-space: pre-wrap;
            max-height: 800px;
            overflow-y: auto;
        }
        </style>
        """, unsafe_allow_html=True)

        report_html = f'<div class="macro-report-box">{st.session_state["last_report"]}</div>'
        st.markdown(report_html, unsafe_allow_html=True)

        # Auto-refresh dopo 5 minuti
        if auto_refresh:
            time.sleep(300)  # 5 minuti
            st.rerun()

    else:
        st.info("👆 Clicca su 'Genera Report Adesso' per iniziare l'analisi macro-finanziaria globale")

    # ══════════════════════════════════════════════════════════════════
    # SEZIONE SPIEGAZIONE
    # ══════════════════════════════════════════════════════════════════

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">📚 Come Leggere il Report</h2>', unsafe_allow_html=True)

    with st.expander("🌍 Analisi Geografica", expanded=False):
        st.markdown("""
        **8 Macro-Aree Monitorate:**

        1. **🇺🇸 America del Nord** - S&P 500, Dow Jones, Nasdaq, TSX Canada
        2. **🇧🇷 America del Sud** - Merval (ARG), Bovespa (BRA), IPC (MEX), COLCAP (COL)
        3. **🇪🇺 Europa** - Euro Stoxx 50, FTSE 100, DAX, CAC 40
        4. **🌍 Nord Africa** - EGX 30 Egitto
        5. **🕌 Medio Oriente** - Tadawul Arabia Saudita
        6. **🇿🇦 Sudafrica** - JSE Top 40
        7. **🌏 Asia & Oceania** - Nikkei, Shanghai, Hang Seng, ASX 200, KLSE, Jakarta

        **Cosa guardare:**
        - 📈 Trend positivo: mercato in crescita
        - 📉 Trend negativo: mercato in calo
        - Performance relativa tra regioni
        """)

    with st.expander("💵 Alert Valute", expanded=False):
        st.markdown("""
        **Valute Monitorate:**
        - Dollaro USA (DXY)
        - EUR/USD, GBP/USD, USD/JPY
        - Valute emergenti: MXN, BRL, CNH, AUD, CAD

        **Alert Automatici:**
        - Movimento DXY > 1% → Alert forte
        - Divergenze con commodities
        - Breakout rispetto a medie mobili
        """)

    with st.expander("⚠️ Correlazioni & Divergenze", expanded=False):
        st.markdown("""
        **Correlazioni da Monitorare:**
        - **Petrolio ↔ Dollaro**: Normalmente inversa
        - **Oro ↔ Dollaro**: Normalmente inversa
        - **Azioni ↔ Obbligazioni**: Normalmente inversa
        - **Settore Difesa ↔ Petrolio**: Correlazione in situazioni di crisi

        **Divergenze Anomale:**
        Quando asset correlati si muovono in direzioni inattese:
        - Petrolio sale + Dollaro sale = Anomalia
        - Oro scende + Dollaro scende = Anomalia

        **Cosa Significa:**
        - Possibile cambio di regime di mercato
        - Evento geopolitico in corso
        - Opportunità di trading
        """)

    with st.expander("📅 Eventi Chiave", expanded=False):
        st.markdown("""
        **Calendario Macro da Monitorare:**

        **Banche Centrali:**
        - Fed (USA): decisioni tassi, QE/QT
        - ECB (Europa): politica monetaria
        - BoJ (Giappone): controllo curva rendimenti
        - PBoC (Cina): tassi lending

        **Dati Economici:**
        - Inflazione (CPI, PCE)
        - Occupazione (NFP USA)
        - PIL trimestrale
        - PMI manifatturiero

        **Geopolitica:**
        - Tensioni commerciali
        - Conflitti regionali
        - Sanzioni internazionali
        """)

    # ══════════════════════════════════════════════════════════════════
    # DASHBOARD VELOCE
    # ══════════════════════════════════════════════════════════════════

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2 style="color:#FFFFFF !important;font-size:1.8rem;font-weight:800;margin:40px 0 20px 0;padding-bottom:12px;border-bottom:2px solid #D4AF37;">⚡ Dashboard Veloce</h2>', unsafe_allow_html=True)

    # Quick stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div style="background:#2F5F7F;padding:16px;border-radius:8px;text-align:center;">
            <div style="color:#9CA3AF;font-size:0.8rem;">Mercati Monitorati</div>
            <div style="color:#FFFFFF;font-size:2rem;font-weight:800;">50+</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:#2F5F7F;padding:16px;border-radius:8px;text-align:center;">
            <div style="color:#9CA3AF;font-size:0.8rem;">Macro-Aree</div>
            <div style="color:#FFFFFF;font-size:2rem;font-weight:800;">8</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background:#2F5F7F;padding:16px;border-radius:8px;text-align:center;">
            <div style="color:#9CA3AF;font-size:0.8rem;">Valute</div>
            <div style="color:#FFFFFF;font-size:2rem;font-weight:800;">9</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown("""
        <div style="background:#2F5F7F;padding:16px;border-radius:8px;text-align:center;">
            <div style="color:#9CA3AF;font-size:0.8rem;">Commodities</div>
            <div style="color:#FFFFFF;font-size:2rem;font-weight:800;">8</div>
        </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;color:#9CA3AF;font-size:0.8rem;padding:20px;">
        💡 <b>Tip:</b> Usa questo report per identificare opportunità di trading,
        hedge contro rischi macro, e comprendere i trend globali.<br>
        Report aggiornabile in tempo reale con dati da Yahoo Finance.
    </div>
    """, unsafe_allow_html=True)
