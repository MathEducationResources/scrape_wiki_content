import argparse
import urllib
import lxml
import lxml.html
import pandas as pd
from helpers import (list_recently_updated_questions,
                     delete_recent_questions_in_csv,
                     sort_my_csv)
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
            delete_recent_questions_in_csv(WHERE_TO_SAVE)
            f = open(WHERE_TO_SAVE, 'a')
        except IOError:
            f = open(WHERE_TO_SAVE, 'w')
            f.write('URL,course,exam,question,num_hints,num_sols\n')
        for q in list_recently_updated_questions():
            if verbose:
                print("Updating question %s" % q)
            f.write("%s,%s,%s,%s,%s,%s\n" % get_meta_from_question(q))
        f.close()
        sort_my_csv(WHERE_TO_SAVE)


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


def write_contributors_and_flags(verbose, write_all):
    try:
        df = pd.read_csv(os.path.join('summary_data', 'questions_meta.csv'))
    except IOError:
        raise AssertionError("""Must first create questions_meta.csv by
                             calling this function with --meta flag""")

    # Contributors
    WHERE_TO_SAVE_C = os.path.join('summary_data', 'contributors.csv')

    def info2urls(question_url, num_hints, num_sols):
        ''' Creates list of all urls to check when looking for contributors '''
        urls = []
        question_url = question_url.replace(
            'http://wiki.ubc.ca/', 'http://wiki.ubc.ca/index.php?title=')
        urls.append(question_url + '&action=history')
        urls.append(question_url + '/Statement&action=history')
        for num in range(num_hints):
            url = question_url + '/Hint_%s&action=history' % (num + 1)
            urls.append(url)
        for num in range(num_sols):
            url = question_url + '/Solution_%s&action=history' % (num + 1)
            urls.append(url)
        return urls

    def urls2writer_list(url_s):
        def url2writers(url):
            connection = urllib.urlopen(url)
            dom = connection.read()
            writers = []
            for text in dom.split('title="User:')[1:]:
                writer = text.split(' ')[0]
                writer = writer.replace('"', '')
                writers.append(writer)
            return writers

        sol_writers = []
        writerlist = []
        for url in urls:
            writers = url2writers(url)
            if 'Solution' in url:
                sol_writers.append(writers[-1])
            writerlist += writers
        writerlist = list(set(writerlist))
        for sol_writer in sol_writers:
            if sol_writer in writerlist:
                writerlist.remove(sol_writer)
        return writerlist, sol_writers

    def write_contributors(writer_list, sol_writers, question_url, f):
        for num, sol_writer in enumerate(sol_writers):
            f.write('%s,solver_%s,%s\n' %
                    (question_url, str(num + 1), sol_writer))
        for writer in writer_list:
            f.write('%s,contributor,%s\n' % (question_url, writer))

    if write_all:
        with open(WHERE_TO_SAVE_C, 'w') as f:
            f.write('URL,role,username\n')
            for index, row in df.iterrows():
                question_url = row.URL
                num_hints = row.num_hints
                num_sols = row.num_sols
                urls = info2urls(question_url, num_hints, num_sols)
                writer_list, sol_writers = urls2writer_list(urls)
                write_contributors(writer_list, sol_writers, question_url, f)
    else:
        try:
            delete_recent_questions_in_csv(WHERE_TO_SAVE_C)
            f = open(WHERE_TO_SAVE_C, 'a')
        except IOError:
            f = open(WHERE_TO_SAVE_C, 'w')
            f.write('URL,role,username\n')
        for q in list_recently_updated_questions():
            if verbose:
                print("Updating question %s" % q)

            row = df[df.URL.str.contains(q, regex=False)]
            if len(row.index) == 0:
                print("""WARNING: Missing entry for %s.
                      You might want to update questions_meta.csv""" % q)
                continue
            if len(row.index) > 1:
                print("WARNING: Duplicate entry for %s" % q)
            question_url = row.URL.values[0]
            num_hints = row.num_hints.values[0]
            num_sols = row.num_sols.values[0]
            urls = info2urls(question_url, num_hints, num_sols)
            writer_list, sol_writers = urls2writer_list(urls)
            write_contributors(writer_list, sol_writers, question_url, f)
        f.close()
        sort_my_csv(WHERE_TO_SAVE_C)

    # Flags
    WHERE_TO_SAVE_F = os.path.join('summary_data', 'flags.csv')

    def url2flags(url):
        connection = urllib.urlopen(url)
        dom = connection.read()
        flags = []
        for text in dom.split('[[Category:MER ')[1:]:
            flags.append(text.split(' flag]]')[0])
        return flags

    if write_all:
        with open(WHERE_TO_SAVE_F, 'w') as g:
            g.write('URL,question_flag,hint_flag,solution_flag,tag_flag\n')
            for index, row in df.iterrows():
                question_url = row.URL
                url = question_url.replace(
                    'http://wiki.ubc.ca/',
                    'http://wiki.ubc.ca/index.php?title=') + '&action=edit'
                flags = url2flags(url)

                if len(flags) > 4:
                    print('Question with more than 4 flags:',
                          question_url, flags)

                g.write('%s,%s,%s,%s,%s\n' %
                        (question_url, flags[0], flags[1], flags[2], flags[3]))
    else:
        try:
            delete_recent_questions_in_csv(WHERE_TO_SAVE_F)
            g = open(WHERE_TO_SAVE_F, 'a')
        except IOError:
            g = open(WHERE_TO_SAVE_F, 'w')
            g.write('URL,question_flag,hint_flag,solution_flag,tag_flag\n')
        for q in list_recently_updated_questions():
            if verbose:
                print("Updating question %s" % q)

            row = df[df.URL.str.contains(q, regex=False)]
            if len(row.index) == 0:
                print("""WARNING: Missing entry for %s.
                      You might want to update questions_meta.csv""" % q)
                continue
            if len(row.index) > 1:
                print("WARNING: Duplicate entry for %s" % q)
            question_url = row.URL.values[0]
            url = question_url.replace(
                'http://wiki.ubc.ca/',
                'http://wiki.ubc.ca/index.php?title=') + '&action=edit'
            flags = url2flags(url)
            if len(flags) > 4:
                print('Question with more than 4 flags:',
                      question_url, flags)

            g.write('%s,%s,%s,%s,%s\n' %
                    (question_url, flags[0], flags[1], flags[2], flags[3]))
        g.close()
        sort_my_csv(WHERE_TO_SAVE_F)


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

    p.add_argument('--contributors_flags', dest='contributors_flags',
                   action='store_true',
                   help='write list of contributors and write list of flags')
    p.set_defaults(contributors_flags=False)

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

    if (not args.meta
            and not args.topic
            and not args.examURL
            and not args.contributors_flags):
        raise Exception(
            '''Must choose at least one of --meta, --topic,
               --examURL, --contributors_flags''')
    if args.meta:
        write_questions_meta(args.verbose, args.write_all)
    if args.topic:
        write_questions_topic(args.verbose)
    if args.examURL:
        write_exam_pdf_url(args.verbose)
    if args.contributors_flags:
        write_contributors_and_flags(args.verbose, args.write_all)
