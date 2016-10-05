set cut_paste_input [stack 0]
version 9.0 v5
push $cut_paste_input
add_layer {direct_shadow direct_shadow.red direct_shadow.green direct_shadow.blue}
add_layer {direct direct.red direct.green direct.blue}
add_layer {indirect_shadow indirect_shadow.red indirect_shadow.green indirect_shadow.blue}
add_layer {indirect indirect.red indirect.green indirect.blue}
Group {
 name ShadowMantra
 selected true
 xpos 2623
 ypos -1644
 addUserKnob {20 User l ShadowMantra}
 addUserKnob {41 in_3 l "direct shadow" T directS.in}
 addUserKnob {41 in_2 l direct T Direct.in}
 addUserKnob {41 in_1 l "indirect shadow" T IndrectS.in}
 addUserKnob {41 in_4 l indirect T indirect_.in}
 addUserKnob {26 ""}
 addUserKnob {41 direct T MASTER.direct}
 addUserKnob {41 indirect T MASTER.indirect}
 addUserKnob {26 ""}
 addUserKnob {41 alpha l unpremult -STARTLINE T Unpremult1.alpha}
 addUserKnob {41 invert -STARTLINE T Unpremult1.invert}
 addUserKnob {41 maskChannel l "mask channel" T Keymix1.maskChannel}
 addUserKnob {41 invertMask l invert -STARTLINE T Keymix1.invertMask}
 addUserKnob {41 which l mix T Dissolve1.which}
}
 NoOp {
  inputs 0
  name MASTER
  xpos 589
  ypos -315
  addUserKnob {20 User}
  addUserKnob {7 direct R -1 1}
  direct 0.68
  addUserKnob {7 indirect R 1 -1}
  indirect 0.34
 }
 Input {
  inputs 0
  name mask
  xpos 489
  ypos -494
  number 1
 }
 Dot {
  name IN1
  xpos 543
  ypos -371
 }
 Dot {
  name Dot8
  xpos 535
  ypos 197
 }
 Invert {
  name Invert1
  xpos 427
  ypos 191
 }
 Input {
  inputs 0
  name in
  xpos -166
  ypos -502
 }
 Dot {
  name IN
  xpos -154
  ypos -412
 }
set N70a9f20 [stack 0]
 Dot {
  name Dot1
  xpos -154
  ypos -27
 }
set N70ae940 [stack 0]
 Dot {
  name Dot7
  xpos -154
  ypos 142
 }
set N70b33a0 [stack 0]
 Dot {
  name Dot9
  xpos -154
  ypos 197
 }
push $N70a9f20
 Unpremult {
  channels all
  alpha -rgba.alpha
  name Unpremult1
  label "\[value alpha]"
  xpos -79
  ypos -404
  disable {{alpha==0?1:0 x1048 0}}
 }
 Dot {
  name Dot2
  xpos 31
  ypos -388
 }
set N70c4ef0 [stack 0]
 Dot {
  name Dot3
  xpos 154
  ypos -388
 }
set N70c9cc0 [stack 0]
 Shuffle {
  in indirect
  out rgb
  name indirect_
  xpos 120
  ypos -336
 }
push $N70c4ef0
 Shuffle {
  in indirect_shadow
  out rgb
  name IndrectS
  label "\[value in]"
  xpos -3
  ypos -332
 }
 Multiply {
  channels rgb
  value {{parent.MASTER.indirect}}
  name Multiply_indirect
  xpos -4
  ypos -270
 }
 Invert {
  channels rgb
  name Invert3
  xpos -3
  ypos -201
 }
 Merge2 {
  inputs 2
  operation divide
  Achannels rgb
  Bchannels rgb
  output rgb
  name Merge4
  xpos 120
  ypos -201
 }
 Dot {
  name Dot6
  xpos 154
  ypos -143
 }
push $N70c9cc0
 Dot {
  name Dot4
  xpos 245
  ypos -388
 }
set N7117fe0 [stack 0]
 Dot {
  name Dot5
  xpos 340
  ypos -388
 }
 Shuffle {
  in direct
  out rgb
  name Direct
  label "\[value in]"
  xpos 306
  ypos -344
 }
push $N7117fe0
 Shuffle {
  in direct_shadow
  out rgb
  name directS
  label "\[value in]"
  xpos 211
  ypos -339
 }
 Multiply {
  channels rgb
  value {{parent.MASTER.direct}}
  name Multiply_direct
  xpos 211
  ypos -301
 }
 Invert {
  channels rgb
  name Invert4
  xpos 211
  ypos -259
 }
 Merge2 {
  inputs 2
  operation divide
  Achannels rgb
  Bchannels rgb
  output rgb
  name Merge5
  xpos 306
  ypos -212
 }
 Merge2 {
  inputs 2
  operation plus
  name plus
  xpos 315
  ypos -147
 }
push $N70ae940
 Copy {
  inputs 2
  from0 rgba.red
  to0 rgba.red
  from1 rgba.green
  to1 rgba.green
  from2 rgba.blue
  to2 rgba.blue
  name Copy1
  xpos 315
  ypos -49
 }
 Premult {
  alpha {{{parent.Unpremult1.alpha}}}
  name Premult1
  selected true
  xpos 315
  ypos 85
  disable {{alpha==0?1:0 x1048 0}}
 }
push $N70b33a0
 Dissolve {
  inputs 2
  channels rgb
  which 1
  name Dissolve1
  xpos 315
  ypos 138
 }
 Keymix {
  inputs 3
  channels rgb
  maskChannel -rgba.alpha
  name Keymix1
  label "\[value mask]"
  xpos 315
  ypos 191
  disable {{maskChannel==0?1:0}}
 }
 Output {
  name Output1
  xpos 315
  ypos 292
 }
end_group
