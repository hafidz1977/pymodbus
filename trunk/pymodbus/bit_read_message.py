'''
Bit Reading Request/Response messages

An example flow of data:
  1. Modbus client builds a request message
  2. Modbus client sends request to Modbus server
  ...
  3. Modbus server receives request and decodes
  4. Modbus server passes its context the request execute method
  5. Modbus server Sends the response message generated by execute to client
  ...
  6. Modbus client receives response and decodes
  7. Modbus client parses final results
'''

from pymodbus.pdu import ModbusRequest
from pymodbus.pdu import ModbusResponse
from pymodbus.pdu import ModbusExceptions as merror
from pymodbus.utilities import *

import struct

class ReadBitsRequestBase(ModbusRequest):
    ''' Base class for Messages Requesting bit values '''

    def __init__(self, address, count):
        '''
        Initializes the read request data
        @param address The start address to read from
        @param count The number of bits after 'address' to read
        '''
        ModbusRequest.__init__(self)
        self.address = address
        self.count = count

    def encode(self):
        ''' Encodes request pdu '''
        ret = struct.pack('>HH', self.address, self.count)
        return ret

    def decode(self, data):
        '''
        Decodes request pdu
        @param data The packet data to decode
        '''
        self.address, self.count = struct.unpack('>HH', data)

    def __str__(self):
        return "ReadBitRequest(%d,%d)" % (self.address, self.count)

class ReadBitsResponseBase(ModbusResponse):
    ''' Base class for Messages responding to bit-reading values '''

    def __init__(self, values):
        '''
        Initializes the response message
        @param values The requested values to be returned
        '''
        ModbusResponse.__init__(self)
        if values != None:
            self.bits = values
        else: self.bits = []

    def encode(self):
        ''' Encodes response pdu '''
        ret = packBitsToString(self.bits)
        return chr(len(ret)) + ret

    def decode(self, data):
        '''
        Decodes response pdu
        @param data The packet data to decode
        '''
        self.bits = unpackBitsFromString(data)[0]

    def setBit(self, address, value=1):
        '''
        Helper function to set the specified bit
        @param address The bit to set
        @param value The value to set the bit to
        '''
        self.bits[address] = value != 0

    def resetBit(self, address):
        '''
        Helper function to set the specified bit to 0
        @param address The bit to reset
        '''
        self.setBit(address, 0)

    def getBit(self, address):
        '''
        Helper function to get the specified bit's value
        @param address The bit to query
        '''
        return self.bits[address]

    def __str__(self):
        return "ReadBitResponse ", self.bits

class ReadCoilsRequest(ReadBitsRequestBase):
    '''
    "This function code is used to read from 1 to 2000(0x7d0) contiguous status
    of coils in a remote device. The Request PDU specifies the starting
    address, ie the address of the first coil specified, and the number of
    coils. In the PDU Coils are addressed starting at zero. Therefore coils
    numbered 1-16 are addressed as 0-15."
    '''
    function_code = 1

    def __init__(self, address=None, count=None):
        ReadBitsRequestBase.__init__(self, address, count)

    def execute(self, context):
        '''
        Run a read coils request against a datastore
        @param context The datastore to request from
        '''
        if not (1 <= self.count <= 0x7d0):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, self.count):
            return self.doException(merror.IllegalAddress)
        values = context.getValues(self.function_code, self.address, self.count)
        return ReadCoilsResponse(values)


class ReadCoilsResponse(ReadBitsResponseBase):
    '''
    The coils in the response message are packed as one coil per bit of
    the data field. Status is indicated as 1= ON and 0= OFF. The LSB of the
    first data byte contains the output addressed in the query. The other
    coils follow toward the high order end of this byte, and from low order
    to high order in subsequent bytes.

    If the returned output quantity is not a multiple of eight, the
    remaining bits in the final data byte will be padded with zeros
    (toward the high order end of the byte). The Byte Count field specifies
    the quantity of complete bytes of data.
    '''
    function_code = 1

    def __init__(self, values=None):
        '''
        Intializes the base message
        @param values The request values to respond with
        '''
        ReadBitsResponseBase.__init__(self, values)

class ReadDiscreteInputsRequest(ReadBitsRequestBase):
    '''
    This function code is used to read from 1 to 2000(0x7d0) contiguous status
    of discrete inputs in a remote device. The Request PDU specifies the
    starting address, ie the address of the first input specified, and the
    number of inputs. In the PDU Discrete Inputs are addressed starting at
    zero. Therefore Discrete inputs numbered 1-16 are addressed as 0-15.
    '''
    function_code = 2

    def __init__(self, address=None, count=None):
        ReadBitsRequestBase.__init__(self, address, count)

    def execute(self, context):
        '''
        Run a read discrete input request against a datastore
        @param context The datastore to request from
        '''
        if not (1 <= self.count <= 0x7d0):
            return self.doException(merror.IllegalValue)
        if not context.validate(self.function_code, self.address, self.count):
            return self.doException(merror.IllegalAddress)
        values = context.getValues(self.function_code, self.address, self.count)
        return ReadDiscreteInputsResponse(values)

class ReadDiscreteInputsResponse(ReadBitsResponseBase):
    '''
    The discrete inputs in the response message are packed as one input per
    bit of the data field. Status is indicated as 1= ON; 0= OFF. The LSB of
    the first data byte contains the input addressed in the query. The other
    inputs follow toward the high order end of this byte, and from low order
    to high order in subsequent bytes.

    If the returned input quantity is not a multiple of eight, the
    remaining bits in the final data byte will be padded with zeros
    (toward the high order end of the byte). The Byte Count field specifies
    the quantity of complete bytes of data.
    '''
    function_code = 2

    def __init__(self, values=None):
        '''
        Intializes the base message
        @param values The request values to respond with
        '''
        ReadBitsResponseBase.__init__(self, values)

#__all__ = ['']
