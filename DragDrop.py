import tkinter as tk


class DragDrop(tk.Listbox):
    """ A Tkinter listbox with drag'n'drop reordering of entries. """
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.SINGLE
        kw['activestyle'] = 'none'
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<Double-Button-1>', self.printImage)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.curIndex = None

    def setCurrent(self, event):
        self.curIndex = self.nearest(event.y)

    def shiftSelection(self, event):
        i = self.nearest(event.y)
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

    def printImage(self, event):
        index = listbox.curselection()
        if(index == ()):
            print("None")
            return
        else:
            for element in index:
                print(element)

if __name__ == '__main__':
    root = tk.Tk()
    listbox = DragDrop(root)
    for i, name in enumerate(['name'+str(i) for i in range(10)]):
        listbox.insert(tk.END, name)
    listbox.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
