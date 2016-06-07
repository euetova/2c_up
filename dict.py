import os

itog = open("dict_freq_verb.txt", 'w', encoding='utf-8')

dict = {}
dict_all = {}
DICT = {}
cases = ['nom', 'acc', 'abl', 'dat', 'gen', 'ill', 'el', 'loc', 'ins', 'prol', 'egr', 'adv', 'term', 'car'] #+1


def get_output(text):        # save useful information
    outp = []
    for line in text:
         if line[0] != "#":
             line = line.split('\t')
             outp.append([line[0], line[1], line[4], line[9], line[11], line[12], line[13]])
    return outp


def sentences(outp):       #make sentences
    words = outp[0][4] + ' ' + outp[0][5] + ' ' + outp[0][6] +';'
    k = outp[0][0]
    test = []
    for line in range(1, len(outp)):
        w = outp[line][4] + ' ' + outp[line][5] + ' ' + outp[line][6] + '; '
        if outp[line - 1][0] == outp[line][0]:
            if outp[line - 1][1] == outp[line][1]:
                words = words[:-2]
                words += '% '
            words +=  w
        else:
            test.append(k + ';' + words + '\n')
            words = w
        k = outp[line][0]
    return test


def v_sentences(text):  #sentences with 1 verb
    v_sent = []
    for line in range(len(text)):
        if ' V ' in text[line] and 'N' in text[line]:
            text_split = (text[line].strip()).split(';')
            k = 0
            for i in range(len(text_split)):
                if ' V ' in text_split[i]:
                    k += 1
            if k == 1:
                v_sent.append(text[line])
    return v_sent


def dict_verb_nouns(v_s, outp, dict):   #one dictionary for all files
    for i in range(len(v_s)):
        text_split = (v_s[i].strip()).split(';')
        nom_line = text_split[0]
        k = 0
        nouns = ''
        verb = '1'
        for j in range(1, len(text_split)):
            if ' V ' in text_split[j]:
                for v in range(len(outp)):
                    if outp[v][0] == nom_line and outp[v][1] == str(j) and ('V' in outp[v][4] or 'V' in outp[v][5]):
                        verb = outp[v][3]
                        break
            if 'N ' in text_split[j] and '%' not in text_split[j]:
                for el in cases:
                    if el in text_split[j]:
                        nouns = nouns + ';' + el
                        continue
        row = (nouns.strip(';')).strip()
        if row == '':
            continue
        else:
            if verb in dict.keys():
                dict[verb] = dict[verb] + '\n' + row
            else:
                dict[verb] = row
    return dict


def freq_nouns(dict):
    dict_v = {}
    for key in sorted(dict.keys()):
        list_el = []
        unique = set()
        forms = (dict[key].strip()).split('\n')
        length = len(forms)
        for line in forms:
            elems = line.split(';')
            for i in range(len(elems)):
                elems[i] = elems[i].strip()
            unique |= set(elems)
        unique = list(unique)
        unique.sort()
        for el in unique:
            if '%' not in el:
                k = 0
                for line in forms:
                    if el in line:
                        k += 1
                if k > 0: #k > 0.5 * length:
                    list_el.append(el + '-' + str(k/length))
        dict_v[key] = ';'.join(list_el)
    return dict_v


for root, dirs, files in os.walk('C:/Users/lenovo/PycharmProjects/untitled/Cursach/'):
    for fname in files:
        point = fname.rfind('.')
        extension = fname[point + 1:]
        if extension == 'prs':
            file = open(root+'/'+fname, 'r', encoding='utf-8')
            output = get_output(file.readlines())
            verbs_sentences = v_sentences(sentences(output))
            dict = dict_verb_nouns(verbs_sentences, output, dict)


DICT = freq_nouns(dict)

for key in sorted(DICT.keys()):
    itog.write(key + '\n' + DICT[key] + '\n')

