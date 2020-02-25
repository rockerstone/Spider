import base64
import rsa


class Encrypt:
    def __init__(self, modulus, exponent, password):
        self.modulus = modulus
        self.exponent = exponent
        self.password = password

    def rsa_encrypt(self):
        modulus = self.modulus
        exponent = self.exponent
        password = self.password
        # b64tohex
        modulus = self.b64tohex(modulus)
        exponent = self.b64tohex(exponent)
        # setPublic
        modulus = int(modulus, 16)
        exponent = int(exponent, 16)
        # print(modulus)
        # print(exponent)
        # encrypt
        pubkey = rsa.PublicKey(modulus, exponent)
        password = rsa.encrypt(password.encode(), pubkey)
        # print(password)
        rsacode = base64.b64encode(password).decode()
        # rsacode = b64.hex2b64(password)
        # print(rsacode)
        return rsacode

    @staticmethod
    def b64tohex(data):
        BI_RM = "0123456789abcdefghijklmnopqrstuvwxyz"
        b64map = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
        b64pad = "="
        ret = ""
        k = 0
        slop = 0
        for string in data:
            if str == b64pad:
                break
            v = b64map.find(string)
            if v < 0:
                continue
            if k == 0:
                ret += BI_RM[v >> 2]
                slop = v & 3
                k = 1
            elif k == 1:
                ret += BI_RM[(slop << 2) | (v >> 4)]
                slop = v & 0xf
                k = 2
            elif k == 2:
                ret += BI_RM[slop]
                ret += BI_RM[v >> 2]
                slop = v & 3
                k = 3
            else:
                ret += BI_RM[(slop << 2) | (v >> 4)]
                ret += BI_RM[v & 0xf]
                k = 0
        if k == 1:
            ret += BI_RM[slop << 2]
        return ret
