# python grcompile.py geoquery.scfg geoquery.cfg geoquery_sem.py

from __future__ import print_function
import sys
import re
from interpolate import s

def build_rule(consts, term):
    if consts:
        return 'inst("{0}", {1})'.format(consts[0], build_rule(consts[1:], term))
    else:
        return 's(r"{0}")'.format(term)


# set up REs
variable_re = re.compile(r"{([^}]*)}")
semrule_re = re.compile(r"%%\s*((?:[a-zA-Z0-9_]+:\s)*)(.*)")
split_re = re.compile("\s*:\s*")


# set up files
filename = sys.argv[1]
cfg_filename = sys.argv[2]
sem_filename = sys.argv[3]

cfg = open(cfg_filename, "w")
sem = open(sem_filename, "w")

semrules = []


# process input file
f = open(filename, "rU")
for _line in f.readlines():
    line = _line.strip()

    if line == "":
        # empty line => ignore
        pass
    elif line.startswith("#"):
        # comments
        pass
    elif line.startswith("%%"):
        # semantic rule
        children = sorted(variable_re.findall(line)) # find variables like {NP}

        if not children:
            args = "dummy"
        elif len(children) == 1:
            args = "({0},)".format(children[0])
        else:
            args = "(" + ",".join(children) + ")"

        r = semrule_re.search(line)
        constants_part = r.groups()[0]
        constants = filter(lambda x:x, split_re.split(constants_part))
        term = r.groups()[1]

        semrules.append('"{0}": lambda {1}: {2}'.format(cfg_line.replace("'",""),
                                                        args,
            build_rule(constants, term)))
    else:
        print(line, file=cfg)
        cfg_line = line

# create semantic rules file
print('''
from interpolate import s

gensym_next = 1

# TODO - replace by something that parses term first
def inst(x, term):
    global gensym_next
    new_x = x + str(gensym_next)
    gensym_next = gensym_next + 1
    return term.replace(x, new_x)

semrules = {{ {0} }}
'''.format(",\n".join(semrules)), file=sem)


