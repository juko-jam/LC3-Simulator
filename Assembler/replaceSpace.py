import re
from pathlib import Path
import os
import sys


dest = 'output.txt'
src = ''
auxFile = 'auxFile.txt'

lookupTable = {}

labelPattern = re.compile(r'^(\w+)\s*,')
commentLine = re.compile(r'^\s*;')
ORG = re.compile(r'^\s*ORG\s+')
DEC = re.compile(r'\s+DEC\s+[-]?(\d)+')
# HEX = re.compile(r'\bHEX\b[0]?[xX]?(\d)+') ??
HEX = re.compile(r'\s+HEX\s+[0]?[xX]?(\d+)')
IMMEDIATE = re.compile(r'#\s*[-]?(\d)+')
VARIABLE = re.compile(r'')

instructions = {'ADD' : '0001'
                ,'AND' : '0101'
                ,'BR' : '0000'
                ,'JMP' : '1100' # RET & JMP
                ,'JSR' : '0100' # !
                ,'JSRR' : '0100' # !
                ,'LD' : '0010'
                ,'LDI' : '1010'
                ,'LDR' : '0110'
                ,'LEA' : '1110'
                ,'NOT' : '1001'
                ,'RET' : '1100' # RET & JMP
                ,'RTI' : '1000'
                ,'ST' : '0011'
                ,'STI' : '1011'
                ,'STR' : '0111'
                ,'TRAP' : '1111'
                ,'HALT' : '1101'
                }



def dec_to_bin(x : int, length : int = 16, signed = True):

    if signed and (x> (2**(length-1) -1) or x < (-(2**(length-1)))) :
        return #err
    if not signed and (x > 2**length - 1):
        return #err
    if x == 0:
        return '0' * length
    res = ''
    if x > 0:
        res = bin(x)[2:]
        return ('0' * (length-len(res))) + res
    else:
        return bin( x + (1 << length))[2:]


def extend_bin(x: str, length : int = 16) -> str:
    if len(x) > length:
        pass # err

    if len(x) == length:
        return x
    diff = (length - len(x))
    ch = x[0] * diff
    return ch + x


def HexToDec(hexStr : str):
    startIndex = 0
    # startIndex = hexStr.find('x')
    return int(hexStr, base=16)

def HexToBin(hexStr : str):
    temp = int(hexStr, base=16)
    res = bin(temp)[2:]
    if temp > 0 :
        return extend_bin('0' + res, 16)
    else:
        return res


def offsetCalc(labelAddress : int, PC : int):
    return labelAddress - (PC + 1)


WHITESPACES = re.compile(r'\s+')

def replace(src : Path, dest:Path = Path("output.txt")):
    if not os.path.exists(src):
        raise ValueError("the source you provided does not exists")
    
    with open(dest, mode='w') as out:

        with open(src, mode='r') as f:
            for s in f:
                s = s.rstrip()
                # s = f.readline()
                # s = re.sub(r'\s+', ' ', s)
                s = re.sub(r'\s*;.*$', '', s,flags=re.DOTALL)
                if s:
                    print(s, file=out)

def ADD_inst(args : str, PC : int)-> str:
    args = WHITESPACES.sub('', args)
    # args = args.split(',')
    res = re.match(r'^R(?P<DR>[0-7]),R(?P<SR1>[0-7]),(R(?P<SR2>[0-7])|#(?P<IMM>[-]?\d+))$', args)
    
    if res:
        inst = ''
        inst += instructions['ADD']
        inst += dec_to_bin(int(res.group('DR')), 3, False)
        inst += dec_to_bin(int(res.group('SR1')), 3, False)
        if res.group('SR2'):
            inst += '000'
            inst += dec_to_bin(int(res.group('SR2')), 3, False)
        else:
            inst += '1'
            inst += dec_to_bin(int(res.group('IMM')), 5) # check (possibly a large decimal - catch)
        
        return inst
    else :
        pass # err
    
def AND_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    # args = args.split(',')
    res = re.match(r'^R(?P<DR>[0-7]),R(?P<SR1>[0-7]),(R(?P<SR2>[0-7])|#(?P<IMM>[-]?\d+))$', args)
    
    if res:
        inst = ''
        inst += instructions['AND']
        inst += dec_to_bin(int(res.group('DR')), 3, False)
        inst += dec_to_bin(int(res.group('SR1')), 3, False)
        if res.group('SR2'):
            inst += '000'
            inst += dec_to_bin(int(res.group('SR2')), 3, False)
        else:
            inst += '1'
            inst += dec_to_bin(int(res.group('IMM')), 5) # check (possibly a large decimal - catch)
        
        return inst
    else:
        pass # err

def NOT_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    res = re.match(r'^R(?P<DR>[0-7]),R(?P<SR1>[0-7])', args)

    if res:
        inst = ''
        inst += instructions['NOT']
        inst += dec_to_bin(int(res.group('DR')), 3, False)
        inst += dec_to_bin(int(res.group('SR1')), 3, False)
        inst += '111111' # 1 11111
        return inst
    else:
        pass # err

def LD_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    
    res = re.match(r'^R(?P<DR>[0-7]),(?P<LABEL>\w+)$', args)

    if res:

        if res.group('LABEL') not in lookupTable:
            pass # err
        else :
            inst = ''
            inst += instructions['LD']
            inst += dec_to_bin(int(res.group('DR')) ,3, False)
            # inst += dec_to_bin(res.groupdict['DR'])            
            # inst += dec_to_bin(lookupTable[res.group('LABEL')]) # add the address of LABEL in binary format
            offset9 = offsetCalc(lookupTable[res.group('LABEL')], PC)
            inst += dec_to_bin(offset9, 9)
            return inst
    else:
        pass # err

def LDI_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    
    res = re.match(r'^R(?P<DR>[0-7]),(?P<LABEL>\w+)$', args)

    if res:

        if res.group('LABEL') not in lookupTable:
            pass # err
        else :
            inst = ''
            inst += instructions['LD']
            inst += dec_to_bin(int(res.group('DR')), 3, False)
            # inst += dec_to_bin(lookupTable[res.group('LABEL')]) # add the address of LABEL in binary format
            offset9 = offsetCalc(lookupTable[res.group('LABEL')], PC)
            inst += dec_to_bin(offset9, 9)
            return inst
    else:
        pass # err

def LDR_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    
    res = re.match(r'^R(?P<DR>[0-7]),R(?P<baseR>[0-7]),#(?P<offset>[-]?\d+)$', args)

    if res:
        inst = ''
        inst += instructions['LDR']
        inst += dec_to_bin(int(res.group('DR')), 3, False)
        inst += dec_to_bin(int(res.group('baseR')), 3, False)
        inst += dec_to_bin(int(res.group('offset')), 6) # maybe a large value - should catch  (err)

        return inst
    else:
        pass # err

def LEA_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    
    res = re.match(r'^R(?P<DR>[0-7]),(?P<LABEL>\w+)$', args)

    if res:
        if res.group('LABEL') not in lookupTable:
            pass # err

        inst = ''
        inst += instructions['LEA']
        inst += dec_to_bin(int(res.group('DR')), 3, False)
        # inst += dec_to_bin(lookupTable[res.group('LABEL')])
        offset9 = offsetCalc(lookupTable[res.group('LABEL')], PC)
        inst += dec_to_bin(offset9, 9)

        return inst

    else:
        pass # err

def ST_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    
    res = re.match(r'^R(?P<SR>[0-7]),(?P<LABEL>\w+)$', args)

    if res:
        if res.group('LABEL') not in lookupTable:
            pass # err

        inst = ''
        inst += instructions['ST']
        inst += dec_to_bin(int(res.group('SR')), 3, False)
        # inst += dec_to_bin(lookupTable(res.group('LABEL')))
        offset9 = offsetCalc(lookupTable[res.group('LABEL')], PC)
        inst += dec_to_bin(offset9, 9)

        return inst

    else:

        pass # err

def STI_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    
    res = re.match(r'^R(?P<SR>[0-7]),(?P<LABEL>\w+)$', args)

    if res:

        if res.group('LABEL') not in lookupTable:
            pass # err

        inst = ''
        inst += instructions['STI']
        inst += dec_to_bin(int(res.group('SR')), 3, False)
        # inst += dec_to_bin(res.group('LABEL'))
        offset9 = offsetCalc(lookupTable[res.group('LABEL')], PC)
        inst += dec_to_bin(offset9, 9)
        return inst

    else:
        pass # err

def STR_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    
    res = re.match(r'^R(?P<SR>[0-7]),R(?P<baseR>[0-7]),#(?P<offset>\d+)$', args)

    if res:


        inst = ''
        inst += instructions['STR']
        inst += dec_to_bin(int(res.group('SR')), 3, False)
        inst += dec_to_bin(int(res.group('baseR')), 3, False)
        inst += dec_to_bin(int(res.group('offset')), 6) # maybe large should catch - err

        return inst

    else:
        pass # err

# problem
def BR_inst(args : str, PC: int) -> str:
    # args = WHITESPACES.sub('', args)

    res = re.match(r'^BR(?P<n>n)?(?P<z>z)?(?P<p>p)?\s+(?P<LABEL>\w+)$', args)

    if res:
        if res.group('LABEL') not in lookupTable:
            pass # err

        inst = ''
        inst += instructions['BR']
        inst += '1' if res.group('n') else '0'
        inst += '1' if res.group('z') else '0'
        inst += '1' if res.group('p') else '0'

        # offset = lookupTable[res.group('LABEL')] - (PC + 1)
        # inst += dec_to_bin(lookupTable[res.group('LABEL')])
        offset9 = offsetCalc(lookupTable[res.group('LABEL')], PC)
        inst += dec_to_bin(offset9, 9)

        return inst
    
    else :
        pass # err

def JMP_inst(args : str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    
    res = re.match(r'R(?P<baseR>[0-7])', args)

    if res:

        inst = ''
        inst += instructions['JMP']
        inst += '000'
        inst += dec_to_bin(int(res.group('baseR')), 3, False)
        inst += '000000'

        return inst

    else:
        pass # err

def RET_inst(args : str, PC : int) -> str:
    # args = WHITESPACES.sub('', args)
    
    # res = re.match(r'^R(?P<RD>[0-7]),R(?P<SR1>[0-7]),(R(?P<SR2>[0-7])|#(?P<IMM>\d+))$', args)

    if not len(args) == 0:
        pass # err

    inst = ''
    inst += instructions['RET']
    inst += '000'
    inst += '111'
    inst += '000000'

    return inst


def JSR_inst(args: str, PC : int) -> str:
    args = WHITESPACES.sub('', args)
    
    res = re.match(r'^(?P<LABEL>\w+)$', args)

    if res:
        if res.group('LABEL') not in lookupTable:
            pass # err

        inst = ''
        inst += instructions['JSR']
        inst += '1'
        # offset11 = lookupTable[res.group('LABEL')] - (PC + 1)
        offset11 = offsetCalc(lookupTable[res.group('LABEL')], PC)
        inst += dec_to_bin(offset11, 11)
        

        return inst

    else:
        pass # err
def JSRR_inst(args:str, PC : int) -> str:

    args = WHITESPACES.sub('', args)
        
    res = re.match(r'R(?P<baseR>[0-7])', args)

    if res:

        inst = ''
        inst += instructions['JMP']
        inst += '0'
        inst += '00'
        inst += dec_to_bin(int(res.group('baseR')), 3, False)
        inst += '000000'

        return inst

    else:
        pass # err

def DEC_inst(args: str, PC : int) -> str:
    args = args.strip()

    res = re.match(r'^[-]?\d+$', args)

    if res:
        return dec_to_bin(int(args))
    else:
        pass # err
    # if not args.isnumeric():
    #     pass # err

    # else:
    #     return dec_to_bin(int(args))

def HEX_inst(args : str, PC : int) -> str:
    args = args.strip()
    args = args.upper()

    res = re.match(r'^[0]?[X]?[\dA-F]+$', args)
    if res:
        return HexToBin(res.group())
    else:
        pass # err

def BIN_inst(args : str, PC : int) -> str:
    args = args.strip()

    if not args.isnumeric():
        pass # err
    else:
        return extend_bin(int(args))

def HALT_inst(args : str, PC : int) -> str:
    return instructions['HALT'] + "0" * 12

inst_func = {'ADD' : ADD_inst
            ,'AND' : AND_inst
            ,'BR' : BR_inst
            ,'JMP' : JMP_inst # RET & JMP
            ,'JSR' : JSR_inst # !
            ,'JSRR' : JSRR_inst # !
            ,'LD' : LD_inst
            ,'LDI' : LDI_inst
            ,'LDR' : LDR_inst
            ,'LEA' : LEA_inst
            ,'NOT' : NOT_inst
            ,'RET' : RET_inst # RET & JMP
            ,'RTI' : '1000'
            ,'ST' : ST_inst
            ,'STI' : STI_inst
            ,'STR' : STR_inst
            ,'TRAP' : '1111'
            ,'DEC' : DEC_inst
            ,'BIN' : BIN_inst
            ,'HEX' : HEX_inst
            ,'HALT': HALT_inst
            }
def findInstruction(line : str, lineNumber: int) -> str :

    # line = line.rstrip() # ???
    line = line.strip()
    # firstSpace = line.find(' ')
    firstSpace = re.search(r'[ \t]', line)
    if firstSpace == None:
        firstSpace = len(line)
    else:
        firstSpace = firstSpace.start()
    inst = line[:firstSpace]
    args = line[firstSpace+1:]


    try :
        if inst.startswith('BR'):
            return BR_inst(line, lineNumber)
        else:
            if not inst in inst_func.keys():
                pass # err
            else:
                return inst_func[inst](args, lineNumber)
    except Exception as e:
        print(f"err at {lineNumber}", e)

    






# if len(sys.argv) >= 3:
#     dest = sys.argv[2]

# if len(sys.argv) < 2:
#     raise ValueError("must provide an address to read from")



# src = sys.argv[1]

src = 'sample-code.txt'

replace(src, dest)



lineCounter = 0 # to store line of memory
fileLineCounter = 0 # to store the line in input file (text lines)

# phase 1
# building lookup table for labels :

with open(dest, mode='r') as f:
    # s = f.readline()
    for s in f:
        s = s.rstrip()
        fileLineCounter += 1

        res = None



        
        res = labelPattern.match(s)
        if res:
            if res.group(1).rstrip(" ,") in lookupTable:
                pass # duplicate label
            else:
                lookupTable[res.group(1).rstrip(" ,")] = lineCounter
                lineCounter += 1
                continue


        res = commentLine.match(s)
        if res:
            continue

        res = ORG.match(s)
        if res:
            # s = s[res.end():]
            res = re.match(r'^\s*ORG\s+[0]?[xX]?(\d+)', s)
            if res:
                lineCounter = int(res.group(1), 16)
                continue


            # try:
            #     lineCounter = int(s, base=0)
            # except:
            #     pass

            res = HEX.search(s)
            if res:
                lineCounter = HexToDec(res.group(1))
                continue
            res = DEC.search(s)

            if res:
                lineCounter = int(res.group(1))
                continue

        res = re.match(r'^\s*END\s*$', s)
        if res:
            break

        lineCounter += 1

        # findInstruction(s, lineCounter)

        # else -> err
            
        

        # s = s.split(',')

        # fileLineCounter += 1
        # s = s.split()
        # if len(s) == 0:
        #     continue
        
        # if s[0].endswith(';'): # comment
        #     continue

        # if s[0].endswith(','): # label
        #     if s[0] in lookupTable:
        #         pass # duplicate label

        #     else:
        #         lookupTable[s[0]] = lineCounter
        # elif s[0] == 'ORG':
        #     lineCounter = int(s[1])
        #     break

        # elif s[0] == 'END':
        #     break

        # if not s[0] not in instructions:
        #     pass # error
        # lineCounter += 1


#phase 2
# assembling
        
fileLineCounter = -1
with open(dest, mode='r') as f, open(auxFile, mode='w') as aux:
    for s in f:

        s = s.rstrip()
        fileLineCounter += 1

        res = None

        
        res = labelPattern.match(s)
        if res:
            # if res.group(1) in lookupTable:
            #     pass # duplicate label
            # else:
            #     lookupTable[res.group(1)] = lineCounter
            #     lineCounter += 1
            #     continue
            s = labelPattern.sub('', s)
            # function call to find instruction
            code = findInstruction(s, lineCounter)
            print(code, lineCounter, file=aux)
            print(code, lineCounter)
            lineCounter += 1
            continue


        res = commentLine.match(s)
        if res:
            continue

        res = ORG.match(s)
        if res:

            res = re.match(r'^\s*ORG\s+(\d+)', s)
            if res:
                lineCounter = int(res.group(1), 16)
                continue
            res = HEX.search(s)
            if res:
                lineCounter = HexToDec(res.group(1))
                continue
            res = DEC.search(s)

            if res:
                lineCounter = int(res.group(1))
                continue

        res = re.match(r'^\s*END\s*$', s)
        if res:
            break

        code = findInstruction(s, lineCounter)
        print(code, lineCounter, file=aux)
        print(code, lineCounter)
        lineCounter += 1

        






# d = {}

# d[1] = 1
# d[1] = 2

# print(d)

