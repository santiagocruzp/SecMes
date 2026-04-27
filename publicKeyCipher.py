import sys, math

SYMBOLS = f"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890 !?'.,-:;()$/&%+_@\n\\\t"
BLOCKSIZE = 100

def main():
    filename = 'encrypted_file.txt'
    mode = 'decrypt'

    if mode == 'encrypt':
        message = "I want you to know I am not coming back. Look into my eyes I am not coming back. So knives out catch the mouse squash its head throw it in a pot."
        pubKeyFilename = 'Cruz_pubkey.txt'
        print('Encrypting and writing to %s...' % (filename))
        encryptedText = encryptAndWriteToFile(filename, pubKeyFilename, message)

        print('Encrypted text:')
        print(encryptedText)

    elif mode == 'decrypt':
        privKeyFilename = 'Cruz_privkey.txt'
        print('Reading from %s and decrypting...' % (filename))
        decryptedText = readFromFileAndDecrypt(filename, privKeyFilename)

        print('Decrypted text:')
        print(decryptedText)

def getBlocksFromText(message,blockSize):
    for character in message:
        if character not in SYMBOLS:
            print('ERROR: The symbol set does not have the character %s' % (character))
            sys.exit()

    blockInts = []
    for blockStart in range(0, len(message), blockSize):
        # calculate the integer for this block of text:
        blockInt = 0
        for i in range(blockStart, min(blockStart+blockSize, len(message))):  # we use min function to deal with the last block of the message
            blockInt += (SYMBOLS.index(message[i])) * (len(SYMBOLS)**(i%blockSize))  #by modding i by blockSize we get index relative to the block, not to the entire message
        blockInts.append(blockInt)
    return blockInts
    
def getTextFromBlocks(blockInts, messageLength, blockSize):
    message = []
    for blockInt in blockInts:
        blockMessage = []
        for i in range(blockSize-1,-1,-1): # work from back to front all the way down to zero
            if len(message) + i < messageLength:
                # decode the message string from the blockSize no. of characters from this block integer:
                charIndex = blockInt // (len(SYMBOLS)**i)
                blockInt = blockInt % (len(SYMBOLS)**i)
                blockMessage.insert(0,SYMBOLS[charIndex]) # insert at 0 is used bc we can't simply append as we're working backwards
        message.extend(blockMessage)  # extend is needed bc blockMessage itself is a list, not a string
    return ''.join(message)
        
def encryptMessage(message, key, blockSize):
    encryptedBlocks = []
    n,e = key
    for block in getBlocksFromText(message, blockSize):
        # ciphertext = plaintext ^ e mod n
        encryptedBlocks.append(pow(block,e,n))  # the 3rd argument of pow() performs modulo of the result of raising block to the e

    return encryptedBlocks

def decryptMessage(encryptedBlocks, messageLength, key, blockSize):
    decryptedBlocks = []
    n,d = key   # this has to be the private key of course
    print(type(encryptedBlocks))
    for block in encryptedBlocks:
        # plaintext = ciphertext ^ d mod n
        decryptedBlocks.append(pow(block,d,n))
    print("this is at the end of the decryptMessage function: ",decryptedBlocks)
    return getTextFromBlocks(decryptedBlocks,messageLength,blockSize)

def readKeyFile(keyFilename):
    fo = open(keyFilename)
    content = fo.read()
    fo.close()
    keySize, n, EorD = content.split(',')
    return (int(keySize), int(n), int(EorD))

def encryptAndWriteToFile(messageFilename,keyFilename,message,blockSize=None):
    keySize,n,e = readKeyFile(keyFilename)
    if blockSize == None:
        # if blockSize not given, set it to the largest size allowed by the key size and symbol set size.
        blockSize = int(math.log(2**keySize,len(SYMBOLS)))
        # check that keySize is large enough for the block size:
        if not (math.log(2**keySize,len(SYMBOLS)) >= blockSize):
            sys.exit('ERROR: Block size is too large for the key and symbol set size. Did you specify the correct key file and encrypted file?')
        # Encrypt the message:
        encryptedBlocks = encryptMessage(message, (n,e), blockSize)

        # convert the large in values to one string value
        for i in range(len(encryptedBlocks)):
            encryptedBlocks[i] = str(encryptedBlocks[i])  # needed for join function to work
        encryptedContent = ','.join(encryptedBlocks)

        encryptedContent = '%s_%s_%s' % (len(message),blockSize,encryptedContent)
        fo = open(messageFilename, 'w')
        fo.write(encryptedContent)
        fo.close()

        return encryptedContent
    
def readFromFileAndDecrypt(messageFilename,keyFilename):
    keySize,n,d = readKeyFile(keyFilename)
    fo = open(messageFilename)
    content = fo.read()
    messageLength, blockSize, encryptedMessage = content.split('_')
    messageLength = int(messageLength)
    blockSize = int(blockSize)

    # check that the key size is large enough for the block size:
    if not (math.log(2**keySize,len(SYMBOLS)) >= blockSize):
        sys.exit('ERROR: Block size is too large for the key and symbol set size. Did you specify the correct key file and encrypted file?')

    # convert the encrypted message into large int values
    encryptedBlocks = []
    print(encryptedMessage)
    for block in encryptedMessage.split(','):
        encryptedBlocks.append(int(block))
    print(encryptedBlocks)

    # decrypt the large int values
    return decryptMessage(encryptedBlocks, messageLength, (n, d), blockSize)
    
if __name__ == '__main__':
    main()