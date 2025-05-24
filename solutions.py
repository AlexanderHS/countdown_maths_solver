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
    import heapq
    
    all_nodes: List[SolveState] = []
    # Use priority queue for best-first search (lowest error first)
    start_node = starting_nodes(numbers, target)
    nodes_for_expansion = [(start_node.error, 0, start_node)]
    heapq.heapify(nodes_for_expansion)
    seen_formulas = set()
    expanded: int = 0
    start: datetime.datetime = datetime.datetime.now()
    best_error = float('inf')
    exact_solutions_found = []
    
    while nodes_for_expansion:
        # Check time limit
        time_elapsed = datetime.datetime.now() - start
        if time_elapsed.total_seconds() > stop_after_seconds:
            logging.info(f'Stopping due to time limit: {time_elapsed.total_seconds()} seconds')
            break
            
        _, _, current_node = heapq.heappop(nodes_for_expansion)
        expanded += 1
        
        # If we found an exact solution, collect it but keep searching for more
        if current_node.error == 0:
            exact_solutions_found.append(current_node)
            all_nodes.append(current_node)
            best_error = 0
            logging.info(f'Found exact solution: {current_node.solution.formula_str()} in {time_elapsed.total_seconds()} seconds')
            
            # If we have multiple exact solutions and have been searching a while, we can stop
            if len(exact_solutions_found) >= 3 and time_elapsed.total_seconds() > 1.0:
                logging.info(f'Found {len(exact_solutions_found)} exact solutions, stopping search')
                break
            continue
            
        # If we have exact solutions and current error is much worse, skip this branch
        if best_error == 0 and current_node.error > 100:
            continue
            
        # Minimal pruning - only skip if error is enormous to prevent infinite search
        # This ensures we find complex exact solutions that may require poor intermediate steps  
        if current_node.error > 1000 and len(all_nodes) > 10000:
            continue
            
        new_nodes: List[SolveState] = expand_node(current_node)
        for node in new_nodes:
            formula_str = node._unique_string
            if formula_str not in seen_formulas:
                seen_formulas.add(formula_str)
                all_nodes.append(node)
                best_error = min(best_error, node.error)
                
                # Continue expanding all promising nodes
                heapq.heappush(nodes_for_expansion, (node.error, len(all_nodes), node))

        if expanded % 2000 == 0:
            time_elapsed = datetime.datetime.now() - start
            time_elapsed_seconds = time_elapsed.total_seconds()
            expanded_per_second = int(expanded / time_elapsed_seconds) if time_elapsed_seconds > 0 else 0
            logging.debug(f'{int(time_elapsed_seconds)}sec:Expanded {expanded}. {expanded_per_second=}. Found {len(all_nodes)} solutions (best error: {best_error})... {len(nodes_for_expansion)} nodes left to expand')

    # Sort all nodes by error then complexity
    all_nodes = sorted(all_nodes, key=lambda x: (x.error, x._score), reverse=False)
    
    time_elapsed = datetime.datetime.now() - start
    time_elapsed_seconds = time_elapsed.total_seconds()
    logging.info(f'Found {len(all_nodes)} solutions in seconds: {time_elapsed_seconds}')
    
    # Return best solutions, prioritizing exact matches
    # If we found exact solutions, prioritize them
    if exact_solutions_found:
        exact_solutions_found.extend([sol for sol in all_nodes if sol.error > 0])
        return exact_solutions_found[:1000]
    else:
        return all_nodes[:1000]


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