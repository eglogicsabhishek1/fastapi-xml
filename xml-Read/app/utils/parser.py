from xml.sax.handler import ContentHandler

class JobHandler(ContentHandler):
    def __init__(self):
        self.jobs = []
        self.current_data = {}
        self.current_tag = ""
        
def startElement(self, name, attrs):
    self.current_tag = name
    if name == "job":
        self.current_data = {}
    self.current_value = ""

def characters(self, content):
    if self.current_tag:
        self.current_value += content

def endElement(self, name):
    if self.current_tag and self.current_value.strip():
        self.current_data[self.current_tag] = self.current_value.strip()
    if name == "job":
        self.jobs.append(self.current_data)
    self.current_tag = ""
    self.current_value = ""