#Rafal Kaniewski 27/01/16
set cut_paste_input [stack 0]
version 9.0 v7
BackdropNode {
 inputs 0
 name BackdropNode52
 tile_color 0x64646400
 label "Lens Pipeline"
 note_font_size 42
 selected true
 xpos 8556
 ypos -10344
 bdwidth 1001
 bdheight 1330
 z_order -1
}
BackdropNode {
 inputs 0
 name BackdropNode51
 tile_color 0x676767ff
 label Masters
 note_font_size 42
 selected true
 xpos 8641
 ypos -10271
 bdwidth 323
 bdheight 137
}
BackdropNode {
 inputs 0
 name BackdropNode53
 tile_color 0x5d5d5dff
 label "Lens Nodes"
 note_font_size 42
 selected true
 xpos 8643
 ypos -9798
 bdwidth 325
 bdheight 127
}
Read {
 inputs 0
 origset true
 on_error black
 name Read62
 selected true
 xpos 8657
 ypos -9479
}
Dot {
 name Dot245
 selected true
 xpos 8691
 ypos -9269
}
Read {
 inputs 0
 origset true
 on_error black
 name Read63
 selected true
 xpos 8846
 ypos -9468
}
NoOp {
 inputs 0
 name _2D_elements
 label "At Plate Rez\n(roto, projections, plate bits etc.)"
 selected true
 xpos 9087
 ypos -9585
 hide_input true
}
STMap {
 inputs 2
 channels rgb
 uv rgb
 name STMap4
 label "undistort\nin: Plate Rez\nout: CG Rez"
 selected true
 xpos 9087
 ypos -9464
}
NoOp {
 inputs 0
 name _CG_
 label "At CG Rez"
 selected true
 xpos 9246
 ypos -9570
 hide_input true
}
Merge2 {
 inputs 2
 operation under
 name Merge46
 selected true
 xpos 9246
 ypos -9445
}
STMap {
 inputs 2
 channels rgb
 uv rgb
 name STMap5
 label "distort\nin: CG Rez\nout: Plate Rez"
 selected true
 xpos 9246
 ypos -9279
}
push $cut_paste_input
NoOp {
 name _PLATE_
 label "At Plate Rez\n"
 selected true
 xpos 9410
 ypos -9558
 hide_input true
}
Merge2 {
 inputs 2
 name Merge62
 selected true
 xpos 9410
 ypos -9266
}
StickyNote {
 inputs 0
 name StickyNote4
 label "<b>note:</b>\n\n'Plate rez' is the original plate rezolution \nthat that was lens distorted. This is the same rez. that this pipeline undistorts back too.\n\n'CG rez': This is set to just over the maximum size of the largest format\n resulting from the lens distorts.\n\n- the aspect ratios of the two rezolutions must be identical.\n\n\n"
 note_font Verdana
 selected true
 xpos 8987
 ypos -10279
}
Reformat {
 inputs 0
 format "3840 2160 0 0 3840 2160 1 "
 name Reformat45_1
 label "Plate Rez"
 selected true
 xpos 8657
 ypos -10200
}
Reformat {
 inputs 0
 format "4080 2296 0 0 4080 2296 1 test"
 name Reformat56
 label "CG rez"
 selected true
 xpos 8855
 ypos -10205
}
Reformat {
 inputs 0
 format {{{parent.Reformat45_1.format}}}
 resize none
 black_outside true
 name Reformat51
 selected true
 xpos 8653
 ypos -10039
}
set N97782000 [stack 0]
Expression {
 temp_expr0 ((x+0.5)/width)*(1+((r)/width))
 temp_expr1 ((y+0.5)/height)*(1+((g)/height))
 temp_expr2 ((x)/width)-((((r*2)))/width)
 temp_expr3 ((y)/height)-((((g*2)))/(height))
 expr0 ((x+0.5)/width)
 expr1 ((y+0.5)/height)
 channel3 {rgba.alpha none none rgba.alpha}
 expr3 a
 name Expression6
 selected true
 xpos 8843
 ypos -10033
}
BlackOutside {
 name BlackOutside10
 selected true
 xpos 8843
 ypos -9986
}
NoOp {
 name Undistort_Node
 label here
 selected true
 xpos 8843
 ypos -9725
}
LD_3DE_Classic_LD_Model {
 tde4_focal_length_cm 3.0153003
 tde4_custom_focus_distance_cm 91.44
 tde4_filmback_width_cm 2.376
 tde4_filmback_height_cm 1.3365
 Distortion 0.0509755
 Quartic_Distortion 0.006121
 name LD_3DE4_A006C5
 selected true
 xpos 8843
 ypos -9687
}
Reformat {
 format {{{parent.Reformat56.format}}}
 resize none
 pbb true
 name Reformat55
 selected true
 xpos 8843
 ypos -9638
}
Write {
 beforeRender nxCreateWriteDir.createWriteDir()
 name Write4
 label "undistort \nstMap"
 selected true
 xpos 8843
 ypos -9561
}
push $N97782000
Reformat {
 format {{{parent.Reformat56.format}}}
 black_outside true
 name Reformat52
 selected true
 xpos 8653
 ypos -9966
}
Expression {
 temp_expr0 ((x+0.5)/width)*(1+((r)/width))
 temp_expr1 ((y+0.5)/height)*(1+((g)/height))
 temp_expr2 ((x)/width)-((((r*2)))/width)
 temp_expr3 ((y)/height)-((((g*2)))/(height))
 expr0 ((x+0.5)/width)
 expr1 ((y+0.5)/height)
 channel3 {rgba.alpha none none rgba.alpha}
 expr3 a
 name Expression5
 selected true
 xpos 8653
 ypos -9904
}
Reformat {
 format {{{parent.Reformat45_1.format}}}
 resize none
 pbb true
 name Reformat53
 selected true
 xpos 8653
 ypos -9840
}
NoOp {
 name Distort_Node
 label here
 selected true
 xpos 8653
 ypos -9727
}
LD_3DE_Classic_LD_Model {
 direction distort
 tde4_focal_length_cm 3.0153003
 tde4_custom_focus_distance_cm 91.44
 tde4_filmback_width_cm 2.376
 tde4_filmback_height_cm 1.3365
 Distortion 0.0509755
 Quartic_Distortion 0.006121
 name LD_3DE4_A006C2
 selected true
 xpos 8653
 ypos -9689
}
Reformat {
 format {{{parent.Reformat45_1.format}}}
 resize none
 pbb true
 name Reformat59
 selected true
 xpos 8653
 ypos -9640
}
Write {
 beforeRender nxCreateWriteDir.createWriteDir()
 name Write3
 label "Distort \nstmap"
 selected true
 xpos 8663
 ypos -9561
}
