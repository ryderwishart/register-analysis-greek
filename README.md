# Register analysis for Hellenistic Greek (using OpenText data)

## How I use these scripts to do register analysis of ancient Greek texts

I use `extract-projections-from-opentext.xquery` to extract embedded texts from the larger OpenText XML files (in the `/texts` dir)

The results are a single XML file. I will probably create an XSLT to create multi-file output (unless I can find this functionality in xQuery).

I will also need to update the xQuery to extract the full XML, not simply the forms.

I use `register-analysis.py` to analyze the register of XML texts in terms of their relative linguistic probabilities.

TODO: add R scripts for correlation analysis, and instructions for contextual analysis.
TODO: update python paths to be relative, and duplicate all dependencies, such as TF-IDF model

## Acknowledgements

The base text is the 1904 Nestle text of the Greek New Testament.

GBI provided the initial data base used by the OpenText project.