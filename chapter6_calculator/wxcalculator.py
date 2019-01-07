import wx


class CalcPanel(wx.Panel):
    
    def __init__(self, parent):
        super().__init__(parent)
        
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.solution = wx.TextCtrl(self, style=wx.TE_RIGHT)
        self.solution.Disable()
        main_sizer.Add(self.solution, 0, wx.EXPAND)
        self.running_total = wx.StaticText(self)
        main_sizer.Add(self.running_total, 0, wx.ALIGN_RIGHT)
        
        buttons = [['7', '8', '9', '/'],
                   ['4', '5', '6', '*'],
                   ['1', '2', '3', '-'],
                   ['.', '0', '', '+']]
        size = (50, 50)
        for label_list in buttons:
            btn_sizer = wx.BoxSizer()
            for label in label_list:
                button = wx.Button(self, label=label, size=size)
                btn_sizer.Add(button)
                self.Bind(wx.EVT_BUTTON, self.update_equation)
            main_sizer.Add(btn_sizer)
        self.SetSizer(main_sizer)
        
    def update_equation(self, event):
        btn = event.GetEventObject()
        label = btn.GetLabel()
        current_equation = self.solution.GetValue()
        
        self.solution.SetValue(current_equation + ' ' + label)
        
        for item in ['/', '*', '-', '+']:
            if item in self.solution.GetValue():
                self.update_solution()
                break
        
    def update_solution(self):
        try:
            current_solution = str(eval(self.solution.GetValue()))
            self.running_total.SetLabel(current_solution)
            self.Layout()
            return current_solution
        except:
            pass
        
    def on_total(self):
        self.solution.SetValue(self.update_solution())

class CalcFrame(wx.Frame):
    
    def __init__(self):
        super().__init__(
            None, title="wxCalculator",
            size=(400, 400))
        panel = CalcPanel(self)
        self.Show()


if __name__ == '__main__':
    app = wx.App(False)
    frame = CalcFrame()
    app.MainLoop()