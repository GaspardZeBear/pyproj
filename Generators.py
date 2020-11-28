from datetime import datetime

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

  levelToArrow = {
     0 : ' bold black ',
     1 : ' dashed blue ',
     2 : ' dotted yellow ',
     3 : ' dotted grey  ',
     4 : ' grey ',
     5 : ' grey ',
     6 : ' grey ',
     7 : ' grey ',
     8 : ' grey ',
     9 : ' grey '
   }

  #----------------------------------------------------
  def __init__(self,args,tree) :
    self.args=args
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
    #self.lines.append(node.getRow().toGantt())
    self.lines.append(self.nodeToGantt(node))
    for c in node.getChildren() :
      self.nodeAsGantt(c)

  #----------------------------------------------------
  def nodeToGantt(self,node) :
    desc="[" + node.getRow().getDesc() + "]"
    ganttLines=[]
    if len(node.getRow().getStart()) > 0 :
      ganttLines.append(desc + " starts " + node.getRow().getStart())
    if len(node.getRow().getEnd()) > 0 :
      ganttLines.append(desc + " ends " + node.getRow().getEnd())
    return("\n".join(ganttLines))

  #----------------------------------------------------
  def nodeToGantt(self,node) :
    desc="[" + node.getRow().getDesc() + "]"
    ganttLines=[]
    if len(node.getRow().getStart()) > 0 :
      ganttLines.append(desc + " starts " + node.getRow().getStart())
    if len(node.getRow().getEnd()) > 0 :
      ganttLines.append(desc + " ends " + node.getRow().getEnd())
    #[Observability] starts 4 day after [Global Project]'s start with dotted blue link
    if node.getParent() :
      date_format = "%Y-%m-%d"
      pDate = datetime.strptime(node.getParent().getRow().getStart(), date_format)
      cDate = datetime.strptime(node.getRow().getStart(), date_format)
      delta = cDate - pDate
      #print(str(delta.days))
      out="[{:s}] starts {:d} day after [{:s}]'s start with {:s} link".format(
           node.getRow().getDesc(),
           delta.days,
           node.getParent().getRow().getDesc(),
           GanttGenerator.levelToArrow[node.getParent().getLevel()],
           )
      ganttLines.append(out)
      ganttLines.append(desc + " ends " + node.getRow().getEnd())
    else :
      if len(node.getRow().getStart()) > 0 :
        ganttLines.append(desc + " starts " + node.getRow().getStart())
      if len(node.getRow().getEnd()) > 0 :
        ganttLines.append(desc + " ends " + node.getRow().getEnd())
 

    return("\n".join(ganttLines))



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
    self.args=args
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




