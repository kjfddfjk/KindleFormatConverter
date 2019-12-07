#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import deque

class RecordList():

    def __init__(self, maxlen=20):
        self.listRecord = deque(maxlen=maxlen)
        self.position = -1

    def undo(self):
        if(self.position == -1):
            return (False, "WARN: No record")
        if(self.position == 0):
            return (self.getRecord(self.position).copy(), "WARN: Earliest step")
        elif(self.position < -1):
            return (False, "ERROR: self.position %d is less than 0" % self.position)
        else:
            self.position -= 1
            return (self.getRecord(self.position).copy(), "")
    
    def redo(self):
        if(len(self.listRecord) == 0):
            return (False, "WARN: No record")
        elif(self.position + 1 == len(self.listRecord)):
            return (self.getRecord(self.position).copy(), "WARN: Latest step")
        elif(self.position >= self.listRecord.maxlen):
            return (False, "ERROR: self.position %d is outside of record(max%d)" % (self.position, self.listRecord.maxlen-1))
        else:
            self.position += 1
            return (self.getRecord(self.position).copy(), "")
    
    def getRecord(self, index=-1):
        if(len(self.listRecord)==0):
                 return False
        if(index == -1):
            index = self.position
        else:
            self.position = index
        return self.listRecord[index].copy()

    # For insertion need to determine if at the end or middle
    def insert(self, record):
        if(self.position + 1 == len(self.listRecord)):
            if(self.position < self.listRecord.maxlen - 1):
                self.position += 1
            self.listRecord.append(record.copy())
        else:
            while(self.position + 1 != len(self.listRecord)):
                self.listRecord.pop()
            self.listRecord.append(record.copy())
            self.position += 1
        return record



if __name__ == '__main__':
    test = RecordList()
    save=test.undo()
    save=test.redo()
    for i in range(0, 30):
        test.insert([str(i),str(i+1)])
        
    save=test.redo()
    test.insert(['after redo'])

    save=test.undo()
    save=test.undo()
    save=test.undo()
    save=test.redo()
    test.insert(['2 redo'])
    save=test.undo()
    save=test.undo()
    save=test.undo()
    save=test.undo()
    save=test.undo()
    save=test.undo()
    test.insert(['undo'])
    print(save)