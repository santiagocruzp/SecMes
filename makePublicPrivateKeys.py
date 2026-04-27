
import random, sys, os, primeNum, gcd, modInverse

def main():
    print('Making key files...')
    makeKeyFiles('Santiago Cruz',1024)
    print('Key files made successfully.')

def generateKey(keysize):
    p = 0
    q = 0
    # Step 1: create 2 prime numbers p and q, and multiply them as n
    print('Generating p prime...')
    while p == q:
        p = primeNum.generateLargePrime(keysize)
        q = primeNum.generateLargePrime(keysize)
    n = p * q

    # Step 2: create a number e that is relatively prime to (p-1)*(q-1):
    print('Generating e that is relatively prime to (p-1)*(q-1)...')
    while True:
        e = random.randrange(2**(keysize-1),2**(keysize))
        if gcd.gcd(e,(p-1)*(q-1)) == 1:
            break

    # Step 3: calculate d, the mod inverse of e:
    print('Calculating the mod inverse of e...')
    d = modInverse.findModInverse(e,(p-1)*(q-1))

    publicKey = (n,e)
    privateKey = (n,d)

    print('Public key:', publicKey)
    print('Private key:', privateKey)

    return (publicKey,privateKey)

def makeKeyFiles(name,keysize):
    if os.path.exists('%s_pubkey.txt' % (name)) or os.path.exists('%s_privkey.txt' % (name)):
        sys.exit('WARNING: The file already exists! use a different name.')

    publicKey, privateKey = generateKey(keysize)

    print()
    print('The public key is a %s and a %s digit number.' % (len(str(publicKey[0])), len(str(publicKey[1]))))
    print('Writing public key to file %s_pubkey.txt...' % (name))
    fo = open('%s_pubkey.txt' % (name),'w')
    fo.write('%s,%s,%s' % (keysize, publicKey[0], publicKey[1]))
    fo.close()

    print()
    print('The private key is a %s and a %s digit number.' % (len(str(privateKey[0])), len(str(privateKey[1]))))
    print('Writing private key to file %s_privkey.txt...' % (name))
    fo = open('%s_privkey.txt' % (name),'w')
    fo.write('%s,%s,%s' % (keysize, privateKey[0], privateKey[1]))
    fo.close()    

if __name__ == '__main__':
    main()
