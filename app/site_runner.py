class SiteRunner():

  def __init__(self):
    self.abbr = 'MAMA JAMMA'
  
  def __str__(self):
    return self.abbr

my_rocket = SiteRunner()
print(my_rocket)
print(path.dirname(path.abspath(__file__)))

