import urllib
import lxml
import lxml.html


def list_recently_updated_questions():
    URL = "http://wiki.ubc.ca/Science:MER/Lists/Recent_updates"
    connection = urllib.urlopen(URL)
    dom = lxml.html.fromstring(connection.read())
    searchText = '/Science:Math_Exam_Resources/Courses/MATH'
    recentlyUpdatedQuestions = []
    for link in dom.xpath('//a/@href'):
        if searchText in link:
            # to project changes in parts of the questions onto the question
            temp = link.split("/")
            question_only = "/".join(temp[:6])
            recentlyUpdatedQuestions.append(question_only)
    return list(set(recentlyUpdatedQuestions))


def delete_recent_questions_in_meta():
    to_remove = list_recently_updated_questions()
    with open("summary_data/questions_meta.csv", "r") as f:
        lines = f.readlines()

    with open("summary_data/questions_meta.csv", "w") as f:
        for line in lines:
            q_name = line.split(',')[0].replace('http://wiki.ubc.ca', '')
            if q_name not in to_remove:
                f.write(line)


def url2questionID(url):
    ''' Returns unique questionID from UBC wiki URL.
    Hence currently only works for UBC.
    '''
    url = url.strip()
    course, exam, question = url.split('/')[-3:]
    return "UBC+%s+%s+%s" % (course, exam, question.replace("Question_", ""))

import re


def brackets_check(text):
    def check(text, brackets_counter):
        if brackets_counter < 0:
            return False
        if len(text) == 0:
            return 0 == brackets_counter
        rest = text[1:]
        if text[0] == '{':
            return check(rest, brackets_counter + 1)
        elif text[0] == '}':
            return check(rest, brackets_counter - 1)
        else:
            return check(rest, brackets_counter)
    text = text.replace('\{', '').replace('\}', '')
    text = re.sub(r'[^{}]', '', text)
    return check(text, 0)


def beginend_check(text):
    def check(text, beginend_counter):
        if beginend_counter < 0:
            return False
        if len(text) == 0:
            return 0 == beginend_counter
        rest = text[1:]
        if text[:6] == 'begin{':
            return check(rest, beginend_counter + 1)
        elif text[:4] == 'end{':
            return check(rest, beginend_counter - 1)
        else:
            return check(rest, beginend_counter)
    return check(text, 0)


def split_at_equal(text):
    def combine(text_list, acc):
        if len(text_list) == 0:
            return acc
        head = text_list[0]
        rest_list = text_list[1:]
        if brackets_check(head) and beginend_check(head):
            return combine(rest_list, acc + [head])
        combined_first = [head + '=' + rest_list[0]] + rest_list[1:]
        return combine(combined_first, acc)

    if not brackets_check(text) or not beginend_check(text):
        raise Exception("text not well formatted %s" % text)
    return combine(text.split('='), list())


def split_at_nextline(text):
    def combine(text_list, acc):
        if len(text_list) == 0:
            return acc
        head = text_list[0]
        rest_list = text_list[1:]
        if brackets_check(head) and beginend_check(head):
            return combine(rest_list, acc + [head])
        combined_first = [head + '\\\\' + rest_list[0]] + rest_list[1:]
        return combine(combined_first, acc)

    if not brackets_check(text) or not beginend_check(text):
        raise Exception("text not well formatted %s" % text)
    return combine(text.split('\\\\'), list())


def split_at_dot(text):
    def combine(text_list, acc):
        if len(text_list) == 0:
            return acc
        head = text_list[0]
        rest_list = text_list[1:]
        if brackets_check(head) and beginend_check(head):
            return combine(rest_list, acc + [head])
        combined_first = [head + '. ' + rest_list[0]] + rest_list[1:]
        return combine(combined_first, acc)

    if not brackets_check(text) or not beginend_check(text):
        raise Exception("text not well formatted %s" % text)
    return combine(text.split(' .'), list())
