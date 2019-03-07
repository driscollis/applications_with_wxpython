# wxcalculator_key_events.py

import wx


class CalcPanel(wx.Panel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.last_button_pressed = None
        self.whitelist = [['7', '8', '9', '/'],
                          ['4', '5', '6', '*'],
                          ['1', '2', '3', '-'],
                          ['.', '0', '', '+']]
        self.on_key_called = False
        self.empty = True
        self.create_ui()
        
    def create_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)
        
        self.solution = wx.TextCtrl(self, style=wx.TE_RIGHT)
        self.solution.SetFont(font)
        self.solution.Bind(wx.EVT_TEXT, self.on_key)
        main_sizer.Add(self.solution, 0, wx.EXPAND|wx.ALL, 5)
        self.running_total = wx.StaticText(self)
        main_sizer.Add(self.running_total, 0, wx.ALIGN_RIGHT)
        
        for label_list in self.whitelist:
            btn_sizer = wx.BoxSizer()
            for label in label_list:
                button = wx.Button(self, label=label)
                btn_sizer.Add(button, 1, wx.ALIGN_CENTER|wx.EXPAND, 0)
                button.Bind(wx.EVT_BUTTON, self.on_calculate)
            main_sizer.Add(btn_sizer, 1, wx.ALIGN_CENTER|wx.EXPAND)
        
        equals_btn = wx.Button(self, label='=')
        equals_btn.Bind(wx.EVT_BUTTON, self.on_total)
        main_sizer.Add(equals_btn, 0, wx.EXPAND|wx.ALL, 3)
        
        clear_btn = wx.Button(self, label='Clear')
        clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
        main_sizer.Add(clear_btn, 0, wx.EXPAND|wx.ALL, 3)
        
        self.SetSizer(main_sizer)
        
    def on_calculate(self, event):
        btn = event.GetEventObject()
        label = btn.GetLabel()
        self.on_key_called = True
        self.update_equation(label)
        
    def on_clear(self, event):
        self.solution.Clear()
        self.running_total.SetLabel('')
        self.empty = True
        self.solution.SetFocus()
        
    def on_key(self, event):
        if self.on_key_called:
            self.on_key_called = False
            return
        
        key = event.GetString()
        self.on_key_called = True
        
        if key in self.whitelist:
            self.update_equation(key)
    
    def on_total(self, event):
        solution = self.update_solution()
        if solution:
            self.solution.SetValue(solution)
            self.running_total.SetLabel('')
    
    def update_equation(self, text):
        operators = ['/', '*', '-', '+']
        current_equation = self.solution.GetValue()
        
        if text not in operators:
            if self.last_button_pressed in operators:
                self.solution.SetValue(current_equation + ' ' + text)
            elif self.empty and current_equation:
                # The solution is not empty
                self.empty = False
            else:
                self.solution.SetValue(current_equation + text)
        elif text in operators and current_equation is not '' \
             and self.last_button_pressed not in operators:
            self.solution.SetValue(current_equation + ' ' + text)
        
        self.last_button_pressed = text
        self.solution.SetInsertionPoint(-1)
        
        for item in operators:
            if item in self.solution.GetValue():
                self.update_solution()
                break
        
    def update_solution(self):
        try:
            current_solution = str(eval(self.solution.GetValue()))
            self.running_total.SetLabel(current_solution)
            self.Layout()
            return current_solution
        except ZeroDivisionError:
            self.solution.SetValue('ZeroDivisionError')
        except:
            pass
        

class CalcFrame(wx.Frame):
    
    def __init__(self):
        super().__init__(
            None, title="wxCalculator",
            size=(350, 375))
        panel = CalcPanel(self)
        self.SetSizeHints(350, 375, 350, 375)
        self.Show()


if __name__ == '__main__':
    app = wx.App(False)
    frame = CalcFrame()
    app.MainLoop()