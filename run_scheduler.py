#!/usr/bin/env python3
"""
Macro Report Scheduler Launcher
Avvia lo scheduler per generazione automatica report

Usage:
    python run_scheduler.py              # Avvia scheduler (blocking)
    python run_scheduler.py --once       # Genera report una volta e esce
    python run_scheduler.py --info       # Mostra configurazione
    python run_scheduler.py --daemon     # Avvia come daemon (background)
"""
import sys
import os
import logging
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# ── Fix multitasking PRIMA di importare yfinance ──────────────────────────
try:
    import fix_multitasking  # noqa
except Exception:
    pass

from backend.schedulers.macro_scheduler import (
    start_scheduler,
    run_now,
    get_scheduler_info,
    REPORT_CONFIG
)


def setup_logging(verbose: bool = False):
    """Configura logging"""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('macro_scheduler.log')
        ]
    )


def show_info():
    """Mostra informazioni configurazione"""
    info = get_scheduler_info()

    print("\n" + "=" * 70)
    print("📊 MACRO REPORT SCHEDULER - CONFIGURAZIONE")
    print("=" * 70 + "\n")

    print(f"🎯 Orario Pubblicazione Target:  {info['target_publish_time']}")
    print(f"⏰ Anticipo Generazione:         {info['generation_advance_minutes']} minuti")
    print(f"🕐 Orario Generazione Calcolato: {info['calculated_generation_time']}")
    print(f"📅 Prossima Esecuzione:          {info['next_run']}")
    print(f"📆 Giorni Attivi:                {info['active_days']} (1=Lun, 7=Dom)")
    print(f"📁 Directory Output:             {info['output_dir']}")
    print(f"📊 Report Salvati:               {info['reports_stored']}/{info['keep_last_n']}")

    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Macro Report Scheduler - Generazione automatica report finanziari"
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='Genera report una volta e esce (utile per cron)'
    )

    parser.add_argument(
        '--info',
        action='store_true',
        help='Mostra configurazione e esce'
    )

    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Avvia come daemon (background)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Output verboso (debug)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Info mode
    if args.info:
        show_info()
        return

    # Once mode (per cron)
    if args.once:
        print("▶️  Generazione singola report...")
        run_now()
        print("✅ Completato!")
        return

    # Daemon mode
    if args.daemon:
        print("🚀 Avvio scheduler in modalità daemon...")
        print("   Log salvato in: macro_scheduler.log")
        print("   Premi CTRL+C per interrompere\n")

        # TODO: Implement proper daemonization
        # For now, just run blocking
        start_scheduler(blocking=True)
        return

    # Default: blocking mode
    print("🚀 Avvio scheduler in modalità interattiva...")
    show_info()
    print("\n💡 Suggerimenti:")
    print("   - Usa --once per generare un report singolo")
    print("   - Usa --info per vedere la configurazione")
    print("   - Usa --daemon per eseguire in background")
    print("\n")

    start_scheduler(blocking=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Scheduler interrotto dall'utente")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
