from typing import Tuple, List

dict = {'m': 'match', 'i': 'insertion', 'd': 'deletion', 'r': 'replacement'}


def validation_argv() -> None:
    if len(argv) < 3:
        exit('Less arguments...\n' + 'should $' + argv[0] + ' "text1" "text2"')
    for index in range(1, 2):
        if type(argv[index]) is not str:
            exit('Argument must be string')


def initialize_table(word1: str, word2: str) -> List[List[Tuple[int, int, int]]]:
    # (スコア, 遷移前の座標x(row), 遷移前の座標y(column))
    table = [[(0, 0, 0)] * (len(word1) + 1) for i in range(len(word2) + 1)]

    for column in range(1, len(table[0])):
        table[0][column] = table[0][column - 1][0] + 7, 0, column - 1
    for row in range(1, len(table)):
        table[row][0] = table[row - 1][0][0] + 7, row - 1, 0
    return table


def calculate_cost(table: List[List[Tuple[int, int, int]]], word1: str, word2: str) -> List[List[Tuple[int, int, int]]]:
    for row in range(1, len(table)):
        for column in range(1, len(table[0])):
            if word1[column - 1] == word2[row - 1]:
                table[row][column] = table[row - 1][column - 1][0], row - 1, column - 1
            else:
                up_left = (table[row - 1][column - 1][0] + 10, row - 1, column - 1)
                left = (table[row][column - 1][0] + 7, row, column - 1)
                up = (table[row - 1][column][0] + 7, row - 1, column)
                table[row][column] = sorted([up_left, left, up], key=lambda x: x[0])[0]
    return table


def print_table(table: List[List[Tuple[int, int, int]]]) -> None:
    for row in table:
        print(row)


def judge_result(table: List[List[Tuple[int, int, int]]], word1: str, word2: str) -> List[Tuple[str, str]]:
    results = []
    follow = (len(word2), len(word1))
    while follow != (0, 0):
        point = table[follow[0]][follow[1]]
        route = (point[1], point[2])

        if follow[0] == route[0]:
            results.append(([word1[route[1]]], 'd'))
        elif follow[1] == route[1]:
            results.append(([word2[route[0]]], 'i'))
        elif table[route[0]][route[1]][0] == point[0]:
            results.append(([word1[route[1]]], 'm'))
        else:
            results.append(([word1[route[1]], word2[route[0]]], 'r'))
        follow = route
    results.reverse()
    return results


def print_results(results: List[Tuple[str, str]]) -> None:
    for result in results:
        print(result[0], ': ', dict[result[1]])


if __name__ == '__main__':
    word1, word2 = "2bSc8JT)*3v","2bScJ8T)3*Xm"

    table = initialize_table(word1, word2)

    calculated_table = calculate_cost(table, word1, word2)
    # print_table(calculated_table)

    results = judge_result(calculated_table, word1, word2)
    print_results(results)