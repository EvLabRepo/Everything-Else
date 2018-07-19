import re
import numpy

file = open("doc.rtf", "r")
text = file.read()
spl = text.split()

file = open("endnote_database.txt", "r")
refs = file.read()
refspl = refs.split()
refspl_orig = refspl

file = open("refs.txt", "w")
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

        refspl=refspl[:-1]
        file = open("refs.txt","a")
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
