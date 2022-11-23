



def foo():
    print('foo defined here. test_module.py')
    print('name:', __name__)

def bar():
    print('bar here ------------- hehehe')
    print('name:', __name__)

if __name__ == '__main__':
    print('main if statement run.')
    foo()