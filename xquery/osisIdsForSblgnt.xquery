declare namespace functx = "http://www.functx.com";

declare function functx:substring-after-if-contains
($arg as xs:string?,
$delim as xs:string) as xs:string? {
    
    if (contains($arg, $delim))
    then
        substring-after($arg, $delim)
    else
        $arg
};

declare function functx:substring-before-if-contains
($arg as xs:string?,
$delim as xs:string) as xs:string? {
    
    if (contains($arg, $delim))
    then
        substring-before($arg, $delim)
    else
        $arg
};

<root>
    {
        for $book in //book
        return
            <book
                id="{$book/@id}">{
                    for $element in $book//*
                    return
                        
                        if (name($element) eq 'verse-number') then
                            <milestone
                                id="SBLGNT.{
                                        functx:substring-before-if-contains($element/@id, ' ')
                                    }.{
                                        functx:substring-after-if-contains(
                                            functx:substring-before-if-contains($element/@id, ':'), ' ')
                                    }.{
                                        functx:substring-after-if-contains($element/@id, ':')
                                    }"/>
                        else
                            if ($element eq w) then
                                <w
                                    id="{$element/@id}">{$element/text()}</w>
                            else
                                ()
                }
            </book>
    }
</root>