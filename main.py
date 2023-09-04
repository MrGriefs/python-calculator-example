# python 3.11.4

from lexer import LexerState, lexer_state_finalise
from tokens import token_map, is_token_value
from tokenise import token_consume_map
from typing import Literal

def evaluate_expression(expr: str) -> tuple[Literal[0], float] | tuple[Literal[1], int] | tuple[Literal[2], int]:
  '''
  returns a tuple containing (error, result) where error
  is the result type:
  integer 0 denoting no error,
  integer 1 denoting an unexpected token error or
  integer 2 denoting an unclosed bracket error.

  this function also expects the expression string to use the correct
  capitalisation and won't make special checks for caps. it's up to the user
  to lowercase the string beforehand if they wish for case-insentive operators.
  '''

  expr_len = len(expr)
  state = LexerState()
  state.output_queue = []
  state.stack = []
  state.expr_len = expr_len
  # convert the string into lexical tokens we can traverse later
  while state.expr_index != expr_len:
    c = expr[state.expr_index]

    # a match statement was considered for this purpose, but python
    # match statement is not O(1) time. the pattern compiler is
    # naive, producing the equivalent of an if/elif sequence.
    # the python equivalent of a hashmap is used instead.
    if c not in token_map:
      return 1, state.expr_index
    
    token_type = token_map[c]

    # consume token
    r = token_consume_map[token_type](state, token_type, c)
    if r != 0: # r is either 0 or 1
      return r, state.expr_index

    state.expr_index += 1
  
  # last token should always be a value token (integer or bracket), otherwise it's a tokenisation error
  if not is_token_value(state.last_token_type):
    return 1, state.expr_index - 1

  return lexer_state_finalise(state)

if __name__ == '__main__':
  while True:
    expr = input()
    result = evaluate_expression(expr.lower())
    error = result[0]
    if 0 == error:
      print(f'evaluated result: {result[1]}') # type: ignore
    elif 1 == error:
      print(f'unexpected token: {expr[result[1]]}') # type: ignore
    elif 2 == error:
      print(f'unclosed bracket error')
    else:
      print(f'unknown error: {result}')