from Products.CMFCore.utils import getToolByName
from tempfile import mktemp
import os
import sys

def getPOT(self, wf_id=""):
    """ get the pot, copy from:
"dcworkfow2dot.py":http://awkly.org/Members/sidnei/weblog_storage/blog_27014
    """
    out = []
    transitions = {}

    if wf_id:
        w_tool = getToolByName(self, 'portal_workflow')
        wf = getattr(w_tool, wf_id)
    else:
        wf = self

    out.append('digraph "%s" {' % wf.title)
    for s in wf.states.objectValues():
        out.append('%s [shape=box,label="%s (%s)"];' % (s.getId(),
                                                    s.title,
                                                    s.getId().capitalize()))
        for t in s.transitions:
            try:
                trans = wf.transitions[t]
            except KeyError:
                out.append(('# transition %s from state %s '
                        'is missing' % (t, s.getId())))
                continue

            key = (s.getId(), trans.new_state_id)
            value = transitions.get(key, [])
            value.append(trans.actbox_name)
            transitions[key] = value

    for k, v in transitions.items():
        out.append('%s -> %s [label="%s"];' % (k[0], k[1],
                                           ', '.join(v)))

    out.append('}')
    return '\n'.join(out)

def getGraph(self, wf_id="", format="gif", REQUEST=None):
    """show a workflow as a graph, copy from:
"OpenFlowEditor":http://www.openflow.it/wwwopenflow/Download/OpenFlowEditor_0_4.tgz
    """
    pot = getPOT(self, wf_id)
    infile = mktemp('.dot')
    f = open(infile, 'w')
    f.write(pot)
    f.close()
    outfile = mktemp('.%s' % format)
    os.system('/usr/bin/dot -T%s -o %s %s' % (format, outfile, infile))
    out = open(outfile, 'r')
    result = out.read()
    out.close()
    os.remove(infile)
    os.remove(outfile)
    return result

