#!/usr/bin/python
# -*- coding: utf-8 -*-
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#   
# @author : beaengine@gmail.com

from headers.BeaEnginePython import *
from nose.tools import *
import struct
import yaml

class TestSuite:

    def test_SimpleInstructions(self):
        stream = open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'opcode1byte.yml')), "r")
        instructions = yaml.load(stream)
        Instruction = DISASM()
        for instr in instructions:
          Buffer = struct.pack('<B', instr['seq']) 
          Target = create_string_buffer(Buffer,len(Buffer))
          Instruction.EIP = addressof(Target)
          InstrLength = Disasm(addressof(Instruction))
          assert_equal(Instruction.CompleteInstr, instr['entry'])

    def test_manyPrefixes(self):
        Buffer = b'\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\xf0\x90'
        Instruction = DISASM()
        Target = create_string_buffer(Buffer,len(Buffer))
        Instruction.EIP = addressof(Target)
        InstrLength = Disasm(addressof(Instruction))
        assert_equal(Instruction.Prefix.Number, 15)
        assert_equal(Instruction.CompleteInstr, '')


    def test_adcx(self):
        Buffer = b'\x0f\x38\xf6\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        Instruction = DISASM()
        Target = create_string_buffer(Buffer,len(Buffer))
        Instruction.EIP = addressof(Target)
        InstrLength = Disasm(addressof(Instruction))
        assert_equal(Instruction.CompleteInstr, '??? ')

        Buffer = b'\x66\x0f\x38\xf6\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xf38f6')
        assert_equal(myDisasm.Instruction.Mnemonic, 'adcx ')
        assert_equal(myDisasm.Instruction.Category, GENERAL_PURPOSE_INSTRUCTION+ARITHMETIC_INSTRUCTION)
        assert_equal(myDisasm.CompleteInstr, 'adcx edx, dword ptr [eax+11111111h]')

        Buffer = b'\xf3\x0f\x38\xf6\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        Instruction = DISASM()
        Target = create_string_buffer(Buffer,len(Buffer))
        Instruction.EIP = addressof(Target)
        InstrLength = Disasm(addressof(Instruction))
        assert_equal(Instruction.CompleteInstr, 'adox edx, dword ptr [eax-6F6F6F70h]')


    def test_imul(self):
        Buffer = b'\x69\x02\x83\xf6\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'imul eax, dword ptr [rdx], 9090F683h')


    def test_VEX3Bytes(self):
        Buffer = b'\xc4\x82\x83\xf6\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Reserved_.VEX.pp, 3)
        assert_equal(myDisasm.Reserved_.VEX.L, 0)
        assert_equal(myDisasm.Reserved_.VEX.mmmmm, 2)
        assert_equal(myDisasm.Reserved_.REX.W_, 1)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xf6')
        assert_equal(~myDisasm.Reserved_.VEX.vvvv & 0b00001111, 15)
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 64)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 64)
        assert_equal(myDisasm.Argument2.AccessMode, WRITE)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 64)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'mulx rdx, r15, qword ptr [r8-6F6F6F70h]')


    def test_addpd(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x44\x66\x0F\x58\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'addpd xmm10, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\x44\x66\x0F\x58\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        myDisasm.Options = IntrinsicMemSyntax
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.CompleteInstr, 'addpd xmm10, __m128d [rax-6F6F6F70h]')


        Buffer = b'\x66\x0F\x58\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'addpd xmm2, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\xc4\x81\x81\x58\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddpd xmm2, xmm15, xmmword ptr [r8+11111111h]')

        Buffer = b'\xc4\x81\x85\x58\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddpd ymm2, ymm15, ymmword ptr [r8+11111111h]')

    def test_addps(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x44\x0F\x58\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'addps xmm10, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\x0F\x58\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'addps xmm2, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\xc4\x81\x80\x58\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddps xmm2, xmm15, xmmword ptr [r8+11111111h]')

        Buffer = b'\xc4\x81\x84\x58\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddps ymm2, ymm15, ymmword ptr [r8+11111111h]')

    def test_addsd(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x44\xF2\x0F\x58\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 64)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'addsd xmm10, qword ptr [rax-6F6F6F70h]')

        Buffer = b'\xF2\x0F\x58\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 64)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'addsd xmm2, qword ptr [rax-6F6F6F70h]')

        Buffer = b'\xc4\x81\x83\x58\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 64)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddsd xmm2, xmm15, qword ptr [r8+11111111h]')



    def test_addss(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x44\xF3\x0F\x58\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'addss xmm10, dword ptr [rax-6F6F6F70h]')

        Buffer = b'\xF3\x0F\x58\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'addss xmm2, dword ptr [rax-6F6F6F70h]')

        Buffer = b'\xc4\x81\x82\x58\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 32)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddss xmm2, xmm15, dword ptr [r8+11111111h]')

    def test_mov(self):

        Buffer = b'\xB8\x04\x01\x00\x00\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Instruction.Immediat, 0x104)
        assert_equal(myDisasm.CompleteInstr, 'mov eax, 00000104h')

        Buffer = b'\x41\xB8\x04\x01\x00\x00\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(hex(myDisasm.Argument2.ArgType), hex(CONSTANT_TYPE+ABSOLUTE_))
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Instruction.Immediat, 0x104)
        assert_equal(myDisasm.CompleteInstr, 'mov r8d, 00000104h')

    def test_addsubpd(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x66\x0F\xD0\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xfd0')
        assert_equal(myDisasm.Instruction.Mnemonic, 'addsubpd ')
        assert_equal(myDisasm.Instruction.Category, SSE3_INSTRUCTION+SIMD_FP_PACKED)
        assert_equal(myDisasm.CompleteInstr, 'addsubpd xmm2, xmmword ptr [rax+11111111h]')

        Buffer = b'\xc4\x01\x01\xD0\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddsubpd xmm10, xmm15, xmmword ptr [r8+11111111h]')

        Buffer = b'\xc4\x01\x05\xD0\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddsubpd ymm10, ymm15, ymmword ptr [r8+11111111h]')

    def test_addsubps(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\xf2\x0F\xD0\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xfd0')
        assert_equal(myDisasm.Instruction.Mnemonic, 'addsubps ')
        assert_equal(myDisasm.Instruction.Category, SSE3_INSTRUCTION+SIMD_FP_PACKED)
        assert_equal(myDisasm.CompleteInstr, 'addsubps xmm2, xmmword ptr [rax+11111111h]')

        Buffer = b'\xc4\x01\x03\xD0\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddsubps xmm10, xmm15, xmmword ptr [r8+11111111h]')

        Buffer = b'\xc4\x01\x07\xD0\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaddsubps ymm10, ymm15, ymmword ptr [r8+11111111h]')

    def test_aesdec(self):

        Buffer = b'\x66\x0F\x38\xDE\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xf38de')
        assert_equal(myDisasm.CompleteInstr, 'aesdec xmm2, xmmword ptr [rax+11111111h]')

        Buffer = b'\xc4\x02\x01\xDE\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaesdec xmm10, xmm15, xmmword ptr [r8+11111111h]')

    def test_aesdeclast(self):

        Buffer = b'\x66\x0F\x38\xDF\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xf38df')
        assert_equal(myDisasm.CompleteInstr, 'aesdeclast xmm2, xmmword ptr [rax+11111111h]')

        Buffer = b'\xc4\x02\x01\xDF\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaesdeclast xmm10, xmm15, xmmword ptr [r8+11111111h]')

    def test_aesenc(self):

        Buffer = b'\x66\x0F\x38\xDC\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xf38dc')
        assert_equal(myDisasm.CompleteInstr, 'aesenc xmm2, xmmword ptr [rax+11111111h]')

        Buffer = b'\xc4\x02\x01\xDC\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaesenc xmm10, xmm15, xmmword ptr [r8+11111111h]')

    def test_aesenclast(self):

        Buffer = b'\x66\x0F\x38\xDD\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xf38dd')
        assert_equal(myDisasm.CompleteInstr, 'aesenclast xmm2, xmmword ptr [rax+11111111h]')

        Buffer = b'\xc4\x02\x01\xDD\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaesenclast xmm10, xmm15, xmmword ptr [r8+11111111h]')

    def test_aesimc(self):

        Buffer = b'\x66\x0F\x38\xDB\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xf38db')
        assert_equal(myDisasm.CompleteInstr, 'aesimc xmm2, xmmword ptr [rax+11111111h]')

        Buffer = b'\xc4\x02\x01\xDB\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaesimc xmm10, xmmword ptr [r8+11111111h]')

    def test_aeskeygenassist(self):

        Buffer = b'\x66\x0F\x3A\xDF\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, CONSTANT_TYPE + ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Instruction.Immediat, 0x11)
        assert_equal(hex(myDisasm.Instruction.Opcode), '0xf3adf')
        assert_equal(myDisasm.CompleteInstr, 'aeskeygenassist xmm2, xmmword ptr [rax+11111111h], 11h')

        Buffer = b'\xc4\x03\x01\xDF\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vaeskeygenassist xmm10, xmmword ptr [r8+11111111h], 11h')

    def test_andn(self):

        Buffer = b'\xc4\x02\x00\xf2\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 32)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'andn r10d, r15d, dword ptr [r8+11111111h]')

        Buffer = b'\xc4\x82\x00\xf2\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 32)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'andn edx, r15d, dword ptr [r8+11111111h]')

        Buffer = b'\xc4\x82\x80\xf2\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 64)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 64)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 64)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'andn rdx, r15, qword ptr [r8+11111111h]')

    def test_andps(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x44\x0F\x54\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'andps xmm10, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\x0F\x54\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'andps xmm2, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\xc4\x81\x80\x54\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vandps xmm2, xmm15, xmmword ptr [r8+11111111h]')

        Buffer = b'\xc4\x81\x84\x54\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vandps ymm2, ymm15, ymmword ptr [r8+11111111h]')

    def test_andnps(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x44\x0F\x55\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'andnps xmm10, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\x0F\x55\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'andnps xmm2, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\xc4\x81\x80\x55\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vandnps xmm2, xmm15, xmmword ptr [r8+11111111h]')

        Buffer = b'\xc4\x81\x84\x55\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vandnps ymm2, ymm15, ymmword ptr [r8+11111111h]')

    def test_andpd(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x44\x66\x0F\x54\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'andpd xmm10, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\x44\x66\x0F\x54\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        myDisasm.Options = IntrinsicMemSyntax
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.CompleteInstr, 'andpd xmm10, __m128d [rax-6F6F6F70h]')


        Buffer = b'\x66\x0F\x54\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90\x90'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'andpd xmm2, xmmword ptr [rax-6F6F6F70h]')

        Buffer = b'\xc4\x81\x81\x54\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vandpd xmm2, xmm15, xmmword ptr [r8+11111111h]')

        Buffer = b'\xc4\x81\x85\x54\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vandpd ymm2, ymm15, ymmword ptr [r8+11111111h]')

    def test_blendpd(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x44\x66\x0F\x3A\x0D\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blendpd xmm10, xmmword ptr [rax+11111111h], 11h')

        Buffer = b'\x44\x66\x0F\x3A\x0D\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        myDisasm.Options = IntrinsicMemSyntax
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.CompleteInstr, 'blendpd xmm10, __m128 [rax+11111111h], 11h')


        Buffer = b'\x66\x0F\x3A\x0D\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blendpd xmm2, xmmword ptr [rax+11111111h], 11h')

        Buffer = b'\xc4\x03\x81\x0D\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Instruction.Immediat, 0x11)
        assert_equal(myDisasm.CompleteInstr, 'vblendpd xmm10, xmmword ptr [r8+11111111h], 11h')

        Buffer = b'\xc4\x03\x85\x0D\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Instruction.Immediat, 0x11)
        assert_equal(myDisasm.CompleteInstr, 'vblendpd ymm10, ymmword ptr [r8+11111111h], 11h')

    def test_blendps(self):
        # using REX.R to access extended xmm registers
        Buffer = b'\x44\x66\x0F\x3A\x0C\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blendps xmm10, xmmword ptr [rax+11111111h], 11h')

        Buffer = b'\x44\x66\x0F\x3A\x0C\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        myDisasm.Options = IntrinsicMemSyntax
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.CompleteInstr, 'blendps xmm10, __m128 [rax+11111111h], 11h')


        Buffer = b'\x66\x0F\x3A\x0C\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG2)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blendps xmm2, xmmword ptr [rax+11111111h], 11h')

        Buffer = b'\xc4\x03\x81\x0C\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Instruction.Immediat, 0x11)
        assert_equal(myDisasm.CompleteInstr, 'vblendps xmm10, xmmword ptr [r8+11111111h], 11h')

        Buffer = b'\xc4\x03\x85\x0C\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Instruction.Immediat, 0x11)
        assert_equal(myDisasm.CompleteInstr, 'vblendps ymm10, ymmword ptr [r8+11111111h], 11h')

    def test_bextr(self):

        Buffer = b'\xc4\x02\x04\xf7\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument3.ArgSize, 32)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'bextr r10d, dword ptr [r8+11111111h], r15d')

        Buffer = b'\xc4\x02\x80\xf7\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 64)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 64)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument3.ArgSize, 64)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'bextr r10, qword ptr [r8+11111111h], r15')

    def test_blendvpd(self):

        Buffer = b'\x44\x66\x0F\x38\x15\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blendvpd xmm10, xmmword ptr [rax+11111111h]')

        Buffer = b'\xc4\x02\x85\x15\x90\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)

        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)

        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)

        assert_equal(myDisasm.Argument4.ArgType, REGISTER_TYPE + AVX_REG + REG0)
        assert_equal(myDisasm.Argument4.ArgSize, 256)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vblendvpd ymm10, ymm15, ymmword ptr [r8+11111111h], ymm0')


        Buffer = b'\xc4\x02\x81\x15\x90\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)

        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)

        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)

        assert_equal(myDisasm.Argument4.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument4.ArgSize, 128)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vblendvpd xmm10, xmm15, xmmword ptr [r8+11111111h], xmm0')

    def test_blendvps(self):

        Buffer = b'\x44\x66\x0F\x38\x14\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blendvps xmm10, xmmword ptr [rax+11111111h]')

        Buffer = b'\xc4\x02\x85\x14\x90\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)

        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)

        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)

        assert_equal(myDisasm.Argument4.ArgType, REGISTER_TYPE + AVX_REG + REG0)
        assert_equal(myDisasm.Argument4.ArgSize, 256)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vblendvps ymm10, ymm15, ymmword ptr [r8+11111111h], ymm0')


        Buffer = b'\xc4\x02\x81\x14\x90\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)

        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)

        assert_equal(myDisasm.Argument3.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)

        assert_equal(myDisasm.Argument4.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument4.ArgSize, 128)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vblendvps xmm10, xmm15, xmmword ptr [r8+11111111h], xmm0')

    def test_blsi(self):

        Buffer = b'\xc4\x02\x00\xf3\x18\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blsi r15d, dword ptr [r8]')

        Buffer = b'\xc4\x02\x80\xf3\x18\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument1.ArgSize, 64)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 64)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blsi r15, qword ptr [r8]')

    def test_blmsk(self):

        Buffer = b'\xc4\x02\x00\xf3\x10\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blmsk r15d, dword ptr [r8]')

        Buffer = b'\xc4\x02\x80\xf3\x10\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument1.ArgSize, 64)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 64)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blmsk r15, qword ptr [r8]')

    def test_blsr(self):

        Buffer = b'\xc4\x02\x00\xf3\x08\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blsr r15d, dword ptr [r8]')

        Buffer = b'\xc4\x02\x80\xf3\x08\x11\x11\x11\x11\x00\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument1.ArgSize, 64)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 64)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'blsr r15, qword ptr [r8]')

    def test_bzhi(self):

        Buffer = b'\xc4\x02\x04\xf5\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 32)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 32)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument3.ArgSize, 32)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'bzhi r10d, dword ptr [r8+11111111h], r15d')

        Buffer = b'\xc4\x02\x80\xf5\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + GENERAL_REG + REG10)
        assert_equal(myDisasm.Argument1.ArgSize, 64)
        assert_equal(myDisasm.Argument1.AccessMode, WRITE)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 64)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType, REGISTER_TYPE + GENERAL_REG + REG15)
        assert_equal(myDisasm.Argument3.ArgSize, 64)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'bzhi r10, qword ptr [r8+11111111h], r15')

    def test_clac(self):

        Buffer = b'\x0F\x01\xCA\x90\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.CompleteInstr, 'clac ')

    def test_cmppd(self):

        Buffer = b'\x66\x0F\xC2\x00\x00\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpeqpd xmm0, xmmword ptr [rax]')

        Buffer = b'\x66\x0F\xC2\x00\x01\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpltpd xmm0, xmmword ptr [rax]')

        Buffer = b'\x66\x0F\xC2\x00\x02\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmplepd xmm0, xmmword ptr [rax]')

        Buffer = b'\x66\x0F\xC2\x00\x03\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpunordpd xmm0, xmmword ptr [rax]')

        Buffer = b'\x66\x0F\xC2\x00\x04\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpneqpd xmm0, xmmword ptr [rax]')

        Buffer = b'\x66\x0F\xC2\x00\x05\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpnltpd xmm0, xmmword ptr [rax]')

        Buffer = b'\x66\x0F\xC2\x00\x06\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpnlepd xmm0, xmmword ptr [rax]')

        Buffer = b'\x66\x0F\xC2\x00\x07\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpordpd xmm0, xmmword ptr [rax]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x00\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpeqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x01\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpltpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x02\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmplepd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x03\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpunordpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x04\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpneqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x05\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnltpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x06\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnlepd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x07\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpordpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x08\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpeq_uqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x09\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpngepd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x0a\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpngtpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x0b\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpfalsepd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x0c\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpneq_oqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x0d\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpgepd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x0e\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpgtpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x0f\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmptruepd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x10\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpeq_ospd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmplt_oqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x12\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmple_oqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x13\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpunord_spd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x14\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpneq_uspd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x15\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnlt_uqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x16\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnle_uqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x17\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpord_spd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x18\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpeq_uspd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x19\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnge_uqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x1a\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpngt_uqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x1b\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpfalse_ospd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x1c\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpneq_ospd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x1d\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpge_oqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x1e\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpgt_oqpd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x81\xc2\x00\x1f\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmptrue_uspd xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x05\xc2\x00\x1f\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmptrue_uspd ymm8, ymm15, ymmword ptr [r8]')


    def test_cmpps(self):

        Buffer = b'\x0F\xC2\x00\x00\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpeqps xmm0, xmmword ptr [rax]')

        Buffer = b'\x0F\xC2\x00\x01\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpltps xmm0, xmmword ptr [rax]')

        Buffer = b'\x0F\xC2\x00\x02\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpleps xmm0, xmmword ptr [rax]')

        Buffer = b'\x0F\xC2\x00\x03\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpunordps xmm0, xmmword ptr [rax]')

        Buffer = b'\x0F\xC2\x00\x04\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpneqps xmm0, xmmword ptr [rax]')

        Buffer = b'\x0F\xC2\x00\x05\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpnltps xmm0, xmmword ptr [rax]')

        Buffer = b'\x0F\xC2\x00\x06\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpnleps xmm0, xmmword ptr [rax]')

        Buffer = b'\x0F\xC2\x00\x07\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG0)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, MEMORY_TYPE)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument3.ArgSize, 8)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'cmpordps xmm0, xmmword ptr [rax]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x00\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpeqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x01\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpltps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x02\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpleps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x03\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpunordps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x04\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpneqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x05\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnltps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x06\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnleps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x07\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpordps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x08\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpeq_uqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x09\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpngeps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x0a\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpngtps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x0b\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpfalseps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x0c\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpneq_oqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x0d\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpgeps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x0e\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpgtps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x0f\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmptrueps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x10\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpeq_osps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmplt_oqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x12\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmple_oqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x13\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpunord_sps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x14\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpneq_usps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x15\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnlt_uqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x16\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnle_uqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x17\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpord_sps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x18\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpeq_usps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x19\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpnge_uqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x1a\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpngt_uqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x1b\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpfalse_osps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x1c\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpneq_osps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x1d\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpge_oqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x1e\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmpgt_oqps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x80\xc2\x00\x1f\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + SSE_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 128)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + SSE_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 128)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 128)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmptrue_usps xmm8, xmm15, xmmword ptr [r8]')

        Buffer = b'\xc4\x01\x04\xc2\x00\x1f\x11\x11\x11\x11\x11\x11\x11\x11\x11'
        myDisasm = DISASM()
        myDisasm.Archi = 64
        Target = create_string_buffer(Buffer,len(Buffer))
        myDisasm.EIP = addressof(Target)
        InstrLength = Disasm(addressof(myDisasm))
        assert_equal(myDisasm.Argument1.ArgType, REGISTER_TYPE + AVX_REG + REG8)
        assert_equal(myDisasm.Argument1.ArgSize, 256)
        assert_equal(myDisasm.Argument1.AccessMode, READ)
        assert_equal(myDisasm.Argument2.ArgType, REGISTER_TYPE + AVX_REG + REG15)
        assert_equal(myDisasm.Argument2.ArgSize, 256)
        assert_equal(myDisasm.Argument2.AccessMode, READ)
        assert_equal(myDisasm.Argument3.ArgType,  + MEMORY_TYPE)
        assert_equal(myDisasm.Argument3.ArgSize, 256)
        assert_equal(myDisasm.Argument3.AccessMode, READ)
        assert_equal(myDisasm.Argument4.ArgType,  + CONSTANT_TYPE+ABSOLUTE_)
        assert_equal(myDisasm.Argument4.ArgSize, 8)
        assert_equal(myDisasm.Argument4.AccessMode, READ)
        assert_equal(myDisasm.CompleteInstr, 'vcmptrue_usps ymm8, ymm15, ymmword ptr [r8]')