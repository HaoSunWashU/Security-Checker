import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.crypto import encrypt, decrypt


def test_roundtrip():
    plaintext = "Hello, 终端安全检查工具！"
    password = "TestPass@123"
    assert decrypt(encrypt(plaintext, password), password) == plaintext


def test_different_passwords_fail():
    plaintext = "sensitive data"
    encrypted = encrypt(plaintext, "correct_password")
    try:
        result = decrypt(encrypted, "wrong_password")
        assert result != plaintext
    except Exception:
        pass


def test_empty_string():
    assert decrypt(encrypt("", "pass"), "pass") == ""


def test_unicode():
    text = "绝密\t机密\n秘密 🔒"
    password = "Sec@2026"
    assert decrypt(encrypt(text, password), password) == text
