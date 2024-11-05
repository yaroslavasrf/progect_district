# first_line, second_line = [int(elem) for elem in input().split()], [int(elem) for elem in input().split()]
# for i in range(10 ** 9):
#     if (first_line[0] * first_line[1] + second_line[0] * second_line[1]) <= (i * i):
#         print(i - 2)
#         break

# first_line, second_line = [int(elem) for elem in input().split()], [int(elem) for elem in input().split()]
# a = first_line[0]
# b = first_line[1]
# c = second_line[0]
# d = second_line[1]
# first = a * b
# second = c * d
# max_1 = max(first, second)
# if max_1 == first:
#     sc = min(a, b)
# else:
#     sc = min(c, d)
# min_1 = min(a, b)
# min_2 = min(c, d)
# min_3 = min(b, d)
# if (min_1 + min_2) < sc or min_3 < sc:
#     print(sc)
# elif (min_1 + min_2) >= min_3:
#     print(min_3)
# else:
#     print(min_1 + min_2)

def minimum_tunnel_crossing_time(times, fatigue):
    times.sort()
    res = return_one(fastest=fatigue)
    global total_time
    total_time = 0
    return res

def move_pair(slow, fast):
    global total_time
    total_time = 0
    total_time += max(int(slow), int(fast))
    return slow + fast, fast + fast

def return_one(fastest):
    global total_time
    total_time += fastest
    return fastest + total_time
A, B, C, D = input().split()
A, B = move_pair(A, B)
C, D = move_pair(C, D)
E = int(input())

print(minimum_tunnel_crossing_time([A, B, C, D], E))


