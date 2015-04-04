import argparse
import urllib
import lxml
import lxml.html
import pandas as pd
from helpers import (list_recently_updated_questions,
                     delete_recent_questions_in_meta)
import os


def write_questions_meta(verbose, write_all):
    MER_URL = 'http://wiki.ubc.ca/Science:Math_Exam_Resources'
    WHERE_TO_SAVE = os.path.join('summary_data', 'questions_meta.csv')

    def get_all_courses():
        connection = urllib.urlopen(MER_URL)
        dom = lxml.html.fromstring(connection.read())
        searchText = '/Science:Math_Exam_Resources/Courses/MATH'
        courseLinks = []
        for link in dom.xpath('//a/@href'):  # url in href for tags (are links)
            if searchText in link and len(link.split('/')) == 4:
                courseLinks.append(link)
        courseLinks = sorted(list(set(courseLinks)))
        return courseLinks

    def get_all_exams_from_course(courseURL):
        try:
            connection = urllib.urlopen(courseURL)
        except IOError:
            connection = urllib.urlopen("http://wiki.ubc.ca%s" % courseURL)
        dom = lxml.html.fromstring(connection.read())

        searchTextA = courseURL.split(':')[1] + '/April'
        searchTextD = courseURL.split(':')[1] + '/December'
        examLinks = []
        for link in dom.xpath('//a/@href'):
            if searchTextA in link or searchTextD in link:
                examLinks.append(link)
        return examLinks

    def get_all_questions_from_exam(examURL):
        connection = urllib.urlopen('http://wiki.ubc.ca' + examURL)
        dom = lxml.html.fromstring(connection.read())
        searchText = examURL.split(':')[1] + '/Question'
        questionLinks = []
        for link in dom.xpath('//a/@href'):
            if searchText in link:
                questionLinks.append(link)
        return questionLinks

    def get_meta_from_question(questionURL):
        def get_num_hs_question():
            num_hints = 1
            tryer = True
            while tryer:
                requestURL = ('http://wiki.ubc.ca' + questionURL +
                              '/Hint_' + str(num_hints))
                raw = urllib.urlopen(requestURL).read()
                if 'There is currently no text in this page' in raw:
                    tryer = False
                    num_hints = num_hints - 1
                else:
                    num_hints = num_hints + 1
            num_sols = 1
            tryer = True
            while tryer:
                requestURL = ('http://wiki.ubc.ca' + questionURL +
                              '/Solution_' + str(num_sols))
                raw = urllib.urlopen(requestURL).read()
                if 'There is currently no text in this page' in raw:
                    tryer = False
                    num_sols = num_sols - 1
                else:
                    num_sols = num_sols + 1
            return num_hints, num_sols

        def get_URL_course_exam_question():
            question_info = questionURL.split('/')
            URL = 'http://wiki.ubc.ca' + questionURL
            course = question_info[3]
            exam = question_info[4]
            question = question_info[5]
            question = question.replace('Question_0', '')
            question = question.replace('Question_', '')
            question = question.replace('_', ' ')
            return URL, course, exam, question

        URL, course, exam, question = get_URL_course_exam_question()
        num_hints, num_sols = get_num_hs_question()

        return URL, course, exam, question, num_hints, num_sols

    if write_all:
        with open(WHERE_TO_SAVE, 'w') as f:
            f.write(
                'URL,course,exam,question,num_hints,num_sols\n')

            courseURLs = get_all_courses()
            for courseURL in courseURLs:
                if verbose:
                    print(courseURL)
                examURLs = get_all_exams_from_course(courseURL)
                for exam in examURLs:
                    if verbose:
                        print(exam)
                    for q in get_all_questions_from_exam(exam):
                        f.write("%s,%s,%s,%s,%s,%s\n" %
                                get_meta_from_question(q))

    else:
        try:
            delete_recent_questions_in_meta()
            f = open(WHERE_TO_SAVE, 'a')
        except IOError:
            f = open(WHERE_TO_SAVE, 'w')
            f.write('URL,course,exam,question,num_hints,num_sols\n')
        for q in list_recently_updated_questions():
            if verbose:
                print("Updating question %s" % q)
            f.write("%s,%s,%s,%s,%s,%s\n" % get_meta_from_question(q))
        f.close()


def write_questions_topic(verbose):
    def get_all_topics():
        MER_URL = 'http://wiki.ubc.ca/Science:MER/Lists/Popular_tags'
        connection = urllib.urlopen(MER_URL)
        dom = lxml.html.fromstring(connection.read())
        searchText = 'MER_Tag_'
        topicLinks = []
        for link in dom.xpath('//a/@href'):  # url in href for tags (are links)
            if searchText in link:
                if not 'Category' in link:
                    # Fixing an error in the wiki where 'Category:' is missing
                    link = link.replace(
                        'wiki.ubc.ca/MER_Tag', 'wiki.ubc.ca/Category:MER_Tag')
                topicLinks.append(link)
        topicLinks = list(set(topicLinks))
        topicLinks.sort()
        return topicLinks

    def get_questionURLs_parent_from_topicURL(topicURL):
        topicURL = topicURL.replace('http://wiki.ubc.cahttp://wiki.ubc.ca',
                                    'http://wiki.ubc.ca')
        connection = urllib.urlopen(topicURL)
        dom = lxml.html.fromstring(connection.read())
        searchText = '/Question'
        searchParent = '/Category:MER_Parent_Tag_'
        parent = None
        questionLinks = []
        for link in dom.xpath('//a/@href'):  # url in href for tags (are links)
            if searchText in link:
                questionLinks.append(link)
            elif searchParent in link:
                parent = link.replace(searchParent, '')
        questionLinks = list(set(questionLinks))
        return questionLinks, parent

    WHERE_TO_SAVE = os.path.join('summary_data', 'questions_topic.csv')
    topics = get_all_topics()

    with open(WHERE_TO_SAVE, 'w') as f:
        f.write('parent,topic,URL\n')
        for topic in topics:
            questions, parent = get_questionURLs_parent_from_topicURL(topic)
            topic_human = topic.replace(
                'http://wiki.ubc.ca/Category:MER_Tag_', '').replace('%27', "'")
            if verbose:
                print(topic_human)
            for q in questions:
                f.write('%s,%s,%s\n' % (parent, topic_human,
                                        'http://wiki.ubc.ca' + q)
                        )


def write_exam_pdf_url(verbose):
    WHERE_TO_SAVE = os.path.join('summary_data', 'exam_pdf_url.csv')

    try:
        df = pd.read_csv(os.path.join('summary_data', 'questions_meta.csv'))
    except IOError:
        raise AssertionError("""Must first create questions_meta.csv by
                             calling this function with --meta flag""")

    url_questions = df['URL']

    url_exams_pages = list(
        set([url.split('/Question')[0] for url in url_questions]))
    url_exams_pages.sort()
    list_exam_url = []
    list_exam = []
    list_course = []
    for url in url_exams_pages:
        counter = 0
        if verbose:
            print(url)
        list_exam.append(url.split('/')[-1].strip())
        list_course.append(url.split('/')[-2].strip())

        connection = urllib.urlopen(url)
        dom = lxml.html.fromstring(connection.read())
        for link in dom.xpath('//a/@href'):
            if '.pdf' in link and counter == 0:
                list_exam_url.append(link.strip())
                counter = counter + 1

    with open(WHERE_TO_SAVE, 'w') as f:
        f.write('examURL,course,exam\n')
        for zahl in range(len(list_exam)):
            f.write('%s,%s,%s\n' %
                    (list_exam_url[zahl], list_course[zahl], list_exam[zahl]))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description='Download MER meta or topic data')
    p.add_argument('--meta', dest='meta',
                   action='store_true',
                   help='create meta file')
    p.set_defaults(meta=False)

    p.add_argument('--topic', dest='topic',
                   action='store_true',
                   help='download topic (category) data')
    p.set_defaults(topic=False)

    p.add_argument('--examURL', dest='examURL',
                   action='store_true',
                   help='make list of exam url')
    p.set_defaults(examURL=False)

    p.add_argument('--verbose', dest='verbose',
                   action='store_true',
                   help='print progress')
    p.set_defaults(verbose=False)

    p.add_argument('--write_all', dest='write_all',
                   action='store_true',
                   help='''completely write questions_meta from scratch.
                           Default: only update most recent changes.''')
    p.set_defaults(write_all=False)

    args = p.parse_args()

    if not args.meta and not args.topic and not args.examURL:
        raise Exception(
            "Must choose at least one of --meta, --topic, --examURL")
    if args.meta:
        write_questions_meta(args.verbose, args.write_all)
    if args.topic:
        write_questions_topic(args.verbose)
    if args.examURL:
        write_exam_pdf_url(args.verbose)
