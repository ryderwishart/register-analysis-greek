'''
This is the script I will be using to analyze the new OpenText 2.0 
script for my linguistics circle presentation on Feb 6, 2020

Ideally, I will establish some patterns I can use for the rest of my dissertation research.
'''

# GSP analysis

''' 

The goal of this script will be to produce an automatic analysis of papyri texts in Celano's XML annotation format.

Ideally, it will generate an analysis of every file in a folder, with an output description of each work in a table format.

I would like the output to have some components that are easily amenable to a visualization, whether that be the structure, or some other property.

I would like the analysis to proceed along metafunctional lines.

TODO: add a Text() method to generate a topic model (ideally hierarchical, so that it infers topics—however this should be of a relatively high granularity). A topic model approach would be an interesting notion to introduce into discussions of Lemke's ITF's, where ITF's could be conceptualized as topics in a corpus of semantically similar texts OR segments of texts.

'''
#TODO: make a tf-idf vector space on an entire corpus of hellenistic texts... or just the letters I can find?
# save this tf-idf space as a stripped-down gensim wv model for faster loading/querying.

from lxml import etree
from gensim import corpora, similarities, models
import os
from pprint import pprint
import json

# Make a flag for papyri vs. hellenistic-text vs. just letters? This would allow me to select an appropriate tf-idf model 

class Text:
    '''
    
    Instantiate a new text() class for each new file, with properties such as:

    Introduction:
    title
    author

    Mode:
    length
    lexical-density (unique lexemes per word) (TODO: lexical density per section, length per section, etc?)
    major sections estimate (texttiling algorithm?)

    Tenor:
    participants (use person property values and proper names)
    mood ratios (for total text and per section)
    special-features (vocatives per sentence?... etc.?)

    Field:
    subject matter (tf-idf on entire corpus? Use a pre-trained vector space?) 
    transitivity[causality] ratios (using voice, for total text and per section)

    Text() is initialized with an optional corpus parameter. 
    So far the options are 'hellenistic' (default), 'papyri'
    '''
    # initialize empty properties which can subsequently be filled
    def __init__(self, file_path, corpus='hellenistic'):
        self.file_path = file_path
        self.corpus = corpus

        # initialize the following properties with empty values to be called up by each instance of the text() class
        introduction = {'title':'', 'author':'', 'file-name':''}
        mode = {'length':0, 'lexical-density':0.0, 'sections':0} 
        # 'sections' here is just the estimated number of major sections
        # TODO: need to add a way to break down the sections themselves. Each section needs, for example, a mood and causality ratio.
        tenor = {'participants':{'first':[0.0, 0], 'second':[0.0, 0], 'third':[0.0, 0]}, 'pronouns':[0,[]], 'mood-ratios':{'total-text':{'indicative':[0.0, 0], 'subjunctive':[0.0, 0], 'imperative':[0.0, 0], 'infinitive':[0.0, 0], 'optative':[0.0, 0], 'participle':[0.0, 0]}, 'per-section':[]}, 'special-features':{'vocatives':[0, []]}}
        # for now participants could be a ratio of person values
        field = {'subject-matter':[], 'causality':[{'active':[0.0, 0], 'middle':[0.0, 0], 'medeo-passive':[0.0, 0], 'passive':[0.0, 0]}], 'aspectuality':{'perfective':[0.0, 0], 'imperfective':[0.0, 0], 'stative':[0.0, 0]}}
        
        # remove this call for an alias if you are analyzing a folder via batch function below
        alias = '-'.join(input('Enter alias for text: ').split())

        forms = list()
        lemmas = list()
        
        self.introduction = introduction
        self.mode = mode
        self.tenor = tenor
        self.field = field
        self.alias = alias
        self.forms = forms
        self.lemmas = lemmas
    
    def save(self):
        if self.introduction['title'] == '':
            print('\nPlease use analyze() function before saving\n')
        else:
            with open(self.alias +'.txt', 'w+') as s:
                s.write(json.dumps(self.introduction, ensure_ascii=False))
                
                s.write('\nFIELD\n')
                s.write(json.dumps(self.field, ensure_ascii=False))
                s.write('\nTENOR\n')
                s.write(json.dumps(self.tenor, ensure_ascii=False))
                s.write('\nMODE\n')
                s.write(json.dumps(self.mode, ensure_ascii=False))
            print('File saved as \'{0}\''.format(self.alias))

    # TODO: split the various metafunctional analyses into separate functions, and then have a method such as def analyze_all to call all subsequent functions. analyze_all() could have flags such as 'ftm' as default (field, tenor, mode), or any mixture of these.
    def analyze(self, w=20, dims=100):
        
        self.w = w
        self.dims = dims

        if self.file_path.endswith('.xml'):
            with open(self.file_path) as f:
                # Parse xml file in celano's format
                tree = etree.parse(self.file_path)
                for text in tree.xpath('//text'):
                    
                    ''' Introduction '''

                    # extract title
                    try:
                        self.introduction['title'] = tree.xpath('//seg[@type="w"]')[0].attrib['osisID'].split('.')[0]
                    except:
                        pass
                    '''
                    # This introduction material is irrelevant with the new XML, but it may be added back in as attributes on the <text> element
                    try:
                        self.introduction['title'] = text.attrib['file-name'].split('.')  
                    except:
                        pass
                    try:
                        self.introduction['title'] = text.attrib['text-id'].split('.')
                    except:
                        pass

                    # extract author
                    try:
                        self.introduction['author'] = text.attrib['author'].split('.')
                    except:
                        self.introduction['author'] = 'unknown'
                    
                    # extract filename
                    try:
                        self.introduction['file-name'] = text.attrib['file-name'].split('.')
                    except:
                        self.introduction['file-name'] = self.file_path.split('/')[-1] # set the file name as the last part of the path  
                    '''

                    ''' Mode '''
                    # mode = {'length':0, 'lexical-density':0.0, 'sections':0}
                    # extract the lemmas from the xml tree and add them to a list
                    current_text = list()
                    
                    for element in tree.xpath('//seg[@type="w"]'):
                        current_text.append(element.get('lemma'))

                    # also extract the forms in case someone wants to read the text
                    for sentence in tree.xpath('//m[@unit="s"]'):
                        temp_sentence = list()
                        for word in sentence.findall('.//seg[@type="w"]'):
                            temp_sentence.append(word.attrib['norm'])
                        if len(temp_sentence) >= 0: # don't add the temporary sentence to self.forms if it is empty (this causes gensim's LSI functions to yell at you)
                            self.forms.extend(temp_sentence)
                            self.forms.append('\n')
                        else:
                            pass
                    del temp_sentence
                    
                    self.forms = ' '.join(self.forms)

                    # make a string of all the lexemes in the text currently being parsed
                    text_string = str()

                    # strip out punctuation and numerals etc.
                    # it would make more sense to use the unicode encoding directly, and then include only letters within the range of the greek alphabet
                    letters = 'ͻ α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ ς σ τ υ φ χ ψ ω ϊ ϋ ϙ ϛ ϝ ϟ ϡ ϲ ϼ ἀ ἁ ἂ ἃ ἄ ἅ ἆ ἇ ἐ ἑ ἒ ἓ ἔ ἕ ἠ ἡ ἢ ἣ ἤ ἥ ἦ ἧ ἰ ἱ ἲ ἳ ἴ ἵ ἶ ἷ ὀ ὁ ὂ ὃ ὄ ὅ ὐ ὑ ὒ ὓ ὔ ὕ ὖ ὗ ὠ ὡ ὢ ὣ ὤ ὥ ὦ ὧ ὰ ά ὲ έ ὴ ή ὶ ί ὸ ό ὺ ύ ὼ ώ ᾀ ᾁ ᾂ ᾄ ᾅ ᾆ ᾇ ᾐ ᾑ ᾒ ᾔ ᾕ ᾖ ᾗ ᾠ ᾡ ᾤ ᾥ ᾦ ᾧ ᾲ ᾳ ᾴ ᾶ ᾷ ῂ ῃ ῄ ῆ ῇ ῒ ΐ ῖ ῗ ῢ ΰ ῤ ῥ ῦ ῧ ῲ ῳ ῴ ῶ ῷ'.split() 
                    
                    for word in current_text:
                        new_word = ''.join([letter.lower() for letter in word if letter.lower() in letters])
                        text_string += ' ' + new_word

                    
                    # (see '/Users/ryderwishart/Documents/Programming/Corpora/celano/hellenistic-authors/lemmatized_indiv_texts/tf-idf')
                    # In this directory I have the following corpus: MmCorpus(392 documents, 31105 features, 530359 non-zero entries)
                    if self.corpus == 'hellenistic':
                        corpus = corpora.MmCorpus('../tf-idf/oct2018.mm')
                        dictionary = corpora.Dictionary.load('../tf-idf/jun2019.dict')
                        #TODO: it would be a good idea to create a tf-idf matrix based only on letters, to compare what is significant for the genre verses what distinguishes works within the genre; add parameter to class
                        # also, I think the tfidf model I'm importing could use some token normalization prior to processing, as I normalize the current text below
                    elif self.corpus == 'papyri':
                        corpus = corpora.MmCorpus('/Volumes/Storage/Programming/Corpora/papyri_xml/papyri_tfidf/papyri.mm')
                        dictionary = corpora.Dictionary.load('/Volumes/Storage/Programming/Corpora/papyri_xml/papyri_tfidf/papyri.dict')
                    # list all lexemes in romans
                    text_bow = dictionary.doc2bow(text_string.lower().split())
                    # get the tf-idf value for each lexeme
                    tfidf = models.TfidfModel(corpus, normalize=True)
                    text_tfidf = tfidf[text_bow] # convert the query to tfidf space

                    # count the number of lemmas, divide by the total number of words. This is the lexical density
                    total_words = text_string.split()
                    total_lemmas = set(total_words)
                    lexical_density = len(total_lemmas) / len(total_words)

                    self.mode['length'] = len(total_words)
                    self.mode['lexical-density'] = lexical_density

                    self.lemmas = text_string


                    ''' Tenor '''
                    # tenor = {'participants':{'first':[0.0, 0], 'second':[0.0, 0], 'third':[0.0, 0]}, 'mood-ratios':{'total-text':{'indicative':[0.0, 0], 'subjunctive':[0.0, 0], 'imperative':[0.0, 0], 'infinitive':[0.0, 0], 'optative':[0.0, 0], 'participle':[0.0, 0]}, 'per-section':[]}, 'special-features':{'vocatives':[0, []]}}
                    
                    # calculate person ratios and totals
                    person_totals = 0 
                    firsts = len(tree.xpath('//seg[@person="first"]'))
                    seconds = len(tree.xpath('//seg[@person="second"]'))
                    thirds = len(tree.xpath('//seg[@person="third"]'))

                    self.tenor['participants']['first'][1] = firsts
                    self.tenor['participants']['second'][1] = seconds
                    self.tenor['participants']['third'][1] = thirds

                    # create a count of all person forms for making a ratio
                    person_totals += firsts + seconds + thirds

                    # find ratio values for each person in the text
                    self.tenor['participants']['first'][0] = round(firsts / person_totals, 2)
                    self.tenor['participants']['second'][0] = round(seconds / person_totals, 2)
                    self.tenor['participants']['third'][0] = round(thirds / person_totals, 2)
                    
                    # calculate mood ratios and totals
                    mood_totals = 0
                    indicatives = len(tree.xpath('//seg[@mood="indicative"]'))
                    subjunctives = len(tree.xpath('//seg[@mood="subjunctive"]'))
                    imperatives = len(tree.xpath('//seg[@mood="imperative"]'))
                    infinitives = len(tree.xpath('//seg[@mood="infinitive"]'))
                    optatives = len(tree.xpath('//seg[@mood="optative"]'))
                    participles = len(tree.xpath('//seg[@mood="participle"]'))

                    self.tenor['mood-ratios']['total-text']['indicative'][1] = indicatives
                    self.tenor['mood-ratios']['total-text']['subjunctive'][1] = subjunctives
                    self.tenor['mood-ratios']['total-text']['imperative'][1] = imperatives
                    self.tenor['mood-ratios']['total-text']['infinitive'][1] = infinitives
                    self.tenor['mood-ratios']['total-text']['optative'][1] = optatives
                    self.tenor['mood-ratios']['total-text']['participle'][1] = participles

                    # create a count of all mood forms for making a ratio
                    mood_totals += indicatives + subjunctives + imperatives + infinitives + optatives + participles

                    # find ratio values for each voice in the text
                    self.tenor['mood-ratios']['total-text']['indicative'][0] = round(indicatives / mood_totals, 2)
                    self.tenor['mood-ratios']['total-text']['subjunctive'][0] = round(subjunctives / mood_totals, 2)
                    self.tenor['mood-ratios']['total-text']['imperative'][0] = round(imperatives / mood_totals, 2)
                    self.tenor['mood-ratios']['total-text']['infinitive'][0] = round(infinitives / mood_totals, 2)
                    self.tenor['mood-ratios']['total-text']['optative'][0] = round(optatives / mood_totals, 2)
                    self.tenor['mood-ratios']['total-text']['participle'][0] = round(participles / mood_totals, 2)

                    # count vocatives and append forms to list
                    voc_forms = list()
                    for i in tree.xpath('//seg[@case="vocative"]'):
                        voc_forms.append(i.attrib['norm'])
                    vocatives = len(voc_forms)

                    self.tenor['special-features']['vocatives'][0] = vocatives
                    self.tenor['special-features']['vocatives'][1] = voc_forms

                    # record pronouns
                    pronouns = list()
                    for i in tree.xpath('//seg[@pos="pron"]'):
                        pronouns.append(i.attrib['norm'])
                    pronoun_count = len(pronouns)

                    self.tenor['pronouns'][1] = pronouns
                    self.tenor['pronouns'][0] = pronoun_count

                    ''' Field '''
                    # field = {'subject-matter':[], 'causality':[{'active':[0.0, 0], 'middle':[0.0, 0], 'medeo-passive':[0.0, 0], 'passive':[0.0, 0]}], 'aspectuality':{'perfective':[0.0, 0], 'imperfective':[0.0, 0], 'stative':[0.0, 0]}}
                    
                    ## calculate aspect  
                    perfectives = len(tree.xpath('//seg[@tense="aorist"]'))
                    imperfectives = len(tree.xpath('//seg[@tense="present"]')) + len(tree.xpath('//seg[@tense="imperfect"]')) 
                    statives = len(tree.xpath('//seg[@tense="perfect"]')) + len(tree.xpath('//seg[@tense="pluperfect"]')) 

                    self.field['aspectuality']['perfective'][1] = perfectives
                    self.field['aspectuality']['imperfective'][1] = imperfectives
                    self.field['aspectuality']['stative'][1] = statives

                    # create a count of all aspect forms for making a ratio
                    aspect_totals = perfectives + imperfectives + statives

                    # find ratio values for each aspect in the text
                    self.field['aspectuality']['perfective'][0] = round(perfectives / aspect_totals, 2)
                    self.field['aspectuality']['imperfective'][0] = round(imperfectives / aspect_totals, 2)
                    self.field['aspectuality']['stative'][0] = round(statives / aspect_totals, 2)

                    ## calculate voice ratios
                    
                    voice_totals = 0 
                    actives = len(tree.xpath('//seg[@voice="active"]'))
                    middles = len(tree.xpath('//seg[@voice="middle"]'))
                    medeo_passives = len(tree.xpath('//seg[@voice="middlepassive"]'))
                    passives = len(tree.xpath('//seg[@voice="passive"]'))

                    self.field['causality'][0]['active'][1] = actives
                    self.field['causality'][0]['middle'][1] = middles
                    self.field['causality'][0]['medeo-passive'][1] = medeo_passives
                    self.field['causality'][0]['passive'][1] = passives

                    # create a count of all voice forms for making a ratio
                    voice_totals += actives + middles + medeo_passives + passives

                    # find ratio values for each voice feature in the text
                    self.field['causality'][0]['active'][0] = round(actives / voice_totals, 2)
                    self.field['causality'][0]['middle'][0] = round(middles / voice_totals, 2)
                    self.field['causality'][0]['medeo-passive'][0] = round(medeo_passives / voice_totals, 2)
                    self.field['causality'][0]['passive'][0] = round(passives / voice_totals, 2)

                    # approximate the subject matter using a pre-trained Greek tf-idf matrix 
                    # here I am essentially representing the 'subject matter' of the text as the 20 most significant lexemes
                    # use text_tdidf, which is a tfidf model of the current text
                    
                    # sort the values
                    sorted_terms = sorted(text_tfidf, key=lambda item: -item[1])
                    # return top 10 or 20 labeled sims
                    output_words = ['{0}: {1}'.format(dictionary.get(i[0]), i[1]) for i in sorted_terms]
                    # pprint(output_words[0:11])
                    self.field['subject-matter'] = output_words[0:21]

        else:
            print('Selected file does not appear to be an XML file.')
'''
    def graph(self):
        # This function runs the analyze() method, but also outputs a graph of the sections. 
        output_series = self.analyze()
        try:
            # Graphing digital time series
            from matplotlib import pylab
            pylab.xlabel("Segment Gap index")
            pylab.ylabel("Gap Scores")

            # reorganize output series for graphing
            zipped_output = zip(*output_series)
            pylab.plot(*zip(*output_series))
            pylab.show()
        except NameError:
            print('Must analyze text before graphing section breaks.')
'''
        

#Here's a loop to analyze and save all the texts in a folder
'''
# this version of the loop is wrapped in a while loop
dummy_var = True

while dummy_var == True:
    try:        

        file_dir = ''.join(input('Input directory: ').split())

        for i in os.listdir(file_dir):
            if i.endswith('.xml'):
                filename = i
                print(filename)
                newtext = Text('{0}'.format(os.path.join(file_dir, i)))
                newtext.analyze()
                newtext.save()
    
    except Exception as e:
        print('Script exited with exception --> {0}'.format(e))
'''

file_dir = ''.join(input('Input directory: ').split())

for i in os.listdir(file_dir):
    if i.endswith('.xml'):
        filename = i
        print(filename)
        newtext = Text('{0}'.format(os.path.join(file_dir, i)))
        newtext.analyze()
        newtext.save()
'''









Dev...

Here is the code I used to generate a TDIDF model:


from gensim.models import Tfidfmodel as tfidf
from gensim import corpora
import os

dir_path = input("Enter directory where corpus is contained:")
dir = ''.join(dir_path.split())

documents = os.listdir(dir)
texts = list()

# reads each document as a single string, stripping out newline characters
for doc in documents:
    if doc.endswith('.txt'):
        with open(os.path.join(dir,doc)) as f:
            lines = [line.rstrip() for line in f]
            texts.append(' '.join(lines).split())

dictionary = corpora.Dictionary(texts)
dictionary.save('oct2018.dict')
corpus = [dictionary.doc2bow(text) for text in texts]
corpora.MmCorpus.serialize('oct2018.mm', corpus)

corpus = corpora.MmCorpus('oct2018.mm')


# subject_term_database.save('oct2018_tfidf.model')

tfidf = models.TfidfModel(corpus, normalize=True)
index = similarities.MatrixSimilarity(tfidf[corpus])
index.save('oct2018.index')

# Now this model can be queried using the bag-of-words formulated for each text being analyzed in this program





### Here is a corpus and tf-idf model for papyri
from gensim.models import TfidfModel as tfidf
from gensim import corpora
import os

dir_path = input("Enter directory where corpus is contained: ")
dir = ''.join(dir_path.split())

documents = os.listdir(dir)
texts = list()

# reads each document as a single string, stripping out newline characters
class MySentences(object):
    def __iter__(self):
        for j in os.listdir(dir): # the directory where the text files are.
            if j.endswith(".xml"): # and j.startswith('TLG'):
                with open(j) as f:
                    tree = etree.parse(f)
                    current_text = list()
                    for element in tree.xpath('//l'):
                        for lemmas in element.getchildren():
                            current_text.append(lemmas.text)
                            break # break so that only the first possible lemma analysis is selected
                    yield current_text

# Instantiate the corpus streamer.

sentences = MySentences()

model = Word2Vec(sentences, size=size_input, window=window_input, min_count=min_count_input, workers=4)
        
            # Parse xml file in celano's format
            tree = etree.parse(self.file_path)
            for text in tree.xpath('//text'):







pylab.plot(range(len(output_series)), output_series, label="Gap Scores")
plot([1,2,3,4], [1,4,9,16], 'ro')

pylab.plot(range(len(d)), d, label="Depth scores")
pylab.stem(range(len(b)), b)
pylab.legend()
pylab.show()







    <voice>
        <active>{ count($x[matches(data(@o), '.....a...')]) }</active>,
        <passive>{ count($x[matches(data(@o), '.....p...')]) }</passive>,
        <middle>{ count($x[matches(data(@o), '.....m...')]) }</middle>,
        <medio-passive>{ count($x[matches(data(@o), '.....e...')]) }</medio-passive>,
    </voice>

            properties_dict[doc_name] = dict()
            for par in text.getchildren():
                properties_dict[doc_name][par.tag] = dict()
                for elem in par:
                    properties_dict[doc_name][par.tag][elem.tag] = elem.text
'''



'''

Here I open a loop to keep the program running, creating a UI for selecting files, giving them an alias (for retrieval),
analyzing them, and outputting the results both in the UI for immediate inspection and also in a log file for graphing purposes, etc.

# Set variable for keeping main loop running
quit_option = False

# Main loop
while quit_option == False:
     
    # Main operations: open file, open a folder, quit
    ui_main_selection = input('What do you want to do?\n(o)pen a file\n(b)atch open files in a folder\n(q)uit\n\nselection: ')

    # Open 

    # Instantiate a new text() object
    current_text = text(''.join(input('Enter file path for file: ').split()))

    # Batch Open

    # Quit 
    if ui_main_selection == 'q':
        quit_option = True

'''