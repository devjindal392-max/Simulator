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

#LOAD
def load(filepath):
    addr=0
    with open(filepath) as f:
        for line in f:
            line =line.strip()
            if line:
                if(addr % 4 != 0):
                    print(f"Error: Program counter {hex(addr)} is not divisible by 4. Breaking load.")
                    break

                # each line is an one 32-bit instruction in binary
                program[addr]=int(line,2)
                addr+=4

#EXECUTE
def execute():
    global pc

    if pc not in program:
        return False

    ins =program[pc]
    opcode=ins&0x7F

    #R TYPE
    if(opcode==0b0110011):
        rd=(ins>>7)&0x1F
        f3=(ins>>12)&0x07
        rs1=(ins>>15)&0x1F
        rs2=(ins>>20)&0x1F
        f7=(ins>>25)&0x7F

        a,b=s32(regs[rs1]),s32(regs[rs2])
        ua,ub=u32(regs[rs1]),u32(regs[rs2])

        if(f3==0 and f7==0):
            write_reg(rd,a+b)
        elif(f3==0 and f7==0b0100000):
            write_reg(rd,a-b)
        elif(f3==1):
            write_reg(rd,ua<<(ub&31))
        elif(f3==2):
            write_reg(rd,1 if a<b else 0)
        elif(f3==3):
            write_reg(rd,1 if ua<ub else 0)
        elif(f3==4):
            write_reg(rd,ua^ub)
        elif(f3==5 and f7==0):
            write_reg(rd,ua>>(ub&31))
        elif(f3==5 and f7==0b0100000):
            write_reg(rd,a>>(ub&31))
        elif(f3==6):
            write_reg(rd,ua|ub)
        elif(f3==7):
            write_reg(rd,ua&ub)

        pc+=4

    #I TYPE (addi, sltiu)
    elif(opcode ==0b0010011):
        rd=(ins>>7)&0x1F
        f3=(ins>>12)&0x07
        rs1=(ins>>15)&0x1F
        imm=sext((ins>>20)&0xFFF,12)

        if(f3==0):      # addi
            write_reg(rd,s32(regs[rs1])+imm)
        elif(f3 ==3):    # sltiu
            write_reg(rd,1 if u32(regs[rs1])<u32(imm) else 0)

        pc+=4
