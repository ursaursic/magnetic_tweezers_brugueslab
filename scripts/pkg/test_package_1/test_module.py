


print('In test_package_1.test_module. Name:', __name__)
from ..test_package_2.test_module import bar as barec



def foo():
    print('foo defined here. test_module.py')
    print('name:', __name__)


    # test_package_2.
    # test_module.bar()
    barec()
    # sonce()



if __name__ == '__main__':
    print('main if statement run.')
    foo()