# -*- coding: utf-8 -*-
#
# Blockchain parser
# Copyright (c) 2015-2021 Denis Leonov <466611@gmail.com>
#

import os
import datetime
import hashlib
import json


def reverse(input):
    L = len(input)
    if (L % 2) != 0:
        return None
    else:
        Res = ''
        L = L // 2
        for i in range(L):
            T = input[i*2] + input[i*2+1]
            Res = T + Res
            T = ''
        return (Res)


def merkle_root(lst):  # https://gist.github.com/anonymous/7eb080a67398f648c1709e41890f8c44
    def sha256d(x): return hashlib.sha256(hashlib.sha256(x).digest()).digest()
    def hash_pair(x, y): return sha256d(x[::-1] + y[::-1])[::-1]
    if len(lst) == 1:
        return lst[0]
    if len(lst) % 2 == 1:
        lst.append(lst[-1])
    return merkle_root([hash_pair(x, y) for x, y in zip(*[iter(lst)]*2)])


def read_bytes(file, n, byte_order='L'):
    data = file.read(n)
    if byte_order == 'L':
        data = data[::-1]
    data = data.hex().upper()
    return data


def read_varint(file):
    b = file.read(1)
    bInt = int(b.hex(), 16)
    c = 0
    data = ''
    if bInt < 253:
        c = 1
        data = b.hex().upper()
    if bInt == 253:
        c = 3
    if bInt == 254:
        c = 5
    if bInt == 255:
        c = 9
    for j in range(1, c):
        b = file.read(1)
        b = b.hex().upper()
        data = b + data
    return data


# Directory where blk*.dat files are stored
dirA = '/home/benni/StudioWork/dogecoin/test/'
#dirA = sys.argv[1]
# Directory where to save parsing results
dirB = '/home/benni/StudioWork/dogecoin/test/results'
#dirA = sys.argv[2]

fList = os.listdir(dirA)
fList = [x for x in fList if (x.endswith('.dat') and x.startswith('blk'))]
fList.sort()

for i in fList:
    nameSrc = i
    nameRes = nameSrc.replace('.dat', '.txt')
    resList = []
    resJson = {
        # "tx hash": {
        #     }
        # ]
        # }
    }
    a = 0
    t = dirA + nameSrc
    f = open(t, 'rb')
    tmpHex = ''
    fSize = os.path.getsize(t)
    while f.tell() != fSize:
        magicNumber = read_bytes(f, 4)
        blockSize = read_bytes(f, 4)
        tmpPos3 = f.tell()
        hash = read_bytes(f, 80, 'B')
        hash = bytes.fromhex(hash)
        hash = hashlib.new('sha256', hash).digest()
        hash = hashlib.new('sha256', hash).digest()
        hash = hash[::-1]
        hash = hash.hex().upper()
        f.seek(tmpPos3, 0)
        versionNumber = read_bytes(f, 4)
        previousBlockHash = read_bytes(f, 32)
        merkleRootHash = read_bytes(f, 32)
        MerkleRoot = merkleRootHash
        timeStamp = read_bytes(f, 4)
        difficulty = read_bytes(f, 4)
        randomNumber = read_bytes(f, 4)
        transactionCount = read_varint(f)
        txCount = int(transactionCount, 16)
        resJson[str(hash)] = {'magicNumber': str(magicNumber),
                              'blockSize': str(blockSize),
                              "versionNumber": str(versionNumber),
                              "previousBlockHash": str(previousBlockHash),
                              "merkleRootHash": str(merkleRootHash),
                              "timeStamp": str(timeStamp),
                              "difficulty": str(difficulty),
                              "randomNumber": str(randomNumber),
                              "transactionCount": str(transactionCount),
                              "transactions": [],
                              }
        tmpHex = ''
        RawTX = ''
        tx_hashes = []
        for k in range(txCount):
            txVersionNumber = read_bytes(f, 4)
            print('TX version number = ' + txVersionNumber)
            RawTX = reverse(txVersionNumber)
            tmpHex = ''
            Witness = False
            b = f.read(1)
            tmpB = b.hex().upper()
            bInt = int(b.hex(), 16)
            if bInt == 0:
                tmpB = ''
                f.seek(1, 1)
                c = 0
                c = f.read(1)
                bInt = int(c.hex(), 16)
                tmpB = c.hex().upper()
                Witness = True
            c = 0
            if bInt < 253:
                c = 1
                tmpHex = hex(bInt)[2:].upper().zfill(2)
                tmpB = ''
            if bInt == 253:
                c = 3
            if bInt == 254:
                c = 5
            if bInt == 255:
                c = 9
            for j in range(1, c):
                b = f.read(1)
                b = b.hex().upper()
                tmpHex = b + tmpHex
            inCount = int(tmpHex, 16)
            inputCount = tmpHex
            tmpHex = tmpHex + tmpB
            RawTX = RawTX + reverse(tmpHex)
            txJson = {
                "txVersionNumber": str(txVersionNumber),
                "inputCount": str(inputCount),
            }
            for m in range(inCount):
                txFromHash = read_bytes(f, 32)
                txJson['txFromHash' + str(m)] = str(txFromHash)
                RawTX = RawTX + reverse(txFromHash)

                nOutput = read_bytes(f, 4)
                txJson['nOutput' + str(m)] = str(nOutput)
                RawTX = RawTX + reverse(nOutput)

                tmpHex = ''
                b = f.read(1)
                tmpB = b.hex().upper()
                bInt = int(b.hex(), 16)
                c = 0
                if bInt < 253:
                    c = 1
                    tmpHex = b.hex().upper()
                    tmpB = ''
                if bInt == 253:
                    c = 3
                if bInt == 254:
                    c = 5
                if bInt == 255:
                    c = 9
                for j in range(1, c):
                    b = f.read(1)
                    b = b.hex().upper()
                    tmpHex = b + tmpHex
                scriptLength = int(tmpHex, 16)
                tmpHex = tmpHex + tmpB
                RawTX = RawTX + reverse(tmpHex)
                inputScript = read_bytes(f, scriptLength, 'B')
                txJson['inputScript' + str(m)] = str(inputScript)
                RawTX = RawTX + inputScript

                sequenceNumber = read_bytes(f, 4, 'B')
                txJson['sequenceNumber' + str(m)] = str(sequenceNumber)
                RawTX = RawTX + sequenceNumber

                tmpHex = ''
            b = f.read(1)
            tmpB = b.hex().upper()
            bInt = int(b.hex(), 16)
            c = 0
            if bInt < 253:
                c = 1
                tmpHex = b.hex().upper()
                tmpB = ''
            if bInt == 253:
                c = 3
            if bInt == 254:
                c = 5
            if bInt == 255:
                c = 9
            for j in range(1, c):
                b = f.read(1)
                b = b.hex().upper()
                tmpHex = b + tmpHex
            outputCount = int(tmpHex, 16)
            tmpHex = tmpHex + tmpB
            txJson['outputCount'] = str(outputCount)

            RawTX = RawTX + reverse(tmpHex)
            for m in range(outputCount):
                tmpHex = read_bytes(f, 8)
                Value = tmpHex
                RawTX = RawTX + reverse(tmpHex)
                tmpHex = ''
                b = f.read(1)
                tmpB = b.hex().upper()
                bInt = int(b.hex(), 16)
                c = 0
                if bInt < 253:
                    c = 1
                    tmpHex = b.hex().upper()
                    tmpB = ''
                if bInt == 253:
                    c = 3
                if bInt == 254:
                    c = 5
                if bInt == 255:
                    c = 9
                for j in range(1, c):
                    b = f.read(1)
                    b = b.hex().upper()
                    tmpHex = b + tmpHex
                scriptLength = int(tmpHex, 16)
                tmpHex = tmpHex + tmpB
                RawTX = RawTX + reverse(tmpHex)
                outputScript = read_bytes(f, scriptLength, 'B')
                txJson['outputValue' + str(m)] = str(Value)
                txJson['outputScript' + str(m)] = str(outputScript)
                RawTX = RawTX + outputScript

                tmpHex = ''
            if Witness == True:
                for m in range(inCount):
                    tmpHex = read_varint(f)
                    WitnessLength = int(tmpHex, 16)
                    for j in range(WitnessLength):
                        tmpHex = read_varint(f)
                        WitnessItemLength = int(tmpHex, 16)
                        tmpHex = read_bytes(f, WitnessItemLength)
                        txJson['Witness' + str(m) + str(j)
                               ] = str(WitnessItemLength) + tmpHex
                        tmpHex = ''
            Witness = False
            lockTime = read_bytes(f, 4)
            txJson['lockTime'] = str(lockTime)
            RawTX = RawTX + reverse(lockTime)

            tmpHex = RawTX
            tmpHex = bytes.fromhex(tmpHex)
            tmpHex = hashlib.new('sha256', tmpHex).digest()
            tmpHex = hashlib.new('sha256', tmpHex).digest()
            tmpHex = tmpHex[::-1]
            txHash = tmpHex.hex().upper()

            tx_hashes.append(txHash)
            resJson[str(hash)]['transactions'].append({str(txHash): txJson})
            tmpHex = ''
            RawTX = ''
        a += 1
        tx_hashes = [bytes.fromhex(h) for h in tx_hashes]
        tmpHex = merkle_root(tx_hashes).hex().upper()
        if tmpHex != MerkleRoot:
            print('Merkle roots does not match! >', MerkleRoot, tmpHex)
        # Db call
        print(resJson)
    f.close()
    f = open(dirB + nameRes, 'w')
    # for j in resList:
    #     f.write(j + '\n')
    f.close()
