import csv
import copy
import logging
import argparse

#============================================
class WbsGenerator() :
  head='''
@startwbs
<style>
wbsDiagram {
  .group {
      RoundCorner 40
  }
  .backlog {
      BackgroundColor silver
  }
  .backlogLate {
      BackgroundColor red
  }
  .runningLate {
      BackgroundColor red
  }
  .done {
      BackgroundColor green
  }
  .critical {
    BackgroundColor orange
    LineColor red
    LineThickness 5.0
  }
  .neutral {
      BackgroundColor white
  }
}
</style>
'''
  tail="@endwbs"

  #----------------------------------------------------
  def __init__(self,args,tree) :
    self.tree=tree
    self.lines=[]
    self.treeToWbs()

  #----------------------------------------------------
  def treeToWbs(self) :
    self.lines.append(WbsGenerator.head)
    self.nodeAsWbs(self.tree.getRoot())
    self.lines.append(WbsGenerator.tail)
    for l in self.lines :
      print(l)

  #----------------------------------------------------
  def nodeAsWbs(self,node) :
    self.lines.append(node.getRow().toWbs())
    for c in node.getChildren() :
      self.nodeAsWbs(c)

#============================================
class GanttGenerator() :
  head='''
@startuml
<style>
wbsDiagram {
  .group {
      RoundCorner 40
  }
  .backlog {
      BackgroundColor silver
  }
  .backlogLate {
      BackgroundColor red
  }
  .runningLate {
      BackgroundColor red
  }
  .done {
      BackgroundColor green
  }
  .critical {
    BackgroundColor orange
    LineColor red
    LineThickness 5.0
  }
  .neutral {
      BackgroundColor white
  }
}
</style>
saturday are closed
sunday are closed
'''
  tail="@enduml"

  #----------------------------------------------------
  def __init__(self,args,tree) :
    self.tree=tree
    self.lines=[]
    self.treeToGantt()

  #----------------------------------------------------
  def treeToGantt(self) :
    self.lines.append(GanttGenerator.head)
    self.lines.append("project starts " + self.tree.getRoot().getRow().getStart())
    self.nodeAsGantt(self.tree.getRoot())
    self.lines.append(GanttGenerator.tail)
    for l in self.lines :
      print(l)

  #----------------------------------------------------
  def nodeAsGantt(self,node) :
    self.lines.append(node.getRow().toGantt())
    for c in node.getChildren() :
      self.nodeAsGantt(c)


#============================================
class Row() :
  #----------------------------------------------------
  def __init__(self,row) :
    self.id=row['id'].strip()
    depth=row['depth'].strip()
    self.direction=''
    if depth.endswith("*") :
      self.depth=row['depth'].strip()
    else :
      self.depth=depth[:-1]
      self.direction=depth[-1:]
    self.desc=row['desc'].strip() if row['desc'] else ''
    self.start=row['start'].strip() if row['start'] else '' 
    self.end=row['end'].strip() if row['end'] else ''
    self.who=row['who'].strip() if row['who'] else ''
    #self.statusValues={
    # 'unknown' : 0,
    # 'backlog' : 1,
    # 'running' : 2,
    # 'done'    : 3
    #}
    #status=row['status'].strip().lower() if row['status'] else ''
    status=int(row['status'].strip()) if row['status'] else 0
    self.setStatus(status)
    #self.statusNum=self.statusValues[self.status] if self.status in self.statusValues else 0
    logging.warning("Created new Row <" + self.toString() +">")
   
  #----------------------------------------------------
  def getDepth(self) :
    return(self.depth)
  #----------------------------------------------------
  def getStart(self) :
    return(self.start)
  #----------------------------------------------------
  def getEnd(self) :
    return(self.end)
  #----------------------------------------------------
  def getDesc(self) :
    return(self.desc)
  #----------------------------------------------------
  def getStatus(self) :
    return(self.status)
  #----------------------------------------------------
  def getStatusNum(self) :
    return(self.statusNum)
  #----------------------------------------------------
  def getStatusStr(self) :
    return(self.statusStr)
  #----------------------------------------------------
  def getWho(self) :
    return(self.who)
  #----------------------------------------------------
  def getId(self) :
    return(self.id)
  #----------------------------------------------------
  def getDirection(self) :
    return(self.direction)

  #----------------------------------------------------
  def setStart(self,start) :
    self.start=start
  #----------------------------------------------------
  def setEnd(self,end) :
    self.end=end
  #----------------------------------------------------
  def setDepth(self,depth) :
    self.depth=depth
  
  #----------------------------------------------------
  def setStatus(self,status) :
    self.status=status
    if self.status < 0 :
      self.statusStr="None"
    elif self.status < 1 :
      self.statusStr="Backlog"
    elif self.status < 100 :
      self.statusStr="Running"
    else :
      self.statusStr="Done"
    self.statusNum=status
    #self.statusNum=self.statusValues[self.status] if self.status in self.statusValues else 0

  #----------------------------------------------------
  def toString(self) :
    return("{:s} {:20s} {:1s} {:12s} {:10s} {:10s} {:20s} {:3d} {:3d} ".format(
      self.getDepth(),
      self.getDesc(),
      self.getDirection(),
      self.getId(),
      self.getStart(),
      self.getEnd(),
      self.getWho(),
      self.getStatus(),
      self.getStatusNum(),
    ))
  #----------------------------------------------------
  def toWbs(self) :
    level=self.getDepth() + self.getDirection()
    return("{:s} <b>{:s}</b>\\n{:s}\\n{:s}\\n{:3d}%<<{:s}>>".format(
      level,
      self.getDesc(),
      self.start,
      self.end,
      self.status,
      self.statusStr,
      ))

  #----------------------------------------------------
  def toGantt(self) :
    desc="[" + self.getDesc() + "]"
    ganttLines=[]
    if len(self.start) > 0 :
      ganttLines.append(desc + " starts " + self.start)
    if len(self.end) > 0 :
      ganttLines.append(desc + " ends " + self.end)
    
    return("\n".join(ganttLines))

#============================================
class Node() :
  #----------------------------------------------------
  def __init__(self,parent,level,row) :
    self.parent=parent
    self.children=[]
    self.row=row
    self.upRow=None
    self.downRow=None
    self.level=level
    logging.warning("Creating New node : row={:s} level={:d} ".format(self.row.toString(),self.level))
    if self.parent :
      logging.warning("Parent node : " + self.parent.getDesc())
    else :
      logging.warning("Parent node is None " )

  #----------------------------------------------------
  def getChildren(self) :
    return(self.children)
  #----------------------------------------------------
  def addChild(self,node) :
    return(self.children.append(node))
  #----------------------------------------------------
  def getLevel(self) :
    return(self.level)
  #----------------------------------------------------
  def setLevel(self,level) :
    self.level=level
  #----------------------------------------------------
  def getRow(self) :
    return(self.row)
  #----------------------------------------------------
  def getUpRow(self) :
    return(self.upRow)
  #----------------------------------------------------
  def setUpRow(self) :
    self.upRow=copy.deepcopy(self.row)
  #----------------------------------------------------
  def setDownRow(self) :
    self.downRow=copy.deepcopy(self.row)
  #----------------------------------------------------
  def getDownRow(self) :
    return(self.downRow)
  #----------------------------------------------------
  def setParent(self,parent) :
    self.parent=parent
  #----------------------------------------------------
  def getParent(self) :
    return(self.parent)

  #----------------------------------------------------
  def toString(self) :
    return("{:d} {:s}".format(
      self.getLevel(),
      self.getRow().toString(),
    ))

  #----------------------------------------------------
  def toStringAll(self) :
    return("{:d}\n{:s}\n{:s}\n{:s}".format(
      self.getLevel(),
      self.getRow().toString(),
      self.getUpRow().toString(),
      self.getDownRow().toString(),
    ))


  #----------------------------------------------------
  def getDesc(self) :
    return("<{:d}>-<{:s}>-<{:s}>".format(
      self.getLevel(),
      self.getRow().getId(),
      self.getRow().getDesc(),
    ))

#============================================
class Tree() :
  #----------------------------------------------------
  def __init__(self,rootLevel=0) :
    self.root=None
    self.rootLevel=rootLevel
    self.treeBuilder=TreeBuilder(self)
  #----------------------------------------------------
  def setRoot(self,node) :
    self.root=node
  #----------------------------------------------------
  def getRoot(self) :
    return(self.root)
  #----------------------------------------------------
  def getRootLevel(self) :
    return(self.rootLevel)
  #----------------------------------------------------
  def getTreeBuilder(self) :
    return(self.treeBuilder)

  #----------------------------------------------------
  def adjustLevel(self,node) :
    level=node.getParent().getLevel()
    logging.warning("adjust level  " + node.getDesc() )
    logging.warning("adjust level  parent " + node.getParent().getDesc())
    node.setLevel(level + 1)
    node.getRow().setDepth("*" * (node.getLevel() +1) )
    logging.warning("adjust level done  " + node.getDesc() )
    for c in node.getChildren() :
      self.adjustLevel(c)

  #----------------------------------------------------
  def display(self,node) :
    print(node.toString())
    for c in node.getChildren() :
      self.display(c)


#============================================
class TreeBuilder() :

  #----------------------------------------------------
  def __init__(self,tree) :
    self.tree=tree
    self.currentNode=None

  #----------------------------------------------------
  def addNodeToTree(self,row) :
    logging.warning("addNodeToTree self.treeBuilder " + str(self))
    if self.currentNode :
      # Tree exists
      logging.warning("currentNode is at begining " + self.currentNode.getDesc())
      if self.currentNode.getParent() :
        logging.warning("currentNode parent  " + self.currentNode.getParent().getDesc())
      upCount=self.currentNode.getLevel() - (len(row.getDepth()) -1 )
      logging.warning("addNodeToTree row depth {:s} node level {:d} upCount {:d} ".format(
       row.getDepth(),
       self.currentNode.getLevel(),
       upCount
      ))

      i=0
      while i <= upCount :
      #for i in range(1,upCount) :
        self.currentNode=self.currentNode.getParent()
        i += 1
        logging.warning("currentNode went up is now " + self.currentNode.getDesc())
      logging.warning("currentNode is finally " + self.currentNode.getDesc())
      node=Node(self.currentNode,len(row.getDepth())-1,row)
      self.currentNode.addChild(node)
      self.currentNode=node
      logging.warning("currentNode is " + self.currentNode.getDesc())
    else :
      # Create the root !
      self.currentNode=Node(None,self.tree.getRootLevel(),row)
      self.tree.setRoot(self.currentNode)
      logging.warning("currentNode init " + self.currentNode.getDesc())
    self.tree.display(self.tree.getRoot())

  #----------------------------------------------------
  def addSubtree(self,row,subtree) :
      dummyRow=Row(row)
      logging.warning("addSubtree self.treeBuilder " + str(self))
      if self.currentNode :
        logging.warning("currentNode is at begining " + self.currentNode.getDesc())
        if self.currentNode.getParent() :
          logging.warning("currentNode parent  " + self.currentNode.getParent().getDesc())
      #upCount=len(dummyRow.getDepth()) - self.currentNode.getLevel() -1
      upCount=self.currentNode.getLevel() - (len(dummyRow.getDepth()) -1)
      logging.warning("addSubtree row depth {:s} node level {:d} upCount {:d} ".format(
       dummyRow.getDepth(),
       self.currentNode.getLevel(),
       upCount
      ))
      i=0
      while i <= upCount :
      #for i in range(1,upCount) :
        self.currentNode=self.currentNode.getParent()
        i += 1
        logging.warning("currentNode went up is now  " + self.currentNode.getDesc())
      logging.warning("currentNode is finally " + self.currentNode.getDesc())
      self.currentNode.addChild(subtree.getRoot())
      subtree.getRoot().setParent(self.currentNode)
      subtree.adjustLevel(subtree.getRoot())
      #self.currentNode.addChild(subTree.getRoot())


#============================================
class Percolator() :

  #----------------------------------------------------
  def __init__(self,args,tree) :
    self.args=args
    self.tree=tree
    print("Initial")
    self.display(tree.getRoot())
    self.percolate(tree.getRoot())
    print("Final")
    self.display(tree.getRoot())
    self.displayAll(tree.getRoot())

  #----------------------------------------------------
  # status was character string
  def XparentToChild(self,parent,child) :
    child.setUpRow()
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
  def parentToChild(self,parent,child) :
    child.setUpRow()
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
      if ((child.getRow().getStatus() >= 0) and (child.getRow().getStatus() < 100))  and   parent.getRow().getStatus() >= 100 :
        logging.warning(child.getRow().getDesc() + " status " + str(child.getRow().getStatus()) + " too high " + str(parent.getRow().getStatus()))
        if self.args.fix :
          logging.warning("Fixing")
          child.getRow().setStatus(parent.getRow().getStatus())
      else :
        logging.debug(child.getRow().getDesc() + " status coherent")
    else :
      logging.debug(child.getRow().getDesc() + " status not set")
      child.getRow().setStatus(parent.getRow().getStatus())

  #----------------------------------------------------
  def parentToChildAll(self,parent,child) :
    parent.setUpRow()
    child.setUpRow()
    if not child.getUpRow().getStart() :
      logging.debug(child.getUpRow().getDesc() + " start not set")
      child.getUpRow().setStart(parent.getUpRow().getStart())
    if not child.getUpRow().getEnd() :
      logging.debug(child.getUpRow().getDesc() + " end not set")
      child.getUpRow().setEnd(parent.getUpRow().getEnd())
    if not child.getUpRow().getStatus() :
      logging.debug(child.getUpRow().getDesc() + " status not set")
      child.getUpRow().setStatus(parent.getUpRow().getStatus())

  #----------------------------------------------------
  def childToParentAll(self,parent,child) :
    parent.setDownRow()
    child.setDownRow()
    if not parent.getDownRow().getStart() :
      logging.debug(parent.getDownRow().getDesc() + " start not set")
      parent.getDownRow().setStart(child.getDownRow().getStart())
    if not parent.getDownRow().getEnd() :
      logging.debug(parent.getDownRow().getDesc() + " end not set")
      parent.getDownRow().setEnd(child.getUpRow().getEnd())
    if not parent.getDownRow().getStatus() :
      logging.debug(parent.getDownRow().getDesc() + " status not set")
      parent.getDownRow().setStatus(child.getDownRow().getStatus())


  #----------------------------------------------------
  def display(self,node) :
    print(node.toString())
    for c in node.getChildren() :
      self.display(c)


  #----------------------------------------------------
  def displayAll(self,node) :
    print(node.toStringAll())
    for c in node.getChildren() :
      self.displayAll(c)


  #----------------------------------------------------
  def percolate(self,node) :
    logging.debug("before " + node.toString())
    for c in node.getChildren() :
      self.parentToChildAll(node,c)
      self.parentToChild(node,c)
      self.percolate(c)
      self.childToParentAll(node,c)
    logging.debug("after  " + node.toString())

#----------------------------------------------------
def build(csvFile,tree) :
  logging.warning("csvFile  " + csvFile)
  with open(csvFile) as csvfile:
    taskReader=csv.DictReader(csvfile, fieldnames=["depth","id","desc","start","end","who","status"], delimiter=',', quotechar='"')
    treeBuilder=tree.getTreeBuilder()
    for row in taskReader:
      logging.warning("\n")
      logging.debug(row['depth'])
      if row['depth'] and row['depth'].startswith("*") :
        nRow=Row(row)
        if row['id'] and row['id'].startswith("!") : 
          fileName=nRow.getId()[1:].rstrip()
          subTree=Tree()
          build(fileName,subTree)
          treeBuilder.addSubtree(row,subTree)
        else :                             
          treeBuilder.addNodeToTree(nRow)

#----------------------------------------------------
def fScan(args) :
  tree=Tree()
  build(args.file,tree)
  Percolator(args,tree)
  WbsGenerator(args,tree)
  GanttGenerator(args,tree)

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
parserScan.add_argument('--wbs',help="Generate WBS",action="store_true",default=False)

args=parser.parse_args()
loglevel=[logging.WARNING,logging.INFO,logging.DEBUG,1]
logging.basicConfig(format="%(asctime)s %(module)s %(name)s  %(funcName)s %(lineno)s %(levelname)s %(message)s", level=loglevel[args.verbose])
logging.log(1,'Deep debug')
args.func(args)


