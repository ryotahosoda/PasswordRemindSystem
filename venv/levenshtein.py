class Levenshtein:
    # ここで配列を立ち上げて、初期値を入れる
    def initArray(self, str1, str2):
        distance = []
        for i in range(len(str1) + 1):
            distance.append([0] * (len(str2) + 1))
            distance[i][0] = i
        for j in range(len(str2) + 1):
            distance[0][j] = j
        return distance

    # セルに値を入れる
    def editDist(self, str1, str2, distance):
        dist = [0] * 3
        for i in range(1, len(str1) + 1):
            for j in range(1, len(str2) + 1):
                dist[0] = distance[i - 1][j - 1] if str1[i - 1] == str2[j - 1] else distance[i - 1][j - 1] + 1
                dist[1] = distance[i][j - 1] + 1
                dist[2] = distance[i - 1][j] + 1
                distance[i][j] = min(dist)
        return distance[i][j]

    def __init__(self, str1: object, str2: object) -> object:
        self.str1 = str1
        self.str2 = str2
        Levenshtein.distance = self.initArray(str1, str2)
        Levenshtein.dist = self.editDist(str1, str2, Levenshtein.distance)


if __name__ == '__main__':
    str1 = 'w-V2sv8BhP4J'
    str2 = 'w-'
    l = Levenshtein(str1, str2)

    print(l.dist)
