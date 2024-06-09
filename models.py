from dataclasses import dataclass, field
import logging
from typing import List, Optional, Union

logging.basicConfig(level=logging.DEBUG)

def flatten_list(nested_list):
    flattened = []
    
    def _flatten(sublist):
        for item in sublist:
            if isinstance(item, list):
                _flatten(item)
            else:
                flattened.append(item)
    
    _flatten(nested_list)
    return flattened

@dataclass
class Operation():
    total: int
    operator: str
    left: Union['Operation', None]  # Using forward references
    right: Union['Operation', None]  # Using forward references

    def formula_str(self) -> str:
        if self.left is None and self.right is None:
            return str(self.total)
        left_str = self.left.formula_str() if self.left is not None else ''
        right_str = self.right.formula_str() if self.right is not None else ''
        return f'({left_str} {self.operator} {right_str})'
    
    def used_numbers(self) -> List[int]:
        if self.left is None and self.right is None:
            return [self.total]
        left_numbers = self.left.used_numbers() if self.left is not None else []
        right_numbers = self.right.used_numbers() if self.right is not None else []
        return left_numbers + right_numbers
    
    def __post_init__(self):
        if self.operator is not None and self.left is None and self.right is None:
            raise ValueError('Operator {self.operator} must have left and right operands')
        if self.operator is None and (self.left is not None or self.right is not None):
            raise ValueError('Operand {self.operator} must not have left or right operands')
        commutative_operators = ['+', '*']
        if self.operator in commutative_operators and self.left.total < self.right.total:
            self.left, self.right = self.right, self.left


@dataclass
class SolveState():
    used_numbers: List[int]
    unused_numbers: List[int]
    operation_pool: List[Operation]
    target: int
    error: Optional[int] = None
    score: Optional[int] = None
    solution: Optional[Operation] = None
    _sorted_solutions: List[Operation] = field(init=False, repr=False)
    _unique_string: str = None
    _score: int = None


    def __post_init__(self):
        self._sorted_solutions = self.sorted_possible_solutions()
        self.solution = self._sorted_solutions[0]
        self.used_numbers = sorted(self.solution.used_numbers())
        self.error = abs(self.target - self.solution.total)
        self.score = abs(self.error) + len(self.used_numbers)
        remaining_solutions = self._sorted_solutions[1:]
        self.unused_numbers = sorted(flatten_list([x.used_numbers() for x in remaining_solutions]))
        self._unique_string = self.unique_string()
        self._score = self.get_score()

    def sorted_possible_solutions(self) -> List[Operation]:
        return sorted(self.operation_pool, key=lambda x: abs(x.total - self.target))
    
    def unique_string(self) -> str:
        possible_solutions = self._sorted_solutions
        ordered_substrings = [x.formula_str() for x in possible_solutions]
        # now join the results into a single string
        return ':'.join(ordered_substrings)

    def formula_str(self) -> str:
        if self.solution is None:
            return ''
        return self.solution.formula_str()
    
    def total_str(self) -> str:
        if self.solution is None:
            return ''
        return str(self.solution.total)
    
    def total(self) -> int:
        if self.solution is None:
            return 0
        return self.solution.total
    
    def get_score(self) -> int:
        return (100 * self.error) + len(self.used_numbers)
    
    '''
    
    def __hash__(self):
        return hash(self._unique_string)
    
    def __eq__(self, other):
        if isinstance(other, SolveState):
            return self._unique_string == other._unique_string
        return False

    '''