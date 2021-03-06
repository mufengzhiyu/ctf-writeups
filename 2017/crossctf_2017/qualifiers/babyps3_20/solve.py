#! /usr/bin/env python2
##
# Created for the PS3 challenge
# By Amos Ng
##
from Crypto.Hash import SHA
from Crypto.PublicKey import DSA
from Crypto.Random import random
from DSAregenK import DSAregenK
from gmpy2 import powmod
import hashlib
from pwn import *

# Original variables
N = 2048
L = 256
p = int('df633b7301871415bef5017d0c0910c7072222433a309d69ffd012f9d3e208e4d31ebdfd0aa30dfb4a7d13ef7832d363d855e2169df89e60acbfc4137a59c3945eb494650913b6087f2e2700eb3b4294eb4377e9cea6d35ddf232519624cc3bd1e7e534aa9379ded37ff6ddff10758124250e3e5a40a1f789f2c0cc16cb96e0f5261b98b01689dbad6f62842a6c3365fcf25fd3def7baad7bfd99bd70dbe067a5b2af7737caba77787537f1c406338b1c3b86c3875563a03024156bf92a6c770010c63e123a0b2b4661970bf522034ea1e376406c5194c5bb82d1c69d77dcca4b8e04d4a347fcc5bd8c91504458c0eb086a0bf10fa7cc8caa11af2e22f32d06f', 16)
q = int('9f3710274717b060dee9fef0aaf01572e9cc53ba6ac10492bd5446bb41a248a9',16)
g = int('93b411063c7d3b82189c7ea2624be9087a6e40e79020801367a9bc13012630ae2778244492cca9cd86a07dee31163713a2623f3c418b19e7e8fb3ba5e2db359cc6e5efa1c35c37a16bb2dbfe7c8b6bb123bd26a8f299acdd5c6886748d3db1ffa5ce439571de7efac3482ebf5b4a45324963d99506af9e210988c0a26c443659172df05e094572421ca1c5005f4a1650081c532663dd0e5812f4b8ea43f6cdca317755aac3c3f63754be18c0063b919a7a547cb04d44dba2f67154339eaddfadbd8398c94ba5565d7a2d07c1d20e39befee427346e630f5f72176444fed7d8314ca7c472261f8311974da2ddcafab1ee63c6c7377e7592161e1d31b32abaa3bd', 16)
y = 20636836524380396244196072696577569262126621637693518417515831389588156010110727694179220341766312812167934840038173702512714672935256591366304513258964123770331403988242338829851121917054712366378000466271493525015744412519308988145299857577333546970037261427973290256403898499766279180979277265983341722384272524689611144938145070671581385845523894185215290296247151150557881827136342152143825772770126693742120775894397288900938364960208586264826886039992581043142765638948169372930513082826136892625732961853419727731657648155505907704183872630951714970690302024937399383304248276584035831599631104415986634886780

def H(m):
    return int(hashlib.sha256(m).hexdigest(), 16)

def sign((p,q,g), Hm, (x, y), k, k_):
    r = powmod(g,k,p) % q
    z = Hm
    s = (k_*(z+x*r)) % q
    return (r, s)

def inverse(z,a):
    if z > 0 and z < a and a > 0:
        i = a
        j = z
        y1 = 1
        y2 = 0
        while j > 0:
            q = i/j
            r = i-j*q
            y = y2 - y1*q
            i, j = j, r
            y2, y1 = y1, y
        if i == 1:
            return y2 % a
    raise Exception('Inverse Error')

def verify((p,q,g), Hm, y, (r,s)):
    if 0 < r and r < q and 0 < s and s < q:
        w = inverse(s, q)
        z = Hm
        u1 = (z*w) % q
        u2 = (r*w) % q
        v = ((powmod(g,u1,p) * powmod(y,u2,p)) % p) % q
        return v == r
    return False


# Generate private keypair
pubkey = DSA.construct((y, g, p, q))
a = DSAregenK(pubkey=pubkey)

with open("miniman_xvsigned", "rb") as file:
    data = file.read()
    r = int(data[263:519].encode('hex'), 16)
    s = int(data[527:783].encode('hex'), 16)
    game = data[796:]
    a.add((r, s), H(game))

with open("first_fantasy_xxviiisigned", "rb") as file:
    data = file.read()
    r = int(data[263:519].encode('hex'), 16)
    s = int(data[527:783].encode('hex'), 16)
    game = data[796:]
    a.add((r, s), H(game))

for privkey in a.run(asDSAobj=False):
    k, x = privkey
    k_ = inverse(k, q)

    with open("halo_3", "r") as file:
        data = file.read()
        game = data[796:-2] + "\n"
        old_r = int(data[263:519].encode('hex'), 16)
        old_s = int(data[527:783].encode('hex'), 16)
        r, s = sign((p,q,g), H(game), (x, y), k, k_)
        print("old r: %d" % old_r)
        print("new r: %d" % r)
        print("old s: %d" % old_s)
        print("new s: %d" % s)

        # Try to verify signature
        if verify((p,q,g), H(game), y, (r, s)):
            # Try to submit signature to server
            t = remote("188.166.248.56", 3333)
            t.recvuntil("Please enter the signature: ")
            t.sendline(str(s))
            flag = t.recv()
            print("Flag: %s" % flag)