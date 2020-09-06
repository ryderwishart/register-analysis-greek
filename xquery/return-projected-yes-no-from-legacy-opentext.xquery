<root>
    {
        for $text in //text
        return
            <text
                book="{$text/@xml:id}">
                {
                    for $word in $text//w
                    return
                        <w
                            id="{$word/@xml:id}"
                            projected="{
                                    if ($word/ancestor::*[@projected = 'yes'])
                                    then
                                        'yes'
                                    else
                                        'no'
                                }">{$word/text()}</w>
                }
            </text>
    }
</root>