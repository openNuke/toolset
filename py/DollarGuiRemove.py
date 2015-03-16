#egoman http://community.thefoundry.co.uk/discussion/topic.aspx?f=190&t=102170
import re
for node in nuke.allNodes(recurseGroups=True):
    for knob in node.allKnobs():
        if knob.hasExpression():
            for anim in knob.animations():
                expr = anim.expression()
                if re.search("\$gui", expr):
                    node.setSelected(True)
                    nuke.zoomToFitSelected()
                    print "Knob: %s.%s" % (node.fullName(), anim.knobAndFieldName())
