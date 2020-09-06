print('Generating ranges...')

textArray = []
outputArray = ['<?xml version="1.0" encoding="UTF-8"?>', '\n<root>']

with open('/Volumes/Storage/Programming/dissertation-research/texts/NA28/na28-base-projections-flagged.xml', 'r') as inputFile:
    for line in inputFile:
        textArray.append(line) 

discourseFlag = {'start':False,'end':False}

for index in range(0, len(textArray)):
    
    # get line id
    if 'id="' in textArray[index]:
        currentLineWordId = textArray[index].split('"')[1]

    # set previous and next_ indices
    if index > 0:
        previous = textArray[index - 1]
    else:
        previous = 'None'

    if index < (len(textArray) - 1):
        next_ = textArray[index + 1]
    else:
        next_ = 'None'

    # if projected word, then set flags based on context
    if 'projected="yes"' in textArray[index]:
        # check previous
        if 'projected="yes"' in previous:
            discourseFlag = {'start':False,'end':False} # reset flags
        elif 'projected="no"' in previous:
            discourseFlag['start'] = True
        else:
            pass
        
        # check next_
        if 'projected="yes"' in next_:
            discourseFlag['end'] = False # reset flags
        elif 'projected="no"' in next_:
            discourseFlag['end'] = True
        else:
            discourseFlag['end'] = True
            
    else:
        discourseFlag = {'start':False,'end':False} # reset flags

    if discourseFlag['start'] == True:
        outputArray.append('\n<Discourse start="{0}" '.format(currentLineWordId))
    
    if discourseFlag['end'] == True:
        outputArray.append('end="{0}"/>'.format(currentLineWordId))

    discourseFlag = {'start':False,'end':False} # reset flags

outputArray.append('\n</root>')

outputFileName = 'discourse-ranges-from-legacy.xml'

with open(outputFileName, 'a') as outputFile:
    outputString = ''.join(outputArray)
    outputFile.write(outputString)

print('Ranges generated and saved in: {0}'.format(outputFileName))