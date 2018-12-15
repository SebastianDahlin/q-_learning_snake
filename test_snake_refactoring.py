from snake_refactoring import *

def test_new_Q_matrix():
    '''Make sure that all cells of the matrix eqals -1'''
    snake = Snake(10, 10)
    matrix = snake.new_Q_matrix()
    cell_count = 0
    for row in matrix:
        for cell in row:
            assert cell == -1
            cell_count += 1
    assert cell_count == 100   