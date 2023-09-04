from typing import Literal

# token enum (python stdlib enum is overkill, we don't need enum member names)
TOKEN_INTEGER = 0
# special tokens
TOKEN_BRACKET_R = 1
TOKEN_WHITESPACE = 2
TOKEN_NONE = 3
TOKEN_BRACKET_L = 4
# this token only exists during state creation
TOKEN_MULTIPLICATION_OR_INDICE = 5
# binary operators
TOKEN_FLOAT = 6
TOKEN_INDICE = 7
TOKEN_DIVISION = 8
TOKEN_MULTIPLICATION = 9
TOKEN_ADDITION = 10
TOKEN_SUBTRACTION = 11
TOKEN_EXPONENT = 12 # E notation
# unary operators
TOKEN_UNARY_ADDITION = 13
TOKEN_UNARY_SUBTRACTION = 14

# enum util operations
def is_token_value(enum):
  # these tokens are guaranteed to contain the resulting value when finalised
  return TOKEN_WHITESPACE >= enum

def is_token_unary_operator(enum):
  return TOKEN_UNARY_ADDITION <= enum

# token consts
tokens = {
  TOKEN_INTEGER: ('0','1','2','3','4','5','6','7','8','9'),
  TOKEN_FLOAT: ('.'),
  TOKEN_INDICE: ('^'),
  TOKEN_DIVISION: ('/', '÷'),
  TOKEN_MULTIPLICATION: ('x', '×'),
  TOKEN_ADDITION: ('+'),
  TOKEN_SUBTRACTION: ('-'),
  TOKEN_EXPONENT: ('e'),
  TOKEN_BRACKET_L: ('('),
  TOKEN_BRACKET_R: (')'),
  # mul/ind share the same token, so special enum case needed
  TOKEN_MULTIPLICATION_OR_INDICE: ('*'),
  TOKEN_WHITESPACE: (' ', '\t'),
}

# a map containing each operator's precedence and associativity
# as the tuple (precedence, associativity) where precedence is
# an integer representing the operator's order of precedence, and
# associativity is 0 or 1, 0 being left and 1 being right.
operator_map: dict[int, tuple[int, Literal[0] | Literal[1]]] = {
  # float tokens can't be consumed in state creation,
  # so we handle it as an operator instead.
  TOKEN_FLOAT: (0, 1),
  TOKEN_UNARY_ADDITION: (1, 1),
  TOKEN_UNARY_SUBTRACTION: (1, 1),

  # the default operator precedence (BIDMAS).
  # we can easily let the user customise this later.
  TOKEN_EXPONENT: (1, 1),
  TOKEN_INDICE: (3, 0),
  TOKEN_DIVISION: (4, 0),
  TOKEN_MULTIPLICATION: (5, 0),
  TOKEN_ADDITION: (6, 0),
  TOKEN_SUBTRACTION: (7, 0),
}

token_map = {}

for enum, token_list in tokens.items():
  for char in token_list:
    assert(char not in token_map)
    token_map[char] = enum

# these consts are only used to build the token map, unbind to deter accidental use
del tokens
