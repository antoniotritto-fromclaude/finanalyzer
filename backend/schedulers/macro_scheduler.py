"""
Macro Report Scheduler
Genera report automaticamente a orari programmati
"""
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import os

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════
# 📅 CONFIGURAZIONE ORARI
# ══════════════════════════════════════════════════════════════════

REPORT_CONFIG = {
    # Orario di pubblicazione target (quando vuoi che il report sia pronto)
    "target_publish_time": "08:15",  # HH:MM formato 24h

    # Anticipo per generazione (1 ora e 30 minuti prima)
    "generation_advance_minutes": 90,  # 1h 30min

    # Giorni attivi (1=Lunedì, 7=Domenica)
    "active_days": [1, 2, 3, 4, 5],  # Lun-Ven

    # Directory output
    "output_dir": Path(__file__).parent.parent.parent / "reports" / "macro",

    # Formato nome file
    "filename_format": "macro_report_{date}_{time}.txt",

    # Mantieni ultimi N report
    "keep_last_n_reports": 30,
}


# ══════════════════════════════════════════════════════════════════
# 🕐 CALCOLO ORARI
# ══════════════════════════════════════════════════════════════════

def calculate_generation_time() -> str:
    """
    Calcola orario di generazione basato su target e anticipo

    Returns:
        Orario generazione formato "HH:MM"

    Example:
        Target: 08:15
        Anticipo: 90 minuti
        Risultato: 06:45
    """
    target_time = REPORT_CONFIG["target_publish_time"]
    advance_minutes = REPORT_CONFIG["generation_advance_minutes"]

    # Parse target time
    hour, minute = map(int, target_time.split(":"))

    # Crea datetime di oggi con target time
    target_dt = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Sottrai anticipo
    generation_dt = target_dt - timedelta(minutes=advance_minutes)

    # Ritorna formato HH:MM
    return generation_dt.strftime("%H:%M")


def get_next_generation_time() -> datetime:
    """
    Calcola prossimo orario di generazione

    Returns:
        Prossimo datetime di generazione
    """
    generation_time = calculate_generation_time()
    hour, minute = map(int, generation_time.split(":"))

    now = datetime.now()
    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

    # Se l'orario è già passato oggi, programma per domani
    if next_run <= now:
        next_run += timedelta(days=1)

    # Salta weekend se non attivo
    while next_run.isoweekday() not in REPORT_CONFIG["active_days"]:
        next_run += timedelta(days=1)

    return next_run


# ══════════════════════════════════════════════════════════════════
# 📊 GENERAZIONE E SALVATAGGIO
# ══════════════════════════════════════════════════════════════════

def generate_and_save_report() -> str:
    """
    Genera report macro e salva su disco

    Returns:
        Path del file salvato
    """
    logger.info("🔄 Avvio generazione report automatico...")

    try:
        # Import qui per evitare dipendenze circolari
        from backend.analyzers.macro_report import generate_macro_report

        # Genera report
        report_text = generate_macro_report()

        # Crea directory se non esiste
        output_dir = REPORT_CONFIG["output_dir"]
        output_dir.mkdir(parents=True, exist_ok=True)

        # Nome file con timestamp
        now = datetime.now()
        filename = REPORT_CONFIG["filename_format"].format(
            date=now.strftime("%Y%m%d"),
            time=now.strftime("%H%M")
        )

        filepath = output_dir / filename

        # Salva report
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_text)

        logger.info(f"✅ Report salvato: {filepath}")

        # Pulizia vecchi report
        cleanup_old_reports()

        return str(filepath)

    except Exception as e:
        logger.error(f"❌ Errore generazione report: {e}")
        raise


def cleanup_old_reports():
    """
    Rimuove report vecchi, mantenendo solo gli ultimi N
    """
    try:
        output_dir = REPORT_CONFIG["output_dir"]
        keep_n = REPORT_CONFIG["keep_last_n_reports"]

        if not output_dir.exists():
            return

        # Lista tutti i report
        reports = sorted(
            output_dir.glob("macro_report_*.txt"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Elimina i più vecchi
        for old_report in reports[keep_n:]:
            old_report.unlink()
            logger.info(f"🗑️  Rimosso report vecchio: {old_report.name}")

    except Exception as e:
        logger.warning(f"⚠️  Errore pulizia report vecchi: {e}")


# ══════════════════════════════════════════════════════════════════
# 📬 NOTIFICHE E EXPORT
# ══════════════════════════════════════════════════════════════════

def get_latest_report() -> str:
    """
    Ottiene il report più recente

    Returns:
        Contenuto del report più recente
    """
    output_dir = REPORT_CONFIG["output_dir"]

    if not output_dir.exists():
        return None

    reports = sorted(
        output_dir.glob("macro_report_*.txt"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if reports:
        with open(reports[0], 'r', encoding='utf-8') as f:
            return f.read()

    return None


def export_for_messaging(format_type: str = "telegram") -> str:
    """
    Esporta report formattato per piattaforme di messaggistica

    Args:
        format_type: "telegram", "whatsapp", "email"

    Returns:
        Report formattato
    """
    report = get_latest_report()

    if not report:
        return "Nessun report disponibile"

    if format_type == "telegram":
        # Telegram supporta markdown
        return report

    elif format_type == "whatsapp":
        # WhatsApp ha limiti di caratteri, accorcia
        lines = report.split('\n')
        # Prendi prime 50 righe
        short_report = '\n'.join(lines[:50])
        short_report += "\n\n... (report completo disponibile su FinAnalyzer Pro)"
        return short_report

    elif format_type == "email":
        # Email supporta HTML
        html_report = f"""
        <html>
        <body style="font-family: monospace; background: #1E293B; color: #FFFFFF; padding: 20px;">
            <pre style="white-space: pre-wrap;">{report}</pre>
        </body>
        </html>
        """
        return html_report

    return report


# ══════════════════════════════════════════════════════════════════
# 🤖 SCHEDULER PRINCIPALE
# ══════════════════════════════════════════════════════════════════

def job():
    """
    Job principale eseguito dallo scheduler
    """
    now = datetime.now()

    # Controlla se oggi è un giorno attivo
    if now.isoweekday() not in REPORT_CONFIG["active_days"]:
        logger.info(f"⏭️  Oggi è {now.strftime('%A')}, scheduler non attivo")
        return

    logger.info("=" * 60)
    logger.info(f"🤖 MACRO REPORT SCHEDULER - {now.strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 60)

    try:
        # Genera e salva report
        filepath = generate_and_save_report()

        logger.info(f"📊 Report disponibile: {filepath}")
        logger.info(f"⏰ Pronto per pubblicazione alle {REPORT_CONFIG['target_publish_time']}")

        # Qui puoi aggiungere invio email/telegram/etc
        # send_telegram_notification(filepath)
        # send_email_notification(filepath)

    except Exception as e:
        logger.error(f"❌ Errore job scheduler: {e}")

    logger.info("=" * 60)


def start_scheduler(blocking: bool = False):
    """
    Avvia lo scheduler

    Args:
        blocking: Se True, blocca il thread principale
    """
    generation_time = calculate_generation_time()

    logger.info("=" * 60)
    logger.info("🚀 AVVIO MACRO REPORT SCHEDULER")
    logger.info("=" * 60)
    logger.info(f"📅 Orario pubblicazione target: {REPORT_CONFIG['target_publish_time']}")
    logger.info(f"⏰ Anticipo generazione: {REPORT_CONFIG['generation_advance_minutes']} minuti")
    logger.info(f"🕐 Orario generazione: {generation_time}")
    logger.info(f"📆 Giorni attivi: {REPORT_CONFIG['active_days']} (Lun=1, Dom=7)")
    logger.info(f"📁 Output directory: {REPORT_CONFIG['output_dir']}")

    next_run = get_next_generation_time()
    logger.info(f"⏭️  Prossima generazione: {next_run.strftime('%d/%m/%Y %H:%M:%S')}")
    logger.info("=" * 60)

    # Programma job
    schedule.every().day.at(generation_time).do(job)

    if blocking:
        logger.info("🔄 Scheduler in esecuzione (modalità blocking)...")
        logger.info("   Premi CTRL+C per interrompere")

        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check ogni minuto
        except KeyboardInterrupt:
            logger.info("🛑 Scheduler interrotto dall'utente")
    else:
        logger.info("✅ Scheduler configurato (modalità non-blocking)")
        logger.info("   Ricorda di chiamare schedule.run_pending() periodicamente")


def run_now():
    """
    Esegue il job immediatamente (per test)
    """
    logger.info("▶️  Esecuzione manuale immediata...")
    job()


# ══════════════════════════════════════════════════════════════════
# 📊 INFO E STATISTICHE
# ══════════════════════════════════════════════════════════════════

def get_scheduler_info() -> dict:
    """
    Ottiene informazioni sullo scheduler

    Returns:
        Dict con configurazione e stato
    """
    generation_time = calculate_generation_time()
    next_run = get_next_generation_time()

    # Conta report esistenti
    output_dir = REPORT_CONFIG["output_dir"]
    num_reports = len(list(output_dir.glob("macro_report_*.txt"))) if output_dir.exists() else 0

    return {
        "target_publish_time": REPORT_CONFIG["target_publish_time"],
        "generation_advance_minutes": REPORT_CONFIG["generation_advance_minutes"],
        "calculated_generation_time": generation_time,
        "next_run": next_run.strftime("%d/%m/%Y %H:%M:%S"),
        "active_days": REPORT_CONFIG["active_days"],
        "output_dir": str(REPORT_CONFIG["output_dir"]),
        "reports_stored": num_reports,
        "keep_last_n": REPORT_CONFIG["keep_last_n_reports"],
    }


# ══════════════════════════════════════════════════════════════════
# 🧪 TEST
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("\n" + "=" * 60)
    print("📊 MACRO REPORT SCHEDULER - TEST")
    print("=" * 60 + "\n")

    # Mostra info
    info = get_scheduler_info()
    print("📋 CONFIGURAZIONE:")
    for key, value in info.items():
        print(f"   {key}: {value}")

    print("\n" + "-" * 60 + "\n")

    # Menu test
    print("Opzioni:")
    print("1. Esegui report adesso (test)")
    print("2. Avvia scheduler (blocking)")
    print("3. Mostra ultimo report")
    print("4. Esporta per Telegram")
    print("5. Esporta per WhatsApp")

    choice = input("\nScelta (1-5): ").strip()

    if choice == "1":
        run_now()
    elif choice == "2":
        start_scheduler(blocking=True)
    elif choice == "3":
        report = get_latest_report()
        if report:
            print("\n" + "=" * 60)
            print(report)
            print("=" * 60)
        else:
            print("❌ Nessun report disponibile")
    elif choice == "4":
        export = export_for_messaging("telegram")
        print("\n📱 TELEGRAM FORMAT:")
        print(export)
    elif choice == "5":
        export = export_for_messaging("whatsapp")
        print("\n💬 WHATSAPP FORMAT:")
        print(export)
