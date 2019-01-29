import wx


class CalcPanel(wx.Panel):
    
    def __init__(self, parent):
        super().__init__(parent)
        self.last_button_pressed = None
        self.whitelist = ['0', '1', '2', '3', '4',
                          '5', '6', '7', '8', '9']
        self.create_ui()
        
    def create_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)
        
        self.solution = wx.TextCtrl(self, style=wx.TE_RIGHT)
        self.solution.SetFont(font)
        self.solution.Bind(wx.EVT_KEY_DOWN, self.on_key)
        main_sizer.Add(self.solution, 0, wx.EXPAND|wx.ALL, 5)
        self.running_total = wx.StaticText(self)
        main_sizer.Add(self.running_total, 0, wx.ALIGN_RIGHT)
        
        buttons = [['7', '8', '9', '/'],
                   ['4', '5', '6', '*'],
                   ['1', '2', '3', '-'],
                   ['', '0', '', '+']]

        for label_list in buttons:
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
        self.update_equation(label)
        
    def on_clear(self, event):
        self.solution.Clear()
        self.running_total.SetLabel('')
        
    def on_key(self, event):
        keycode = event.GetKeyCode()
        unicode_key = event.GetUnicodeKey()
        if keycode in [wx.WXK_NUMPAD_ADD, wx.WXK_ADD]:
            self.update_equation('+')
        elif keycode in [wx.WXK_NUMPAD_SUBTRACT, wx.WXK_SUBTRACT]:
            self.update_equation('-')
        elif keycode in [wx.WXK_NUMPAD_MULTIPLY, wx.WXK_MULTIPLY]:
            self.update_equation('*')
        elif keycode in [wx.WXK_NUMPAD_DIVIDE, wx.WXK_DIVIDE]:
            self.update_equation('/')

        else:        
            decoded_key = chr(unicode_key)
            if decoded_key in self.whitelist:
                self.update_equation(decoded_key)

    
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
            else:
                self.solution.SetValue(current_equation + text)
        elif text in operators and current_equation is not '' \
             and self.last_button_pressed not in operators:
            self.solution.SetValue(current_equation + ' ' + text)
        
        self.last_button_pressed = text
        
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