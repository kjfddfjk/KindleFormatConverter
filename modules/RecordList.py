#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import deque

class RecordList():

    def __init__(self, maxlen=20):
        self.listRecord = deque(maxlen=maxlen)
        self.pointer = -1

    def undo(self):
        if(self.pointer == -1):
            return (False, "WARN: No record")
        if(self.pointer == 0):
            return (self.getRecord(self.pointer).copy(), "WARN: Earliest step")
        elif(self.pointer < -1):
            return (False, "ERROR: self.pointer %d is less than 0" % self.pointer)
        else:
            self.pointer -= 1
            return (self.getRecord(self.pointer).copy(), "")
    
    def redo(self):
        if(len(self.listRecord) == 0):
            return (False, "WARN: No record")
        elif(self.pointer + 1 == len(self.listRecord)):
            return (self.getRecord(self.pointer).copy(), "WARN: Latest step")
        elif(self.pointer >= self.listRecord.maxlen):
            return (False, "ERROR: self.pointer %d is outside of record(max%d)" % (self.pointer, self.listRecord.maxlen-1))
        else:
            self.pointer += 1
            return (self.getRecord(self.pointer).copy(), "")
    
    def getRecord(self, index=-1):
        if(len(self.listRecord)==0):
                 return False
        if(index == -1):
            index = self.pointer
        else:
            self.pointer = index
        return self.listRecord[index].copy()

    # For insertion need to determine if at the end or middle
    def insert(self, record):
        if(record == []):
            return False
        if(self.pointer + 1 == len(self.listRecord)):
            if(self.pointer < self.listRecord.maxlen - 1):
                self.pointer += 1
            self.listRecord.append(record.copy())
        else:
            while(self.pointer + 1 != len(self.listRecord)):
                self.listRecord.pop()
            self.listRecord.append(record.copy())
            self.pointer += 1
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