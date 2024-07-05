# import re

# args = 'R1,R2,#10'
# res = re.match(r'^R(?P<RD>[0-7]),R(?P<SR1>[0-7]),(R(?P<SR2>[0-7])|#(?P<IMM>\d+))$', args)

# print(res.group('SR2'))

# args = WHITESPACES.sub(args, '')
#     # args = args.split(',')
#     res = re.match(r'^R(?P<RD>[0-7]),R(?P<SR1>[0-7]),(R(?P<SR2>[0-7])|#(?P<IMM>\d+))$', args)

# def _inst(args : str) -> str:
#     args = WHITESPACES.sub(args, '')
    
#     res = re.match(r'^R(?P<RD>[0-7]),R(?P<SR1>[0-7]),(R(?P<SR2>[0-7])|#(?P<IMM>\d+))$', args)

#     if res:

#         inst = ''
#         inst += instructions[]

#     else:
#         pass # err

# import re
# labelPattern = re.compile(r'^(\w+)\s*,')
# s = 'BRn '
# res = re.match(r'^BR(?P<n>n)?(?P<p>p)?(?P<z>z)? (?P<LABEL>\w+)$', s)


import re
# print(res)
args = 'R0,R1,#0'
res = re.match(r'^R(?P<RD>[0-7]),R(?P<SR1>[0-7]),(R(?P<SR2>[0-7])|#(?P<IMM>\d+))$', args)

print(res)
# print(res.group("DR"))
print(res.groupdict())

