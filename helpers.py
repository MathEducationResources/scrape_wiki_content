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
