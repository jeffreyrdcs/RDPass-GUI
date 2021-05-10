import bcrypt
import base64
from RDconfig import rdstatus
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto import Random


def get_hashed_key(input_key):
    """
        Hash the input master key using bcrypt
    """
    depth = 5
    return bcrypt.hashpw(input_key.encode('utf8'), bcrypt.gensalt(depth))


def validate_hashed_key(input_pw_to_check, hashed_key):
    """
        Check if the input
    """
    # Check hashed password. Using bcrypt, the salt is saved into the hash itself
    return bcrypt.checkpw(input_pw_to_check.encode('utf8'), hashed_key.encode('utf8'))


def gen_salt(salt_depth):
    """
        Use Bcrypt gensalt to generate a salt
    """
    return bcrypt.gensalt(salt_depth)


def sha_mod_key(in_encode_key):
    """
        Use SHA256 to digest the input password to a 16-byte key for AES
        Input should be str
    """
    return SHA256.new(in_encode_key).digest()


def encrypt_pass(in_pass_byte, salt):
    """
        Encrypt the password given a salt and iv
        In password, salt, iv should all be in bytes
    """
    # Generate an iv
    iv = Random.new().read(AES.block_size)

    # Input password need to be padded to a multiple of 16 bytes
    padding = (AES.block_size - len(in_pass_byte)) % AES.block_size
    in_pass_byte = in_pass_byte + bytes([padding]) * padding

    # Hash the key again with the salt
    key = rdstatus.config_status['gen_key']
    modkey = sha_mod_key(key + salt)

    aes = AES.new(modkey, AES.MODE_CBC, iv)
    enc_pass = aes.encrypt(in_pass_byte)
    return base64.b64encode(iv + enc_pass).decode()


def decrypt_pass(in_enc_pass_byte, salt):
    """
        Decrypt the message from encrypt_pass
        In byte, salt should be in bytes
    """
    in_enc_pass_byte = base64.b64decode(in_enc_pass_byte)

    iv = in_enc_pass_byte[0:AES.block_size]

    # Hash the key again with the salt
    key = rdstatus.config_status['gen_key']     # Note that decryption will fail if this changes
    modkey = sha_mod_key(key + salt)
    aes = AES.new(modkey, AES.MODE_CBC, iv)

    # Decrypt
    out_pass = aes.decrypt(in_enc_pass_byte[AES.block_size:])

    # Remove the padding
    padding = out_pass[-1]
    out_pass = out_pass[:-padding]

    return out_pass.decode()

