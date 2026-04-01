"""
Tests for DES implementation.

Uses the NIST/official DES test vector:
  Plaintext : 0123456789ABCDEF
  Key       : 133457799BBCDFF1
  Ciphertext: 85E813540F0AB405
"""

import unittest
from des import des_encrypt, des_decrypt, des_encrypt_block, des_decrypt_block


# ── NIST test vector ──────────────────────────────────────────────────────────

PLAINTEXT_HEX  = "0123456789ABCDEF"
KEY_HEX        = "133457799BBCDFF1"
CIPHERTEXT_HEX = "85E813540F0AB405"

PT_INT  = int(PLAINTEXT_HEX,  16)
KEY_INT = int(KEY_HEX,        16)
CT_INT  = int(CIPHERTEXT_HEX, 16)

PT_BYTES  = bytes.fromhex(PLAINTEXT_HEX)
KEY_BYTES = bytes.fromhex(KEY_HEX)
CT_BYTES  = bytes.fromhex(CIPHERTEXT_HEX)


class TestDESBlock(unittest.TestCase):
    """Test integer-level encrypt/decrypt helpers."""

    def test_encrypt_block(self):
        self.assertEqual(des_encrypt_block(PT_INT, KEY_INT), CT_INT)

    def test_decrypt_block(self):
        self.assertEqual(des_decrypt_block(CT_INT, KEY_INT), PT_INT)

    def test_roundtrip_block(self):
        ct = des_encrypt_block(PT_INT, KEY_INT)
        self.assertEqual(des_decrypt_block(ct, KEY_INT), PT_INT)


class TestDESBytes(unittest.TestCase):
    """Test bytes-level encrypt/decrypt helpers."""

    def test_encrypt_bytes(self):
        self.assertEqual(des_encrypt(PT_BYTES, KEY_BYTES), CT_BYTES)

    def test_decrypt_bytes(self):
        self.assertEqual(des_decrypt(CT_BYTES, KEY_BYTES), PT_BYTES)

    def test_roundtrip_bytes(self):
        ct = des_encrypt(PT_BYTES, KEY_BYTES)
        self.assertEqual(des_decrypt(ct, KEY_BYTES), PT_BYTES)

    def test_invalid_key_length(self):
        with self.assertRaises(ValueError):
            des_encrypt(PT_BYTES, b"short")

    def test_invalid_plaintext_length(self):
        with self.assertRaises(ValueError):
            des_encrypt(b"short", KEY_BYTES)

    def test_invalid_ciphertext_length(self):
        with self.assertRaises(ValueError):
            des_decrypt(b"short", KEY_BYTES)


class TestDESAdditionalVectors(unittest.TestCase):
    """Additional known-answer tests using widely-published DES vectors."""

    # Vector 2: all-zero plaintext + all-zero key → 8CA64DE9C1B123A7
    def test_all_zeros(self):
        pt  = bytes(8)
        key = bytes(8)
        ct  = des_encrypt(pt, key)
        self.assertEqual(ct, bytes.fromhex("8CA64DE9C1B123A7"))
        self.assertEqual(des_decrypt(ct, key), pt)

    # Vector 3: encrypt then decrypt recovers original for arbitrary data
    def test_arbitrary_roundtrip(self):
        pt  = bytes(range(8))          # 0x00 01 02 03 04 05 06 07
        key = bytes(range(8, 16))      # 0x08 09 0A 0B 0C 0D 0E 0F
        ct  = des_encrypt(pt, key)
        self.assertNotEqual(ct, pt)    # ciphertext differs from plaintext
        self.assertEqual(des_decrypt(ct, key), pt)


if __name__ == "__main__":
    unittest.main()
