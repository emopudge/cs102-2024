import random
from copy import deepcopy
from random import choice, randint
from typing import List, Optional, Tuple, Union

import pandas as pd


def create_grid(rows: int = 15, cols: int = 15) -> List[List[Union[str, int]]]:
    return [["■"] * cols for _ in range(rows)]


def remove_wall(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> List[List[Union[str, int]]]:
    """
    удаляет случайную стену
    """
    x, y, col, row = coord[0], coord[1], len(grid) - 1, len(grid[0]) - 1
    paths = ["go_up", "go_right"]
    path = choice(paths)
    if path == "go_up" and 0 <= x - 2 < col and 0 <= y < row:
        grid[x - 1][y] = " "
    else:
        path = "go_right"
    if path == "go_right" and 0 <= x < col and 0 <= y + 2 < row:
        grid[x][y + 1] = " "
    elif path == "go_right" and 0 <= x - 2 < col and 0 <= y < row:
        grid[x - 1][y] = " "

    return grid


def bin_tree_maze(rows: int = 15, cols: int = 15, random_exit: bool = True) -> List[List[Union[str, int]]]:
    """генерирует лабиринт с помощью алгоритма случайного удаления стен"""
    grid = create_grid(rows, cols)
    empty_cells = []
    for x, row in enumerate(grid):
        for y, _ in enumerate(row):
            if x % 2 == 1 and y % 2 == 1:
                grid[x][y] = " "
                empty_cells.append((x, y))
    while empty_cells:
        x, y = empty_cells.pop(0)
        grid = remove_wall(grid, (x, y))
        # генерация входа и выхода
    if random_exit:
        x_in, x_out = randint(0, rows - 1), randint(0, rows - 1)
        y_in = randint(0, cols - 1) if x_in in (0, rows - 1) else choice((0, cols - 1))
        y_out = randint(0, cols - 1) if x_out in (0, rows - 1) else choice((0, cols - 1))
    else:
        x_in, y_in = 0, cols - 2
        x_out, y_out = rows - 1, 1

    grid[x_in][y_in], grid[x_out][y_out] = "X", "X"
    return grid


def get_exits(grid: List[List[Union[str, int]]]) -> List[Tuple[int, int]]:
    """

    :param grid:
    :return:
    """
    exits = [(i, j) for i, row in enumerate(grid) for j, cell in enumerate(row) if cell == "X"]
    return exits


def make_step(grid: List[List[Union[str, int]]], k: int) -> List[List[Union[str, int]]]:
    """

    :param grid:
    :param k:
    :return:
    """

    rows = len(grid)
    cols = len(grid[0])

    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if val == k:
                for deltarow, deltacol in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    newrow, newcol = r + deltarow, c + deltacol
                    if 0 <= newrow < rows and 0 <= newcol < cols and grid[newrow][newcol] == 0:
                        grid[newrow][newcol] = k + 1

    return grid


def shortest_path(
    grid: List[List[Union[str, int]]], exit_coord: Tuple[int, int]
) -> Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]:
    """
    :param grid:
    :param exit_coord:
    :return:
    """
    """ищем кратчайшее расстояние от входа до выхода."""

    selected_coord, k, len_of_path = (
        exit_coord,
        grid[exit_coord[0]][exit_coord[1]],
        grid[exit_coord[0]][exit_coord[1]],
    )
    coords = [(x, y) for x, row in enumerate(grid) for y, _ in enumerate(row)]
    path = [selected_coord]

    while grid[selected_coord[0]][selected_coord[1]] != 1:
        near_to = [
            (selected_coord[0] - 1, selected_coord[1]),
            (selected_coord[0] + 1, selected_coord[1]),
            (selected_coord[0], selected_coord[1] - 1),
            (selected_coord[0], selected_coord[1] + 1),
        ]
        for x, y in near_to:
            if (x, y) in coords and grid[x][y] == int(k) - 1:
                path.append((x, y))
                selected_coord = (x, y)
                k = int(k) - 1
                break
    if len(path) != len_of_path:
        grid[selected_coord[0]][selected_coord[1]] = " "
        shortest_path(grid, exit_coord)
    return path


def encircled_exit(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> bool:
    """

    :param grid:
    :param coord:
    :return:
    """

    x, y = coord
    rows, cols = len(grid), len(grid[0])

    pass
    if (x in (0, rows - 1) and y in (0, cols - 1)) or (x - 1 == 0 and y + 1 == cols - 1):
        return True

    if x == 0 and y in range(0, cols) and grid[x + 1][y] == "■":
        return True
    if x == rows - 1 and y in range(0, cols) and grid[x - 1][y] == "■":
        return True
    if y == 0 and x in range(0, rows) and grid[x][y + 1] == "■":
        return True
    if y == cols - 1 and x in range(0, rows) and grid[x][y - 1] == "■":
        return True
    return False


def solve_maze(
    grid: List[List[Union[str, int]]],
) -> Tuple[List[List[Union[str, int]]], Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]]:
    """
    решает лабиринт, представленный в виде сетки
    """
    entry_and_exit = get_exits(grid)

    if len(entry_and_exit) == 1:
        return grid, entry_and_exit[0]

    start_point, end_point = entry_and_exit[0], entry_and_exit[1]

    if encircled_exit(grid, start_point) or encircled_exit(grid, end_point):
        return grid, None

    grid[start_point[0]][start_point[1]] = 1
    for row_index, row in enumerate(grid):
        for col_index, cell in enumerate(row):
            if cell in [" ", "X"]:
                grid[row_index][col_index] = 0

    current_step = 0
    while grid[end_point[0]][end_point[1]] == 0:
        current_step += 1
        make_step(grid, current_step)

    solution_path = shortest_path(grid, end_point)

    return grid, solution_path


def add_path_to_grid(
    grid: List[List[Union[str, int]]],
    path: Optional[Union[Tuple[int, int], List[Tuple[int, int]]]],
) -> List[List[Union[str, int]]]:
    """

    :param grid:
    :param path:
    :return:
    """

    if path:
        for i, row in enumerate(grid):
            for j, _ in enumerate(row):
                if (i, j) in path:
                    grid[i][j] = "X"
    return grid


if __name__ == "__main__":
    print(pd.DataFrame(bin_tree_maze(15, 15)))
    GRID = bin_tree_maze(15, 15)
    print(pd.DataFrame(GRID))
    _, PATH = solve_maze(GRID)
    MAZE = add_path_to_grid(GRID, PATH)
    print(pd.DataFrame(MAZE))
