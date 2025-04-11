from reportlab.platypus.flowables import Flowable

class RotatedText(Flowable):
    """Custom flowable for vertical text"""
    def __init__(self, text, angle=90):
        Flowable.__init__(self)
        self.text = text
        self.angle = angle

    def draw(self):
        canvas = self.canv
        canvas.saveState()
        canvas.rotate(self.angle)
        canvas.drawString(0, 0, self.text)
        canvas.restoreState()

    def wrap(self, *args):
        return self.canv._leading, self.canv.stringWidth(self.text)