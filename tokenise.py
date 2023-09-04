from ctypes import c_ulong
from typing import cast
from lexer import LexerState, lexer_state_add_output, lexer_state_push_stack, lexer_state_pop_stack, LexerTokenValue, LexerTokenOperator
from tokens import *

integer_map = {
  '0': 0,
  '1': 1,
  '2': 2,
  '3': 3,
  '4': 4,
  '5': 5,
  '6': 6,
  '7': 7,
  '8': 8,
  '9': 9,
}

# implementation based on https://en.wikipedia.org/wiki/Shunting_yard_algorithm#The_algorithm_in_detail
def add_operator_token(state: LexerState, token_type: int):
  while state.stack_index != -1:
    token2 = cast(int, state.stack[state.stack_index])
    if TOKEN_BRACKET_L == token2:
      break

    token2_info = operator_map[token2]
    token_info = operator_map[token_type]
    if not(token2_info[0] < token_info[0] or (token_info[0] == token2_info[0] and token_info[1] == 0)):
      break

    lexer_state_add_output(state, [lexer_state_pop_stack(state)])
  
  lexer_state_push_stack(state, token_type)
  state.last_token_type = token_type

# token consumption methods
token_consume_map = {}

def consume_token_integer(state: LexerState, token_type: int, char: str):
  if state.last_token_type == TOKEN_INTEGER:
    integer = integer_map[char]
    ulong = cast(c_ulong, state.output_queue[state.output_queue_index][1])

    if integer == 0 and ulong.value == 0:
      state.output_queue[state.output_queue_index][2] += 1 # type: ignore
    else:
      ulong.value *= 10
      # int(c) has too much overhead compared to a constant integer hashmap
      ulong.value += integer
  else:
    # whitespace should not be inbetween two integer tokens
    if is_token_value(state.last_token_type):
      return 1

    integer = integer_map[char]
    decimal = 1 if integer == 0 else 0

    if state.last_token_type == TOKEN_MULTIPLICATION_OR_INDICE:
      add_operator_token(state, TOKEN_MULTIPLICATION)

    lexer_state_add_output(state, [token_type, c_ulong(integer), decimal])
    state.last_token_type = token_type

  return 0

def consume_token_float(state: LexerState, token_type: int, char: str):
  # the float operator shouldn't accept bracket values
  if state.last_token_type != TOKEN_INTEGER:
    return 1

  add_operator_token(state, token_type)

  return 0

# a generic function to handle the consumption of binary operator tokens that don't need special handling
def consume_binary_operator_token(state: LexerState, token_type: int, char: str):
  if not is_token_value(state.last_token_type):
    return 1

  add_operator_token(state, token_type)

  return 0

def consume_unary_operator_token(state: LexerState, token_type: int, char: str):
  if not is_token_value(state.last_token_type):
    # last token is an operator (or no token), thus this cannot be a binary operator
    
    # the 2nd to last token must be a value token (to allow unary operations)
    # checking if the last token is a binary operator asserts the above
    # good: 1++ or 1--
    # good: )++ or )--
    # bad: (++ or (--
    # bad: +++ or ---
    # bad: +)+ or -)- (gets caught by consume_token_bracket_r anyway)
    if is_token_unary_operator(state.last_token_type):
      return 1

    if state.last_token_type == TOKEN_MULTIPLICATION_OR_INDICE:
      add_operator_token(state, TOKEN_MULTIPLICATION)

    # hack: this will need to be changed if new binary operators are added
    add_operator_token(state, token_type + 3)
  else: # last token is a value
    add_operator_token(state, token_type)

  return 0

def consume_token_bracket_l(state: LexerState, token_type: int, char: str):
  # an operator token (or no token) must precede left bracket
  if is_token_value(state.last_token_type):
    return 1

  if state.last_token_type == TOKEN_MULTIPLICATION_OR_INDICE:
    add_operator_token(state, TOKEN_MULTIPLICATION)
  
  lexer_state_push_stack(state, token_type)

  return 0

def consume_token_bracket_r(state: LexerState, token_type: int, char: str):
  # an operator token must not precede right bracket (this includes a left bracket)
  if not is_token_value(state.last_token_type):
    return 1

  while cast(LexerTokenOperator, state.stack[state.stack_index]) != TOKEN_BRACKET_L:
    if state.stack_index == 0:
      return 1
    lexer_state_add_output(state, [cast(int, lexer_state_pop_stack(state))])
  
  lexer_state_pop_stack(state)
  state.last_token_type = token_type

  return 0

def consume_token_multiplication_or_indice(state: LexerState, token_type: int, char: str):
  if state.last_token_type == TOKEN_MULTIPLICATION_OR_INDICE:
    add_operator_token(state, TOKEN_INDICE)
  else:
    if not is_token_value(state.last_token_type):
      return 1
    
    state.last_token_type = token_type

  return 0

def consume_token_whitespace(state: LexerState, token_type: int, char: str):
  # we only care about the whitespace token if it appears after a value token
  # (and therefore the whitespace token can be considered a value token)

  # magic expression equivalent to "TOKEN_INTEGER == state.last_token_type or
  # TOKEN_BRACKET_R == state.last_token_type"
  if TOKEN_BRACKET_R >= state.last_token_type:
    state.last_token_type = token_type

  return 0

token_consume_map[TOKEN_INTEGER] = consume_token_integer
token_consume_map[TOKEN_FLOAT] = consume_token_float
token_consume_map[TOKEN_INDICE] = consume_binary_operator_token
token_consume_map[TOKEN_DIVISION] = consume_binary_operator_token
token_consume_map[TOKEN_MULTIPLICATION] = consume_binary_operator_token
token_consume_map[TOKEN_ADDITION] = consume_unary_operator_token
token_consume_map[TOKEN_SUBTRACTION] = consume_unary_operator_token
token_consume_map[TOKEN_EXPONENT] = consume_binary_operator_token
token_consume_map[TOKEN_BRACKET_L] = consume_token_bracket_l
token_consume_map[TOKEN_BRACKET_R] = consume_token_bracket_r
token_consume_map[TOKEN_MULTIPLICATION_OR_INDICE] = consume_token_multiplication_or_indice
token_consume_map[TOKEN_WHITESPACE] = consume_token_whitespace
