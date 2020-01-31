(: TODO: need to clarify sentences within sentences :)

<texts>{
        (: for each span of projected text :)
        for $x in doc('../texts/02-mark.xml')//m[@name = "projection"]
        
        (: return a text element, with the first id reference so you know where the embedded text starts :)
        return
            <text
                ref="{($x//seg[@type = "w"]/@osisID)[1]}">
                {
                    (: for every sentence in the text :)
                    for $sent in $x//m[@unit = 's']
                    (: return a sentence element :)
                    return
                        <sent>
                            {
                                (: for every word in the sentence :)
                                for $word in $sent//seg[@type = "w"]
                                (: return the data, or content, of the word's text attribute :)
                                return
                                    data($word/@text)
                            }</sent>
                }
            </text>
    }</texts>