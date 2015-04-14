#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pypandoc
import re
import os
import json
import argparse
import sys
import subprocess
import pandas as pd
from helpers import (split_at_equal, split_at_nextline,
                     brackets_check, file_loc_from_question_url)
reload(sys)
sys.setdefaultencoding('utf-8')


def preCleaning(input):
    input = input.decode('latin1')
    input = input.replace(u'ï¬', 'fi')
    input = input.replace('&amp;', '&')
    input = input.replace('&lt;', '<')
    input = input.replace('&le;', '<math>\leq</math>')
    input = input.replace('&gt;', '>')
    input = input.replace('&ge;', '<math>\geq</math>')
    input = input.replace('&ne;', '<math>\\neq</math>')
    input = re.sub(r'([-+]?)&infin;', r'<math>\1\\infty</math>', input)
    input = input.replace(u'â', '<math>\infty</math>')
    input = input.replace(u'â¥', '<math>\geq</math>')
    input = input.replace(u'â¤', '<math>\leq</math>')
    input = input.replace(u'â', '<math>^{\prime}</math>')
    input = input.replace(u'â²â²', '<math>^{\prime\prime}</math>')
    input = input.replace(u'â²', '<math>^{\prime}</math>')
    input = input.replace(u'â³', '<math>^{\prime\prime}</math>')
    input = input.replace(u'Â°', '<math>^{\circ}</math>')
    input = input.replace(u'â', '')
    input = input.replace(u'â¨', u'<math>\\vee</math>')
    input = input.replace(u'â', u'<math>\\rightarrow</math>')
    input = re.sub(r'&radic;{{overline\|(.*)}}',
                   r'<math>\\sqrt{\1}</math>', input)
    input = re.sub(r'<math> *\\ +', r'<math>', input)
    input = re.sub(r'\\ +</math>', r'</math>', input)
    input = re.sub(r':+ *<math>', r':<math>', input)
    input = re.sub(r'$\\ (.*)$', r'$\1$', input)  # todo
    input = re.sub(r'$\\displaystyle (.*)$', r'$\1$', input)  # todo
    input = re.sub(r':<math>\\displaystyle{\\begin{align}(.*)'
                   r'\\end{align}}</math>',
                   r':<math>\\begin{align}\1\\end{align}</math>', input)
    input = re.sub(r':<math>\\displaystyle{(.*)}</math>',
                   r':<math>\n\1\n</math>', input)
    input = re.sub(r'(?<!\\)\$', r'\\$', input)
    return input


def postCleaning(input):
    input = input.replace(u'ƒ', '$f$')
    input = input.replace(u'\u00c6\u0092', '$f$')
    input = input.replace("$f$$^{\prime}$", "$f'$")
    input = input.replace("$f$$^{\prime\prime}$", "$f''$")
    input = input.replace("\emph{f$^{\prime\prime}$}", "$f''$")
    input = re.sub(r"([a-zA-Z)])\s*'",
                   r"\1'", input)
    input = re.sub(r"([a-zA-Z)])\s*'\s*'",
                   r"\1''", input)

    input = re.sub(r"\\color{(.*)\s(.*)}",
                   r"\\color{\1\2}", input)

    input = input.replace(u'\u00cf\u0080', '$\pi$')
    input = input.replace(u'\u03b8', '$\\theta$')
    input = input.replace(u'\u03c0', '$\pi$')
    input = input.replace(u'\u03c6', '$\phi$')
    input = input.replace(u'\u03c1', '$\\rho$')
    input = input.replace(u'\u221e', '$\infty$')
    input = input.replace(u'\u2229', '$\cap$')
    input = input.replace(u'\u222a', '$\cup$')
    input = input.replace(u'\u03b1', '$\\alpha$')
    input = input.replace(u'\u2208', '$\in$')
    input = input.replace(u'\u2192', '$\\rightarrow$')
    input = input.replace(u'\u2286', '$\subseteq$')
    input = input.replace(u'\u00c2', '')
    input = input.replace(u'\u00a0', '')
    input = input.replace(u'\u03b5', '$\\varepsilon$')
    input = input.replace(u'\u00ac', '$\\neg$')
    input = input.replace(u'\u03bc', '$\\mu$')
    input = input.replace(u'\u03bb', '$\\lambda$')
    input = input.replace(u'\u03b7', '$\\eta$')
    input = input.replace(u'\u03a3', '$\\Sigma$')
    input = input.replace(u'\u00e2\u0088\u00921', '-1')
    input = input.replace(u'\xd7', '$\\times$')
    input = input.replace(u'\xb1', '$\\pm$')
    input = input.replace(u'\xc3\xb4', '\^{o}')
    input = input.replace(u'\xc3\x97', '$\\times$')
    input = input.replace(u'\xe2\x80\x9c', '``')
    input = input.replace(u'\xe2\x80\x9d', '``')

    input = re.sub(r'\$\\displaystyle\s*\n*',
                   r'$\\displaystyle ', input)
    input = input.replace("\[\\begin{align}", "\\begin{align*}")
    input = re.sub(r'\$\\displaystyle\s*\\begin{align}',
                   r'\\begin{align*}', input)
    input = input.replace("$\displaystyle\\begin{align}", "\\begin{align*}")
    input = input.replace("\[\displaystyle \\begin{align}", "\\begin{align*}")
    input = input.replace("\[\displaystyle\\begin{align}", "\\begin{align*}")

    input = input.replace("\[\n\\begin{align}", "\\begin{align*}")
    input = input.replace("\[\displaystyle\n\\begin{align}", "\\begin{align*}")
    input = input.replace('\[\\begin{alignat}', '\\begin{alignat*}')

    input = input.replace("\end{align}\]", "\end{align*}")
    input = input.replace('\end{align*}\\\\', '\end{align*}\n')
    input = input.replace('\end{align}.\\]', '\end{align*}')
    input = input.replace('\end{alignat}\\]', '\end{alignat*}')

    input = input.replace('$\displaystyle\\begin{align}', '\\begin{align*}')
    input = input.replace('$\\begin{align}', '\\begin{align*}')
    input = input.replace('\\begin{align}', '\\begin{align*}')
    input = input.replace('\end{align}$', '\end{align*}')
    input = input.replace("\\\\]", "\\]")
    input = re.sub(r"\\\[\\displaystyle\s*\n\\begin{align\*}",
                   r"\\begin{align*}", input)
    input = re.sub('\\begin{align\*}\n+', '\\begin{align*}\n', input)

    input = input.replace('\\toprule\\addlinespace\n', '')
    input = input.replace('\n\\bottomrule', '')
    input = re.sub(r'\n\\+addlinespace', r'\\\\', input)
    input = input.replace('\\addlinespace\n', '')
    input = input.replace('\\\\end{longtable}', '\\end{longtable}')

    input = input.replace('\midrule\endhead', '')
    input = input.replace('style=""\\textbar{} ', '')

    input = re.sub(r'\$(.*)(?<!\\)%(.*)\$', r'$\1\%\2$', input)
    input = re.sub(r"\$f\$('*)\(\\emph{(.)}\)", r"$f\1(\2)$", input)
    input = re.sub(r"([\^_])\\sqrt{([^\s]*)}", r"\1{\\sqrt{\2}}", input)
    input = re.sub(
        r"\[\\displaystyle{\\begin{align\*}([\s\S]*)\\end{align}}\\]",
        r"\\begin{align*}\1\\end{align*}", input)

    input = re.sub(r"\\+begin{align\*}", r'\\begin{align*}', input)
    input = re.sub(r'\\end{align\*}\\+', r'\\end{align*}\n', input)
    input = re.sub(r'\n+\\end{align\*}', r'\n\end{align*}', input)
    input = re.sub(r'(\\\\\s*)*\n\\end{align\*}', r'\n\end{align*}', input)
    input = re.sub(r'(\\\\)+\\end{align\*}', r'\n\end{align*}', input)

    input = re.sub(r'\\\[{\\color{(.*)}\n\\begin{align\*}([\s\S]*)\\end{align}\n}\\\]',
                   r'{\\color{\1}\[\n\\begin{aligned}\2\\end{aligned}\n\]}',
                   input)

    input = re.sub(r'\\\[([\s\S]*)\\begin{align\*}([\s\S]*)\\end{align}',
                   r'\[\1\\begin{aligned}\2\\end{aligned}', input)

    input = re.sub(r'\\]([,.])', r'\1\\]', input)

    input = re.sub(r'&\s*=', '&=', input)
    input = re.sub(r'=\s*&', '&=', input)
    input = re.sub(r'\$\(\\emph(.*)\)', r'(\1)$', input)
    input = input.replace(
        '\[', '\\begin{align*}').replace('\]', '\end{align*}')
    input = re.sub(r'\\left\.\s+', r'\\left.', input)
    input = re.sub(r'\\right\.\s+', r'\\right.', input)

    input = re.sub(r'\\begin{align\*}\s*(?!\n)', r'\\begin{align*}\n', input)
    input = re.sub(r'(?<!\n)\\end{align\*}', r'\n\\end{align*}', input)

    return input.strip()


def fix_details(content, loc):
    image_path = os.path.join(*(['..'] + loc.split('/')[:-1]))

    def fix_image_path(content):
        if not 'includegraphics' in content:
            return content
        else:
            matches = re.findall(r'\\includegraphics(.*){(.*)}', content)
            matches = list(set([m[1] for m in matches]))
            fixes = [m.strip().replace(' ', '_') for m in matches]
            for match, fix in zip(matches, fixes):
                content = content.replace(match, image_path + '/' + fix)
            return content.replace('includegraphics',
                                   'includegraphics[width=0.5\\textwidth]')

    def gif_to_png(content):
        return content.replace('.gif}', '.png}')

    def fix_href(content):
        if not '\\href' in content:
            return content
        else:
            return re.sub(r'\\href{[^}]*}', '', content)

    def remove_figure_environment(content):
        figures = re.findall(
            r'\\begin{figure}\[htbp\](?:\n.*){4,7}\\end{figure}', content)
        figures = list(set(figures))
        replaces = ['\\includegraphics' +
                    text.split('includegraphics')[-1].split('}')[0] + '}'
                    for text in figures]
        for figure, replace in zip(figures, replaces):
            content = content.replace(figure, replace)
        return content

    def remove_description_environment(content):
        return(content)
#        descriptions = re.findall(
#            r'\\begin{description}((?:\n.*){3,6})\\end{description}', content)
#        print(descriptions)
#
#        if '{description}' in content:
#            figure_list = content.split('{description}')
#            content = ''
#            for text in figure_list:
#                if '\\item[]' in text:
#                    text = '\\includegraphics' + \
#                        text.split('includegraphics')[-1].split('}')[0] + '}'
#                if text[-6:] == '\\begin':
#                    text = text[:-6]
#                content = content + text
#        return content

    return remove_figure_environment(
        gif_to_png(fix_image_path(fix_href(content))))


def make_final_answer(content):
    if content == '':
        return content

    content = content.strip()
    answer = content.split('\n\n')[-1]

    if 'align' in answer:
        answerB = answer.split('\\begin{align*}')[0]
        answerE = answer.split('\\end{align*}')[-1]
        answerM = answer.split(
            '\\begin{align*}')[-1].split('\\end{align*}')[0].strip()

        zahlMax = len(split_at_nextline(answerM))

        answerMlast = split_at_equal(
            split_at_nextline(answerM)[-1].replace('&', ''))
        answerM1 = answerMlast[0].strip()
        zahl = 2
        while answerM1 == '':
            if zahl > zahlMax:
                answerM1 = split_at_nextline(
                    answerM)[-zahl + 1].replace('&',
                                                '').replace('=', '').strip()
            else:
                answerM1 = split_at_nextline(answerM)[-zahl].replace('&', '')
                answerM1 = split_at_equal(answerM1)[0].strip()
            zahl = zahl + 1

        if answerMlast[-1].strip() == '':
            answerMlast = split_at_equal(
                split_at_nextline(answerM)[-2].replace('&', ''))
            answerM2 = answerMlast[-1].strip()
        else:
            answerM2 = answerMlast[-1].strip()

        if answerM1 == answerM2:
            answer = ' $' + answerM1 + '$ ' + answerE
        else:
            answer = ' $' + answerM1 + '=' + answerM2 + '$ ' + answerE

    elif 'figure' not in answer:
        answer = answer.strip().split('. ')
        answer = [s for s in answer if not s == ''][-1]

        if '$' in answer:
            answer = ' ' + answer + ' '
            answer.replace('\\$', 'backslashDollar')
            answerlist = answer.split('$')
            answerlist = [s.replace('backslashDollar', '\\$')
                          for s in answerlist]
            answer = ''

            for string in answerlist:
                if '=' in string:
                    splitstring = split_at_equal(string)
                    string = splitstring[0] + '=' + splitstring[-1]
                answer = answer + '$' + string
            answer = answer[1:].strip()

        elif '=' not in answer and '\\emph{' not in answer and 'answer' not in answer:
            content = content.split(answer)[0]
            answer1 = make_final_answer(content)
            answer = answer1 + answer

    if '}' == answer[-1] and not brackets_check(answer):
        answer = answer[:-1]
    if '\\end{itemize}' in answer and '\\begin{itemize}' not in answer:
        answer = '\\begin{itemize}' + '\\item ' + answer
    if '\\end{enumerate}' in answer and '\\begin{enumerate}' not in answer:
        answer = '\\begin{enumerate}' + '\\item ' + answer
    if '\\end{description}' in answer and '\\begin{description}' not in answer:
        answer = '\\begin{description}' + '\\item ' + answer

    return answer


def make_raw_2_latex(df):

    for index, row in df.iterrows():
        loc = row.location

        with open(loc, 'r') as fd:
            data = json.loads(fd.read())

        statement_raw = data['statement_raw']
        hints_raw = data['hints_raw']
        sols_raw = data['sols_raw']

        statement_latex = postCleaning(
            pypandoc.convert(preCleaning(statement_raw), 'latex',
                             format='mediawiki'))
        statement_latex = fix_details(statement_latex, loc)
        hints_latex = []
        for hint in hints_raw:
            hint_latex = postCleaning(
                pypandoc.convert(preCleaning(hint), 'latex',
                                 format='mediawiki'))
            hint_latex = fix_details(hint_latex, loc)
            hints_latex.append(hint_latex)
        sols_latex = []
        for sol in sols_raw:
            sol_latex = postCleaning(
                pypandoc.convert(preCleaning(sol), 'latex',
                                 format='mediawiki'))
            sol_latex = fix_details(sol_latex, loc)
            sols_latex.append(sol_latex)
        try:
            answer_latex = make_final_answer(sols_latex[0])
        except:
            print('Can not make final answer for %s' % data['ID'])
            raise

        data['statement_latex'] = statement_latex
        data['hints_latex'] = hints_latex
        data['sols_latex'] = sols_latex
        data['answer_latex'] = answer_latex

        if not os.path.exists(loc.split('/Question')[0]):
            os.makedirs(loc.split('/Question')[0])
        with open(loc, "w") as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('MER topic or exam to json'
                                                  ' with the option to compile'
                                                  ' to LaTeX'))
    parser.add_argument('--course', dest='course', default='/',
                        help='filter on course')
    parser.set_defaults(course='/')
    args = parser.parse_args()

    if not os.path.exists(os.path.join('summary_data', 'questions_meta.csv')):
        raise Exception('Require summary_data/questions_meta.csv')

    df = pd.read_csv(os.path.join('summary_data', 'questions_meta.csv'))
    if args.course == '/':
        courses = df.groupby('course').groups.keys()
        print(
            'No course specified. Updating all following courses in parallel.')
        print(sorted(courses))
        subprocess.check_output(
            ['parallel', 'python', 'raw2latex.py',
             '--course', ':::'] + courses)

    df['location'] = df['URL'].apply(file_loc_from_question_url)
    df = df[df.URL.str.contains(args.course, regex=False)]

    make_raw_2_latex(df)
