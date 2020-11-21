import csv
import logging
import argparse

#============================================
class Row() :
  def __init__(self,row) :
    logging.debug("<" + row['depth'] +">")
    self.id=row['id'].strip()
    self.depth=row['depth'].strip()
    self.desc=row['desc'].strip() if row['desc'] else ''
    self.start=row['start'].strip() if row['start'] else '' 
    self.end=row['end'].strip() if row['end'] else ''
    self.who=row['who'].strip() if row['who'] else ''
    self.statusValues={
     'unknown' : 0,
     'backlog' : 1,
     'running' : 2,
     'done'    : 3
    }
    status=row['status'].strip().lower() if row['status'] else ''
    self.setStatus(status)
    #self.statusNum=self.statusValues[self.status] if self.status in self.statusValues else 0
    logging.debug("<" + self.depth +">")
    logging.warning("<" + self.toString() +">")
   

  def getDepth(self) :
    return(self.depth)
  def getStart(self) :
    return(self.start)
  def getEnd(self) :
    return(self.end)
  def getDesc(self) :
    return(self.desc)
  def getStatus(self) :
    return(self.status)
  def getStatusNum(self) :
    return(self.statusNum)
  def getWho(self) :
    return(self.who)
  def getId(self) :
    return(self.id)

  def setStart(self,start) :
    self.start=start
  def setEnd(self,end) :
    self.end=end
  
  def setStatus(self,status) :
    self.status=status
    self.statusNum=self.statusValues[self.status] if self.status in self.statusValues else 0

  def toString(self) :
    return("{:50s} {:12s} {:10s} {:10s} {:20s} {:8s} {:d} ".format(
      self.getDesc(),
      self.getId(),
      self.getStart(),
      self.getEnd(),
      self.getWho(),
      self.getStatus(),
      self.getStatusNum(),
    ))

#============================================
class Node() :
  def __init__(self,parent,level,row) :
    self.parent=parent
    self.children=[]
    self.row=row
    self.level=level

  def getChildren(self) :
    return(self.children)
  def addChild(self,node) :
    return(self.children.append(node))
  def getLevel(self) :
    return(self.level)
  def getRow(self) :
    return(self.row)

  def toString(self) :
    return("{:d} {:s}".format(
      self.getLevel(),
      self.getRow().toString()
    ))

#============================================
class Tree() :
  def __init__(self) :
    self.root=None
  def setRoot(self,node) :
    self.root=node
  def getRoot(self) :
    return(self.root)

#============================================
class TreeBuilder() :

  def __init__(self,tree) :
    self.tree=tree
    self.currentNode=None

  def addToTree(self,row) :
    if self.currentNode :
      # Tree exists
      upCount=len(row.getDepth()) - self.currentNode.getLevel() -1 
      for i in range(1,upCount) :
        self.currentNode=self.currentNode.getParent()
      node=Node(self.currentNode,len(row.getDepth())-1,row)
      self.currentNode.addChild(node)
      self.currentNode=node
    else :
      # Create the root !
      self.currentNode=Node(None,0,row)
      self.tree.setRoot(self.currentNode)

#============================================
class Percolator() :

  def __init__(self,args,tree) :
    self.args=args
    self.tree=tree
    print("Initial")
    self.display(tree.getRoot())
    self.percolate(tree.getRoot())
    print("Final")
    self.display(tree.getRoot())

  #----------------------------------------------------
  def parentToChild(self,parent,child) :

    if child.getRow().getStart() :
      if child.getRow().getStart() < parent.getRow().getStart() :
        logging.warning(child.getRow().getDesc() + " start date too small")
        if self.args.fix :
          logging.warning("Fixing")
          child.getRow().setStart(parent.getRow().getStart())
      else :
        logging.debug(child.getRow().getDesc() + " start date coherent")
    else :
      logging.debug(child.getRow().getDesc() + " start not set")
      child.getRow().setStart(parent.getRow().getStart())

    if child.getRow().getEnd() :
      if child.getRow().getEnd() > parent.getRow().getEnd() :
        logging.warning(child.getRow().getDesc() + " end date too high")
        if self.args.fix :
          logging.warning("Fixing")
          child.getRow().setEnd(parent.getRow().getEnd())
      else :
        logging.debug(child.getRow().getDesc() + " end date coherent")
    else :
      logging.debug(child.getRow().getDesc() + " end not set")
      child.getRow().setEnd(parent.getRow().getEnd())

    if child.getRow().getStatus() :
      if child.getRow().getStatusNum() > 0 and child.getRow().getStatusNum() < parent.getRow().getStatusNum() :
        logging.warning(child.getRow().getDesc() + " status " + child.getRow().getStatus() + " too high " + parent.getRow().getStatus())
        if self.args.fix :
          logging.warning("Fixing")
          child.getRow().setStatus(parent.getRow().getStatus())
      else :
        logging.debug(child.getRow().getDesc() + " status coherent")
    else :
      logging.debug(child.getRow().getDesc() + " status not set")
      child.getRow().setStatus(parent.getRow().getStatus())


  #----------------------------------------------------
  def display(self,node) :
    print(node.toString())
    for c in node.getChildren() :
      self.display(c)

  #----------------------------------------------------
  def percolate(self,node) :
    logging.debug("before " + node.toString())
    for c in node.getChildren() :
      self.parentToChild(node,c)
      self.percolate(c)
    logging.debug("after  " + node.toString())

#----------------------------------------------------
def build(args,tree) :
  with open(args.file) as csvfile:
    taskReader=csv.DictReader(csvfile, fieldnames=["depth","id","desc","start","end","who","status"], delimiter=',', quotechar='"')
    treeBuilder=TreeBuilder(tree)
    for row in taskReader:
      logging.debug(row['depth'])
      if row['depth'] :
        if row['depth'].startswith("#") :
          next
        else :
          treeBuilder.addToTree(Row(row))

#----------------------------------------------------
def fScan(args) :
  tree=Tree()
  build(args,tree)
  Percolator(args,tree)

#----------------------------------------------------
parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='sub-command help')
parser.add_argument('-v', '--verbose',
                    action='count',
                    dest='verbose',
                    default=0,
                    help="verbose output (repeat for increased verbosity)")

parserScan = subparsers.add_parser('scan', help='a help')
parserScan.set_defaults(func=fScan)
parserScan.add_argument('--file','-f',help="file",default="WBS.svt")
parserScan.add_argument('--fix',help="Fix errors",action="store_true",default=False)

args=parser.parse_args()
loglevel=[logging.WARNING,logging.INFO,logging.DEBUG,1]
logging.basicConfig(format="%(asctime)s %(module)s %(name)s  %(funcName)s %(lineno)s %(levelname)s %(message)s", level=loglevel[args.verbose])
logging.log(1,'Deep debug')
args.func(args)


