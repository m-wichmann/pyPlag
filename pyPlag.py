#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

#####
# pyPlag
#
# Copyright 2012, erebos42 (https://github.com/erebos42/miscScripts)
#
# This is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 2.1 of
# the License, or (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this software; if not, write to the Free
# Software Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
# 02110-1301 USA, or see the FSF site: http://www.fsf.org.
#####

"""check via google if file is a plagiarism"""

# TODO:
# - introduce a more or less objective "rating" value replacing the current "count" value, so the eval function has some boundaries
# - define a clear data structure for the rating format (e.g. dict with word and rating)
# - make the whole file thing a little more safe using exception handling
# - make sure all words are outputted to html and not only the middle of a chunk...
# - Should we really rely on google so much?!


import json
import re
import urllib
import urllib2
import random
from optparse import OptionParser

# Threshhold values for the output colors
THRESH_ABOVE0 = 0
THRESH_ABOVE2 = 10
THRESH_ABOVE5 = 100
THRESH_ABOVE10 = 1000


def pyplag():
    """main function"""

    # command line parsing
    parser = OptionParser()
    parser.add_option("-s", "--sentence", action="store_true", dest="sentence", help="use sentence detection, only one of s,p and u can be used!")
    parser.add_option("-p", "--paragraph", action="store_true", dest="paragraph", help="use paragraph detection, only one of s,p and u can be used!")
    parser.add_option("-u", "--uppercase", action="store_true", dest="uppercase", help="use upper case detection, only one of s,p and u can be used!")
    parser.add_option("-o", "--outputfile", dest="outputfile", help="output file")
    parser.add_option("-i", "--inputfile", dest="inputfile", help="input file")

    (options, args) = parser.parse_args()

    # check if files are specified
    if (not options.inputfile) or (not options.outputfile):
        parser.error('input or output file not specified')

    # check if exactly one algortihm is specified.
    # TODO: I'm sure this can be done with an xor -.-
    temp = 0
    if options.sentence:
        temp = temp + 1
    if options.paragraph:
        temp = temp + 1
    if options.uppercase:
        temp = temp + 1
    if temp != 1:
        parser.error('please specify exactly one algorithm (s,p or u)')

    # assign vars and start checking...
    if options.inputfile:
        inputfile = options.inputfile
        print "Inputfile: " + str(inputfile)
    if options.outputfile:
        outputfile = options.outputfile
        print "Outputfile: " + str(outputfile)
    if options.sentence:
        print "Algorithm: Sentence"
        data = checkforplag_sentence(inputfile)
        outputtohtml(outputfile, data)
    elif options.paragraph:
        print "Algorithm: Paragraph"
        data = checkforplag_paragraph(inputfile)
        outputtohtml(outputfile, data)
    elif options.uppercase:
        print "Algorithm: Uppercase"
        data = checkforplag_uppercase(inputfile)
        outputtohtml(outputfile, data)


def checkforplag_sentence(path):
    """check fo plagiarism by checking every sentence"""
    data = []

    fd = open(path, 'r')

    # TODO: Assumption: every line is a paragraph
    # This is not true if copy-pasted from a pdf file?!
    for line in fd:

        # filter comments and short lines like newlines and titles
        if len(line) < 5 or line[0] == '#':
            continue

        # split line into sentences if it ends with .!?
        # TODO: a sentece should only start with a capital letter! Otherwise abbreviations like e.g. are also recognized
        sentences = re.split(r'\s*[!?.]\s*', line)

        for sentence in sentences:
            # clean and split sentences
            cleansentence = sentence.replace(",", "")
            cleansentence = cleansentence.replace(":", "")
            cleansentence = cleansentence.replace("\n", "")

            count = googlesearch(cleansentence)
            data.append({"word": cleansentence,"count": count})

    fd.close()
    return data


def checkforplag_paragraph(path):
    """detect plagiarism by checking every paragraph/line"""
    data = []

    fd = open(path, 'r')

    # TODO: Assumption: every line is a paragraph
    # This is not true if copy-pasted from a pdf file?!
    for line in fd:

        # filter comments and short lines like newlines and titles
        if len(line) < 5 or line[0] == '#':
            continue
        else:
            count = googlesearch(line)
            data.append({"word": line,"count": count})

    fd.close()
    return data


def checkforplag_uppercase(path):
    """check for plagiarism with an 'inteligent' algorithm that detects upper case words"""
    data = []

    fd = open(path, 'r')

    # TODO: Assumption: every line is a paragraph
    # This is not true if copy-pasted from a pdf file?!
    for line in fd:

        # filter comments and short lines like newlines and titles
        if len(line) < 5 or line[0] == '#':
            continue

        # split line into sentences if it ends with .!?
        # TODO: a sentence should only start with a capital letter! Otherwise abbreviations like e.g. are also recognized
        sentences = re.split(r'\s*[!?.]\s*', line)

        for sentence in sentences:
            # clean and split sentences
            cleansentence = sentence.replace(",", "")
            cleansentence = cleansentence.replace(":", "")
            cleansentence = cleansentence.replace("\n", "")
            words = cleansentence.split(" ")



            # go through the words and search for significant parts
            for i, word in enumerate(words):
                # if word is long enough. To avoid empty strings and maybe other things
                if len(word) < 3:
                    data.append({"word": words[i],"count": -1})
                    continue
                # if word starts with an upper case character
                if word[0].isupper():
                    # TODO: adjust range to get good results
                    searchfor = ""
                    for j in xrange(-2,3):
                        try:
                            searchfor = searchfor + " " + str(words[i+j])
                        except IndexError:
                            pass
                    count = googlesearch(searchfor)
                    data.append({"word": words[i],"count": count})
                else:
                    data.append({"word": words[i],"count": -1})
    fd.close()
    return data


def outputtohtml(path, data):
    """output data to html"""
    fd = open(path, 'w')

    fd.write('<html>')
    fd.write('<head>')
    fd.write('<title>sample_data_1</title>')
    fd.write('<meta name="generator" content="pyplag">')
    fd.write('<meta http-equiv="content-type" content="text/html; charset=UTF-8">')
    fd.write('<meta http-equiv="content-style-type" content="text/css">')
    fd.write('<link href="./screen.css" rel="stylesheet" type="text/css" media="screen">')
    fd.write('</head>')
    fd.write('<body>')

    fd.write('<div id="legend">')
    fd.write('<table>')
    fd.write('<tr><td><span class="above0">Über ' + str(THRESH_ABOVE0) + ' gefundene Stellen</span></td></tr>')
    fd.write('<tr><td><span class="above2">Über ' + str(THRESH_ABOVE2) + ' gefundene Stellen</span></td></tr>')
    fd.write('<tr><td><span class="above5">Über ' + str(THRESH_ABOVE5) + ' gefundene Stellen</span></td></tr>')
    fd.write('<tr><td><span class="above10">Über ' + str(THRESH_ABOVE10) + ' gefundene Stellen</span></td></tr>')
    fd.write('</table>')
    fd.write('</div>')
    fd.write('<div id="text">')



    # TODO: don't do the color thing on a word basis, but on a substring basis
    for entry in data:
        if entry["count"] > THRESH_ABOVE10:
            spanclass = "10"
            fd.write('<span class="above' + spanclass + '">' + entry["word"] + '</span> ')
        elif entry["count"] > THRESH_ABOVE5 and entry["count"] <= THRESH_ABOVE10:
            spanclass = "5"
            fd.write('<span class="above' + spanclass + '">' + entry["word"] + '</span> ')
        elif entry["count"] > THRESH_ABOVE2 and entry["count"] <= THRESH_ABOVE5:
            spanclass = "2"
            fd.write('<span class="above' + spanclass + '">' + entry["word"] + '</span> ')
        elif entry["count"] > THRESH_ABOVE0 and entry["count"] <= THRESH_ABOVE2:
            spanclass = "0"
            fd.write('<span class="above' + spanclass + '">' + entry["word"] + '</span> ')
        else:
            fd.write(entry["word"] + ' ')

    fd.write('</div>')
    fd.write("</body>")
    fd.write("</html>")


def googlesearch(searchfor):
    # TODO: this parser depends on the language of the result page. This _has_ to be improved!!!
    """use http google site to search"""
    url = 'http://www.google.de/search?hl=de&q=%22' + urllib.quote(str(searchfor)) + '%22'

    # set user agent, so we won't get banned...
    userAgents = (
        'Opera/9.80 (X11; Linux i686; U; de) Presto/2.10.229 Version/11.64',
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729',
        'Mozilla/5.0 (Windows NT 5.2; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0',
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.21 Safari/536.11',
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.2)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.3; ips-agent) Gecko/20090824 Fedora/1.0.7-1.1.fc4 Firefox/3.5.3',
        'Mozilla/5.0 (Windows NT 5.1; rv:12.0) Gecko/20100101 Firefox/12.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; ru; rv:1.9.2.3) Gecko/20100401 Firefox/3.6.3',
        'Opera/9.80 (Android; Opera Mini/7.0.29952/27.1993; U; de) Presto/2.8.119 Version/11.10)',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'
    )
    headers = { 'User-Agent' : random.choice(userAgents) }

#    headers = { 'User-Agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0' }
    request = urllib2.Request(url, None, headers)

    # open url
    search_response = urllib2.urlopen(request)
    search_results = search_response.read()

    temp1 = search_results.find("<div id=resultStats>")
    temp2 = search_results.find("Ergebnisse<nobr>")

    if temp1 != -1 and temp2 != -1:
        if search_results.find("Ungefähr") != -1:
            numstring = search_results[temp1 + 30:temp2 - 1]
        else:
            numstring = search_results[temp1 + 20:temp2 - 1]
        return int(numstring.replace(".",""))
    else:
        return 0


if __name__ == '__main__':
    pyplag()
