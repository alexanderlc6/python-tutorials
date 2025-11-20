# Class definition
class Car:   #(object):
    #Class body
    pass

car = Car()

# Class & Instance Variables:self.xxx
class Dog:
    # Class Global Variable
    iRate = 0.84

    # Class Private Variable
    __iRatio = 0.5

    def __init__(self, name, age, sex = 'Female', amount = 0):
        self.name = name
        self.age = age
        self.sex = sex
        # Instance Private Variable
        self.__amount = amount
# d1 = Dog('Lina', 2)
# print('Dog name:{0}, age: {1}'.format(d1.name, d1.age))
# d2 = Dog('Wodi',1,'Male')
# print('Dog name:{0}, age: {1}'.format(d2.name, d2.age))
# d3 = Dog(name = 'Jack', sex = 'Male', age = 3)
# print('Dog name:{0}, age: {1}'.format(d3.name, d3.age))
# print('iRate:{0}'.format(Dog.iRate))

# Instance methods
#     def run(self):
#         print('{} is running...'.format(self.name))
#
#     def speak(self, sound):
#         print('{} is saying...'.format(self.name, sound))
#
# dog = Dog('Lina', 2)
# dog.run()
# dog.speak('Wo Wo Wo')

#Class method
    @classmethod
    def interest_by(cls, amt):
        return cls.iRate * amt

# interest = Dog.interest_by(2300)
# print('Calculate interest:{0:.4f}'.format(interest))

    def desc(self):
        return '{0} Amount:{1},Ratio:{2}.'.format(self.name, self.__amount, Dog.__iRatio)

# dog = Dog('Lina', 2, 'Male', 5600)
# dog.desc()
# Error:Cannot access private variable out of class! ==> dog.__amount
# print('Name:{0}, Amount:{1}, Ratio:{2}'.format(dog.name, dog.__amount, Dog.__iRatio))

# Private Method
    def __get_info(self):
        return ('Name:{0}, Amount:{1}, Ratio:{2}'.format(self.name, self.__amount, Dog.__iRatio))

    def show(self):
        print(self.__get_info())

# dog = Dog('Lina', 2, 'Male', 5600)
# dog.show()
# Error:Cannot access private method!
# dog.__get_info()

# Define get() & set() or use @property for private variable [__amount]
    @property
    def amount(self):
        return self.__amount
    @amount.setter
    def amount(self, amount):
        self.__amount = amount

dog = Dog('Lina', 2, 'Male')
dog.amount = 8104
print('Name:{0}, Amount:{1}'.format(dog.name, dog.amount))

#List calculate
print([x * x for x in range(1,5)])

