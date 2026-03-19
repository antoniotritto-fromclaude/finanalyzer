#!/usr/bin/env python3
"""
Test script per verificare i collector di dati fondi
Testa: Quantalys, Investing.com, Morningstar

Usage:
    python test_collectors.py [isin|url]
    python test_collectors.py LU0738951036
    python test_collectors.py https://www.quantalys.it/fonds/106139
"""
import sys
import logging
from backend.data_collectors.quantalys import quantalys_collector
from backend.data_collectors.investing import investing_collector
from backend.data_collectors.morningstar import MorningstarCollector

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_quantalys(query):
    """Test Quantalys collector"""
    print("\n" + "="*60)
    print("TEST QUANTALYS")
    print("="*60)

    # Test URL detection
    if quantalys_collector.is_quantalys_url(query):
        print(f"✅ Detected as Quantalys URL")
        fund_id = quantalys_collector.extract_fund_id_from_url(query)
        print(f"   Fund ID: {fund_id}")

        if fund_id:
            # Get fund data
            data = quantalys_collector.get_fund_data(fund_id)
            if data:
                print(f"\n📊 Fund Data:")
                for key, value in data.items():
                    print(f"   {key}: {value}")

            # Get historical prices
            prices = quantalys_collector.get_historical_prices(fund_id, years=1)
            if prices is not None and not prices.empty:
                print(f"\n📈 Historical Prices: {len(prices)} points")
                print(f"   Latest: {prices.tail(3)}")
            else:
                print("   ⚠️  No historical data")
    else:
        # Search by ISIN/name
        print(f"🔍 Searching: {query}")
        results = quantalys_collector.search_fund(query)
        if results:
            print(f"✅ Found {len(results)} results:")
            for r in results[:3]:
                print(f"   - {r.get('name')} (ISIN: {r.get('isin')})")
        else:
            print("   ❌ No results")

def test_investing(query):
    """Test Investing.com collector"""
    print("\n" + "="*60)
    print("TEST INVESTING.COM")
    print("="*60)

    # Test URL detection
    if investing_collector.is_investing_url(query):
        print(f"✅ Detected as Investing.com URL")
        instrument = investing_collector.extract_instrument_from_url(query)
        print(f"   Instrument: {instrument}")

        if instrument:
            # Get historical prices
            prices = investing_collector.get_historical_prices(instrument, years=1)
            if prices is not None and not prices.empty:
                print(f"\n📈 Historical Prices: {len(prices)} points")
                print(f"   Latest: {prices.tail(3)}")
            else:
                print("   ⚠️  No historical data")
    else:
        # Search
        print(f"🔍 Searching: {query}")
        results = investing_collector.search(query)
        if results:
            print(f"✅ Found {len(results)} results:")
            for r in results[:3]:
                print(f"   - {r.get('name')} ({r.get('type')})")
                print(f"     URL: {r.get('url')}")
        else:
            print("   ❌ No results")

def test_morningstar(query):
    """Test Morningstar collector"""
    print("\n" + "="*60)
    print("TEST MORNINGSTAR")
    print("="*60)

    ms = MorningstarCollector()

    # Test URL detection
    if ms.is_morningstar_url(query):
        print(f"✅ Detected as Morningstar URL")
        fund_id = ms.extract_fund_id_from_url(query)
        print(f"   Fund ID: {fund_id}")

        if fund_id:
            # Get historical prices
            prices = ms.get_historical_prices_by_id(fund_id, years=1)
            if prices is not None and not prices.empty:
                print(f"\n📈 Historical Prices: {len(prices)} points")
                print(f"   Latest: {prices.tail(3)}")
            else:
                print("   ⚠️  No historical data")

            # Get fund details
            details = ms.get_fund_details(fund_id)
            if details:
                print(f"\n📊 Fund Details:")
                for key, value in details.items():
                    print(f"   {key}: {value}")
    else:
        # Check if ISIN
        if len(query) == 12 and query[:2].isalpha():
            print(f"🔍 Detected ISIN: {query}")
            prices = ms.get_historical_prices_by_isin(query, years=1)
            if prices is not None and not prices.empty:
                print(f"✅ Historical Prices: {len(prices)} points")
                print(f"   Latest: {prices.tail(3)}")
            else:
                print("   ⚠️  No historical data")
        else:
            # Search
            print(f"🔍 Searching: {query}")
            results = ms.search(query)
            if results:
                print(f"✅ Found {len(results)} results:")
                for r in results[:3]:
                    print(f"   - {r.get('name')} (ID: {r.get('id')}, ISIN: {r.get('isin')})")
            else:
                print("   ❌ No results")

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_collectors.py [isin|url|query]")
        print("\nExamples:")
        print("  python test_collectors.py LU0738951036")
        print("  python test_collectors.py https://www.quantalys.it/fonds/106139")
        print("  python test_collectors.py https://it.investing.com/funds/azimut-az-bond-patriot-a-eur")
        print("  python test_collectors.py https://global.morningstar.com/it/investimenti/fondi/F00000NRA8/quote")
        sys.exit(1)

    query = sys.argv[1]

    print(f"\n🧪 Testing collectors with: {query}\n")

    # Test all collectors
    try:
        test_quantalys(query)
    except Exception as e:
        print(f"❌ Quantalys test failed: {e}")

    try:
        test_investing(query)
    except Exception as e:
        print(f"❌ Investing.com test failed: {e}")

    try:
        test_morningstar(query)
    except Exception as e:
        print(f"❌ Morningstar test failed: {e}")

    print("\n" + "="*60)
    print("DONE")
    print("="*60)

if __name__ == "__main__":
    main()
