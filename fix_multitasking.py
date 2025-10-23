"""
Crea un mock di multitasking per bypassare il problema
"""
import sys
import os
from types import ModuleType

# Crea un modulo mock di multitasking
multitasking = ModuleType('multitasking')

# Funzioni mock
def task(func):
    """Decorator mock - esegue normalmente"""
    return func

def set_max_threads(n):
    """Mock function"""
    pass

def set_engine(engine):
    """Mock function"""
    pass

def wait_for_tasks():
    """Mock function"""
    pass

def cpu_count():
    """Return CPU count"""
    return os.cpu_count() or 4

# Aggiungi al modulo
multitasking.task = task
multitasking.set_max_threads = set_max_threads
multitasking.set_engine = set_engine
multitasking.wait_for_tasks = wait_for_tasks
multitasking.cpu_count = cpu_count

# Installa nel sys.modules
sys.modules['multitasking'] = multitasking

print("✅ Multitasking mock installato")
