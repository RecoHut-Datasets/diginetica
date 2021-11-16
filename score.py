#!/usr/bin/env python

# Program substituting itself to the scoring program to test python configuration
# Isabelle Guyon, ChaLearn, September 2014

# ALL INFORMATION, SOFTWARE, DOCUMENTATION, AND DATA ARE PROVIDED "AS-IS". 
# ISABELLE GUYON, CHALEARN, AND/OR OTHER ORGANIZERS OR CODE AUTHORS DISCLAIM
# ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR ANY PARTICULAR PURPOSE, AND THE
# WARRANTY OF NON-INFRINGEMENT OF ANY THIRD PARTY'S INTELLECTUAL PROPERTY RIGHTS. 
# IN NO EVENT SHALL ISABELLE GUYON AND/OR OTHER ORGANIZERS BE LIABLE FOR ANY SPECIAL, 
# INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF SOFTWARE, DOCUMENTS, MATERIALS, 
# PUBLICATIONS, OR INFORMATION MADE AVAILABLE FOR THE CHALLENGE.
import json
import os
from sys import argv
import data_io
from glob import glob
from numpy import genfromtxt, log, log2
import yaml

if (os.name == "nt"):
	filesep = '\\'
else:
	filesep = '/'

if __name__ == "__main__":

	input_dir = argv[1]
	output_dir = argv[2]

	score_file = open(os.path.join(output_dir, 'scores.txt'), 'wb')

	try:
		# Compute "real scores"
		# Get all the solution files from the solution directory
		solution_name = os.path.join(input_dir, 'ref', 'valid.solution.csv')
		submission_name = os.path.join(input_dir, 'res', 'submission.txt')
		
		with open(solution_name, 'rb') as real_answer, \
				open(submission_name, 'rb') as submission:
			answer_lines, sub_lines = iter(real_answer), iter(submission)
			current_ans = next(answer_lines)  # skip column names
			# Setting up NDCG sum variables and counters
			NDCG_search = 0.0
			NDCG_category = 0.0
			counter_search = 0.0
			counter_category = 0.0
			current_search = True
			skipped_lines = 0
			while True:
				try:
					current_ans = next(answer_lines)
					current_sub = next(sub_lines)
					current_ans_split = current_ans.split(';')
					current_sub_split = current_sub.split(' ')

					# print(current_ans_split[1])
					# id mismatch check
					while current_ans_split[1] != current_sub_split[0]:

						if int(current_ans_split[1]) < int(current_sub_split[0]):
							print("Missing query: ", current_sub_split[1])
							raise Exception()
							# current_ans = next(answer_lines)
						else:
							skipped_lines += 1
							# print("Extra query: ", current_ans_split[1])
							# raise Exception()
							current_sub = next(sub_lines)

						# current_ans_split = current_ans.split(';')
						current_sub_split = current_sub.split(' ')

					# Increase counters
					current_search = (current_ans_split[3] == "TRUE")
					if current_search:
						counter_search += 1
					else:
						counter_category += 1

				except StopIteration:
					answer = next(answer_lines, None)
					if answer is not None:
						print("Submission file not complete!")
						raise Exception()
					break

				scores_raw_string = current_ans_split[4].replace('""', '"')
				if scores_raw_string[-1] == '\n':
					scores_raw_string = scores_raw_string[:-1]
				scores_raw_string = scores_raw_string[1:-1]  # remove quotes
				ans_json = json.loads(scores_raw_string)
				sub_items = current_sub_split[1].replace("\n", "").split(',')

				dcg = 0.
				counted_items = {}
				for i, sub_item in enumerate(sub_items):
					if sub_item not in counted_items:
						counted_items[sub_item] = True # count only first entry of item per query in submission
						dcg += ((2. ** ans_json.get(sub_item, 0)) - 1.) / log2(i + 2.)

				idcg_raw = current_ans_split[5].replace(',', '.')
				idcg = float(idcg_raw)

				if current_search:
					NDCG_search += dcg / idcg
				else:
					NDCG_category += dcg / idcg
			NDCG_search = NDCG_search / counter_search
			NDCG_category = NDCG_category / counter_category
			NDCG_total = NDCG_category * 0.8 + NDCG_search * 0.2
			score_file.write("search_NDCG: %0.6f\n" % NDCG_search)
			score_file.write("category_NDCG: %0.6f\n" % NDCG_category)
			score_file.write("avg_NDCG: %0.6f\n" % NDCG_total)
	except:
		score_file.write("search_NDCG: 0\n")
		score_file.write("category_NDCG: 0\n")
		score_file.write("avg_NDCG: 0\n")
		print('Something went wrong, e.g. the submission file name is not correct or the file format is not correct. Please, see the "Evaluation" for details.')

	score_file.close()

	# Lots of debug stuff
	data_io.show_io(input_dir, output_dir)
	data_io.show_version()
	
	# Example html file
	with open(os.path.join(output_dir, 'scores.html'), 'wb') as html_file:
		html_file.write("<h1>Example HTML file</h1>\nThis shows that we can also have an html file to show extra data.")
		
	exit(0)
