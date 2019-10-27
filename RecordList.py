#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import deque

class RecordList():

    def __init__(self, maxlen=20):
        self.listRecord = deque([], maxlen=maxlen)
        self.pointer = -1

    def undo(self):
        if(self.pointer == -1):
            print("NOTE: No record")
            return False
        if(self.pointer == 0):
            print("NOTE: Earliest step")
            return self.getRecord(self.pointer)
        elif(self.pointer < -1):
            print("ERROR: self.pointer %d is less than 0" % self.pointer)
            return False
        else:
            self.pointer -= 1
            return self.getRecord(self.pointer)
    
    def redo(self):
        if(len(self.listRecord) == 0):
            print("NOTE: No record")
            return False
        elif(self.pointer + 1 == len(self.listRecord)):
            print("NOTE: Latest step")
            return self.getRecord(self.pointer)
        elif(self.pointer >= self.listRecord.maxlen):
            print("ERROR: self.pointer %d is outside of record(max%d)" % (self.pointer, self.listRecord.maxlen-1))
            return False
        else:
            self.pointer += 1
            return self.getRecord(self.pointer)
    
    def getRecord(self, index=-1):
        if(index == -1):
            index = self.pointer
        else:
            self.pointer = index
        return self.listRecord[index]

    # For insertion need to determine if at the end or middle
    def insert(self, record):
        if(record == []):
            return False
        if(self.pointer + 1 == len(self.listRecord)):
            if(self.pointer < self.listRecord.maxlen):
                self.pointer += 1
            self.listRecord.append(record)
        else:
            while(self.pointer + 1 != len(self.listRecord)):
                self.listRecord.pop()
            self.listRecord.append(record)
            self.pointer += 1
        return record



if __name__ == '__main__':
    test = RecordList()
    save=test.undo()
    save=test.redo()

    test.insert(['0','3','9'])
    test.insert(['1','3','9'])
    test.insert(['2','3','9'])
    test.insert(['3','3','9'])
    test.insert(['4','3','9'])
    test.insert(['5','3','9'])
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
