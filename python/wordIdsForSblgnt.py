'''

Input example:
<?xml version="1.0" encoding="UTF-8"?>
<root>
   <book id="Mt">
      <milestone id="SBLGNT.Matthew.1.1"/>
      <w id="">Βίβλος</w>
      <w id="">γενέσεως</w>
      <w id="">Ἰησοῦ</w>
      <w id="">χριστοῦ</w>
      <w id="">υἱοῦ</w>
      <w id="">Δαυὶδ</w>
      <w id="">υἱοῦ</w>
      <w id="">Ἀβραάμ</w>
      <milestone id="SBLGNT.Matthew.1.2"/>
      <w id="">Ἀβραὰμ</w>
      <w id="">ἐγέννησεν</w>
      <w id="">τὸν</w>
      <w id="">Ἰσαάκ</w>
      <w id="">Ἰσαὰκ</w>
      <w id="">δὲ</w>
      <w id="">ἐγέννησεν</w>
      ...

'''

sblgnt_w_list = []

with open('/Volumes/Storage/Programming/dissertation-research/texts/SBLGNTxml/sblgnt-base-w.xml', 'r') as inf:
    for line in inf:
        sblgnt_w_list.append(line.strip())

output_list = []
verse_word_counter = 0

for item in sblgnt_w_list:
    
    if item.startswith('<milestone'):
        milestone_id = item.split('"')[1]
        verse_word_counter = 0
    elif item.startswith('<w'):
        verse_word_counter += 1
        current_line_split = item.split('"')
        current_line_split.pop(1)
        current_line_split.insert(1, '"{0}.w{1}"'.format(milestone_id, verse_word_counter))
        item = ''.join(current_line_split)
    else:
        pass
    output_list.append(item)

with open('sblgnt_base_w.xml', 'a') as output_file:
    for line in output_list:
        output_file.write(line + '\n')