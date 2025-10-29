import pyhtml

#  (Student A) files 
import student_a_level_1
import student_a_level_2
import student_a_level_3

#  (Student B) files
import student_b_level_1
import student_b_level_2
import student_b_level_3

# Enable debug help
pyhtml.need_debugging_help = True

# ROUTES 
#  (Sub-Task A)
pyhtml.MyRequestHandler.pages["/"] = student_a_level_1          # Level 1 (Journalist mission page)
pyhtml.MyRequestHandler.pages["/page2"] = student_a_level_2     # Level 2 (Vaccination by Country)
pyhtml.MyRequestHandler.pages["/page3"] = student_a_level_3     # Level 3 (Global summary)

# (Sub-Task B)
pyhtml.MyRequestHandler.pages["/b1"] = student_b_level_1        # Level 1 for partner
pyhtml.MyRequestHandler.pages["/b2"] = student_b_level_2        # Level 2 for partner
pyhtml.MyRequestHandler.pages["/b3"] = student_b_level_3        # Level 3 for partner

#  Host the site 
pyhtml.host_site()

pyhtml.host_site()
