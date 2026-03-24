"""
💾 Data Manager - Persistent Storage for FinAnalyzer
Handles saving/loading of portfolios and custom funds
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


# ══════════════════════════════════════════════════════════════════════
# 📁 PATHS
# ══════════════════════════════════════════════════════════════════════

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)

PORTFOLIOS_FILE = DATA_DIR / "portfolios.json"
CUSTOM_FUNDS_FILE = DATA_DIR / "custom_funds.json"


# ══════════════════════════════════════════════════════════════════════
# 💼 PORTFOLIOS MANAGEMENT
# ══════════════════════════════════════════════════════════════════════

def save_portfolios(portfolios: Dict[str, Any]) -> bool:
    """
    Save portfolios to JSON file

    Args:
        portfolios: Dict with portfolio_name -> portfolio_data

    Returns:
        bool: Success status
    """
    try:
        # Add metadata
        data = {
            "last_updated": datetime.now().isoformat(),
            "version": "1.0",
            "portfolios": portfolios
        }

        with open(PORTFOLIOS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        print(f"Error saving portfolios: {e}")
        return False


def load_portfolios() -> Dict[str, Any]:
    """
    Load portfolios from JSON file

    Returns:
        Dict: Portfolio data or empty dict if not found
    """
    try:
        if not PORTFOLIOS_FILE.exists():
            return {}

        with open(PORTFOLIOS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get("portfolios", {})

    except Exception as e:
        print(f"Error loading portfolios: {e}")
        return {}


def delete_portfolio(portfolio_name: str) -> bool:
    """
    Delete a specific portfolio

    Args:
        portfolio_name: Name of portfolio to delete

    Returns:
        bool: Success status
    """
    try:
        portfolios = load_portfolios()

        if portfolio_name in portfolios:
            del portfolios[portfolio_name]
            return save_portfolios(portfolios)

        return False

    except Exception as e:
        print(f"Error deleting portfolio: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════
# 📊 CUSTOM FUNDS MANAGEMENT
# ══════════════════════════════════════════════════════════════════════

def save_custom_funds(funds: List[Dict[str, Any]]) -> bool:
    """
    Save custom funds to JSON file

    Args:
        funds: List of custom fund dictionaries

    Returns:
        bool: Success status
    """
    try:
        # Add metadata
        data = {
            "last_updated": datetime.now().isoformat(),
            "version": "1.0",
            "count": len(funds),
            "funds": funds
        }

        with open(CUSTOM_FUNDS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return True

    except Exception as e:
        print(f"Error saving custom funds: {e}")
        return False


def load_custom_funds() -> List[Dict[str, Any]]:
    """
    Load custom funds from JSON file

    Returns:
        List: Custom fund data or empty list if not found
    """
    try:
        if not CUSTOM_FUNDS_FILE.exists():
            return []

        with open(CUSTOM_FUNDS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get("funds", [])

    except Exception as e:
        print(f"Error loading custom funds: {e}")
        return []


def add_custom_fund(fund: Dict[str, Any]) -> bool:
    """
    Add a new custom fund

    Args:
        fund: Fund dictionary with name, isin, nav, etc.

    Returns:
        bool: Success status
    """
    try:
        funds = load_custom_funds()

        # Check if fund already exists (by ISIN or name)
        for existing_fund in funds:
            if (fund.get("isin") and existing_fund.get("isin") == fund.get("isin")) or \
               (existing_fund.get("name") == fund.get("name")):
                # Update existing fund
                existing_fund.update(fund)
                return save_custom_funds(funds)

        # Add new fund
        fund["added_at"] = datetime.now().isoformat()
        funds.append(fund)

        return save_custom_funds(funds)

    except Exception as e:
        print(f"Error adding custom fund: {e}")
        return False


def delete_custom_fund(fund_identifier: str) -> bool:
    """
    Delete a custom fund by ISIN or name

    Args:
        fund_identifier: ISIN or name of fund to delete

    Returns:
        bool: Success status
    """
    try:
        funds = load_custom_funds()

        # Filter out the fund to delete
        funds = [f for f in funds if f.get("isin") != fund_identifier and f.get("name") != fund_identifier]

        return save_custom_funds(funds)

    except Exception as e:
        print(f"Error deleting custom fund: {e}")
        return False


# ══════════════════════════════════════════════════════════════════════
# 📈 STATISTICS
# ══════════════════════════════════════════════════════════════════════

def get_storage_stats() -> Dict[str, Any]:
    """
    Get statistics about stored data

    Returns:
        Dict: Statistics (portfolio count, fund count, file sizes, etc.)
    """
    try:
        portfolios = load_portfolios()
        funds = load_custom_funds()

        return {
            "portfolios_count": len(portfolios),
            "custom_funds_count": len(funds),
            "portfolios_file_size": PORTFOLIOS_FILE.stat().st_size if PORTFOLIOS_FILE.exists() else 0,
            "custom_funds_file_size": CUSTOM_FUNDS_FILE.stat().st_size if CUSTOM_FUNDS_FILE.exists() else 0,
            "data_dir": str(DATA_DIR),
        }

    except Exception as e:
        print(f"Error getting storage stats: {e}")
        return {
            "portfolios_count": 0,
            "custom_funds_count": 0,
            "portfolios_file_size": 0,
            "custom_funds_file_size": 0,
            "data_dir": str(DATA_DIR),
        }


# ══════════════════════════════════════════════════════════════════════
# 🧪 TEST
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Testing Data Manager...")

    # Test portfolios
    test_portfolios = {
        "Test Portfolio": {
            "symbols": ["AAPL", "MSFT"],
            "weights": {"AAPL": 0.5, "MSFT": 0.5},
            "created_at": datetime.now().isoformat()
        }
    }

    print(f"Saving portfolios: {save_portfolios(test_portfolios)}")
    print(f"Loading portfolios: {load_portfolios()}")

    # Test custom funds
    test_fund = {
        "name": "Test Fund",
        "isin": "LU1234567890",
        "nav": 100.50,
        "currency": "EUR"
    }

    print(f"Adding custom fund: {add_custom_fund(test_fund)}")
    print(f"Loading custom funds: {load_custom_funds()}")

    # Stats
    print(f"Storage stats: {get_storage_stats()}")
