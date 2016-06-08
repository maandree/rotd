# -*- python -*-
# See LICENSE file for copyright and license details.

def documentclass(docclass, *vargs, **kwargs):
    opt = ','.join([str(x) for x in vargs] + ['%s=%s' % (k, str(kwargs[k])) for k in kwargs])
    if not opt == '':
        opt = '[' + opt + ']'
    return '\\documentclass%s{%s}\n' % (opt, docclass)

def usepackage(pkg, *vargs, **kwargs):
    opt = ','.join([str(x) for x in vargs] + ['%s=%s' % (k, str(kwargs[k])) for k in kwargs])
    if not opt == '':
        opt = '[' + opt + ']'
    return '\\usepackage%s{%s}\n' % (opt, pkg)


def pagestyle(style, *vargs, **kwargs):
    opt = ','.join([str(x) for x in vargs] + ['%s=%s' % (k, str(kwargs[k])) for k in kwargs])
    if not opt == '':
        opt = '[' + opt + ']'
    return '\\pagestyle%s{%s}\n' % (opt, style)


def begin(cmd, *vargs):
    opt = ''.join('{' + str(x) + '}' for x in vargs)
    return '\\begin{%s}%s' % (str(cmd), opt)
def end(cmd):
    return '\\end{%s}' % str(cmd)


def ln(*text):
    return '\n'.join(text) + '\\\\\n'


def Huge(text, end = '\n'):
    return '{\\Huge %s}%s' % (str(text), str(end))
def huge(text, end = '\n'):
    return '{\\huge %s}%s' % (str(text), str(end))
def LARGE(text, end = '\n'):
    return '{\\LARGE %s}%s' % (str(text), str(end))
def Large(text, end = '\n'):
    return '{\\Large %s}%s' % (str(text), str(end))
def large(text, end = '\n'):
    return '{\\large %s}%s' % (str(text), str(end))
def normalsize(text, end = '\n'):
    return '{\\normalsize %s}%s' % (str(text), str(end))
def small(text, end = '\n'):
    return '{\\small %s}%s' % (str(text), str(end))
def footnotesize(text, end = '\n'):
    return '{\\footnotesize %s}%s' % (str(text), str(end))
def scriptsize(text, end = '\n'):
    return '{\\scriptsize %s}%s' % (str(text), str(end))
def tiny(text, end = '\n'):
    return '{\\tiny %s}%s' % (str(text), str(end))


def normal(text, end = '\n'):
    return '\\textnormal{%s}%s' % (str(text), str(end))
def emph(text, end = '\n'):
    return '\\emph{%s}%s' % (str(text), str(end))
def rm(text, end = '\n'):
    return '\\textrm{%s}%s' % (str(text), str(end))
def sf(text, end = '\n'):
    return '\\textsf{%s}%s' % (str(text), str(end))
def tt(text, end = '\n'):
    return '\\texttt{%s}%s' % (str(text), str(end))
def up(text, end = '\n'):
    return '\\textup{%s}%s' % (str(text), str(end))
def it(text, end = '\n'):
    return '\\textit{%s}%s' % (str(text), str(end))
def sl(text, end = '\n'):
    return '\\textsl{%s}%s' % (str(text), str(end))
def sc(text, end = '\n'):
    return '\\textsc{%s}%s' % (str(text), str(end))
def uppercase(text, end = '\n'):
    return '\\uppercase{%s}%s' % (str(text), str(end))
def bf(text, end = '\n'):
    return '\\textbf{%s}%s' % (str(text), str(end))
def md(text, end = '\n'):
    return '\\textmd{%s}%s' % (str(text), str(end))
def lf(text, end = '\n'):
    return '\\textlf{%s}%s' % (str(text), str(end))
