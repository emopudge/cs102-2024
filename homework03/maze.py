from copy import deepcopy
from random import choice, randint
from typing import List, Optional, Tuple, Union

import pandas as pd


def create_grid(rows: int = 15, cols: int = 15) -> List[List[Union[str, int]]]:
    return [["■"] * cols for _ in range(rows)]


def remove_wall(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> List[List[Union[str, int]]]:
    """Removes a wall from a grid at the specified coordinates.  Assumes integers are walls."""
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    if not (0 <= coord[0] < rows and 0 <= coord[1] < cols):
        return grid

    new_grid = [row[:] for row in grid]  # Deep copy

    if (coord[0] % 2 == 1) and (coord[1] % 2 == 1):
        new_grid[coord[0]][coord[1]] = ""  # Replace with empty string regardless of original type

    return new_grid


def remove_wall_pretty(mas):
    """
    выдает лабиринт с дырками не по координатам, а готовеньким
    """
    for i in range(len(mas)):
        for j in range(len(mas[i])):
            mas = remove_wall(mas, [i, j])
    return mas


def rand_enter(grid):
    """
    выбираем рандомные координаты для входа и выхода
    """
    r = randint(1, 4)
    if r == 1:
        k = randint(1, len(grid) - 2)
        grid[0][k] = "X"
    elif r == 2:
        k = randint(1, len(grid) - 2)
        grid[len(grid) - 1][k] = "X"
    elif r == 3:
        k = randint(1, len(grid) - 2)
        grid[k][0] = "X"
    elif r == 4:
        k = randint(1, len(grid) - 2)
        grid[k][len(grid) - 1] = "X"
    return grid


def rand_enter_double(grid):
    return rand_enter(rand_enter(grid))


def bin_tree_maze(rows: int = 15, cols: int = 15, random_exit: bool = True) -> List[List[Union[str, int]]]:
    """

    :param rows:
    :param cols:
    :param random_exit:
    :return:
    """

    grid = rand_enter_double(remove_wall_pretty(create_grid(rows, cols)))

    # 1. выбрать любую клетку
    # 2. выбрать направление: наверх или направо.
    # Если в выбранном направлении следующая клетка лежит за границами поля,
    # выбрать второе возможное направление
    # 3. перейти в следующую клетку, сносим между клетками стену
    # 4. повторять 2-3 до тех пор, пока не будут пройдены все клетки

    # генерация входа и выхода
    if random_exit:
        for coord in get_exits(grid):
            if coord[0] == 0:
                grid[1][coord[1]] = ""
            elif coord[0] == len(grid) - 1:
                grid[len(grid) - 2][coord[1]] = ""
            elif coord[1] == 0:
                grid[coord[0]][1] = ""
            elif coord[1] == len(grid) - 1:
                grid[coord[0]][len(grid) - 2] = ""
            for i, row in enumerate(grid):
                for j, value in enumerate(row):
                    if value == "":
                        direction = choice(["up", "right"])
                        if direction == "up":
                            if grid[i - 1][j] and i - 1 > 0:
                                grid[i - 1][j] = ""
                            else:
                                direction = "right"
                        else:
                            if grid[i][j + 1] and j + 1 < len(grid) - 1:
                                grid[i][j + 1] = ""
    else:
        pass
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
    """ищем кратчайшее расстояние от входа до выхода."""

    x_out, y_out = exit_coord

    try:
        while grid[x_out][y_out] == 0 or isinstance(grid[x_out][y_out], str):  
            return None 

    except IndexError:
        return None  

    path = [exit_coord]
    x, y = exit_coord
    try:
        k = int(grid[x][y])  
    except (ValueError, IndexError):
        return None  
    while k > 1:
        found_next = False
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            try:
                if (
                    0 <= nx < len(grid)
                    and 0 <= ny < len(grid[0])
                    and isinstance(grid[nx][ny], int)
                    and grid[nx][ny] == k - 1
                ):
                    x, y = nx, ny
                    path.append((x, y))
                    k -= 1
                    found_next = True
                    break
            except IndexError:
                pass  

        if not found_next:
            return None  # путь не найден

    return path[::-1]


def encircled_exit(grid: List[List[Union[str, int]]], coord: Tuple[int, int]) -> bool:
    """

    :param grid:
    :param coord:
    :return:
    """

    rows = len(grid)
    cols = len(grid[0])
    x, y = coord

    if x == 0 or x == rows - 1 or y == 0 or y == cols - 1:
        return False

    if grid[x - 1][y] == "■" and grid[x + 1][y] == "■" and grid[x][y - 1] == "■" and grid[x][y + 1] == "■":
        return True
    else:
        return False


def solve_maze(
    grid: List[List[Union[str, int]]],
) -> Tuple[List[List[Union[str, int]]], Optional[Union[Tuple[int, int], List[Tuple[int, int]]]]]:
    """

    :param grid:
    :return:
    """

    exits = get_exits(grid)
    if not exits:
        return grid, None  # не найдено выходов

    if len(exits) == 1:
        return grid, exits  # только вход

    # несколько выходов. прокладываем путь от одного до другого
    new_grid = deepcopy(grid)
    new_grid[exits[0][0]][exits[0][1]] = 1  # блокируем один выход
    if not encircled_exit(grid, exits[1]):
        path = shortest_path(new_grid, exits[1])
        if path:
            return new_grid, path

    return grid, None


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
