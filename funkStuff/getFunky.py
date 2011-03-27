#!/usr/bin/env python
# coding=UTF-8

import getopt, sys, re

def usage():
    print """
Usage: getFunky.py [OPTION...] [VALUE]
Rechnet entweder anhand --min und --max ODER VALUE die passenden Werte aus.
--min und --max dürfen nur in hz (khz,mhz,thz) angegeben werden!
VALUE kann in hz (khz,mhz,thz) oder m (mm, cm, km) angegeben werden!
In beiden fällen muss das Wertezeichen hinzu. Werte wie 100 sind ungültig.
Kommazahlen und Tausendertrennzeichen werden angenommen.
Bsp.: 
getFunky.py --min=400mhz --max=460mhz
oder
getFunky.py 70cm
oder
getFunky.py 102,8mhz

========================================================================

  -h, --help\t\tdisplay this help and exit
  -c	\t\tVerkürzt die Wellenlänge um den Faktor 0.97 (Antennbau Kupferdraht)
      --min=WERT\tRechnet anhand min und max den Frequenzmittelwert und die passende Wellenlänge
      --max=WERT\tgehört zu --min. Es müssen beide oder keiner der Werte gegeben sein
      --out-hz=EINHEIT\tFormat für die Ausgabe der Frequenzen (Default: hz)
      --out-m=EINHEIT\tFormat für die Ausgabe der Wellenlänge (Default: m)
  -2	\t\tgibt zusätzlich noch Lambda (Wellenlänge) / 2 aus
  -4    \t\tgibt zusätzlich noch Lambda (Wellenlänge) / 4 aus
  -8    \t\tgibt zusätzlich noch Lambda (Wellenlänge) / 8 aus
    
"""

def parseValue(rawArgument):

    values = re.match(r'([0-9,\.]+)([a-zA-Z]+)', rawArgument)
    
    if not values:
        return False
    
    number = values.group(1)
    type = values.group(2)
    
    number = number.replace('.', '')
    number = number.replace(',', '.')
    number = float(number)
        
    type = type.lower()
    
    if type in ['hz', 'khz', 'mhz', 'ghz', 'thz']:
        if type == 'khz':
            number = number * 1000
        elif type == 'mhz':
            number = number * 1000000
        elif type == 'ghz':
            number = number * 1000000000
        elif type == 'thz':
            number = number * 1000000000000
        
        type = 'hz'    
    elif  type in ['mm', 'cm', 'm', 'km']:
        if type == 'mm':  
            number = number / 1000
        elif type == 'cm':
            number = number / 100
        elif type == 'km':
            number = number * 1000
                    
        type = 'm'        
    else:
        return False
    

    return {'val': number, 'type': type}


def getFormat(value, newFormat):

    type = newFormat
    number = value['val']

    if type in ['hz', 'khz', 'mhz', 'ghz', 'thz']:
        if type == 'khz':
            number = number / 1000
        elif type == 'mhz':
            number = number / 1000000
        elif type == 'ghz':
            number = number / 1000000000
        elif type == 'thz':
            number = number / 1000000000000
        
    elif  type in ['mm', 'cm', 'm', 'km']:
        if type == 'mm':  
            number = number * 1000
        elif type == 'cm':
            number = number * 100
        elif type == 'km':
            number = number / 1000
    else:
        return value
        
    return {'val': number, 'type': type}      

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ch248", ["help", "min=", "max=", "out-hz=", "out-m="])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(2)
    
    verkuerzung = 1
    schall = 299792458
    min = False
    max = False
    outHz = False
    outM = False
    halbe = False
    viertel = False
    achtel = False
    einhHz = 'hz'
    einhm = 'm'
      
   
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o == '-c':
            verkuerzung = 0.97
        elif o == '--min':
            min = parseValue(a)
        elif o == '--max':
            max = parseValue(a)
        elif o == '--out-hz':
            einhHz = a.lower()
        elif o == '--out-m':
            einhm = a.lower()
        elif o == '-2':
            halbe = True
        elif o == '-4':   
            viertel = True
	elif o == '-8':   
            achtel = True
        else:
            assert False, "unhandled option"

    if len(args) == 1:
        val = parseValue(args[0])
    else:
        val = None
    
    if min and max:
        if min['type'] == 'hz' and max['type'] == 'hz':
            outHz = max['val'] - min['val']
            outHz = outHz / 2
            outHz = outHz + min['val']
            outHz = {'val': outHz, 'type': 'hz'}
            outM = {'val': schall / outHz['val'], 'type': 'm'}
        else:
            usage()
            sys.exit(-1)
    elif val:
        if val['type'] == 'hz':
            min = val
            max = val
            outHz = val
            outM = {'val': schall / val['val'], 'type': 'm'}
        elif val['type'] == 'm':
            min = None
            max = None
            outM = val
            outHz = {'val': schall / val['val'], 'type': 'hz'}
       
    else:
        usage()
        sys.exit(-1)

    print ""
    
    if verkuerzung != 1:
        print "ACHTUNG! Die Wellenlänge enthält den Verkürzungsfaktor von einfachen Kupferdraht (%f)" % verkuerzung
        outM['val'] = outM['val']*verkuerzung

    outHz = getFormat(outHz, einhHz)
    outM = getFormat(outM, einhm)        
    
    if min and max:
        min = getFormat(min, einhHz)
        max = getFormat(max, einhHz)
        print "Minimum Freq:\t%f %s" % (min['val'], min['type'])
        print "Maximum Freq:\t%f %s" % (max['val'], min['type'])

    print "Mittel Freq:\t%f %s" % (outHz['val'], outHz['type'])
    print "Wellenlänge:\t%f %s" % (outM['val'],outM['type'])    

    if halbe:
        halbe = outM['val'] / 2
        print "Wellenlänge/2:\t%f %s" % (halbe, outM['type'])
    if viertel:
        viertel = outM['val'] / 4
        print "Wellenlänge/4:\t%f %s" % (viertel, outM['type'])
    if achtel:
        achtel = outM['val'] / 8
        print "Wellenlänge/8:\t%f %s" % (achtel, outM['type'])
        
    print ""

if __name__ == "__main__":
    main()
