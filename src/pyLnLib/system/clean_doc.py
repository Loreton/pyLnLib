# clean_doc.py
# Funzioni per la pulizia del testo dei documenti
#
#
import inspect

def clean_doc(text: object, *args) -> str:
    # Se il msg contiene placeholder come %s, sostituiscili
    if args:
        formatted_msg = text % args
        args=() # azzera args
    else:
        formatted_msg = text
    """Wrapper per inspect.cleandoc con type ignore."""
    return inspect.cleandoc(formatted_msg)  # type: ignore


if __name__ == "__main__":
    project_name = "test_cleanDOC"

    content = clean_doc(f'''
        #!/usr/bin/env python3
        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).parent))

        from {project_name.lower()}.main import main

        if __name__ == "__main__":
            sys.exit(main())
    ''')
    print(content)
