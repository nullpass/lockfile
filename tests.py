#!/usr/bin/env python
import locker


def main():
    print('#### instance')
    # a = locker.Locker(file='./foo.pid', age_limit=1)
    # a = locker.Locker(age_limit=0)
    a = locker.Locker(file='/tmp/foo.pid', age_limit=10)
    # a = locker.Locker(file='./foo.pid', age_limit=0, kill=True)

    print('#### try create')
    if a.create():
        print('created')
    else:
        print('create failed')


    print('#### check')
    print(a.check())

    print('#### try another create')
    print(a.create())

    print('#### dump log')
    print(a.log)
    return


if __name__ == '__main__':
    main()
