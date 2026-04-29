try:
    from src.main import main
    main()
except Exception as e:
    print(f"Boot error: {e}")
