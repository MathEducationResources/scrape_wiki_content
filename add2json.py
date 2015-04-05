import os
import json
import argparse
import pandas as pd
import pypandoc
from helpers import file_loc_from_question_url
import subprocess
import numpy as np


def contributors2json(df, verbose=False):
    df_list = df.groupby(["URL", "role"])["username"].apply(
        lambda df_list: df_list.tolist())
    for num, writers in enumerate(df_list):
        url = df_list.index[num][0]
        role = df_list.index[num][1]
        location = file_loc_from_question_url(url)
        if verbose and num % 100 == 0:
            print(num, location)

        if os.path.exists(location):
            with open(location, 'r') as f:
                data = json.loads(f.read())

            if 'solver' in role:
                data['solvers'] = writers
            elif 'contributor' in role:
                data['contributors'] = writers

            with open(location, "w") as outfile:
                json.dump(data, outfile, indent=4, sort_keys=True)


def flags2json(df, verbose=False):
    for index in df.itertuples():
        location = index[6]
        if verbose and index[0] % 100 == 0:
            print(index)
        if os.path.exists(location):
            flags = list(index[2:6])

            with open(location, 'r') as f:
                data = json.loads(f.read())

            data['flags'] = flags

            with open(location, "w") as outfile:
                json.dump(data, outfile, indent=4, sort_keys=True)


def topics2json(df, verbose=False):
    df_list = df.groupby(["URL"])["topic"].apply(
        lambda df_list: df_list.tolist())
    for num, topics in enumerate(df_list):
        url = df_list.index[num]
        location = file_loc_from_question_url(url)
        if verbose and num % 100 == 0:
            print(num, location)

        if os.path.exists(location):
            with open(location, 'r') as f:
                data = json.loads(f.read())

            data['topics'] = topics

            with open(location, "w") as outfile:
                json.dump(data, outfile, indent=4, sort_keys=True)


def votes2json(df, verbose=False):
    grouped = df.groupby(["URL"])
    for url, group in grouped:
        location = file_loc_from_question_url(url)
        if verbose:
            print(location)

        ratings_5 = [(int(r) - 1) / 20 + 1 for r in group["rating"].values]
        rating = np.mean(ratings_5)
        num_votes = len(ratings_5)
        userIDs = group["userID"].values
        times = group["time"].values
        votes = zip(ratings_5, userIDs, times)
        votes = sorted(votes, key=lambda x: x[2])
        if os.path.exists(location):
            with open(location, 'r') as f:
                data = json.loads(f.read())

            data['rating'] = rating
            data['num_votes'] = num_votes
            data['votes'] = votes

            with open(location, "w") as outfile:
                json.dump(data, outfile, indent=4, sort_keys=True)


def add_html(df, verbose=False):
    def latex2html(text):
        text = pypandoc.convert(
            text, 'html', format='latex', extra_args=["--mathjax", "--ascii"])
        return text

    for num, row in df.iterrows():
        location = row.location
        if verbose and num % 100 == 0:
            print(num, location)

        if os.path.exists(location):
            with open(location, 'r') as f:
                data = json.loads(f.read())

            try:
                sols_latex = data['sols_latex']
            except KeyError:
                print(location)

            hints_latex = data['hints_latex']
            statement_latex = data['statement_latex']
            answer_latex = data['answer_latex']

            statement_html = latex2html(statement_latex)
            answer_html = latex2html(answer_latex)
            hints_html = []
            for hint_latex in hints_latex:
                hint_html = latex2html(hint_latex)
                hints_html.append(hint_html)
            sols_html = []
            for sol_latex in sols_latex:
                sol_html = latex2html(sol_latex)
                sols_html.append(sol_html)

            data['statement_html'] = statement_html
            data['hints_html'] = hints_html
            data['sols_html'] = sols_html
            data['answer_html'] = answer_html

            with open(location, "w") as outfile:
                json.dump(data, outfile, indent=4, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('Add additional info'
                                                  ' to json files'))
    parser.add_argument('--q_filter', dest='q_filter', default='/',
                        help='q_filter on course')
    parser.set_defaults(q_filter='/')

    parser.add_argument('--verbose', dest='verbose',
                        action='store_true',
                        help='print progress')
    parser.set_defaults(verbose=False)

    args = parser.parse_args()

    if args.verbose:
        print("Adding contributors")
        print("-" * 50)
    try:
        df_contr = pd.read_csv(os.path.join('summary_data',
                                            'contributors.csv'))
    except IOError:
        raise AssertionError("""Must first create contributors.csv""")
    df_contr = df_contr[df_contr.URL.str.contains(args.q_filter, regex=False)]
    contributors2json(df_contr, args.verbose)

    if args.verbose:
        print("Adding flags")
        print("-" * 50)
    try:
        df_flags = pd.read_csv(os.path.join('summary_data', 'flags.csv'))
    except IOError:
        raise AssertionError("""Must first create flags.csv""")
    df_flags = df_flags[df_flags.URL.str.contains(args.q_filter, regex=False)]
    df_flags['location'] = df_flags['URL'].apply(file_loc_from_question_url)
    flags2json(df_flags, args.verbose)

    if args.verbose:
        print("Adding topics")
        print("-" * 50)
    try:
        df_topics = pd.read_csv(os.path.join('summary_data',
                                             'questions_topic.csv'))
    except IOError:
        raise AssertionError("""Must first create questions_topic.csv""")
    df_topics = df_topics[
        df_topics.URL.str.contains(args.q_filter, regex=False)]
    topics2json(df_topics, args.verbose)

    if args.verbose:
        print("Adding votes")
        print("-" * 50)
    if not os.path.exists(os.path.join('summary_data', 'rating_pid_url.csv')):
        try:
            subprocess.check_output(
                ['cp', os.path.join('..', 'import_wiki_rating',
                                    'rating_pid_url.csv'),
                 'summary_data'])
            df_votes = pd.read_csv(os.path.join('summary_data',
                                                'rating_pid_url.csv'))
        except IOError:
            raise AssertionError("""Must have rating_pid_url.csv ready.
                                 See GitHub for corresponding partner repo.""")

    df_votes = pd.read_csv(os.path.join('summary_data',
                                        'rating_pid_url.csv'))
    df_votes = df_votes[df_votes.URL.str.contains(args.q_filter, regex=False)]
    votes2json(df_votes, args.verbose)

    if args.verbose:
        print("Adding html")
        print("-" * 50)
    add_html(df_flags, args.verbose)
