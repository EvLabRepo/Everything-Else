import subprocess
import os
import requests
import re
import sys
import time
import numpy
import unicodedata
from googlesearch import search

file = open("doc.rtf", "r")
text = file.read()
spl = text.split()

file = open("endnote_database.txt", "r")
refs = file.read()
refspl = refs.split()
refspl_orig = refspl

file = open("refs.txt","w")
file.close()

#get years
years = []
for year in range(1800,2019):
    inds = [i for i, j in enumerate(spl) if str(year) in j]
    if len(inds) > 0:
        for ind in inds:
            years.append(ind)

cites = [];
cformat= [];
for y in years:
    spl = text.split()
    #Isolate year string
    stryear = spl[y]
    cind = 0
    c1 = 0
    c2 = 0
    c3 = 0
    for c in stryear:
        cind=cind+1
        if '(' in c:
            c1 = cind
        if ')' in c or  ',' in c or ';' in c:
            c2 = cind
            break
        elif 'a' in c or 'b' in c or 'c' in c:
            c3 = cind
            break

    if c2 > 0:
        sy = stryear[:c2-1]
    if c3 > 0:
        sy = stryear[:c3]
    if c1 == 0 and c2 == 0 and c3 == 0:
        sy = stryear
    if c1 > 0:
        sy = sy[1:]

    #DETERMINE FORMAT
    
    #Author, year
    a = 0
    while a == 0:
        yearf = 0
        for year in range(1800,2018):
            if str(year) in spl[y-1]:
                yearf = 1
                spl[y-6:y] = spl[y-7:y-1]

        break
    
    #Author et al year
    if 'al' in spl[y-1] and 'et' in spl[y-2]:
        spl3 = spl[y-3]
        if '\i' in spl3:
            spl3 = spl[y-5]
        if spl3[0] == '(':
            spl3 = spl3[1:]
        phrase = spl3 + ' ' + spl[y-2] + ' ' + spl[y-1] + ' ' + sy
        phrase=re.sub(',','',phrase)
        phrase=re.sub('al ','al. ',phrase)
        phrase=re.sub("\'f1","n",phrase)
        phrase=re.sub(" and "," & ",phrase)
        diginds = [i for i, j in enumerate(phrase) if j.isdigit()]
        if len(diginds) > 0:
            diginds=numpy.max(diginds)
            phrase=phrase[:diginds+1]
        else:
            continue
        cformat.append('aea')
        cites.append(phrase + ' aea')

    #Author & author year
    elif '&' in spl[y-2] or 'and' in spl[y-2]:
        spl3 = spl[y-3]
        if '\i' in spl3:
            spl3 = spl[y-5]
        if spl3[0] == '(':
            spl3 = spl3[1:]
        phrase = spl3 + ' ' + spl[y-2] + ' ' + spl[y-1] + ' ' + sy
        phrase=re.sub(',','',phrase)
        phrase=re.sub('al ','al. ',phrase)
        phrase=re.sub("\'f1","n",phrase)
        phrase=re.sub(" and "," & ",phrase)
        diginds = [i for i, j in enumerate(phrase) if j.isdigit()]
        if len(diginds) >0:
            diginds=numpy.max(diginds)
            phrase=phrase[:diginds+1]
        else:
            continue
        cformat.append('ana')
        cites.append(phrase + ' ana')

    #Author, year if otherwise
    else:
        phrase = spl[y-1] + ' ' + sy
        phrase=re.sub(',','',phrase)
        phrase=re.sub('al ','al. ',phrase)
        phrase=re.sub('[(]','',phrase)
        phrase=re.sub("\'f1","n",phrase)
        phrase=re.sub(" and "," & ",phrase)
        diginds = [i for i, j in enumerate(phrase) if j.isdigit()]
        if len(diginds) >0:
            diginds=numpy.max(diginds)
            phrase=phrase[:diginds+1]
        else:
            continue
        cformat.append('ayy')
        cites.append(phrase + ' ayy')

cites=set(cites)
cites=sorted(cites)



#Search endnote txt file

found=[]
notfound=[]
ind=0
for cite in cites[0:len(cites)]:
    #Get citation and format
    cite=cite[:-4]
    ind=ind+1
    form=cite[:3]
    cspl = cite.split()
    auth=str(cspl[0])
    auth = re.sub(',','',auth)
    year=str(cspl[-1])
    stop=0
    
    #reset refs
    refspl=refspl_orig
    
    #find author
    authind = [s for s in refspl if auth in s]
    authind = [i for i, e in enumerate(refspl) if auth in e]
    
    if len(authind) == 0:
        notfound.append(cite)
        continue
    
    got=0
    for ai in authind:
        refspl=refspl_orig
        ai = int(ai)
        temp=refspl[ai:]
        
        ss = [i for i, e in enumerate(temp) if '\\' in e]
        ss=numpy.min(ss)
        refspl = temp[:ss+1]
        
        #find year
        yearind = [i for i, e in enumerate(refspl) if year in e]

        if len(yearind) == 0:
            continue
        else:
            yearind = int(yearind[0])
       
       #exclusions
        if yearind < 5 and (form == 'aea' or form == 'ana'):
            continue
        if yearind > 4 and form == 'ayy':
            continue
        if form == 'ana' and "&" not in refspl[2:5] and " and " not in refspl[2:5]:
            continue


        refspl = ' '.join(refspl)
        refspl=str(refspl)
        
        caps1 = re.findall('([0-9][a-e][()])', refspl)
        for c in caps1:
            refspl = refspl.replace(c,c[0]+c[2])

        refspl=refspl[-10:]
        file = open("refs_to_keep.txt","a")
        file.write(refspl)
        file.write('\n')
        file.write('\n')
        found.append(cite)
        got=1
        break
        
    if got == 0:
        notfound.append(cite)


print '\n\n'
print 'FOUND THESE'
print '\n'
for f in found:
    print f
print '\n'
print '\n\n\n'

print 'DID NOT FIND THESE'
print '\n'
for c in notfound:
    print c

print '\n'

#
#cites=notfound
#
#
##Google each citation
#goodcount = 0
#cite_ind = []
#found1=[]
#ind=0
#for cite in range(0,len(cites)):
#    ind=ind+1
#    cite1 = cites[cite]
#    cite1f = re.sub(',', '', cite1)
##    if 'Broca' not in cite1f:
##        h=6
##        #continue
#    sp = cite1f.find(' ')
#    auth = cite1f[:sp]
#    yearsl = cite1f[-8:]
#    if '/' in yearsl:
#        year = cite1f[-9:-5]
#    else:
#        year = cite1f[-4:]
#
#    if year[-1:] == 'a' or year[-1:] == 'b' or year[-1:] == 'c':
#        year = cite1f[-5:]
#
#    cite1f = '\"' + cite1 + '\"' + ' language brain'
#
#    cite1 = re.sub(',', '', cite1)
#    print cite1
#
#    bashCommand = 'googler  \"' + cite1 + '\"' 
#    bashCommand = bashCommand + ' language brain'
#    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
#    output, error = process.communicate()
#    output = re.sub(',', '', output)
#    output = re.sub('[()]', '', output)
#
#    #Look for ref by looping through URLs
#    stop = 0
#    while stop == 0:
#        match = output.find(cite1)
#        print match
#        #if AND appears before
#        if 'and' in output[match-6:match]:
#            output = output[match+10:]
#            continue
#        chunk = output[:match+10]
#        url1 = chunk.rfind('http')
#        if url1 == -1:
#            stop=1
#            break
#        url_match = chunk[url1:]
#        space1 = url_match.find('\n')
#        ss = url_match.find('//')
#        url = url_match[:space1-2]
#        sp = url.find(' ')
#        url = url[:sp-1]
#        output = output[match+10:]
#        print url
#
#        print ' '
#
#        if 'onlinelibrary' in url and 'doi' in url and 'pdf' not in url:
#            print url
#            
#            print ' '
#            page = requests.get(url).content
#            #time.sleep(25)
#            ref_ind = page.find('LITERATURE CITED')
#            if ref_ind == -1:
#                ref_ind = page.find('Citing Literature')
#            if ref_ind == -1:
#                continue
#            page = page[ref_ind:]
#            #page = re.sub('<[^<]+?>', '', page)
#            page = re.sub('&#x02019;', "'", page)
#            #print page
#
#            auth_stop = 0
#            while auth_stop == 0:
#                auth_ind = page.find(auth)
#                #print page[auth_ind-30:auth_ind]
#                #print page[auth_ind:auth_ind+60]
#                if auth_ind == -1:
#                    stop = 1
#                    break
#                if '<li data-bib-id="bib' in page[auth_ind-150:auth_ind] and year in page[auth_ind:auth_ind+150]:
#                    page = page[auth_ind:auth_ind+400]
#                    break
#                else:
#                    page = page[auth_ind+10:]
#                    continue
#
#            #Parse HTML
#            auths = page[:page.find('.')]
#            page = page[page.find('</span>.')+5:]
#            journ = page[page.find('<i>')+3:page.find('</i>')]
#            vol = page[page.find('vol">')+5:page.find('</span>:')]
#            tit = page[page.find('Title')+7:page.find('</span>.')]
#            pgs = page[page.find('</span>:')+8:page.find('</span>:')+50]
#            print auths
#            print year
#            print tit
#            print journ
#            print vol
#            pgs = re.sub(' ','',pgs)
#            pgs = re.sub('\n','',pgs)
#            #pgs = re.sub('.','',pgs)
#            print pgs
#            print ' '
#                
#            refer1 = auths + '. (' + year + '). ' + tit + '. '
#            refer2 = '. ' + vol + ': ' + pgs
#            journ = '"""{\\\\rtf1 \\\i' + ' ' + journ + ' ' + '\\\i0}"""'
#            print refer1
#        
##refer = refer.encode("UTF-8")
#            refile = open("refs.txt","a")
#            refile.write(cite1)
#            refile.write('\n')
#            refile.write('\n')
#            refile.write(refer1)
#            refile.write(eval(journ))
#            refile.write(refer2)
#            refile.write('\n')
#            refile.write('\n')
#            refile.write('\n')
#            refile.write('\n')
#            goodcount = goodcount+1
#            stop=1
#            print ' '
#            print 'got ', str(goodcount), ' out of ', str(cite+1)
#            print ' '
#            cite_ind.append(cite)
#
#
#
#
#
#        elif 'ncbi' in url and 'articles' in url:
#        
#            print url
#
#            print ' '
#            page = requests.get(url).content
#            #time.sleep(25)
#            ref_ind = page.find('References')
#            if ref_ind == -1:
#                ref_ind = page.find('LITERATURE CITED')
#            if ref_ind == -1:
#                continue
#            page = page[ref_ind:]
#            
#            page = re.sub('<[^<]+?>', '', page)
#            page = re.sub('&#x02019;', "'", page)
#           
#            auth_stop = 0
#            while auth_stop == 0:
#                auth_ind = page.find(auth)
#                if auth_ind == -1:
#                    stop = 1
#                    break
#                page = page[auth_ind:]
#                y_inds = []
#                if page[len(auth)+1].isupper() and page[len(auth)] == ' ':
#                    for y in range(1800,2018):
#                        if page.find(str(y)) > -1:
#                            y_inds.append(page.find(str(y)))
#                    year_i = page.find(year)
#                    if numpy.min(y_inds) < year_i:
#                        page = page[10:]
#                        continue
#                    else:
#                        auth_stop=1
#                
#                else:
#                    page = page[auth_ind+10:]
#                    continue
#
#
#            if stop == 0:
#                ref = page[:1000]
#                ref = re.sub('&#x0201c;', '"', ref)
#                ref = re.sub('&#x0201d;', '"', ref)
#                ref = re.sub('&#x02013;', '-', ref)
#                #Get title
#                for i in range(0,200):
#                    ref1 = ref
#     
#                    if ref1[i] == '.' and ref1[i+1] == ' ' and ref1[i+2].isupper() and '.' not in ref1[i+3]:
#                        yi = i+2
#                        ref1 = ref1[i+2:]
#                        pdot = ref1.find('.')
#                        tit = ref1[:pdot]
#                        tit_ind = i
#                        break
#                    if ref1[i] == '.' and ref1[i+1] == ' ' and ref1[i+2] == '"':
#                        yi = i+3
#                        ref1 = ref1[i+3:]
#                        pdot = ref1.find(',"')
#                        tit = ref1[:pdot]
#                        tit_ind = i
#                        break
#                    if ref1[i] == ')' and ref1[i+1] == ' ' and ref1[i+2].isupper() and '.' not in ref1[i+3]:
#                        yi = i+2
#                        ref1 = ref1[i+2:]
#                        pdot = ref1.find('.')
#                        tit = ref1[:pdot]
#                        tit_ind = i
#                        break
#                    if ref1[i] == '.' and ref1[i+1] == ' ' and ref1[i+2] == ' ' and ref1[i+3].isupper() and '.' not in ref1[i+4]:
#                        yi = i+2
#                        ref1 = ref1[i+2:]
#                        pdot = ref1.find('.')
#                        tit = ref1[:pdot]
#                        tit_ind = i
#                        break
#
#
#                #Get authors
#                auths = ref[:tit_ind]
#                regex = re.compile("[^a-zA-Z -']")
#                auths = regex.sub('', auths)
#                if auths[-1:].islower():
#                   auths = auths[:-1]
#                print 'Authors:', auths
#                print ' '
#                print 'title:', tit
#                print ' '
#                print 'year:', year
#
#                #Get issue and page
#                yind = ref.find(year)
#                ref1 = ref[yind+5:]
#                ref1 = unicode(ref1, 'utf-8')
#                #method1
#                a = 0
#                found = 0
#                for i in range(0,250):
#                    if ref1[i].isnumeric():
#                        vol_ind = i
#                        vol = ref1[vol_ind:vol_ind+25]
#                        vol = re.sub('&#x02013;', '-', vol)
#                        vol = re.sub(',', ':', vol)
#                        vol = re.sub('\n', ':', vol)
#                        pdot1 = vol.find('10.1')
#                        if pdot1 == -1:
#                            pdot1 = vol.find('.')
#                        vol = vol[:pdot1]
#                        vol = vol.replace(" ","")
#                        print vol
#                        diginds = [i for i, j in enumerate(vol) if j.isdigit() or ":" in j or "(" in j or ")" in j]
#                        print diginds
#                        noninds=set(range(len(vol)))-set(diginds)
#                        if len(noninds) > 0:
#                            noninds=list(noninds)
#                            noninds=str(noninds)
#                            noninds=noninds.replace("[","")
#                            noninds=noninds.replace("]","")
#                            noninds=int(noninds)
#                            vol = vol[:noninds-1] + '-' + vol[noninds+1:]
#                        print vol
#                        found = 1
#                        print vol
#                        break
#
#                if found == 0:
#                    print ref1[:1000]
#                
#                #See if vol is actually year of next entry
#                skip_journ = 0
#                vol_y_inds = []
#                for stryear in range(1800,2018):
#                    if str(stryear) in vol[0:4]:
#                        skip_journ = 1
#                        ref1 = ref[yi+pdot+2:]
#                        pdot2 = ref1.find('.')
#                        refer = ref[:yi+pdot+2+pdot2]
#                        print 'ay'
#                        print refer
#
#                #fix auths
#                caps1 = re.findall('([A-Z] )', auths)
#                for c in caps1:
#                    auths=re.sub(c,c[0]+'., ',auths)
#
#                caps2 = re.findall('([A-Z][A-Z])', auths)
#                for c in caps2:
#                    auths=re.sub(c,c[0]+'. '+c[1],auths)
#
#                caps3 = re.findall('([a-z] )', auths)
#                for c in caps3:
#                    auths=re.sub(c,c[0]+', ',auths)
#
#
#                if skip_journ == 0:
#                    #Get journal
#                    ref1 = ref[yi:]
#                    ref1 = re.sub(' pp.', ' ', ref1)
#                    ref1 = re.sub('J.', 'J', ref1)
#                    #tit_ind = ref1.find(tit_ind)
#                    year_ind = ref1.find(year)
#                    if year_ind == -1:
#                        year_ind = ref1.find(vol)
#                    journ = ref1[pdot+2:year_ind]
#                    print journ
#                    journ = journ.replace(".","")
#                    journ = journ[:-1]+'.'
#                    #print journ
#                    if len(journ) == 0:
#                        refer = auths + '. (' + year + '). ' + tit + '. ' + journ + vol
#                        journ = '"""\\\\rtf1 \\\i' + ' ' + journ + '\\\i0"""'
#                    else:
#                        print 'Journal:', journ
#                        print
#                        print 'Volume:', vol
#                        refer = auths + '. (' + year + '). ' + tit + '. ' + journ + vol
# 
#
#
#                refer = refer.encode("UTF-8")
##refer2 = refer2.encode("UTF-8")
#                refile = open("refs_to_add.txt","a")
#                refile.write(cite1)
#                refile.write(r'\line')
#                refile.write(r'\line')
#                refile.write(' ' + refer)
#                refile.write(r'\line')
#                refile.write(r'\line')
#                if ind == 1:
#
##file.close()
#                goodcount = goodcount+1
#                stop=1
#                print ' '
#                print 'got ', str(goodcount), ' out of ', str(cite+1)
#                cite_ind.append(cite)
#                found1.append(cite)
#                print found1
#
#
#
#
#
#                
#        else:
#            continue
#
#
#citesfound1 = [i for j, i in enumerate(cites) if j not in found1]
#citesleft = [i for j, i in enumerate(cites) if j  in found1]
#print '\n'
#print '\n'
#for cf in citesfound1:
#    print cf
#print '\n'
#print '\n'
#for cl in citesleft:
#    print cl


























