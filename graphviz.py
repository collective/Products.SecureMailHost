"""
PloneCollectorNG - A Plone-based bugtracking system

(C) by Andreas Jung, andreas@andreas-jung.com & others

Published under the Zope Public License

$Id: graphviz.py,v 1.2 2003/09/30 15:10:24 ajung Exp $
"""

##########################################################################
# This module creates a graphical representation of the
# issue references using the graph drawing tool Graphviz
# available from www.research.att.com/sw/tools/graphviz
##########################################################################

import os, tempfile
from urllib import unquote

def issue2id(issue):
    """ convert an issue to an ID """
    url = unquote(issue.absolute_url(1))
    url = url.replace('/', '_')
    url = url.replace(' ', '_')
    return url

def collector2id(collector):
    """ convert an collector to an ID """
    id = unquote(collector.absolute_url(1))
    id = id.replace('/', '_')
    id = id.replace(' ', '_')
    return (id, collector.title_or_id()) 


class Node:
    """ simple node class """

    def __init__(self, issue):
        self.id = issue2id(issue)
        self.url = issue.absolute_url(1)
        self.collector_url = issue.aq_parent.absolute_url(1)
        self.text = '%s: %s' % (issue.getId(), issue.Title())

    def __str__(self):
        return self.id

class Edge:
    """ simple edge class """
    
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __cmp__(self, o):
        return self.src==o.src and self.dest==o.dest

    def __str__(self):
        return '%s -> %s' % (self.src, self.dest)


def build_tree(issue, graphs={}, nodes=[], edges=[]):
    """ build a dependency tree for all references """

    node = Node(issue)
    if not node.id in [n.id for n in nodes]:
        nodes.append(node)
    else:
        return   # stop recursion

    collector_id = collector2id(issue.aq_parent)
    if not graphs.has_key(collector_id):
        graphs[collector_id] = []

    if not node.id in graphs[collector_id]:
        graphs[collector_id].append(node)
    
    for ref in issue.getRefs():
        from urllib import unquote
        ref_issue = issue.unrestrictedTraverse(unquote(ref.absolute_url(1)))
        e = Edge(node, Node(ref_issue)) 
        edges.append(e) 
        build_tree(ref_issue, graphs, nodes, edges)

    return graphs, nodes, edges


def build_graphviz(graphs, nodes, edges):
    """ Graphviz generation """

    external_edges = []

    fname = tempfile.mktemp()
    fp = open(fname, 'w')
    print >>fp, 'digraph G {'
    for graph in graphs.keys():
        print >>fp, '\tsubgraph cluster_%s {' % graph[0]

        for e in edges:
            if e.src.id.startswith(graph[0]) and e.dest.id.startswith(graph[0]):
                print >>fp, '\t\t"%s" -> "%s";' % (e.src.text, e.dest.text)
            elif e.src.id.startswith(graph[0]):
                    external_edges.append( e )

        print >>fp, '\t\tlabel="%s";' % graph[1]
        print >>fp, '\t}\n'

    for e in external_edges:
        print >>fp, '\t"%s" -> "%s";' % (e.src.text, e.dest.text)

    print >>fp, '}'
    fp.close()
    return fname

def viz2image(fname, format='gif', RESPONSE=None):

    outputname = tempfile.mktemp()
    st = os.system('dot -Gpack -T %s  %s > %s' % (format, fname, outputname))
    if st != 0: raise RuntimeError('graphviz execution failed')     
    data = open(outputname).read()

    if format in ('svg',):
        RESPONSE.setHeader('content-type', 'image/svg+xml')
    if format in ('ps',):
        RESPONSE.setHeader('content-type', 'application/postscript')
    else:
        RESPONSE.setHeader('content-type', 'image/%s' % format)
    RESPONSE.write(data)

def viz2map(fname, format='cmap', RESPONSE=None):

    outputname = tempfile.mktemp()
    st = os.system('dot -T %s  %s > %s' % (format, fname, outputname))
    if st != 0: raise RuntimeError('graphviz execution failed')     
    data = open(outputname).read()

    if format in ('svg',):
        RESPONSE.setHeader('content-type', 'image/svg+xml')
    else:
        RESPONSE.setHeader('content-type', 'image/%s' % format)
    RESPONSE.write(data)
