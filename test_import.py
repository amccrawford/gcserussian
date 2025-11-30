try:
    from streamlit_audiorecorder import audiorecorder
    print("Successfully imported streamlit_audiorecorder")
except ImportError as e:
    print(f"Import failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
