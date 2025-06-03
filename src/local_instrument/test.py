from Yokogawa_GS200 import YokogawaGS200
yoko = YokogawaGS200("GPIB::3")
applied_dc = -0.5
yoko.source_mode = "voltage"
yoko.source_range = applied_dc
yoko.current_limit = 1e-3
yoko.source_enabled = True
yoko.source_level = applied_dc

