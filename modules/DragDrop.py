# -*- coding: utf-8
import tkinter as tk


class DragDropList(tk.Listbox):
    """ A Tkinter listbox with drag'n'drop reordering of entries. """

    def __init__(self, master, **kw):
        self.count = 0
        kw['selectmode'] = tk.SINGLE
        kw['activestyle'] = 'none'
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        # self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None

    def setCurrent(self, event):
        self.curIndex = self.nearest(event.y)

    def shiftSelection(self, event):
        i = self.nearest(event.y)
        self.count += 1
        if i < self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i+1, x)
            self.curIndex = i
        elif i > self.curIndex:
            x = self.get(i)
            self.delete(i)
            self.insert(i-1, x)
            self.curIndex = i
        temp = list(self.get(0, self.size()-1))
        return temp


if __name__ == '__main__':
    root = tk.Tk()
    listbox = DragDropList(root)
    for i, name in enumerate(['name'+str(i) for i in range(10)]):
        listbox.insert(tk.END, name)
    listbox.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
