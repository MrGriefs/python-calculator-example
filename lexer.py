import operator
from ctypes import c_ulong, c_double
from dataclasses import dataclass, field
from typing import Literal, cast
from tokens import *

LexerTokenValue = list[int | c_ulong | c_double]
LexerTokenOperator = list[int]
LexerToken = LexerTokenValue | LexerTokenOperator
# dataclass is used here as it removes most garbage methods from traditional
# python class. precedural is almost always preferable over object-oriented
@dataclass(init=False, repr=False, eq=False, match_args=False)
class LexerState:
  output_queue: list[LexerToken]
  output_queue_index = -1
  stack: list
  stack_index = -1
  last_token_type = TOKEN_NONE
  expr_index = 0
  expr_len: int
  
def lexer_state_add_output(state: LexerState, token: LexerToken):
  state.output_queue_index += 1
  state.output_queue.append(token)

def lexer_state_pop_output(state: LexerState):
  state.output_queue_index -= 1
  return state.output_queue.pop()

def lexer_state_push_stack(state: LexerState, item):
  state.stack_index += 1
  state.stack.append(item)
  
def lexer_state_pop_stack(state: LexerState):
  state.stack_index -= 1
  return state.stack.pop()

# this function evaluates the lexer state by popping tokens off the stack. state is no longer usable after this
def lexer_state_finalise(state: LexerState) -> tuple[Literal[0], float] | tuple[Literal[2], int]:
  while state.stack_index != -1:
    token_type = lexer_state_pop_stack(state)
    
    # report an unclosed bracket error
    if token_type == TOKEN_BRACKET_L:
      # the "unclosed bracket" will always be the last opened bracket.
      # we'll leave it up to the user to decide whether they want its location
      # instead of using unnecessary computation here
      return 2, 0

    lexer_state_add_output(state, [token_type])

  for token in state.output_queue:
    lexer_state_token_operation_map[token[0]](state, token)
  
  return 0, cast(c_double, state.stack[0][1]).value

# token operation methods
lexer_state_token_operation_map = {}
lexer_state_token_minioperation_map = {}

def minioperate_token_float(a: float, b: float):
  while b >= 1:
    b /= 10
  return a + b

def minioperate_token_exponent(a: float, b: float):
  return a * (10 ** b)

lexer_state_token_minioperation_map[TOKEN_FLOAT] = minioperate_token_float
lexer_state_token_minioperation_map[TOKEN_INDICE] = operator.pow
lexer_state_token_minioperation_map[TOKEN_DIVISION] = operator.truediv
lexer_state_token_minioperation_map[TOKEN_MULTIPLICATION] = operator.mul
lexer_state_token_minioperation_map[TOKEN_ADDITION] = operator.add
lexer_state_token_minioperation_map[TOKEN_SUBTRACTION] = operator.sub
lexer_state_token_minioperation_map[TOKEN_EXPONENT] = minioperate_token_exponent
lexer_state_token_minioperation_map[TOKEN_UNARY_ADDITION] = operator.pos
lexer_state_token_minioperation_map[TOKEN_UNARY_SUBTRACTION] = operator.neg

def operate_token_integer(state: LexerState, token: LexerToken):
  lexer_state_push_stack(state, token)

def operate_token_float(state: LexerState, token: LexerToken):
  right = lexer_state_pop_stack(state)
  left = cast(LexerTokenValue, state.stack[state.stack_index])
  double = c_double(right[1].value)

  while double.value >= 1:
    double.value /= 10

  # add additional decimal places
  double.value /= (10 ** right[2])

  double.value += cast(c_ulong, left[1]).value
  left[1] = double

def operate_binary_operator_token(state: LexerState, token: LexerToken):
  right = lexer_state_pop_stack(state)
  left = cast(LexerTokenValue, state.stack[state.stack_index])
  left[1] = c_double(lexer_state_token_minioperation_map[token[0]](cast(c_ulong, left[1]).value, right[1].value))

def operate_unary_operator_token(state: LexerState, token: LexerToken):
  left = cast(LexerTokenValue, state.stack[state.stack_index])
  left[1] = c_double(lexer_state_token_minioperation_map[token[0]](cast(c_ulong, left[1]).value))

lexer_state_token_operation_map[TOKEN_INTEGER] = operate_token_integer
lexer_state_token_operation_map[TOKEN_FLOAT] = operate_token_float
lexer_state_token_operation_map[TOKEN_INDICE] = operate_binary_operator_token
lexer_state_token_operation_map[TOKEN_DIVISION] = operate_binary_operator_token
lexer_state_token_operation_map[TOKEN_MULTIPLICATION] = operate_binary_operator_token
lexer_state_token_operation_map[TOKEN_ADDITION] = operate_binary_operator_token
lexer_state_token_operation_map[TOKEN_SUBTRACTION] = operate_binary_operator_token
lexer_state_token_operation_map[TOKEN_EXPONENT] = operate_binary_operator_token
lexer_state_token_operation_map[TOKEN_UNARY_ADDITION] = operate_unary_operator_token
lexer_state_token_operation_map[TOKEN_UNARY_SUBTRACTION] = operate_unary_operator_token