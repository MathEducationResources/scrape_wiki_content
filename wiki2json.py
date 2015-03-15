import pandas as pd
import os
import argparse
import urllib
import lxml
import lxml.html
import json
import re
import subprocess
import warnings
from helpers import list_recently_updated_questions, url2questionID


def handleImages(state_or_hint_or_sol, where_to_save):

    def save_image(imageName, directory):
        imageFileURL = "http://wiki.ubc.ca/File:" + imageName
        connection = urllib.urlopen(imageFileURL)
        dom = lxml.html.fromstring(connection.read())
        for link in dom.xpath('//a/@href'):
            if '//wiki.ubc.ca/images' in link:
                raw_image_url = link
                break
        if not os.path.exists(directory):
            os.makedirs(directory)

        urllib.urlretrieve(
            "http:" + raw_image_url, os.path.join(
                directory, imageName.replace('\xe2\x80\x8e', '')))

    def handle_gif(imageName, directory):
        newName = imageName.replace('.gif', '.png')
        fullOldName = os.path.join(directory, imageName)
        fullNewName = os.path.join(directory, newName)
        subprocess.check_output(["convert", fullOldName, fullNewName])
        os.remove(fullOldName)
        return newName

    directory = where_to_save.split('/Question')[0]
    # images are either referenced by "File:"" or "Image:"
    # print state_or_hint_or_sol
    image_list = re.findall(r"File:(.*?)]]", state_or_hint_or_sol)
    file_list = re.findall(r"Image:(.*?)]]", state_or_hint_or_sol)

    image_list = image_list + file_list
    image_list = [i.split('|')[0].strip().replace(' ', '_')
                  for i in image_list]

    for imageName in image_list:
        save_image(imageName, directory)
        if '.gif' in imageName:
            imageName = handle_gif(imageName, directory)


def get_dict_action_urls(url, state_or_hint_or_sol):
    URL = (url.replace("Science", "index.php?title=Science") +
           "/" + state_or_hint_or_sol + "&action=edit")
    return URL


def file_loc_from_question_url(url):
    course, exam, q_name = url.split('/')[5:8]
    file_loc = os.path.join('json_data', course, exam, q_name + '.json')
    return file_loc


def grab_raw(df):
    def get_content(url, state_or_hint_or_sol):
        requestURL = get_dict_action_urls(url, state_or_hint_or_sol)
        raw = urllib.urlopen(requestURL).read()
        try:
            return raw.split('name="wpTextbox1">')[1].split('</textarea')[0]
        except IndexError:
            warnings.warn('There is a problem with %s. Maybe no content?'
                          % url)
            return 'No content found'

    for index, row in df.iterrows():
        course = row.course
        year = int(row.exam[-4:])
        term = row.exam[:-5]
        url = row.URL
        num_hints = row.num_hints
        num_sols = row.num_sols
        loc = row.location
        question = row.question
        statement_raw = get_content(url, 'Statement')
        statement_raw = statement_raw.strip()
        handleImages(statement_raw, loc)
        hints_raw = []
        if num_hints == 1:
            hint = get_content(url, 'Hint_1')
            handleImages(hint, loc)
            hints_raw.append(hint)
        elif num_hints > 1:
            for i in range(num_hints):
                hint = get_content(
                    url, 'Hint_%s' % (i + 1))
                handleImages(hint, loc)
                hints_raw.append(hint)
        else:
            hints_raw.append('No content found.')
        hints_raw = [h.strip() for h in hints_raw]

        solutions_raw = []
        if num_sols == 1:
            sol = get_content(url, 'Solution_1')
            handleImages(sol, loc)
            solutions_raw.append(sol)
        elif num_sols > 1:
            for i in range(num_sols):
                sol = get_content(
                    url, 'Solution_%s' % (i + 1))
                handleImages(sol, loc)
                solutions_raw.append(sol)
        else:
            solutions_raw.append('No content found.')
        solutions_raw = [s.strip() for s in solutions_raw]

        question_json = {"course": course,
                         "year": int(year),
                         "term": term,
                         "url": url,
                         "statement_raw": statement_raw,
                         "hints_raw": hints_raw,
                         "sols_raw": solutions_raw,
                         "question": question,
                         "ID": url2questionID(url)
                         }

        where_to_save = loc

        if not os.path.exists(where_to_save.split('/Question')[0]):
            os.makedirs(where_to_save.split('/Question')[0])
        with open(where_to_save, "w") as outfile:
            json.dump(question_json, outfile, indent=4, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('MER topic or exam to json'
                                                  ' with the option to compile'
                                                  ' to LaTeX'))
    parser.add_argument('--q_filter', dest='q_filter', default='/',
                        help='q_filter on course')
    parser.set_defaults(q_filter='/')

    parser.add_argument('--write_all', dest='write_all', action='store_true',
                        help='''Completely re-write all question content.
                             Default: only update most recent changes.''')
    parser.set_defaults(write_all=False)

    args = parser.parse_args()

    if not os.path.exists('summary_data/questions_meta.csv'):
        raise Exception('Require summary_data/questions_meta.csv')

    df = pd.read_csv('summary_data/questions_meta.csv')
    if args.q_filter == '/':
        if args.write_all:
            courses = df.groupby('course').groups.keys()
            print(
                'No filter specified. Updating following courses in parallel.')
            print(sorted(courses))
            subprocess.check_output(['parallel', 'python', 'wiki2json.py',
                                     '--q_filter', ':::'] + courses)
        else:
            recent_changes = list_recently_updated_questions()
            subprocess.check_output(['parallel', 'python', 'wiki2json.py',
                                     '--q_filter', ':::'] + recent_changes)

    else:
        df = df[df.URL.str.contains(args.q_filter, regex=False)]
        df['location'] = df['URL'].apply(file_loc_from_question_url)
        grab_raw(df)
