from math import sqrt

from save_data import words
from collections import OrderedDict


def standard_deviation(arr):
    arithmetic_mean = 0.0
    for i in arr:
        arithmetic_mean += arr[i]
    arithmetic_mean /= len(arr)
    deviation = 0.0
    for i in arr:
        deviation += (arr[i] - arithmetic_mean) ** 2
    return sqrt(deviation / len(arr)), arithmetic_mean


def get_arr(id):
    words_cnt = dict()
    for word in words[id]:
        if word in words_cnt:
            words_cnt[word] += 1
        else:
            words_cnt[word] = 1
    deviation, mean = standard_deviation(words_cnt)
    deviation *= 3
    words_cnt_list = list()
    for word in words_cnt:
        words_cnt_list.append([words_cnt[word], word])
    words_cnt_list = sorted(words_cnt_list)
    return words_cnt_list, deviation, mean


def top(id, n, asc):
    words_cnt_list, deviation, mean = get_arr(id)
    if asc == True:
        words_cnt_list = reversed(words_cnt_list)
    cnt = int(n)
    outlier = list()
    for word in words_cnt_list:
        if abs(word[0] - mean) < deviation and cnt > 0:
            outlier.append(word[1])
            cnt -= 1
    return outlier


def stop_words(id):
    words_cnt_list, deviation, mean = get_arr(id)
    outlier = list()
    for word in words_cnt_list:
        if abs(word[0] - mean) >= deviation:
            outlier.append(word[1])
    return outlier


def describe(id):
    size_words = OrderedDict()
    for word in words[id]:
        if len(word) in size_words:
            size_words[len(word)] += 1
        else:
            size_words[len(word)] = 1
    length = list()
    for cnt in size_words:
        length.append([int(cnt), int(size_words[cnt])])
    length = sorted(length)

    words_cnt = OrderedDict()
    size_cnt = OrderedDict()
    for word in words[id]:
        if word in words_cnt:
            words_cnt[word] += 1
        else:
            words_cnt[word] = 1
    for i in words_cnt:
        if words_cnt[i] in size_cnt:
            size_cnt[words_cnt[i]] += 1
        else:
            size_cnt[words_cnt[i]] = 1
    inclusion = list()
    for cnt in size_cnt:
        inclusion.append([int(cnt), int(size_cnt[cnt])])
    inclusion = sorted(inclusion)
    return inclusion, length


def describe_word(id, WORD):
    words_cnt = dict()
    for word in words[id]:
        if word in words_cnt:
            words_cnt[word] += 1
        else:
            words_cnt[word] = 1
    cnt = 0
    if WORD not in words[id]:
        return -1, -1
    for word in words[id]:
        if words_cnt[word] < words_cnt[WORD]:
            cnt += 1

    return words_cnt[WORD], cnt
