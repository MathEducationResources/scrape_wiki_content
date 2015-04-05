import os
import json
import pandas as pd
import urllib
import re


def url2videos2json(url, topic):
    def find(lhs, text):
        pattern = r"%s\s*=\s*(.*)" % lhs
        match = re.search(pattern, str(text))
        if match:
            return match.group(1)
        else:
            return None

    connection = urllib.urlopen(url)
    dom = connection.read()
    pattern = r"({{MER Video[\s\S]*?}})"

    videos = []

    if "livescribe" in dom:
        print("Missing pencast in topic", topic)

    for match in re.findall(pattern, dom):
        if "youtube id" in find("id", match):
            # No actual content, just the template.
            continue
        videos.append({
            "title": find("title", match),
            "text": find("text", match),
            "src": "https://www.youtube.com/embed/" + find("id", match),
            "credit": find("towhom", match),
        })

    to_save = {"url": url.replace("index.php?title=",
                                  "").replace("&action=edit", ""),
               "topic": topic,
               "parent": parent,
               "content": videos
               }

    WHERE_TO_SAVE = os.path.join('json_topics/', topic + '.json')

    with open(WHERE_TO_SAVE, "w") as outfile:
        json.dump(to_save, outfile, indent=4, sort_keys=True)


if __name__ == '__main__':

    df = pd.read_csv(os.path.join('summary_data', 'questions_topic.csv'))
    topics = df['topic'].values.tolist()
    topics = list(set(topics))

    if not os.path.exists('json_topics'):
        os.makedirs('json_topics')

    for num, topic in enumerate(topics):
        parent = list(set(df.loc[df['topic'] == topic, "parent"].values))
        if len(parent) > 1:
            raise Exception("Topic \s has more then one parent:" % topic)
        else:
            parent = parent[0]
        url = ('http://wiki.ubc.ca/index.php?title=Category:MER_Tag_' +
               topic +
               "&action=edit")
        videos = url2videos2json(url, topic)
