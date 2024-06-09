import datetime
import itertools
import logging
from typing import Dict, FrozenSet, List, Set
from concurrent.futures import ProcessPoolExecutor, as_completed

from cache import time_limited_cache, CACHE_TIMEOUT

# modules
from forms import PuzzleInputForm
from models import Operation, SolveState

logging.basicConfig(level=logging.DEBUG)

@time_limited_cache(CACHE_TIMEOUT)
def get_solutions(numbers: List[int], target: int, stop_after_seconds: int = 30) -> List[SolveState]:
    nodes: List[SolveState] = [starting_nodes(numbers, target)]
    nodes_for_expansion: List[SolveState] = nodes.copy()
    seen_formulas = set()
    expanded: int = 0;
    start: datetime.datetime = datetime.datetime.now()
    solution_found = False
    while nodes_for_expansion:
        current_node: SolveState = nodes_for_expansion.pop(0)
        expanded += 1
        new_nodes: List[SolveState] = expand_node(current_node)
        new_nodes_without_repeat: List[SolveState] = []
        for node in new_nodes:
            formula_str = node._unique_string
            error = node.error
            if formula_str not in seen_formulas:
                seen_formulas.add(formula_str)
                new_nodes_without_repeat.append(node)
                #logging.debug(f'Adding {formula_str} to seen formulas')
            if error == 0:
                solution_found = True
                time_elapsed = datetime.datetime.now() - start
                time_elapsed_seconds = time_elapsed.total_seconds()
                logging.info(f'Found solution: {node.solution.formula_str()} in seconds: {time_elapsed_seconds}')
        if solution_found:
            time_elapsed = datetime.datetime.now() - start
            time_elapsed_seconds = time_elapsed.total_seconds()
            if time_elapsed_seconds > stop_after_seconds:
                nodes_for_expansion = []    # stop expanding nodes
                print(f'Stopping after {time_elapsed_seconds} seconds')

        nodes_for_expansion.extend(new_nodes_without_repeat)
        nodes.extend(new_nodes_without_repeat)
        if expanded % 5000 == 0:
            time_elapsed = datetime.datetime.now() - start
            time_elapsed_seconds = time_elapsed.total_seconds()
            expanded_per_second = int(expanded / time_elapsed_seconds)
            logging.debug(f'{int(time_elapsed_seconds)}sec:Expanded {expanded}. {expanded_per_second=}. Found {len(nodes)} solutions... {len(nodes_for_expansion)} nodes left to expand')

    # sort the nodes by error then length of formula
    nodes = sorted(nodes, key=lambda x: (x.error, x._score), reverse=False)
    logging.debug(f'Found {len(nodes)} solutions')

    nodes = nodes[:1_000]
    time_elapsed = datetime.datetime.now() - start
    time_elapsed_seconds = time_elapsed.total_seconds()
    logging.info(f'Found {len(nodes)} solutions in seconds: {time_elapsed_seconds}')
    return nodes


#@time_limited_cache(CACHE_TIMEOUT)
def expand_node(node: SolveState) -> List[SolveState]:
    new_nodes: List[SolveState] = []
    operation_pool = node.operation_pool
    num_operations = len(operation_pool)

    for i in range(num_operations):
        left = operation_pool[i]
        for j in range(num_operations):
            if i == j:
                continue
            right = operation_pool[j]

            for operator in ['+', '-', '*', '/']:
                if operator == '/':
                    if right.total == 0 or left.total % right.total != 0:
                        continue
                    result = left.total // right.total
                elif operator in ['*', '/']:
                    if left.total == 1 or right.total == 1:
                        continue
                    result = left.total * right.total
                elif operator == '-':
                    result = left.total - right.total
                elif operator == '+':
                    result = left.total + right.total

                if result <= 0:
                    continue

                new_operation_pool = [operation_pool[k] for k in range(num_operations) if k != i and k != j]
                new_operation_pool.append(Operation(
                    total=result,
                    operator=operator,
                    left=left,
                    right=right
                ))

                new_node = SolveState(
                    used_numbers=node.used_numbers + [left.total, right.total],
                    unused_numbers=[x for x in node.unused_numbers if x not in [left.total, right.total]],
                    operation_pool=new_operation_pool,
                    target=node.target
                )
                new_nodes.append(new_node)

    return new_nodes


def starting_nodes(numbers: List[int], target: int) -> List[SolveState]:
    return SolveState(
        used_numbers=[],
        unused_numbers=numbers.copy(),
        target=target,
        operation_pool=[
            Operation(total=x, operator=None, left=None, right=None) for x in numbers
        ])