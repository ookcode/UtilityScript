#!/usr/bin python2
#coding:utf-8
###################################################
#
# encrypt or decrypt file with xxtea algorithm
#
# Created by Vincent on 16-6-24.
#
###################################################
import struct  
import sys,os,shutil

SIGN_KEY = 123456
SIGN_LEN = 4
KEY = "vincent"

DELTA = 0x9E3779B9
def _long2str(v, w):  
    n = (len(v) - 1) << 2  
    if w:  
        m = v[-1]  
        if (m < n - 3) or (m > n): return ''  
        n = m  
    s = struct.pack('<%iL' % len(v), *v)  
    return s[0:n] if w else s  
  
def _str2long(s, w):  
    n = len(s)  
    m = (4 - (n & 3) & 3) + n  
    s = s.ljust(m, "\0")  
    v = list(struct.unpack('<%iL' % (m >> 2), s))  
    if w: v.append(n)  
    return v  
  
def encrypt(str, key):  
    if str == '': return str  
    v = _str2long(str, True)  
    k = _str2long(key.ljust(16, "\0"), False)  
    n = len(v) - 1  
    z = v[n]  
    y = v[0]  
    sum = 0  
    q = 6 + 52 // (n + 1)  
    while q > 0:  
        sum = (sum + DELTA) & 0xffffffff  
        e = sum >> 2 & 3  
        for p in xrange(n):  
            y = v[p + 1]  
            v[p] = (v[p] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[p & 3 ^ e] ^ z))) & 0xffffffff  
            z = v[p]  
        y = v[0]  
        v[n] = (v[n] + ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[n & 3 ^ e] ^ z))) & 0xffffffff  
        z = v[n]  
        q -= 1  
    return _long2str(v, False)  
  
def decrypt(str, key):  
    if str == '': return str  
    v = _str2long(str, False)  
    k = _str2long(key.ljust(16, "\0"), False)  
    n = len(v) - 1  
    z = v[n]  
    y = v[0]  
    q = 6 + 52 // (n + 1)  
    sum = (q * DELTA) & 0xffffffff  
    while (sum != 0):  
        e = sum >> 2 & 3  
        for p in xrange(n, 0, -1):  
            z = v[p - 1]  
            v[p] = (v[p] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[p & 3 ^ e] ^ z))) & 0xffffffff  
            y = v[p]  
        z = v[n]  
        v[0] = (v[0] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ (sum ^ y) + (k[0 & 3 ^ e] ^ z))) & 0xffffffff  
        y = v[0]  
        sum = (sum - DELTA) & 0xffffffff  
    return _long2str(v, True)  

def encrypt_file(path):
    #open file
    src_file = open(path, 'rb')
    img_data = src_file.read()
    #do encrypt
    img_data = encrypt(img_data, KEY)
    des_file = open(path, 'wb')
    #add pre sign key
    pre_sign = struct.pack("i", SIGN_KEY)
    #rewrite
    des_file.write(pre_sign)
    des_file.write(img_data)
    des_file.close()
    print path + " encrypt success"

def decrypt_file(path):
    #open file
    src_file = open(path,'rb')
    img_data = src_file.read()
    #do decrypt
    img_data = decrypt(img_data[SIGN_LEN:], KEY)
    #rewite
    des_file = open(path,'wb')
    des_file.write(img_data)
    des_file.close()
    print path + " decrypt success"

def isEncrypt(path):
    size = os.path.getsize(path)
    file = open(path, "rb")
    if size < SIGN_LEN:
        print("error: file size is too small")
        sys.exit()
    sign_id, = struct.unpack("i", file.read(SIGN_LEN))
    file.close()
    if sign_id == SIGN_KEY :
        return True
    else:
        return False

def main():
    file_path = raw_input("please drag in a file: ")
    file_path = file_path.strip()   #remove the space
    if isEncrypt(file_path):
        decrypt_file(file_path)
    else:
        encrypt_file(file_path)

if __name__ == '__main__':
    main()