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
  .runningHalf1 {
      BackgroundColor GreenYellow
  }
  .runningHalf2 {
      BackgroundColor SpringGreen
  }
  .late {
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
    status=int(row['status'].strip()) if row['status'] else 0
    self.setStatus(status)
    logging.debug("Created new Row <" + self.toString() +">")
   
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
  #def getStatusNum(self) :
  #  return(self.statusNum)
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
      self.statusStr="Neutral"
    elif self.status < 1 :
      self.statusStr="Backlog"
    elif self.status < 50 :
      self.statusStr="RunningHalf1"
    elif self.status < 100 :
      self.statusStr="RunningHalf2"
    else :
      self.statusStr="Done"

  #----------------------------------------------------
  def toString(self) :
    return("{:s} {:20s} {:1s} {:12s} {:10s} {:10s} {:20s} {:3d} {:s} ".format(
      self.getDepth(),
      self.getDesc(),
      self.getDirection(),
      self.getId(),
      self.getStart(),
      self.getEnd(),
      self.getWho(),
      self.getStatus(),
      self.getStatusStr(),
    ))
  #----------------------------------------------------
  def toWbs(self) :
    level=self.getDepth() + self.getDirection()
    status="{:3d}".format(self.status) if self.status >= 0 else ''
    return("{:s} <b>{:s}</b>\\n{:s}\\n{:s}\\n{:s}%<<{:s}>>".format(
      level,
      self.getDesc(),
      self.start,
      self.end,
      status,
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
    self.setUpRow()
    #logging.warning("setUpRow : upRow :  " + str(self.upRow))
    self.setDownRow()
    self.level=level
    #logging.warning("Creating New node : {:s}".format(self.toString()))
    #logging.warning("New node : row={:s} level={:d} ".format(self.row.toString(),self.level))
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
    #logging.warning("setDownRow for row " + self.row.toString())
    self.downRow=copy.deepcopy(self.row)
    #logging.warning("setDownRow : downRow :  " + self.downRow.toString())
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
    return("{:d} row {:s}".format(
      self.getLevel(),
      self.getRow().toString(),
    ))

  #----------------------------------------------------
  def toStringAll(self) :
    return("Level {:d}\ndown : {:s}\nrow  : {:s}\nup   :{:s}".format(
      self.getLevel(),
      self.getDownRow().toString(),
      self.getRow().toString(),
      self.getUpRow().toString(),
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
    logging.debug("adjust level  " + node.getDesc() )
    logging.debug("adjust level  parent " + node.getParent().getDesc())
    node.setLevel(level + 1)
    node.getRow().setDepth("*" * (node.getLevel() +1) )
    logging.debug("adjust level done  " + node.getDesc() )
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
    logging.debug("addNodeToTree self.treeBuilder " + str(self))
    if self.currentNode :
      # Tree exists
      logging.debug("currentNode is at begining " + self.currentNode.getDesc())
      if self.currentNode.getParent() :
        logging.debug("currentNode parent  " + self.currentNode.getParent().getDesc())
      upCount=self.currentNode.getLevel() - (len(row.getDepth()) -1 )
      logging.debug("addNodeToTree row depth {:s} node level {:d} upCount {:d} ".format(
       row.getDepth(),
       self.currentNode.getLevel(),
       upCount
      ))

      i=0
      while i <= upCount :
      #for i in range(1,upCount) :
        self.currentNode=self.currentNode.getParent()
        i += 1
        logging.debug("currentNode went up is now " + self.currentNode.getDesc())
      logging.debug("currentNode is finally " + self.currentNode.getDesc())
      node=Node(self.currentNode,len(row.getDepth())-1,row)
      self.currentNode.addChild(node)
      self.currentNode=node
      logging.debug("currentNode is " + self.currentNode.getDesc())
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
        logging.debug("currentNode is at begining " + self.currentNode.getDesc())
        if self.currentNode.getParent() :
          logging.debug("currentNode parent  " + self.currentNode.getParent().getDesc())
      #upCount=len(dummyRow.getDepth()) - self.currentNode.getLevel() -1
      upCount=self.currentNode.getLevel() - (len(dummyRow.getDepth()) -1)
      logging.debug("addSubtree row depth {:s} node level {:d} upCount {:d} ".format(
       dummyRow.getDepth(),
       self.currentNode.getLevel(),
       upCount
      ))
      i=0
      while i <= upCount :
      #for i in range(1,upCount) :
        self.currentNode=self.currentNode.getParent()
        i += 1
        logging.debug("currentNode went up is now  " + self.currentNode.getDesc())
      logging.debug("currentNode is finally " + self.currentNode.getDesc())
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
    self.display(tree.getRoot())
    self.percolate(tree.getRoot())
    self.display(tree.getRoot())
    self.displayAll(tree.getRoot())
    if args.fix :
      logging.warning("----------------------------------- FIX -----------------------------------------------------")
      self.fix(tree.getRoot())

  #----------------------------------------------------
  def parentToChildAll(self,parent,child) :
    logging.warning("parentToChildAll() in parent " + parent.toStringAll())
    logging.warning("parentToChildAll() in  child " + child.toStringAll())

    if not child.getUpRow().getStart() :
      logging.warning(child.getUpRow().getDesc() + " start not set")
      child.getUpRow().setStart(parent.getUpRow().getStart())
    if not child.getUpRow().getEnd() :
      logging.warning(child.getUpRow().getDesc() + " end not set")
      child.getUpRow().setEnd(parent.getUpRow().getEnd())
    if not child.getUpRow().getStatus() :
      logging.warning(child.getUpRow().getDesc() + " status not set")
      child.getUpRow().setStatus(parent.getUpRow().getStatus())
    else : 
      if ((child.getRow().getStatus() >= 0) and (child.getRow().getStatus() < 100))  and   parent.getRow().getStatus() >= 100 :
        logging.warning("Parent status cannot be 100% as child is not, forcing it to child' value")
        parent.getRow().setStatus(child.getRow().getStatus())
    logging.warning("parentToChildAll() child out " + child.toStringAll())


  #----------------------------------------------------
  def childToParentAll(self,parent,child) :
    logging.warning("childToParentAll() in parent " + parent.toStringAll())
    logging.warning("childToParentAll() in  child " + child.toStringAll())

    if not parent.getDownRow().getStart() :
      logging.warning(parent.getDownRow().getDesc() + " start not set")
      parent.getDownRow().setStart(child.getDownRow().getStart())
    else : 
      if child.getDownRow().getStart() < parent.getDownRow().getEnd() :
        parent.getDownRow().setStart(child.getDownRow().getStart())

    if not parent.getDownRow().getEnd() :
      logging.warning(parent.getDownRow().getDesc() + " end not set")
      parent.getDownRow().setEnd(child.getUpRow().getEnd())
    else : 
      if child.getDownRow().getEnd() > parent.getDownRow().getEnd() :
        parent.getDownRow().setEnd(child.getDownRow().getEnd())

    if not parent.getDownRow().getStatus() :
      logging.warning(parent.getDownRow().getDesc() + " status not set")
      parent.getDownRow().setStatus(child.getDownRow().getStatus())
    else :
      if ((child.getRow().getStatus() >= 0) and (child.getRow().getStatus() < 100))  and   parent.getRow().getStatus() == 0 :
        logging.warning("Parent status cannot be 0% as child is not, forcing it to child' value")
        parent.getRow().setStatus(child.getRow().getStatus())

    logging.warning("childToParentAll() parent out " + parent.toStringAll())


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
    #logging.warning("percolate() before " + node.toString())
    for c in node.getChildren() :
      #logging.warning("percolate() " + c.toString())
      self.parentToChildAll(node,c)
      #self.parentToChild(node,c)
      self.percolate(c)
      self.childToParentAll(node,c)
    #logging.debug("percolate() after  " + node.toString())

  #----------------------------------------------------
  def setFinalStart(self,node) :
    dru=0
    dru += 0 if len(node.getDownRow().getStart()) == 0 else 4 
    dru += 0 if len(node.getRow().getStart()) == 0 else 2 
    dru += 0 if len(node.getUpRow().getStart()) == 0 else 1
    logging.warning(" node {:s}  dru {:d}".format(node.toStringAll(),dru))
    if dru==0 :
      pass
    elif dru==1 :
      node.getRow().setStart(node.getUpRow().getStart())
    elif dru==2 :
      pass
    elif dru==3 :
      pass
    elif dru==4 :
      node.getRow().setStart(node.getDownRow().getStart())
    elif dru==5 :
      node.getRow().setStart(node.getDownRow().getStart())
    elif dru==6 :
      if node.getDownRow().getStart() < node.getRow().getStart() :
        node.getRow().setStart(node.getDownRow().getStart())
    elif dru==7 :
      if node.getDownRow().getStart() < node.getRow().getStart() :
        node.getRow().setStart(node.getDownRow().getStart())
    logging.warning(" node {:s}  dru {:d}".format(node.toStringAll(),dru))
 
  #----------------------------------------------------
  def setFinalEnd(self,node) :
    dru=0
    dru += 0 if len(node.getDownRow().getEnd()) == 0 else 4
    dru += 0 if len(node.getRow().getEnd()) == 0 else 2
    dru += 0 if len(node.getUpRow().getEnd()) == 0 else 1
    logging.warning(" node {:s}  dru {:d}".format(node.toStringAll(),dru))
    if dru==0 :
      pass
    elif dru==1 :
      node.getRow().setEnd(node.getUpRow().getEnd())
    elif dru==2 :
      pass
    elif dru==3 :
      pass
    elif dru==4 :
      node.getRow().setEnd(node.getDownRow().getEnd())
    elif dru==5 :
      node.getRow().setEnd(node.getDownRow().getEnd())
    elif dru==6 :
      if node.getDownRow().getEnd() > node.getRow().getEnd() :
        node.getRow().setEnd(node.getDownRow().getEnd())
    elif dru==7 :
      if node.getDownRow().getEnd() > node.getRow().getEnd() :
        node.getRow().setEnd(node.getDownRow().getEnd())
    logging.warning(" node {:s}  dru {:d}".format(node.toStringAll(),dru))

  #----------------------------------------------------
  def setFinalRow(self,node) :
    self.setFinalStart(node)
    self.setFinalEnd(node)

  #----------------------------------------------------
  def fix(self,node) :
    logging.warning(" Entering fix for node {:s}".format(node.toStringAll()))
    for c in node.getChildren() :
      self.fix(c)
    self.setFinalRow(node)
    logging.warning(" Leaving  fix for node {:s}".format(node.toStringAll()))

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
  if args.wbs :
    WbsGenerator(args,tree)
  if args.gantt :
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
parserScan.add_argument('--gantt',help="Generate Gantt",action="store_true",default=False)

args=parser.parse_args()
loglevel=[logging.WARNING,logging.INFO,logging.DEBUG,1]
logging.basicConfig(format="%(asctime)s %(module)s %(name)s  %(funcName)s %(lineno)s %(levelname)s %(message)s", level=loglevel[args.verbose])
logging.log(1,'Deep debug')
args.func(args)


