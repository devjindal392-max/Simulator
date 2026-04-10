import sys

#memory constraints
DATA_MEM_START=0x00010000
STACK_START=0x00000100
STACK_END=0x0000017F
SP_START=0x0000017C

#registers
regs=[0]*32
regs[2]=SP_START   

pc=0
program={}
data_mem=[0]*32
stack_mem={}

def s32(val):
    val= u32(val)
    if(val>=0x80000000):
        val-=0x100000000
    return val


def u32(val):
    return val&0xFFFFFFFF


def sext(val, bits):
    if(val&(1<<(bits-1))):
        val-=(1<<bits)
    return val

def to_bin32(val):
    # 32-bit binary string which has '0b' as its  prefix
    return '0b'+format(u32(val),'032b')

def write_reg(r,val):
    if(r!=0):
        regs[r]= u32(val)

def read_mem(addr):
    addr=u32(addr)


    #stack memory
    if(STACK_START<=addr<=STACK_END-3):
        word=0
        for i in range(4):
            word|=stack_mem.get(addr+i,0)<<(8*i)
        return word

    #data memory
    elif(DATA_MEM_START<=addr<DATA_MEM_START+128):
        idx=(addr-DATA_MEM_START)//4
        if(0<=idx<32):
            return data_mem[idx]

    return 0

def write_mem(addr,val):
    addr=u32(addr)
    val=u32(val)

    #stack memory
    if(STACK_START<=addr<=STACK_END-3):
        for i in range(4):
            stack_mem[addr+i]=(val>>(8*i))&0xFF

    #data memory
    elif(DATA_MEM_START<=addr<DATA_MEM_START+128):
        idx=(addr-DATA_MEM_START)//4
        if(0<=idx<32):
            data_mem[idx]=val

