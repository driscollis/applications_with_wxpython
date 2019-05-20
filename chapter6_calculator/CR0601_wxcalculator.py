# CR0601_wxcalculator.py

import wx


class CalcPanel(wx.Panel):

    def __init__(self, parent):
        super().__init__(parent)
        self.last_button_pressed = None
        self.create_ui()

    def create_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.NORMAL)

        self.solution = wx.TextCtrl(self, style=wx.TE_RIGHT)
        self.solution.SetFont(font)
        self.solution.Disable()
        main_sizer.Add(self.solution, 0, wx.EXPAND|wx.ALL, 5)
        self.running_total = wx.StaticText(self)
        main_sizer.Add(self.running_total, 0, wx.ALIGN_RIGHT)

        buttons = [['7', '8', '9', '/'],
                   ['4', '5', '6', '*'],
                   ['1', '2', '3', '-'],
                   ['.', '0', '', '+']]
        for label_list in buttons:
            btn_sizer = wx.BoxSizer()
            for label in label_list:
                button = wx.Button(self, label=label)
                btn_sizer.Add(button, 1, wx.ALIGN_CENTER|wx.EXPAND, 0)
                button.Bind(wx.EVT_BUTTON, self.update_equation)
            main_sizer.Add(btn_sizer, 1, wx.ALIGN_CENTER|wx.EXPAND)

        equals_btn = wx.Button(self, label='=')
        equals_btn.Bind(wx.EVT_BUTTON, self.on_total)
        main_sizer.Add(equals_btn, 0, wx.EXPAND|wx.ALL, 3)

        clear_btn = wx.Button(self, label='Clear')
        clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
        main_sizer.Add(clear_btn, 0, wx.EXPAND|wx.ALL, 3)

        self.SetSizer(main_sizer)

    def update_equation(self, event):
        operators = ['/', '*', '-', '+']
        btn = event.GetEventObject()
        label = btn.GetLabel()
        current_equation = self.solution.GetValue()

        if label not in operators:
            if self.last_button_pressed in operators:
                self.solution.SetValue(current_equation + ' ' + label)
            else:
                self.solution.SetValue(current_equation + label)
        elif label in operators and current_equation != '' \
             and self.last_button_pressed not in operators:
            self.solution.SetValue(current_equation + ' ' + label)

        self.last_button_pressed = label

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

    def on_clear(self, event):
        self.solution.Clear()
        self.running_total.SetLabel('')

    def on_total(self, event):
        solution = self.update_solution()
        if solution:
            self.solution.SetValue(solution)
            self.running_total.SetLabel('')

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