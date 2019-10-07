#!/usr/bin/python
# -*- coding: utf-8 -*-

#ENGLISH TO HINDI

import re
import codecs
import numpy
from django.utils.encoding import smart_str, smart_unicode

no_of_files = 1

eng_tokens = numpy.zeros(shape=(1,1))
hin_tokens = numpy.zeros(shape=(1,1))
eng_dic = {}
hin_dic = {}
hin_uni_prob = {}
count_e = 0
count_h = 0

for i in range(no_of_files):
	if i <= 8:
		filename = "Hindi_English/eng_tourism_set0" + str(i+1) + ".txt"
	else:
		filename = "Hindi_English/eng_tourism_set" + str(i+1) + ".txt"

	fo = open(filename, "rw+")
	lines = fo.readlines()
	lines = lines[1:]
	for line in lines:
		present_line = line.split('\t')
		eng_tokens = numpy.append(eng_tokens, present_line[0])
		present_line = present_line[1].split(' ')
		for word in present_line:
			word = word.split('\\')			
			eng_tokens = numpy.append(eng_tokens, word[0])
			if word[0] not in eng_dic:
				eng_dic[word[0]] = count_e
				count_e += 1

for i in range(no_of_files):
	if i <= 8:
		filename = "Hindi_English/hin_tourism_set0" + str(i+1) + ".txt"
	else:
		filename = "Hindi_English/hin_tourism_set" + str(i+1) + ".txt"

	fo = codecs.open(filename, "rw+", encoding='utf-8')
	lines = fo.readlines()
	lines = lines[1:]
	for line in lines:
		present_line = line.split('\t')
		hin_tokens = numpy.append(hin_tokens, present_line[0])
		present_line = present_line[1].split(' ')
		for word in present_line:
			word = word.split('\\')			
			hin_tokens = numpy.append(hin_tokens, word[0])
			if word[0] not in hin_dic:
				hin_dic[word[0]] = count_h
				count_h += 1

obs_prob = numpy.zeros(shape=(count_e, count_h))

reverse_dic = {}
for tkn in hin_dic:
	reverse_dic[hin_dic[tkn]] = tkn

for i in range(no_of_files):
	if i <= 8:
		filename_english = "Hindi_English/eng_tourism_set0" + str(i+1) + ".txt"
		filename_hindi = "Hindi_English/hin_tourism_set0" + str(i+1) + ".txt"
	else:
		filename_english = "Hindi_English/eng_tourism_set" + str(i+1) + ".txt"
		filename_hindi = "Hindi_English/hin_tourism_set" + str(i+1) + ".txt"

	fo_hindi = codecs.open(filename_hindi, "rw+", encoding='utf-8')
	fo_english = open(filename_english, "rw+")

	lines_english = fo_english.readlines()
	lines_hindi = fo_hindi.readlines()
	lines_english = lines_english[1:]
	lines_hindi = lines_hindi[1:]
	for i in range(len(lines_english)):
		line = lines_english[i]
		eng_line = []
		present_line = line.split('\t')
		present_line = present_line[1].split(' ')
		for word in present_line:
			word = word.split('\\')			
			eng_line.append(word[0])

		line = lines_hindi[i]
		hin_line = []
		present_line = line.split('\t')
		present_line = present_line[1].split(' ')
		for word in present_line:
			word = word.split('\\')			
			hin_line.append(word[0])

		for et in eng_line:
			for ht in hin_line:
					obs_prob[eng_dic[et]][hin_dic[ht]] += 1

for r in range(len(obs_prob)):
	total = 0
	for c in range(len(obs_prob[r])):
		total += obs_prob[r][c]
	for c in range(len(obs_prob[r])):
		obs_prob[r][c] /= total

trans_prob = {}
prev = hin_tokens[1]
for tkn in hin_tokens[2:]:
	if re.match(r'htd*', tkn):
		continue
	if re.match(r'htd*', prev):
		prev = '</s>'
	if prev not in trans_prob:
		trans_prob[prev] = {}
		trans_prob[prev][tkn] = 1
	else:
		if tkn not in trans_prob[prev]:
			trans_prob[prev][tkn] = 1
		else:
			trans_prob[prev][tkn] += 1
	prev = tkn

for tkn in hin_tokens:
	if re.match(r'htd*', tkn):
		tkn = '</s>'
	if tkn not in hin_uni_prob:
		hin_uni_prob[tkn] = 1
	else:
		hin_uni_prob[tkn] += 1

for tkn in trans_prob:
	for keys in trans_prob[tkn]:
		trans_prob[tkn][keys] /= hin_uni_prob[tkn]

#HMM Viterbi

fo = open("test.txt", "rw+")
lines = fo.readlines()
lines = lines[1:]
for line in lines:
	tokens = []
	present_line = line.split('\t')
	present_line = present_line[1].split(' ')
	for word in present_line:
		word = word.split("\\")
		tokens.append(word[0])
	beta = numpy.zeros(shape = (count_h,len(tokens)))
	si = numpy.zeros(shape = (count_h,len(tokens)))

	stop = 0
	for tkn in tokens:
		if tkn not in eng_dic:
			print "New Word"
			stop = 1
			break
	
	if stop != 1:
		for i in range(len(tokens)):
			for word in hin_dic:
				if i == 0:
					try:
						beta[hin_dic[word]][0] = obs_prob[eng_dic[tokens[i]]][hin_dic[word]] * trans_prob['</s>'][word]		#check
					except:
						beta[hin_dic[word]][0] = obs_prob[eng_dic[tokens[i]]][hin_dic[word]] * 0.000001
				else:
					max_prob = 0
					for word2 in hin_dic:
						try:
							temp = beta[hin_dic[word2]][i-1] * trans_prob[word2][word]
						except:
							temp = beta[hin_dic[word2]][i-1] * 0.000001
						if temp > max_prob:
							max_prob = temp
							max_word = word2
					beta[hin_dic[word]][i] = max_prob * obs_prob[eng_dic[tokens[i]]][hin_dic[word]]
					si[hin_dic[word]][i] = hin_dic[max_word]

	output_tokens = []
	l = len(tokens)
	
	max_beta = 0
	for word in hin_dic:
		if beta[hin_dic[word]][l - 1] > max_beta:
				max_beta = beta[hin_dic[word]][l - 1]
				max_word = word
	output_tokens.append(word)
	prev_word = reverse_dic[si[hin_dic[word]][l-1]]

	for i in range(len(tokens) - 1):
		output_tokens.append(prev_word)
		prev_word = reverse_dic[si[hin_dic[prev_word]][l-i-2]]

	for tkn in output_tokens:
		print smart_str(tkn),
#	print "Completed"
	print '\n'
