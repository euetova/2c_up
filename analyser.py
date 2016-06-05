import copy

file = open("fname.prs", 'r', encoding='utf-8')
aux_verbs = open("aux_verbs.txt", 'r', encoding='utf-8')
comp_words = open("comp_words.txt", 'r', encoding='utf-8')
after_verbs = open("after_verbs.txt", 'r', encoding='utf-8')
final = open("final.md", 'w', encoding='utf-8')

aux_v = (aux_verbs.read().strip()).split(';')
comp_w = (comp_words.read().strip()).split(';')
after_v = (after_verbs.read().strip()).split(';')
root = ''
dict = {}
cases_s = ['abl', 'dat', 'gen', 'loc', 'ins', 'adv', 'car']
cases_m = ['ill', 'el', 'loc', 'prol', 'egr', 'term', 'app']


def get_words(text):         # save useful information
    outp = []
    for line in text:
         if '#' not in line:
             line = line.split('\t')
             outp.append([line[0], line[1], line[4], line[9], line[11], line[12]])
    return outp


def sentences(outp):       # make sentences
    words = ' ' + outp[0][4] + ' ' + outp[0][5] +';'
    k = outp[0][0]
    test = []
    for line in range(1, len(outp)):
        w = ' ' + outp[line][4] + ' ' + outp[line][5] + ';'
        if outp[line - 1][0] == outp[line][0]:
            if outp[line - 1][1] == outp[line][1]:
                words = words[:-1]
                words += ' %'
            words +=  w
        else:
            test.append(k + ';' + words + '\n')
            words = w
        k = outp[line][0]
    return test


def v_sentences(text):
    v_sent = []
    for line in range(len(text)):
        if 'VERB' in text[line]:
            text_split = (text[line].strip()).split(';')
            k = 0
            t = 0
            p = 0
            for i in range(len(text_split)):
                if 'VERB' in text_split[i]:
                    k += 1
                    if 'pres' in text_split[i] or 'past' in text_split[i] or 'fut' in text_split[i] or 'cond' in text_split[i]:
                        t += 1
                if text_split[i] == '  ':
                    p += 1
            if k == 1 and t == 1 and p == 0:
                v_sent.append(text[line])
    return v_sent


def sg_pl(v):
    if 'pl' in v and 'sg' not in v:
        return 'pl'
    elif 'sg' in v and 'pl' not in v:
        return 'sg'
    else:
        return 'sg pl'


def after_verb(sent, i):
    global dict
    for w in range(len(words)):
        if words[w][0] == sent[0] and words[w][1] == str(i):
            if words[w][2] in comp_w or words[w][2] in after_v or 'PART' in sent[i + 1]:
                dict[i + 1] = root + '\taux'
                sent[i + 1] = '_'
    if 'fut' in sent[i] and 'VERB'in sent[i + 1]:
        dict[i + 1] = root + '\tneg'
        sent[i + 1] = '_'
    if i + 2 < len(sent):
        if 'VERB' in sent[i + 2]:
            dict[i + 2] = root + '\taux'
            sent[i + 2] = '_'


def root_s(sent):
    global number_v, root, dict
    dict = {}
    length = len(sent)
    for i in range(1, length):
        if 'pres' in sent[i] or 'past' in sent[i] or 'fut' in sent[i]:
            dict[i] = '0\troot'
            root = str(i)
            number_v = sg_pl(sent[i])
            sent[i] = '_'
            if i + 1 < length:
                after_verb(sent, i)
            for k in range(1, 3):
                if i - k > 1:
                    if 'VERB' in sent[i - k]:
                        for j in range(1, k):
                            dict[i - k] = root + '\taux'
                            sent[i - k] = '_'
    try:
        verb_ind = sent.index('_')
        if verb_ind - 1 >= 1:
            if 'ADJ' in sent[verb_ind - 1]:
                dict[verb_ind - 1] = root + '\tamod'
                sent[verb_ind - 1] = '_'
            elif 'ADV' in sent[verb_ind - 1]:
                dict[verb_ind - 1] = root + '\tadvmod'
                sent[verb_ind - 1] = '_'
    except ValueError:
        pass
    return dict


def adv(sent, sent1, dict):
    global number, root
    length = len(sent)
    for i in range(1, length):
        if 'ADV' in sent[i]:
            if i + 1 <= length:
                if 'ADV' in sent1[i + 1]:
                    dict[i] = str(i + 1) + '\tadvmod'
                    sent[i] = '_'
    return dict


def nomin(sent, i):
    global dict, number_v
    sgpl = ['sg', 'pl']
    length = len(sent)
    nsubj = ''
    for w in range(len(words)):
        if words[w][0] == sent[0] and words[w][1] == str(i):
            if words[w][2] not in comp_w:
                try:
                    for v in sgpl:
                        if v in sent[i] and v in number_v:
                            if i + 1 <= length and '%' not in sent[i + 1] and v in sent[i + 1] and 'nom' in sent[i + 1] and words[w + 1][2] not in comp_w:
                                dict[i + 1] = root + '\tnsubj'
                                nsubj = str(i + 1)
                                dict[i] = nsubj + '\tamod'
                                sent[i] = '_'
                                sent[i + 1] = '_'
                            else:
                                dict[i] = root + '\tnsubj'
                                nsubj = str(i)
                                sent[i] = '_'
                except NameError:
                    if i + 1 <= length and '%' not in sent[i + 1] and 'nom' in sent[i + 1] and words[w + 1][2] not in comp_w:
                        dict[i + 1] = root + '\tnsubj'
                        nsubj = str(i + 1)
                        dict[i] = nsubj + '\tamod'
                        sent[i] = '_'
                        sent[i + 1] = '_'
                    else:
                        dict[i] = root + '\tnsubj'
                        nsubj = str(i)
                        sent[i] = '_'
    return nsubj


def subj(sent, sent1, dict):
    global number_v, root, nsubj
    length = len(sent)
    nsubj = ''
    for i in range(1, length):
        if 'nom' in sent[i] and '%' not in sent[i]:
            nsubj = nomin(sent, i)
    if nsubj == '':
        for i in range(1, length):
            if 'nom' in sent[i] and 'acc' not in sent[i]:
                nsubj = nomin(sent, i)
    try:
        insubj = int(nsubj)
        if insubj + 1 < length:
            if 'ins' in sent[insubj + 1]:
                dict[insubj + 1] = nsubj + '\tidobj'
                if insubj + 2 < length and 'ADJ' in sent[insubj + 1] and 'ins' in sent[insubj + 2]:
                    dict[insubj + 2] = nsubj + '\tidobj'
                    dict[insubj + 1] = str(insubj + 1) + '\tamod'
                    sent[insubj + 1] = '_'
                    sent[insubj + 2] = '_'
                if 'rel_n' in sent[insubj + 1]:
                    dict[insubj + 1] = nsubj + '\tcase'
                    sent[insubj + 1] = '_'
        try:
            if insubj - 1 >= 1:
                if ('ADJ' in sent[insubj - 1] or 'NOUN' in sent[insubj - 1]) and 'rel_n' not in sent[insubj - 1] and 'acc' not in sent[insubj - 1]:
                    dict[insubj - 1] = nsubj + '\tamod'
                    sent[insubj - 1] = '_'
        except IndexError:
            pass
    except ValueError:
        pass
    return dict


def obj(sent, sent1, dict):
    global number, root, nsubj
    length = len(sent)
    for i in range(1, length):
        if 'acc' in sent[i]:
            dict[i] = root + '\tdobj'
            sent[i] = '_'
            if i - 1 >= 1 and ('ADJ' in sent[i - 1] or 'N' in sent[i - 1] or 'PRON' in sent1[i - 1]):
                dict[i -1] = str(i) + '\tamod'
                sent[i - 1] = '_'
        for el in cases_s:
            if el in sent[i]:
                dict[i] = root + '\tidobj'
                sent[i] = '_'
        for el in cases_m:
            if el in sent[i] and 'rel_n' not in sent[i]:
                dict[i] = root + '\tidobj'
                sent[i] = '_'
        if 'CNJ' in sent[i]:
            dict[i] = root + '\tcc'
            sent[i] = '_'
        if 'ADJ' in sent[i] and i + 1 <= length:
            dict[i] = str(i + 1) + '\tamod'
            sent[i] = '_'
        if 'ADV' in sent[i]:
            dict[i] = root + '\tadvmod'
            sent[i] = '_'
        if 'PART' in sent[i] and i - 1 >= 1:
            dict[i] = str(i - 1) + '\tpart'
            sent[i] = '_'
        if 'POST' in sent[i] and i - 1 >= 1 or 'rel_n' in sent[i]:
            dict[i - 1] = str(i) + '\tcase'
            sent[i - 1] = '_'
    return dict


def conllu_POS(sent):
    for i in range(len(sent)):
        if 'N' in sent[i][4] and 'NJ' not in sent[i][4] and 'IN' not in sent[i][4] and 'NU' not in sent[i][4]:
            sent[i][4] = sent[i][4].replace('N', 'NOUN')
        elif 'V' in sent[i][4] and 'ADV' not in sent[i][4]:
            sent[i][4] = sent[i][4].replace('V', 'VERB')
        elif 'PRO' in sent[i][4]:
            sent[i][4] = sent[i][4].replace('PRO', 'PRON')
        elif 'INTRJ' in sent[i][4]:
            sent[i][4] = sent[i][4].replace('INTRJ', 'INTJ')


def conllu_ftr(pos, features):
    nmbr = {'sg':'Sing',
            'pl':'Plur'}
    mood = {'subj':'Sub',
            'imper':'Imp'}
    verbForm = {'ptcp':'Part',
                'inf':'Inf',
                'cnv':'Convb'}
    poss = ['1sg', '2sg', '3sg', '1pl', '2pl', '3pl']
    if features == '':
        features = '_'
    else:
        ftr = features.split()
        for i in range(len(ftr)):
            if ftr[i] == '1' or ftr[i] == '2' or ftr[i] == '3':
                    ftr[i] = 'Person=' + ftr[i]
            elif ftr[i] == 'pres' or ftr[i] == 'fut' or ftr[i] == 'past':
                ftr[i] = 'Tense=' + ftr[i].capitalize()
            elif ftr[i] == 'neg':
                ftr[i] = 'Negative=Neg'
            elif ftr[i] in mood:
                ftr[i] = 'Mood=' + mood[ftr[i]]
            elif ftr[i] == 'pass' or ftr[i] == 'act':
                ftr[i] = 'Voice=' + ftr[i].capitalize()
            elif ftr[i] in verbForm:
                ftr[i] = 'VerbForm=' + verbForm[ftr[i]]
            elif ftr[i] == 'perf' or ftr[i] == 'freq':
                ftr[i] = 'Aspect=' + ftr[i].capitalize()
            if ftr[i] == 'comp':
                ftr[i] = 'Degree=Cmp'
            elif ftr[i] in nmbr:
                ftr[i] = 'Number=' + nmbr[ftr[i]]
            elif ftr[i] in cases_m or ftr[i] in cases_s or ftr[i] == 'nom' or ftr[i] == 'acc':
                ftr[i] = 'Case=' + ftr[i].capitalize()
            elif ftr[i] == poss:
                ftr[i] = 'Poss=' + ftr[i]
            else:
                ftr[i] = ftr[i].capitalize()
        features = '|'.join(ftr)
    if 'VERB' in pos:
        conjug = ''
        if len(pos) > 5:
            pos, conjug = pos.split()
        if features != '_':
            if conjug != '':
                features += '|' +conjug
        else:
            if conjug != '':
                features = conjug
    return pos, features


final.write('---\nlayout: entry\ntitle: try\n---\n\n')


words = get_words(file.readlines())
conllu_POS(words)
sent_all = sentences(words)
svs = v_sentences(sent_all)
for line in range(len(svs)):
    svs[line] = (svs[line].strip()).split(';')
sent_whole = copy.deepcopy(svs)

for line in range(len(svs)):
    dict = root_s(svs[line])
    dict = adv(svs[line], sent_whole[line], dict)
    dict = subj(svs[line], sent_whole[line], dict)
    dict = obj(svs[line], sent_whole[line], dict)
    nomer_p = svs[line][0]
    nom = 0
    final.write('~~~ conllu\n')
    final.write('#sent ' + nomer_p + '\n')
    for w in range(len(words)):
        if words[w][0] == nomer_p:
            if w == 1 or words[w][1] != str(nom):
                sl = sent_whole[line]
                nom = int(words[w][1])
                try:
                    k = dict[nom]
                except KeyError:
                    k = '_\t_'
                if nom != int(words[w + 1][1]):
                    words[w][4], words[w][5] = conllu_ftr(words[w][4], words[w][5])
                    final.write(str(nom) + '\t' + words[w][2] + '\t' + words[w][3] + '\t' + words[w][4] + '\t_\t' + words[w][5] + '\t' + k + '\t_\t_\n')
                else:
                    final.write(str(nom) + '\t' + words[w][2] + '\t' + words[w][3] + '\t' + sl[nom] + '\t_\t_\t' + k + '\t_\t_\n')
    final.write('~~~\n\n')

final.write('----------')

file.close()
aux_verbs.close()
comp_words.close()
after_verbs.close()
final.close()
