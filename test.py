import re
import fileasobj

#test_file = fileasobj.FileAsObj('Test.txt', verbose=True)
test_file = fileasobj.FileAsObj('Test.txt')


x = 'w.*rd'
print('Find {}'.format(x))
print(test_file.egrep(x))
print('---')

x = 'bird'
print('Find {}'.format(x))
print(test_file.egrep(x))
print('---')

# Just using * is invalid, 
x = '*rd'
print('Find {}'.format(x))
print(test_file.egrep(x))
# There ya go
x = '.*rd'
print('Find {}'.format(x))
print(test_file.egrep(x))
print('---')

x = 'b.*rd'
print('Find {}'.format(x))
print(test_file.egrep(x))
print('---')

x = '[a-z]ird'
print('Find {}'.format(x))
print(test_file.egrep(x))
print('---')

x = '(host|bird)'
print('Find {}'.format(x))
print(test_file.egrep(x))
print('---')

x = 'h[o0]stname'
print('Find {}'.format(x))
print(test_file.egrep(x))
print('---')

x = '.*mail[0-9]'
print('Find {}'.format(x))
print(test_file.egrep(x))
print('---')

x = 'tld$'
print('Find {}'.format(x))
print(test_file.egrep(x))
print('---')

x = '^10.*'
print('Remove {} from {}, RESULT={}'.format(
        x,
        test_file.egrep(x),
        test_file.rm(test_file.egrep(x))
        )
      )
print('---')

x = ' h0st.*'
print('Remove {} from {}, RESULT={}'.format(
        x,
        test_file.egrep(x),
        test_file.rm(test_file.egrep(x))
        )
      )
print('---')

x = '#'
print('Remove whole line "{}" from {}, RESULT={}'.format(
        x,
        test_file.grep(x),
        test_file.rm(x)
        )
      )
print(test_file.grep(x))
print('---')

old = '172.19.18.17    freebird.example.com'
new = '172.19.18.17    freebird.example.com  # Added 1976.10.29 -jh'
print('Replace {} with {}'.format(old, new))
print(test_file.replace(old, new))
print('---')

# Replace does not yet support lists as input
#old = test_file.egrep('^[ ]+#.*')
#new = '#'
#print('Replace {} with {}'.format(old, new))
#print(test_file.replace(old, new))
# so instead...
x = '^[ ]+#.*'
print('Remove {} from {}, RESULT={}'.format(
        x,
        test_file.egrep(x),
        test_file.rm(test_file.egrep(x))
        )
      )
print('---')




x = '#FOO'
print('Add line {}'.format(x))
print(test_file.add(x))


x = '#FOO'
print('Add line {}'.format(x))
print(test_file.add(x))

x = '#FOO'
print('non-unique Add line {}'.format(x))
print(test_file.add(x, unique=False))





#print(test_file)
#print(test_file.Trace)


