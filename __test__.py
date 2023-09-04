# these test cases were taken from my javascript library calculate-string. it is licensed under the MIT License
# https://github.com/MrGriefs/calculate-string/blob/main/tests.js

from main import evaluate_expression

count = 0
def test(name: str, expr: str, expected):
  global count
  count += 1
  print(name)
  result = evaluate_expression(expr)
  if result != expected:
    print(f'Invalid result for test {count}.\nGot: {result}\nExpected: {expected}')
    exit(1)
  else:
    print(f'Test {count} passed.')

test('Normal addition', '125 + 125', (0, 250))
test('Normal subtraction', '125 - 25', (0, 100))
test('Normal multiplication', '125 * 5', (0, 625))
test('Normal division', '200 / 2', (0, 100))
test('Normal brackets', '(100 + 10) / 2', (0, 55))
test('Normal indices', '10 ^ 2', (0, 100))

test('Negative numbers', '-12 * 2', (0, -24))
test('Negative addition', '5+-2', (0, 3))
test('Negative addition 2', '-5+2', (0, -3))
test('Negative subtraction', '5--2', (0, 7))
test('Negative subtraction 2', '-5-2', (0, -7))
test('Negative multiplication', '5*-2', (0, -10))
test('Negative multiplication 2', '-5*2', (0, -10))
test('Negative division', '5/-2', (0, -2.5))
test('Negative division 2', '-5/2', (0, -2.5))
test('Negative brackets', '-(5)', (0, -5))
test('Negative indices', '2^-4', (0, 0.0625))
test('Negative indices 2', '-2^4', (0, 16))
test('Negative indices 3', '-(2^4)', (0, -16))

test('Scientific notation', '1e+6', (0, 1e6))
test('Scientific notation addition', '1e+6 + 1e+6', (0, 2e6))
test('Scientific notation subtraction', '1e+6 - 1.001e+4', (0, 989990))
test('Scientific notation multiplication', '1e+2 * 1e+3', (0, 100000))
test('Scientific notation division', '1e+4 / 1e+2', (0, 100))
test('Scientific notation brackets', '(1e+4 + 1e+2) / 1e+2', (0, 101))