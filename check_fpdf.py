try:
    import fpdf
    print(f"fpdf found: {fpdf.__version__}")
except ImportError as e:
    print(f"fpdf not found: {e}")
except Exception as e:
    print(f"Error: {e}")
