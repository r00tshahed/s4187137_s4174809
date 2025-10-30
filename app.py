import pyhtml

# ---- Student A files ----
import student_a_level_1
import student_a_level_2
import student_a_level_3

# ---- Student B files ----
import student_b_level_1
import student_b_level_2
import student_b_level_3

# Optional: show SQL/tracebacks in browser for faster debugging
pyhtml.need_debugging_help = True

# ---------- ROUTES ----------
# Student A (your task A pages)
pyhtml.MyRequestHandler.pages["/"]    = student_a_level_1  # home = A1
pyhtml.MyRequestHandler.pages["/page2"] = student_a_level_2
pyhtml.MyRequestHandler.pages["/page3"] = student_a_level_3

# Aliases (if your nav uses /a1,/a2,/a3 this avoids 404s)
pyhtml.MyRequestHandler.pages["/a1"] = student_a_level_1
pyhtml.MyRequestHandler.pages["/a2"] = student_a_level_2
pyhtml.MyRequestHandler.pages["/a3"] = student_a_level_3

# Student B (your task B pages)
pyhtml.MyRequestHandler.pages["/b1"] = student_b_level_1
pyhtml.MyRequestHandler.pages["/b2"] = student_b_level_2
pyhtml.MyRequestHandler.pages["/b3"] = student_b_level_3

# ---------- START SERVER (call once!) ----------
pyhtml.host_site()
