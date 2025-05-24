# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask web application that solves the numbers round of the UK TV game show Countdown. The app takes 6 numbers and a target value, then finds mathematical solutions using the four basic operations (+, -, *, /) to reach or get as close as possible to the target.

## Development Commands

- **Run the application**: `python app.py` (runs on port 8045)
- **Type checking**: `mypy .` (strict typing enforced via mypy.ini)
- **Install dependencies**: `pip install -r requirements.txt`

## Architecture

The solver uses a breadth-first search algorithm to explore all possible mathematical combinations:

1. **Core solving algorithm** (`solutions.py`): Implements the search with caching and time limits
2. **Data models** (`models.py`): Operation trees and SolveState representation with strict typing
3. **Web interface** (`app.py`): Flask routes with form handling and validation
4. **Form handling** (`forms.py`, `form_validation.py`): WTForms with custom validation rules

### Key Components

- **Operation class**: Represents mathematical operations as trees with formula string generation
- **SolveState class**: Tracks search state including used/unused numbers and operation pools  
- **Caching system** (`cache.py`): Time-limited caching with thread safety for expensive computations
- **Search algorithm**: Expands nodes by trying all combinations of operations between available numbers

The solver prioritizes solutions by error (distance from target) then by formula complexity. It uses commutative operator normalization and duplicate formula detection to optimize search space.

## Technical Notes

- Uses waitress server on POSIX systems, Flask dev server on Windows
- Strict type hints enforced (see mypy.ini configuration)
- Solution search is time-bounded with configurable limits
- Results are cached to improve performance for repeated queries

## Performance Optimizations

The solver has been heavily optimized for both speed and solution quality:

- **Best-first search**: Uses priority queue (heapq) to explore most promising solutions first
- **Early termination**: Stops when exact solutions found or time limit reached
- **Smart pruning**: Eliminates unpromising branches while preserving paths to exact solutions
- **Randomization**: Follows authentic Countdown TV show rules with weighted selection (1-2 large numbers most common)

Performance improvements: ~1000-4000x faster than original breadth-first approach while maintaining ability to find exact solutions for complex cases.