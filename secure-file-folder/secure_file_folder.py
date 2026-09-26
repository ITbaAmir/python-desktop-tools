# ============================================================
# Secure File & Folder
# ============================================================
#
# Was macht dieses Programm?
#
# Dieses Programm verschlüsselt:
#
# - einzelne Dateien
# - komplette Ordner
#
# und kann sie später wieder entschlüsseln.
#
# Sicherheit:
#
# - AES-256-GCM für Verschlüsselung
# - Argon2id für die Ableitung des Schlüssels aus dem Passwort
# - zufälliger Salt für jede Verschlüsselung
# - zufällige Nonces
# - Manipulationsschutz durch AES-GCM
# - Dateiname / Ordnertyp werden ebenfalls verschlüsselt
# - große Dateien werden stückweise verarbeitet
#
# WICHTIG:
#
# Es gibt KEINE Passwort-Wiederherstellung.
#
# Wenn das Passwort verloren geht, kann die Datei nicht
# wiederhergestellt werden.
#
# Das Programm löscht die Originaldateien NICHT automatisch.
#
# ============================================================
# BENÖTIGTE PYTHON-BIBLIOTHEKEN
# ============================================================
#
# Einmal installieren:
#
# py -m pip install cryptography argon2-cffi
#
# ============================================================


# ============================================================
# Standard-Bibliotheken
# ============================================================

import os
import json
import base64
import tarfile
import tempfile
import threading

from pathlib import Path


# ============================================================
# Tkinter
# ============================================================

import tkinter as tk

from tkinter import (
    ttk,
    filedialog,
    messagebox
)


# ============================================================
# Kryptografie
# ============================================================

from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes
)

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from cryptography.exceptions import InvalidTag


# ============================================================
# Argon2id
# ============================================================

from argon2.low_level import (
    hash_secret_raw,
    Type,
    ARGON2_VERSION
)


# ============================================================
# Programm-Konstanten
# ============================================================

APP_NAME = "Secure File & Folder"


# Kennung unseres eigenen verschlüsselten Dateiformats.
#
# So können wir erkennen, ob eine Datei von unserem
# Programm erstellt wurde.
MAGIC = b"PYSEC001"


VERSION = 1


# AES-GCM Authentifizierungs-Tag
GCM_TAG_SIZE = 16


# Wie viele Bytes auf einmal gelesen werden.
#
# Dadurch können auch große Dateien verarbeitet werden,
# ohne sie komplett in den RAM zu laden.
CHUNK_SIZE = 1024 * 1024


# ============================================================
# Argon2id Einstellungen
# ============================================================
#
# memory_cost wird in KiB angegeben.
#
# 65536 KiB = 64 MiB
#
# Argon2id macht Passwort-Raten absichtlich teuer.
# ============================================================

ARGON_MEMORY_COST = 65536

ARGON_TIME_COST = 3

ARGON_PARALLELISM = 1

KEY_LENGTH = 32


# ============================================================
# Globale Variablen
# ============================================================

encrypt_source = None

encrypt_source_type = None

decrypt_source = None

operation_running = False


# ============================================================
# Hilfsfunktion: Base64
# ============================================================

def encode_base64(data):

    return base64.b64encode(
        data
    ).decode(
        "ascii"
    )


def decode_base64(data):

    return base64.b64decode(
        data
    )


# ============================================================
# Schlüssel aus Passwort erstellen
# ============================================================

def derive_key(
    password,
    salt,
    memory_cost,
    time_cost,
    parallelism
):

    password_bytes = password.encode(
        "utf-8"
    )

    key = hash_secret_raw(

        secret=password_bytes,

        salt=salt,

        time_cost=time_cost,

        memory_cost=memory_cost,

        parallelism=parallelism,

        hash_len=KEY_LENGTH,

        type=Type.ID,

        version=ARGON2_VERSION

    )

    return key


# ============================================================
# Passwortstärke
# ============================================================

def calculate_password_strength(
    password
):

    if not password:

        return (
            "Kein Passwort",
            0
        )

    score = 0

    # Länge ist am wichtigsten.
    if len(password) >= 8:
        score += 1

    if len(password) >= 10:
        score += 1

    if len(password) >= 16:
        score += 1

    if len(password) >= 20:
        score += 1

    # Verschiedene Zeichentypen
    if any(
        character.islower()
        for character in password
    ):
        score += 1

    if any(
        character.isupper()
        for character in password
    ):
        score += 1

    if any(
        character.isdigit()
        for character in password
    ):
        score += 1

    if any(
        not character.isalnum()
        for character in password
    ):
        score += 1

    if score <= 2:

        return (
            "Schwach",
            20
        )

    elif score <= 4:

        return (
            "Mittel",
            45
        )

    elif score <= 6:

        return (
            "Stark",
            70
        )

    else:

        return (
            "Sehr stark",
            100
        )


# ============================================================
# Passwortanzeige aktualisieren
# ============================================================

def update_password_strength(
    event=None
):

    password = encrypt_password_entry.get()

    strength, value = (
        calculate_password_strength(
            password
        )
    )

    password_strength_label.config(

        text=f"Passwortstärke: {strength}"

    )

    password_strength_bar["value"] = value


# ============================================================
# Passwort anzeigen / verstecken
# ============================================================

def toggle_encrypt_password():

    if encrypt_show_password_var.get():

        show_character = ""

    else:

        show_character = "*"

    encrypt_password_entry.config(
        show=show_character
    )

    encrypt_confirm_entry.config(
        show=show_character
    )


def toggle_decrypt_password():

    if decrypt_show_password_var.get():

        show_character = ""

    else:

        show_character = "*"

    decrypt_password_entry.config(
        show=show_character
    )


# ============================================================
# Datei auswählen
# ============================================================

def choose_encrypt_file():

    global encrypt_source
    global encrypt_source_type

    file_path = filedialog.askopenfilename(

        title="Datei auswählen"

    )

    if not file_path:

        return

    encrypt_source = Path(
        file_path
    )

    encrypt_source_type = "file"

    encrypt_source_label.config(

        text=str(
            encrypt_source
        )

    )

    encrypt_type_label.config(

        text="Ausgewählt: Datei"

    )


# ============================================================
# Ordner auswählen
# ============================================================

def choose_encrypt_folder():

    global encrypt_source
    global encrypt_source_type

    folder_path = filedialog.askdirectory(

        title="Ordner auswählen"

    )

    if not folder_path:

        return

    encrypt_source = Path(
        folder_path
    )

    encrypt_source_type = "folder"

    encrypt_source_label.config(

        text=str(
            encrypt_source
        )

    )

    encrypt_type_label.config(

        text="Ausgewählt: Ordner"

    )


# ============================================================
# Verschlüsselte Datei auswählen
# ============================================================

def choose_encrypted_file():

    global decrypt_source

    file_path = filedialog.askopenfilename(

        title="Verschlüsselte Datei auswählen",

        filetypes=[

            (
                "Secure Files",
                "*.secure"
            ),

            (
                "Alle Dateien",
                "*.*"
            )

        ]

    )

    if not file_path:

        return

    decrypt_source = Path(
        file_path
    )

    decrypt_source_label.config(

        text=str(
            decrypt_source
        )

    )


# ============================================================
# Prüfen, ob Pfad innerhalb eines Ordners liegt
# ============================================================

def path_is_inside(
    child,
    parent
):

    try:

        child = Path(
            child
        ).resolve()

        parent = Path(
            parent
        ).resolve()

        return os.path.commonpath(

            [
                str(child),
                str(parent)
            ]

        ) == str(parent)

    except Exception:

        return False


# ============================================================
# Encryption Writer
# ============================================================
#
# Dieser kleine Wrapper nimmt normale Daten entgegen,
# verschlüsselt sie und schreibt nur den Ciphertext auf Disk.
#
# Besonders praktisch für Ordner:
#
# tarfile
#    ↓
# EncryptionWriter
#    ↓
# AES-GCM
#    ↓
# .secure
#
# Dadurch müssen wir beim Verschlüsseln eines Ordners KEIN
# unverschlüsseltes ZIP/TAR-Archiv auf der Festplatte anlegen.
# ============================================================

class EncryptionWriter:

    def __init__(
        self,
        output_file,
        encryptor
    ):

        self.output_file = output_file

        self.encryptor = encryptor

        self.position = 0

    def write(
        self,
        data
    ):

        if not data:

            return 0

        encrypted = self.encryptor.update(
            data
        )

        self.output_file.write(
            encrypted
        )

        self.position += len(
            data
        )

        return len(
            data
        )

    def tell(
        self
    ):

        return self.position

    def flush(
        self
    ):

        self.output_file.flush()

    def writable(
        self
    ):

        return True

    def seekable(
        self
    ):

        return False


# ============================================================
# Header erstellen
# ============================================================

def create_header(
    salt,
    metadata_nonce,
    data_nonce,
    encrypted_metadata
):

    header = {

        "version":
            VERSION,

        "kdf":
            "Argon2id",

        "cipher":
            "AES-256-GCM",

        "memory_cost":
            ARGON_MEMORY_COST,

        "time_cost":
            ARGON_TIME_COST,

        "parallelism":
            ARGON_PARALLELISM,

        "salt":
            encode_base64(
                salt
            ),

        "metadata_nonce":
            encode_base64(
                metadata_nonce
            ),

        "data_nonce":
            encode_base64(
                data_nonce
            ),

        "encrypted_metadata":
            encode_base64(
                encrypted_metadata
            )

    }

    header_bytes = json.dumps(

        header,

        separators=(
            ",",
            ":"
        )

    ).encode(
        "utf-8"
    )

    return header_bytes


# ============================================================
# Verschlüsselung starten
# ============================================================

def start_encryption():

    global operation_running

    if operation_running:

        return

    if encrypt_source is None:

        messagebox.showwarning(

            "Nichts ausgewählt",

            "Bitte zuerst eine Datei oder einen Ordner auswählen."

        )

        return

    password = encrypt_password_entry.get()

    confirm_password = (
        encrypt_confirm_entry.get()
    )

    # ========================================================
    # Passwort prüfen
    # ========================================================

    if not password:

        messagebox.showwarning(

            "Passwort fehlt",

            "Bitte ein Passwort eingeben."

        )

        return

    if password != confirm_password:

        messagebox.showerror(

            "Passwörter stimmen nicht überein",

            "Die beiden Passwörter sind unterschiedlich."

        )

        return

    # Für sensible Verschlüsselung keine sehr kurzen Passwörter.
    if len(password) < 10:

        messagebox.showwarning(

            "Passwort zu kurz",

            "Bitte mindestens 10 Zeichen verwenden.\n\n"
            "Für wichtige Daten sind 16 oder mehr "
            "Zeichen empfehlenswert."

        )

        return

    # ========================================================
    # Ziel auswählen
    # ========================================================

    default_name = (

        encrypt_source.name
        + ".secure"

    )

    output_path = filedialog.asksaveasfilename(

        title="Verschlüsselte Datei speichern",

        initialfile=default_name,

        defaultextension=".secure",

        filetypes=[

            (
                "Secure File",
                "*.secure"
            )

        ]

    )

    if not output_path:

        return

    output_path = Path(
        output_path
    )

    # ========================================================
    # Sicherheitsprüfung für Ordner
    # ========================================================
    #
    # Niemals die .secure Datei INNERHALB des Ordners speichern,
    # den wir gerade archivieren.
    #
    # Sonst würde sich das Archiv während der Erstellung
    # möglicherweise selbst einlesen.
    # ========================================================

    if (
        encrypt_source_type == "folder"
        and path_is_inside(
            output_path,
            encrypt_source
        )
    ):

        messagebox.showerror(

            "Ungültiger Speicherort",

            "Die verschlüsselte Datei darf nicht innerhalb "
            "des Ordners gespeichert werden, der gerade "
            "verschlüsselt wird.\n\n"
            "Bitte einen anderen Speicherort auswählen."

        )

        return

    operation_running = True

    set_encrypt_controls(
        False
    )

    encrypt_progress.start(
        12
    )

    encrypt_status_label.config(

        text="Verschlüsselung wird vorbereitet..."

    )

    threading.Thread(

        target=encrypt_worker,

        args=(
            encrypt_source,
            encrypt_source_type,
            password,
            output_path
        ),

        daemon=True

    ).start()


# ============================================================
# Eigentliche Verschlüsselung
# ============================================================

def encrypt_worker(
    source_path,
    source_type,
    password,
    output_path
):

    try:

        # ====================================================
        # Zufällige Werte
        # ====================================================

        salt = os.urandom(
            16
        )

        metadata_nonce = os.urandom(
            12
        )

        data_nonce = os.urandom(
            12
        )

        # ====================================================
        # Schlüssel ableiten
        # ====================================================

        update_encrypt_status(
            "Sicherer Schlüssel wird aus Passwort erzeugt..."
        )

        key = derive_key(

            password,

            salt,

            ARGON_MEMORY_COST,

            ARGON_TIME_COST,

            ARGON_PARALLELISM

        )

        # ====================================================
        # Metadaten
        # ====================================================
        #
        # Auch der ursprüngliche Dateiname wird verschlüsselt.
        # ====================================================

        metadata = {

            "name":
                source_path.name,

            "type":
                source_type

        }

        metadata_bytes = json.dumps(

            metadata,

            ensure_ascii=False,

            separators=(
                ",",
                ":"
            )

        ).encode(
            "utf-8"
        )

        # Kleine Metadaten können bequem mit AESGCM
        # in einem Schritt verschlüsselt werden.
        metadata_aes = AESGCM(
            key
        )

        encrypted_metadata = metadata_aes.encrypt(

            metadata_nonce,

            metadata_bytes,

            MAGIC

        )

        # ====================================================
        # Header
        # ====================================================

        header_bytes = create_header(

            salt,

            metadata_nonce,

            data_nonce,

            encrypted_metadata

        )

        header_length = len(
            header_bytes
        ).to_bytes(
            4,
            "big"
        )

        # Der Header wird selbst nicht verschlüsselt,
        # enthält aber keine Original-Dateinamen.
        authenticated_header = (

            MAGIC
            + header_length
            + header_bytes

        )

        # ====================================================
        # AES-256-GCM für eigentliche Daten
        # ====================================================

        cipher = Cipher(

            algorithms.AES(
                key
            ),

            modes.GCM(
                data_nonce
            )

        )

        encryptor = cipher.encryptor()

        # Header gegen Manipulation absichern.
        encryptor.authenticate_additional_data(

            authenticated_header

        )

        # ====================================================
        # Ausgabedatei
        # ====================================================

        with open(
            output_path,
            "wb"
        ) as output_file:

            # MAGIC
            output_file.write(
                MAGIC
            )

            # Header-Länge
            output_file.write(
                header_length
            )

            # Header
            output_file.write(
                header_bytes
            )

            encryption_writer = EncryptionWriter(

                output_file,

                encryptor

            )

            # =================================================
            # DATEI
            # =================================================

            if source_type == "file":

                update_encrypt_status(

                    f"Verschlüssele Datei:\n"
                    f"{source_path.name}"

                )

                with open(
                    source_path,
                    "rb"
                ) as input_file:

                    while True:

                        chunk = input_file.read(
                            CHUNK_SIZE
                        )

                        if not chunk:

                            break

                        encryption_writer.write(
                            chunk
                        )

            # =================================================
            # ORDNER
            # =================================================

            else:

                update_encrypt_status(

                    "Ordner wird komprimiert und "
                    "gleichzeitig verschlüsselt..."

                )

                # ------------------------------------------------
                # Streaming TAR.GZ
                # ------------------------------------------------
                #
                # Der Ordner wird direkt durch die
                # Verschlüsselung geschrieben.
                #
                # Es entsteht KEIN unverschlüsseltes
                # Zwischenarchiv auf der Festplatte.
                # ------------------------------------------------

                with tarfile.open(

                    fileobj=encryption_writer,

                    mode="w|gz",

                    dereference=True

                ) as archive:

                    for item in source_path.iterdir():

                        archive.add(

                            item,

                            arcname=item.name,

                            recursive=True

                        )

            # =================================================
            # Verschlüsselung finalisieren
            # =================================================

            final_data = encryptor.finalize()

            if final_data:

                output_file.write(
                    final_data
                )

            # GCM-Tag ans Ende schreiben
            output_file.write(
                encryptor.tag
            )

            output_file.flush()

            os.fsync(
                output_file.fileno()
            )

        window.after(

            0,

            encryption_finished,

            output_path

        )

    except Exception as error:

        # Unvollständige Zieldatei entfernen.
        try:

            if output_path.exists():

                output_path.unlink()

        except Exception:

            pass

        window.after(

            0,

            encryption_failed,

            str(error)

        )


# ============================================================
# Verschlüsselungsstatus
# ============================================================

def update_encrypt_status(
    text
):

    window.after(

        0,

        encrypt_status_label.config,

        {
            "text":
                text
        }

    )


# ============================================================
# Verschlüsselung fertig
# ============================================================

def encryption_finished(
    output_path
):

    global operation_running

    operation_running = False

    encrypt_progress.stop()

    set_encrypt_controls(
        True
    )

    encrypt_status_label.config(

        text="Verschlüsselung erfolgreich."

    )

    messagebox.showinfo(

        "Erfolgreich verschlüsselt",

        "Die verschlüsselte Datei wurde erstellt:\n\n"
        f"{output_path}\n\n"
        "WICHTIG:\n"
        "Das Original wurde NICHT gelöscht.\n\n"
        "Bewahre dein Passwort sicher auf. "
        "Es gibt keine Passwort-Wiederherstellung."

    )


# ============================================================
# Verschlüsselungsfehler
# ============================================================

def encryption_failed(
    error
):

    global operation_running

    operation_running = False

    encrypt_progress.stop()

    set_encrypt_controls(
        True
    )

    encrypt_status_label.config(

        text="Verschlüsselung fehlgeschlagen."

    )

    messagebox.showerror(

        "Fehler",

        "Die Verschlüsselung konnte nicht "
        "abgeschlossen werden:\n\n"
        f"{error}"

    )


# ============================================================
# Encrypt Buttons aktivieren / deaktivieren
# ============================================================

def set_encrypt_controls(
    enabled
):

    state = (

        "normal"
        if enabled
        else "disabled"

    )

    encrypt_file_button.config(
        state=state
    )

    encrypt_folder_button.config(
        state=state
    )

    encrypt_button.config(
        state=state
    )


# ============================================================
# Header lesen
# ============================================================

def read_secure_header(
    file
):

    # ========================================================
    # MAGIC
    # ========================================================

    magic = file.read(
        len(MAGIC)
    )

    if magic != MAGIC:

        raise ValueError(

            "Diese Datei ist keine gültige "
            "Secure-File-&-Folder-Datei."

        )

    # ========================================================
    # Header-Länge
    # ========================================================

    length_bytes = file.read(
        4
    )

    if len(length_bytes) != 4:

        raise ValueError(
            "Beschädigter Datei-Header."
        )

    header_length = int.from_bytes(

        length_bytes,

        "big"

    )

    # Schutz gegen völlig ungültige Header.
    if (
        header_length <= 0
        or header_length > 1024 * 1024
    ):

        raise ValueError(
            "Ungültige Header-Länge."
        )

    # ========================================================
    # Header
    # ========================================================

    header_bytes = file.read(
        header_length
    )

    if len(header_bytes) != header_length:

        raise ValueError(
            "Unvollständiger Datei-Header."
        )

    try:

        header = json.loads(

            header_bytes.decode(
                "utf-8"
            )

        )

    except Exception:

        raise ValueError(
            "Beschädigter Datei-Header."
        )

    authenticated_header = (

        MAGIC
        + length_bytes
        + header_bytes

    )

    return (
        header,
        authenticated_header
    )


# ============================================================
# Verschlüsselte Datei prüfen
# ============================================================

def validate_header(
    header
):

    required_fields = [

        "version",
        "kdf",
        "cipher",
        "memory_cost",
        "time_cost",
        "parallelism",
        "salt",
        "metadata_nonce",
        "data_nonce",
        "encrypted_metadata"

    ]

    for field in required_fields:

        if field not in header:

            raise ValueError(

                "Die verschlüsselte Datei "
                "hat einen ungültigen Header."

            )

    if header["version"] != VERSION:

        raise ValueError(

            "Diese Dateiversion wird von "
            "diesem Programm nicht unterstützt."

        )

    if header["kdf"] != "Argon2id":

        raise ValueError(
            "Unbekannte Schlüsselableitung."
        )

    if header["cipher"] != "AES-256-GCM":

        raise ValueError(
            "Unbekanntes Verschlüsselungsverfahren."
        )


# ============================================================
# Entschlüsselung starten
# ============================================================

def start_decryption():

    global operation_running

    if operation_running:

        return

    if decrypt_source is None:

        messagebox.showwarning(

            "Keine Datei",

            "Bitte zuerst eine verschlüsselte "
            ".secure-Datei auswählen."

        )

        return

    password = decrypt_password_entry.get()

    if not password:

        messagebox.showwarning(

            "Passwort fehlt",

            "Bitte das Passwort eingeben."

        )

        return

    output_folder = filedialog.askdirectory(

        title="Zielordner für entschlüsselte Daten auswählen"

    )

    if not output_folder:

        return

    operation_running = True

    decrypt_button.config(
        state="disabled"
    )

    decrypt_file_button.config(
        state="disabled"
    )

    decrypt_progress.start(
        12
    )

    decrypt_status_label.config(

        text="Entschlüsselung wird vorbereitet..."

    )

    threading.Thread(

        target=decrypt_worker,

        args=(

            decrypt_source,

            password,

            Path(output_folder)

        ),

        daemon=True

    ).start()


# ============================================================
# Eindeutigen Dateinamen erzeugen
# ============================================================

def unique_path(
    path
):

    if not path.exists():

        return path

    parent = path.parent

    stem = path.stem

    suffix = path.suffix

    counter = 1

    while True:

        candidate = (

            parent
            / f"{stem}_{counter}{suffix}"

        )

        if not candidate.exists():

            return candidate

        counter += 1


# ============================================================
# Sichere TAR-Pfade prüfen
# ============================================================

def safe_extract_tar(
    archive_path,
    destination
):

    destination = destination.resolve()

    with tarfile.open(

        archive_path,

        "r:gz"

    ) as archive:

        members = archive.getmembers()

        for member in members:

            # Keine Links extrahieren.
            if (
                member.issym()
                or member.islnk()
            ):

                raise ValueError(

                    "Das Archiv enthält einen "
                    "nicht erlaubten Link."

                )

            target = (

                destination
                / member.name

            ).resolve()

            try:

                common = os.path.commonpath(

                    [
                        str(destination),
                        str(target)
                    ]

                )

            except ValueError:

                raise ValueError(
                    "Unsicherer Pfad im Archiv."
                )

            if common != str(
                destination
            ):

                raise ValueError(

                    "Unsicherer Pfad im Archiv erkannt."

                )

        archive.extractall(

            destination,

            members=members

        )


# ============================================================
# Eigentliche Entschlüsselung
# ============================================================

def decrypt_worker(
    source_path,
    password,
    output_folder
):

    temporary_path = None

    try:

        update_decrypt_status(

            "Lese verschlüsselte Datei..."

        )

        with open(
            source_path,
            "rb"
        ) as encrypted_file:

            # =================================================
            # Header
            # =================================================

            (
                header,
                authenticated_header

            ) = read_secure_header(
                encrypted_file
            )

            validate_header(
                header
            )

            # =================================================
            # Parameter lesen
            # =================================================

            salt = decode_base64(
                header["salt"]
            )

            metadata_nonce = decode_base64(
                header["metadata_nonce"]
            )

            data_nonce = decode_base64(
                header["data_nonce"]
            )

            encrypted_metadata = decode_base64(

                header["encrypted_metadata"]

            )

            memory_cost = int(
                header["memory_cost"]
            )

            time_cost = int(
                header["time_cost"]
            )

            parallelism = int(
                header["parallelism"]
            )

            # =================================================
            # Schlüssel erzeugen
            # =================================================

            update_decrypt_status(

                "Passwort wird überprüft..."

            )

            key = derive_key(

                password,

                salt,

                memory_cost,

                time_cost,

                parallelism

            )

            # =================================================
            # Metadaten entschlüsseln
            # =================================================
            #
            # Falsches Passwort wird normalerweise bereits
            # hier erkannt.
            # =================================================

            metadata_aes = AESGCM(
                key
            )

            try:

                metadata_bytes = (
                    metadata_aes.decrypt(

                        metadata_nonce,

                        encrypted_metadata,

                        MAGIC

                    )
                )

            except InvalidTag:

                raise ValueError(

                    "Falsches Passwort oder "
                    "beschädigte/manipulierte Datei."

                )

            metadata = json.loads(

                metadata_bytes.decode(
                    "utf-8"
                )

            )

            original_name = metadata[
                "name"
            ]

            source_type = metadata[
                "type"
            ]

            # =================================================
            # GCM Tag lesen
            # =================================================

            current_position = (
                encrypted_file.tell()
            )

            encrypted_file.seek(

                0,

                os.SEEK_END

            )

            file_size = (
                encrypted_file.tell()
            )

            if (
                file_size
                < current_position + GCM_TAG_SIZE
            ):

                raise ValueError(

                    "Die verschlüsselte Datei "
                    "ist unvollständig."

                )

            ciphertext_end = (

                file_size
                - GCM_TAG_SIZE

            )

            encrypted_file.seek(
                ciphertext_end
            )

            tag = encrypted_file.read(
                GCM_TAG_SIZE
            )

            ciphertext_length = (

                ciphertext_end
                - current_position

            )

            encrypted_file.seek(
                current_position
            )

            # =================================================
            # AES-GCM Decryptor
            # =================================================

            cipher = Cipher(

                algorithms.AES(
                    key
                ),

                modes.GCM(

                    data_nonce,

                    tag

                )

            )

            decryptor = cipher.decryptor()

            decryptor.authenticate_additional_data(

                authenticated_header

            )

            # =================================================
            # Temporäre Datei
            # =================================================
            #
            # GCM garantiert die Integrität erst nach finalize().
            #
            # Deshalb schreiben wir zunächst in eine temporäre
            # Datei und verwenden das Ergebnis erst nach
            # erfolgreicher Authentifizierung.
            # =================================================

            temporary_file = tempfile.NamedTemporaryFile(

                prefix="secure_decrypt_",

                suffix=(
                    ".tar.gz"
                    if source_type == "folder"
                    else ".tmp"
                ),

                delete=False

            )

            temporary_path = Path(
                temporary_file.name
            )

            update_decrypt_status(

                "Daten werden entschlüsselt..."

            )

            remaining = ciphertext_length

            try:

                while remaining > 0:

                    read_size = min(

                        CHUNK_SIZE,

                        remaining

                    )

                    encrypted_chunk = (
                        encrypted_file.read(
                            read_size
                        )
                    )

                    if not encrypted_chunk:

                        raise ValueError(

                            "Die verschlüsselte Datei "
                            "ist unvollständig."

                        )

                    remaining -= len(
                        encrypted_chunk
                    )

                    plain_chunk = decryptor.update(

                        encrypted_chunk

                    )

                    temporary_file.write(
                        plain_chunk
                    )

                # =================================================
                # WICHTIG:
                # Erst hier wissen wir, ob die Daten authentisch
                # und unverändert sind.
                # =================================================

                final_data = decryptor.finalize()

                if final_data:

                    temporary_file.write(
                        final_data
                    )

                temporary_file.flush()

                os.fsync(
                    temporary_file.fileno()
                )

            finally:

                temporary_file.close()

        # ====================================================
        # DATEI wiederherstellen
        # ====================================================

        if source_type == "file":

            destination = unique_path(

                output_folder
                / original_name

            )

            os.replace(

                temporary_path,

                destination

            )

            temporary_path = None

            window.after(

                0,

                decryption_finished,

                destination

            )

        # ====================================================
        # ORDNER wiederherstellen
        # ====================================================

        elif source_type == "folder":

            destination = unique_path(

                output_folder
                / original_name

            )

            destination.mkdir(

                parents=True,

                exist_ok=False

            )

            update_decrypt_status(

                "Ordner wird wiederhergestellt..."

            )

            try:

                safe_extract_tar(

                    temporary_path,

                    destination

                )

            except Exception:

                # Bei Fehler versuchen, leeren Zielordner
                # wieder zu entfernen.
                try:

                    if (
                        destination.exists()
                        and not any(
                            destination.iterdir()
                        )
                    ):

                        destination.rmdir()

                except Exception:

                    pass

                raise

            temporary_path.unlink(
                missing_ok=True
            )

            temporary_path = None

            window.after(

                0,

                decryption_finished,

                destination

            )

        else:

            raise ValueError(

                "Unbekannter Inhaltstyp "
                "in der verschlüsselten Datei."

            )

    except InvalidTag:

        window.after(

            0,

            decryption_failed,

            "Falsches Passwort oder "
            "beschädigte/manipulierte Datei."

        )

    except Exception as error:

        window.after(

            0,

            decryption_failed,

            str(error)

        )

    finally:

        # Temporäre entschlüsselte Datei entfernen,
        # wenn etwas schiefging.
        if temporary_path:

            try:

                temporary_path.unlink(
                    missing_ok=True
                )

            except Exception:

                pass


# ============================================================
# Entschlüsselungsstatus
# ============================================================

def update_decrypt_status(
    text
):

    window.after(

        0,

        decrypt_status_label.config,

        {
            "text":
                text
        }

    )


# ============================================================
# Entschlüsselung fertig
# ============================================================

def decryption_finished(
    destination
):

    global operation_running

    operation_running = False

    decrypt_progress.stop()

    decrypt_button.config(
        state="normal"
    )

    decrypt_file_button.config(
        state="normal"
    )

    decrypt_status_label.config(

        text="Entschlüsselung erfolgreich."

    )

    answer = messagebox.askyesno(

        "Erfolgreich entschlüsselt",

        "Die Daten wurden erfolgreich wiederhergestellt:\n\n"
        f"{destination}\n\n"
        "Möchtest du den Zielordner öffnen?"

    )

    if answer:

        if destination.is_dir():

            folder = destination

        else:

            folder = destination.parent

        os.startfile(
            folder
        )


# ============================================================
# Entschlüsselungsfehler
# ============================================================

def decryption_failed(
    error
):

    global operation_running

    operation_running = False

    decrypt_progress.stop()

    decrypt_button.config(
        state="normal"
    )

    decrypt_file_button.config(
        state="normal"
    )

    decrypt_status_label.config(

        text="Entschlüsselung fehlgeschlagen."

    )

    messagebox.showerror(

        "Entschlüsselung fehlgeschlagen",

        f"{error}"

    )


# ============================================================
# Hauptfenster
# ============================================================

window = tk.Tk()


window.title(
    APP_NAME
)


window.geometry(
    "760x700"
)


window.minsize(
    700,
    650
)


# ============================================================
# Titel
# ============================================================

title_label = tk.Label(

    window,

    text="Secure File & Folder",

    font=(
        "Segoe UI",
        20,
        "bold"
    )

)


title_label.pack(
    pady=(20, 3)
)


subtitle_label = tk.Label(

    window,

    text=(
        "Dateien und Ordner sicher "
        "mit einem Passwort verschlüsseln"
    )

)


subtitle_label.pack(
    pady=(0, 15)
)


# ============================================================
# Tabs
# ============================================================

notebook = ttk.Notebook(
    window
)


notebook.pack(

    fill="both",

    expand=True,

    padx=20,

    pady=10

)


encrypt_tab = tk.Frame(
    notebook
)


decrypt_tab = tk.Frame(
    notebook
)


notebook.add(

    encrypt_tab,

    text="  Verschlüsseln  "

)


notebook.add(

    decrypt_tab,

    text="  Entschlüsseln  "

)


# ============================================================
# VERSCHLÜSSELN
# ============================================================

encrypt_title = tk.Label(

    encrypt_tab,

    text="Datei oder Ordner schützen",

    font=(
        "Segoe UI",
        15,
        "bold"
    )

)


encrypt_title.pack(
    pady=(25, 15)
)


# ============================================================
# Auswahlbuttons
# ============================================================

encrypt_select_frame = tk.Frame(
    encrypt_tab
)


encrypt_select_frame.pack(
    pady=5
)


encrypt_file_button = tk.Button(

    encrypt_select_frame,

    text="Datei auswählen",

    command=choose_encrypt_file,

    width=20,

    height=2

)


encrypt_file_button.grid(

    row=0,
    column=0,
    padx=8

)


encrypt_folder_button = tk.Button(

    encrypt_select_frame,

    text="Ordner auswählen",

    command=choose_encrypt_folder,

    width=20,

    height=2

)


encrypt_folder_button.grid(

    row=0,
    column=1,
    padx=8

)


encrypt_type_label = tk.Label(

    encrypt_tab,

    text="Noch nichts ausgewählt",

    font=(
        "Segoe UI",
        10,
        "bold"
    )

)


encrypt_type_label.pack(
    pady=(15, 3)
)


encrypt_source_label = tk.Label(

    encrypt_tab,

    text="",

    wraplength=650

)


encrypt_source_label.pack(
    pady=(0, 15)
)


# ============================================================
# Passwort
# ============================================================

encrypt_password_frame = tk.LabelFrame(

    encrypt_tab,

    text="Passwort",

    padx=20,

    pady=15

)


encrypt_password_frame.pack(

    fill="x",

    padx=60,

    pady=10

)


tk.Label(

    encrypt_password_frame,

    text="Passwort:"

).grid(

    row=0,
    column=0,

    sticky="w",

    padx=5,
    pady=7

)


encrypt_password_entry = tk.Entry(

    encrypt_password_frame,

    show="*",

    width=35,

    font=(
        "Segoe UI",
        11
    )

)


encrypt_password_entry.grid(

    row=0,
    column=1,

    padx=5,
    pady=7

)


encrypt_password_entry.bind(

    "<KeyRelease>",

    update_password_strength

)


tk.Label(

    encrypt_password_frame,

    text="Bestätigen:"

).grid(

    row=1,
    column=0,

    sticky="w",

    padx=5,
    pady=7

)


encrypt_confirm_entry = tk.Entry(

    encrypt_password_frame,

    show="*",

    width=35,

    font=(
        "Segoe UI",
        11
    )

)


encrypt_confirm_entry.grid(

    row=1,
    column=1,

    padx=5,
    pady=7

)


encrypt_show_password_var = tk.BooleanVar(
    value=False
)


encrypt_show_checkbox = tk.Checkbutton(

    encrypt_password_frame,

    text="Passwort anzeigen",

    variable=encrypt_show_password_var,

    command=toggle_encrypt_password

)


encrypt_show_checkbox.grid(

    row=2,
    column=1,

    sticky="w",

    padx=5

)


password_strength_label = tk.Label(

    encrypt_password_frame,

    text="Passwortstärke: Kein Passwort"

)


password_strength_label.grid(

    row=3,
    column=0,

    columnspan=2,

    pady=(12, 3)

)


password_strength_bar = ttk.Progressbar(

    encrypt_password_frame,

    length=300,

    maximum=100,

    mode="determinate"

)


password_strength_bar.grid(

    row=4,
    column=0,

    columnspan=2,

    pady=5

)


password_hint = tk.Label(

    encrypt_password_frame,

    text=(
        "Mindestens 10 Zeichen. "
        "Für wichtige Daten besser 16+ Zeichen."
    ),

    font=(
        "Segoe UI",
        9
    )

)


password_hint.grid(

    row=5,
    column=0,

    columnspan=2,

    pady=5

)


# ============================================================
# Verschlüsseln
# ============================================================

encrypt_button = tk.Button(

    encrypt_tab,

    text="Verschlüsseln",

    command=start_encryption,

    width=24,

    height=2,

    font=(
        "Segoe UI",
        10,
        "bold"
    )

)


encrypt_button.pack(
    pady=15
)


encrypt_progress = ttk.Progressbar(

    encrypt_tab,

    length=450,

    mode="indeterminate"

)


encrypt_progress.pack(
    pady=5
)


encrypt_status_label = tk.Label(

    encrypt_tab,

    text="Bereit.",

    wraplength=620

)


encrypt_status_label.pack(
    pady=10
)


# ============================================================
# Hinweis
# ============================================================

encrypt_warning = tk.Label(

    encrypt_tab,

    text=(
        "Wichtig: Das Original wird nicht automatisch gelöscht. "
        "Ohne das richtige Passwort gibt es keine "
        "Wiederherstellung."
    ),

    wraplength=600,

    font=(
        "Segoe UI",
        9
    )

)


encrypt_warning.pack(
    pady=10
)


# ============================================================
# ENTSCHLÜSSELN
# ============================================================

decrypt_title = tk.Label(

    decrypt_tab,

    text="Geschützte Datei wiederherstellen",

    font=(
        "Segoe UI",
        15,
        "bold"
    )

)


decrypt_title.pack(
    pady=(30, 20)
)


decrypt_file_button = tk.Button(

    decrypt_tab,

    text=".secure Datei auswählen",

    command=choose_encrypted_file,

    width=25,

    height=2

)


decrypt_file_button.pack(
    pady=5
)


decrypt_source_label = tk.Label(

    decrypt_tab,

    text="Keine Datei ausgewählt",

    wraplength=650

)


decrypt_source_label.pack(
    pady=15
)


# ============================================================
# Entschlüsselungspasswort
# ============================================================

decrypt_password_frame = tk.LabelFrame(

    decrypt_tab,

    text="Passwort",

    padx=20,

    pady=20

)


decrypt_password_frame.pack(

    fill="x",

    padx=80,

    pady=15

)


tk.Label(

    decrypt_password_frame,

    text="Passwort:"

).grid(

    row=0,
    column=0,

    padx=5,
    pady=7

)


decrypt_password_entry = tk.Entry(

    decrypt_password_frame,

    show="*",

    width=35,

    font=(
        "Segoe UI",
        11
    )

)


decrypt_password_entry.grid(

    row=0,
    column=1,

    padx=5,
    pady=7

)


decrypt_show_password_var = tk.BooleanVar(
    value=False
)


decrypt_show_checkbox = tk.Checkbutton(

    decrypt_password_frame,

    text="Passwort anzeigen",

    variable=decrypt_show_password_var,

    command=toggle_decrypt_password

)


decrypt_show_checkbox.grid(

    row=1,
    column=1,

    sticky="w",

    padx=5

)


# ============================================================
# Entschlüsseln
# ============================================================

decrypt_button = tk.Button(

    decrypt_tab,

    text="Entschlüsseln",

    command=start_decryption,

    width=24,

    height=2,

    font=(
        "Segoe UI",
        10,
        "bold"
    )

)


decrypt_button.pack(
    pady=20
)


decrypt_progress = ttk.Progressbar(

    decrypt_tab,

    length=450,

    mode="indeterminate"

)


decrypt_progress.pack(
    pady=5
)


decrypt_status_label = tk.Label(

    decrypt_tab,

    text="Bereit.",

    wraplength=620

)


decrypt_status_label.pack(
    pady=10
)


# ============================================================
# Programm starten
# ============================================================

window.mainloop()
