import argparse
import os
import pandas as pd
import json
import subprocess
import glob
import sys


def file_loc_from_question_url(url):
    course, exam, q_name = url.split('/')[5:8]
    file_loc = os.path.join('json_data', course, exam, q_name + '.json')
    return file_loc


def make_question_title(question, term, year, url):
    if term == '':
        question_title = 'Question ' + question
        question_title = '\\href{' + url + '}{' + question_title + '}'
    else:
        question_title = term + ' ' + \
            str(year) + ' - ' + 'Question ' + question
        question_title = '\\href{' + url + '}{' + question_title + '}'
    return question_title


def write_hints_content(hints_latex, question_title, f_h, rating):
    if 'on' in rating:
        f_h.write('\MERQuestionTitle{' + question_title + '}')
    else:
        f_h.write('\MERQuestionTitle[' + rating + ']{' + question_title + '}')
    for num, hint in enumerate(hints_latex):
        if len(hints_latex) == 1:
            f_h.write('\\begin{MERHint}{}\n')
        else:
            f_h.write('\\begin{MERHint}{ %s}\n' % (num + 1))
        f_h.write(hint)
        f_h.write('\n\\end{MERHint}\n')


def write_sols_content(sols_latex, question_title, f_s, rating):
    if 'on' in rating:
        f_s.write('\MERQuestionTitle{' + question_title + '}')
    else:
        f_s.write('\MERQuestionTitle[' + rating + ']{' + question_title + '}')
    for num, sol in enumerate(sols_latex):
        if len(sols_latex) == 1:
            f_s.write('\\begin{MERSolution}{}\n')
        else:
            f_s.write('\\begin{MERSolution}{ %s}\n' % (num + 1))
        try:
            f_s.write(sol)
        except UnicodeEncodeError:
            print('unicode error in %s\n%s' % (question_title, sols_latex))
            f_s.write('Solution not found, please notify the MER wiki team.')
        f_s.write('\n\\end{MERSolution}\n')


def write_answers_content(answers_latex, question_title, f_a, rating):
    if 'on' in rating:
        f_a.write('\MERQuestionTitle{' + question_title + '}')
    else:
        f_a.write('\MERQuestionTitle[' + rating + ']{' + question_title + '}')
    f_a.write('\\begin{MERAnswer}\n')
    f_a.write(answers_latex)
    f_a.write('\n\\end{MERAnswer}\n')


def write_content(df, exam):
    where_to_save_h = 'latex_help_files/h_content.tex'
    f_h = open(where_to_save_h, 'w')
    where_to_save_s = 'latex_help_files/s_content.tex'
    f_s = open(where_to_save_s, 'w')
    where_to_save_a = 'latex_help_files/a_content.tex'
    f_a = open(where_to_save_a, 'w')

    for index, row in df.iterrows():
        loc = row.location
        question = row.question
        url = row.URL
        try:
            rating = row.rating
        except AttributeError:
            rating = 'None'

        fd = open(loc, 'r')
        data = json.loads(fd.read())
        fd.close()
        # statement_latex = data['statement_latex']
        hints_latex = data['hints_latex']
        sols_latex = data['sols_latex']
        answers_latex = data['answer_latex']

        if exam == '':
            term = data['term']
            year = data['year']
        else:
            term = ''
            year = ''
        question_title = make_question_title(question, term, year, url)

        write_hints_content(hints_latex, question_title, f_h, rating)
        f_h.write('\n')
        write_sols_content(sols_latex, question_title, f_s, rating)
        f_s.write('\n')
        write_answers_content(answers_latex, question_title, f_a, rating)
        f_a.write('\n')

    f_h.close()
    f_s.close()
    f_a.close()


def write_h_latex(course, exam):
    h_latex = open('latex_help_files/MERHints.tex', 'w')
    h_latex.write('\\input{header}\n')
    course = '\\newcommand{\\course}{' + course.strip() + ' }\n'
    h_latex.write(course)
    exam = '\\newcommand{\\exam}{' + exam.strip() + ' }\n'
    h_latex.write(exam)
    h_latex.write('\\input{h_layout}\n')
    h_latex.write('\\begin{document}\n')
    h_latex.write('\\input{h_title}\n')
    h_latex.write('\\input{h_content}\n')
    h_latex.write('\\end{document}')
    h_latex.close()


def write_s_latex(course, exam, examURL):
    s_latex = open('latex_help_files/MERSolutions.tex', 'w')
    s_latex.write('\\input{header}\n')
    course = '\\newcommand{\\course}{' + course.strip() + ' }\n'
    s_latex.write(course)
    exam = '\\newcommand{\\exam}{' + exam.strip() + ' }\n'
    s_latex.write(exam)
    examURL = '\\newcommand{\\examURL}{' + examURL.strip() + ' }\n'
    s_latex.write(examURL)
    s_latex.write('\\input{s_layout}\n')
    s_latex.write('\\begin{document}\n')
    s_latex.write('\\input{s_title}\n')
    s_latex.write('\\input{s_content}\n')
    s_latex.write('\\section*{Good Luck for your exams!}')
    s_latex.write('\\end{document}')
    s_latex.close()


def write_a_latex(course, exam, examURL):
    a_latex = open('latex_help_files/MERAnswers.tex', 'w')
    a_latex.write('\\input{header}\n')
    course = '\\newcommand{\\course}{' + course.strip() + ' }\n'
    a_latex.write(course)
    exam = '\\newcommand{\\exam}{' + exam.strip() + ' }\n'
    a_latex.write(exam)
    examURL = '\\newcommand{\\examURL}{' + examURL.strip() + ' }\n'
    a_latex.write(examURL)
    a_latex.write('\\input{a_layout}\n')
    a_latex.write('\\begin{document}\n')
    a_latex.write('\\input{a_title}\n')
    a_latex.write('\\input{a_content}\n')
    a_latex.write('\\end{document}')
    a_latex.close()


def write_ha_latex(course, exam):
    ha_latex = open('latex_help_files/MERHintsAnswer.tex', 'w')
    ha_latex.write('\\input{header}\n')
    course = '\\newcommand{\\course}{' + course.strip() + ' }\n'
    ha_latex.write(course)
    exam = '\\newcommand{\\exam}{' + exam.strip() + ' }\n'
    ha_latex.write(exam)
    ha_latex.write('\\input{ha_layout}\n')
    ha_latex.write('\\begin{document}\n')
    ha_latex.write('\\input{ha_title}\n\n')
    ha_latex.write('\\section{Hints}\n')
    ha_latex.write('\\input{h_content}\n')
    ha_latex.write('\\section{Final answers}\n')
    ha_latex.write('\\input{a_content}\n')
    ha_latex.write('\\section*{Good Luck with your exams!}\n')
    ha_latex.write('\\end{document}')
    ha_latex.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=('MER topic or exam to json'
                     ' with the option to write out to pdf using LaTeX'))
    parser.add_argument('--course', dest='course', default='/',
                        help='filter on course')
    parser.set_defaults(course='/')
    args = parser.parse_args()

    if not os.path.exists(os.path.join('summary_data', 'questions_meta.csv')):
        raise Exception('Require summary_data/questions_meta.csv')

    df = pd.read_csv(os.path.join('summary_data', 'questions_meta.csv'))
    df['location'] = df['URL'].apply(file_loc_from_question_url)

    if args.course == '/':
        exams = df.groupby(['course', 'exam']).groups.keys()
        print('No course specified. Updating all following exams.')
        print(sorted(exams))
        for (c, e) in sorted(exams):
            q_filter = os.path.join(c, e)
            print(q_filter)
            subprocess.check_output(['python', 'latex2pdf.py',
                                     '--course', q_filter])

            if not os.path.exists('allPDFs'):
                os.makedirs('allPDFs')
            nameNew = os.path.join('allPDFs', '%s_%s_Solutions.pdf' % (c, e))
            x = subprocess.check_output(["mv",
                                         os.path.join('latex_help_files',
                                                      'MERSolutions.pdf'),
                                         nameNew])

            nameNew = os.path.join('allPDFs', '%s_%s_Answers.pdf' % (c, e))
            x = subprocess.check_output(["mv",
                                         os.path.join('latex_help_files',
                                                      'MERAnswers.pdf'),
                                         nameNew])
    else:
        df = df[df.URL.str.contains(args.course)]

        df_examURL = pd.read_csv(os.path.join('summary_data',
                                              'exam_pdf_url.csv'))
        title = args.course

        if 'MATH' in title:
            course = 'MATH' + title.split('MATH')[-1][0:3]
        else:
            course = ''
        if 'December' in title:
            exam = 'December ' + title.split('December')[-1][1:5]
        elif 'April' in title:
            exam = 'April ' + title.split('April')[-1][1:5]
        else:
            exam = ''

        df_examURL = df_examURL[df_examURL.course.str.contains(course)]
        df_examURL = df_examURL[
            df_examURL.exam.str.contains(exam.replace(' ', '_'))]
        for index, row in df_examURL.iterrows():
            examURL = row.examURL

        write_content(df, exam)
        # write_h_latex(course, exam)
        write_s_latex(course, exam, examURL)
        write_a_latex(course, exam, examURL)
        # write_ha_latex(course, exam)

        print('done preparing. On to LaTeX!')

        directory = os.path.join('latex_help_files')
        os.chdir(directory)

        # for myname in ['MERAnswers', 'MERSolutions', 'MERHints',
        # 'MERHintsAnswer']:
        for myname in ['MERSolutions', 'MERAnswers']:
            x = subprocess.check_output(
                ["pdflatex", "%s.tex" % myname])
            x = subprocess.check_output(
                ["pdflatex", "%s.tex" % myname])
        for ending in ['log', 'aux', 'out', 'toc']:
            for doomed in glob.glob('*' + ending):
                os.remove(doomed)
        print('Finished')
