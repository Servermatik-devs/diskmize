"""Built-in translations for DiskMize; no network translation dependency."""

from __future__ import annotations

DEFAULT_LANGUAGE = "es"

LANGUAGES = {"es": "Español", "en": "English"}

_STRINGS: dict[str, dict[str, str]] = {
    "es": {
        "app_title": "DiskMize",
        "menu": "Menú",
        "options": "Opciones",
        "exit": "Salir",
        "about_menu": "Acerca de...",
        "about": "Acerca de DiskMize",
        "updates": "Actualizaciones",
        "help": "Ayuda",
        "choose_option": "Seleccione una opción:",
        "scan_dir": "Escanear directorio",
        "scan_disk": "Escanear disco",
        "stop": "Parar escaneo",
        "search_files": "Buscar archivos:",
        "search": "Buscar",
        "col_name": "Nombre",
        "col_size": "Tamaño",
        "col_modified": "Última modificación",
        "open": "Abrir",
        "delete": "Eliminar",
        "reveal": "Revelar en carpeta",
        "ready": "Listo.",
        "scanning": "Escaneando...",
        "cancelled": "Escaneo cancelado.",
        "done": "Escaneo finalizado: {count} elementos.",
        "errors": "{count} elementos no accesibles.",
        "confirm_delete": "¿Desea eliminar los archivos seleccionados?",
        "delete_title": "Eliminar archivos",
        "deleted": "Eliminados {count} archivo(s), {size} liberados.",
        "delete_errors": "No se pudieron eliminar {count} archivo(s).",
        "language": "Idioma:",
        "scan_type": "Tipo de escaneo:",
        "save": "Guardar cambios",
        "close": "Cerrar",
        "error": "Error",
        "warning": "Aviso",
        "no_selection": "Seleccione un elemento de la lista.",
        "author": "Desarrollado por Mario Ramos",
        "description": (
            "DiskMize te ayuda a identificar qué archivos y carpetas ocupan "
            "más espacio en tu disco. Analiza directorios o unidades y presenta "
            "los resultados para que puedas decidir qué revisar."
        ),
        "github_label": "GitHub: github.com/marrionesa",
        "email_label": "Contacto: diskmize@marioramos.me",
        "license_label": "Licencia: GNU GPL v3 o posterior",
        "help_intro": "GUÍA DE USO",
        "help_text": (
            "1. INICIAR UN ANÁLISIS\n"
            "Pulsa «Escanear directorio» para elegir una carpeta o "
            "«Escanear disco» para seleccionar una unidad o punto de montaje.\n\n"
            "2. REVISAR LOS RESULTADOS\n"
            "La lista muestra los elementos encontrados y su tamaño. En el "
            "análisis de archivos también se indica la última modificación. "
            "Revisa los resultados para localizar los elementos que más espacio ocupan.\n\n"
            "3. ABRIR O LOCALIZAR UN ELEMENTO\n"
            "Selecciona una fila y utiliza «Abrir» para abrir el elemento "
            "o «Revelar en carpeta» para localizarlo en el administrador "
            "de archivos, cuando el sistema lo permita.\n\n"
            "4. CANCELAR UN ANÁLISIS\n"
            "Pulsa «Parar escaneo» para interrumpir el análisis. Los resultados "
            "pueden estar incompletos si lo cancelas.\n\n"
            "5. ELIMINAR ARCHIVOS — PRECAUCIÓN\n"
            "Comprueba cuidadosamente las rutas antes de confirmar. La "
            "eliminación es permanente y no utiliza la papelera. No elimines "
            "archivos del sistema ni elementos cuya función desconozcas.\n\n"
            "6. ARCHIVOS NO ACCESIBLES\n"
            "Los archivos a los que no tengas acceso pueden quedar fuera del "
            "análisis. Los resultados no siempre representan todos los datos "
            "de la unidad.\n\n"
            "PROYECTO Y SOPORTE\n"
            "Consulta el código fuente en GitHub o contacta con el desarrollador "
            "mediante los enlaces de esta ventana."
        ),
        "updates_text": (
            "Versión actual: {version}\n\n"
            "La comprobación automática de actualizaciones todavía no está "
            "implementada en esta versión."
        ),
        "theme": "Tema",
    },
    "en": {
        "app_title": "DiskMize",
        "menu": "Menu",
        "options": "Options",
        "exit": "Exit",
        "about_menu": "About...",
        "about": "About DiskMize",
        "updates": "Updates",
        "help": "Help",
        "choose_option": "Choose an option:",
        "scan_dir": "Scan directory",
        "scan_disk": "Scan drive",
        "stop": "Stop scan",
        "search_files": "Find files:",
        "search": "Search",
        "col_name": "Name",
        "col_size": "Size",
        "col_modified": "Last modified",
        "open": "Open",
        "delete": "Delete",
        "reveal": "Reveal in folder",
        "ready": "Ready.",
        "scanning": "Scanning...",
        "cancelled": "Scan cancelled.",
        "done": "Scan finished: {count} items.",
        "errors": "{count} items could not be read.",
        "confirm_delete": "Delete the selected files?",
        "delete_title": "Delete files",
        "deleted": "Deleted {count} file(s), {size} freed.",
        "delete_errors": "Could not delete {count} file(s).",
        "language": "Language:",
        "scan_type": "Scan type:",
        "save": "Save changes",
        "close": "Close",
        "error": "Error",
        "warning": "Warning",
        "no_selection": "Select an item in the list.",
        "author": "Developed by Mario Ramos",
        "description": (
            "DiskMize helps you identify which files and folders use the most "
            "disk space. Scan directories or drives and review the results "
            "before deciding what to investigate."
        ),
        "github_label": "GitHub: github.com/marrionesa",
        "email_label": "Contact: diskmize@marioramos.me",
        "license_label": "License: GNU GPL v3 or later",
        "help_intro": "USER GUIDE",
        "help_text": (
            "1. START A SCAN\n"
            "Click 'Scan directory' to choose a folder or 'Scan drive' "
            "to select a drive or mount point.\n\n"
            "2. REVIEW THE RESULTS\n"
            "The list displays discovered items and their sizes. File scans "
            "also show the last modification time. Review the results to "
            "identify the items using the most space.\n\n"
            "3. OPEN OR LOCATE AN ITEM\n"
            "Select a row and click 'Open' to open it or 'Reveal in folder' "
            "to locate it in your file manager, where supported.\n\n"
            "4. CANCEL A SCAN\n"
            "Click 'Stop scan' to interrupt the analysis. Results may be "
            "incomplete if you cancel it.\n\n"
            "5. DELETE FILES — CAUTION\n"
            "Carefully check file paths before confirming. Deletion is "
            "permanent and does not use the recycle bin. Never delete system "
            "files or items whose purpose you do not understand.\n\n"
            "6. INACCESSIBLE FILES\n"
            "Files you cannot access may be excluded from the scan. Results "
            "may not represent every item stored on the drive.\n\n"
            "PROJECT AND SUPPORT\n"
            "Visit the source code on GitHub or contact the developer "
            "using the links in this window."
        ),
        "updates_text": (
            "Current version: {version}\n\n"
            "Automatic update checking has not yet been implemented "
            "in this version."
        ),
        "theme": "Theme",
    },
}


def normalize_language(language: str | None) -> str:
    if not language:
        return DEFAULT_LANGUAGE

    code = language.strip().lower()
    if code in _STRINGS:
        return code

    aliases = {
        "spanish": "es",
        "espanol": "es",
        "español": "es",
        "english": "en",
        "ingles": "en",
        "inglés": "en",
    }
    return aliases.get(code, DEFAULT_LANGUAGE)


def translate(
    key: str,
    language: str = DEFAULT_LANGUAGE,
    **kwargs: object,
) -> str:
    """Look up a translation, falling back to Spanish and then the key."""
    code = normalize_language(language)
    text = _STRINGS.get(code, {}).get(key) or _STRINGS[DEFAULT_LANGUAGE].get(key, key)

    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError, ValueError):
            return text

    return text
