class MyException(Exception):
    def __init__(self, message):
        super().__init__(self, message)

a = input("Please input number:")
n =8000
try:
    num = int(a)
    try:
        result = n / num
        print("{0} divide {1} equals {2}".format(n, a, result))
    except ZeroDivisionError as e1:
        print("Cannot divide with 0,Exception: {}".format(e1))
except ValueError as e2:
    print("Please input a number,Exception: {}".format(e2))
    raise MyException("Not allowed to input non digit!")
# Combine multiple exceptions
# except (ZeroDivisionError, ValueError) as e:
#     print("Please input correct format number,Exception: {}".format(e))

