#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import time

# ---------------------------
# Detect if running on a Raspberry Pi
# ---------------------------
def is_raspberry_pi():
    try:
        with open("/proc/cpuinfo") as f:
            cpuinfo = f.read()
        return "BCM" in cpuinfo or "Raspberry Pi" in cpuinfo
    except FileNotFoundError:
        return False

ON_PI = is_raspberry_pi()

# ---------------------------
# Conditional imports / mocks
# ---------------------------
if ON_PI:
    import RPi.GPIO as GPIO
    import spi
else:
    # Mock GPIO
    class MockGPIO:
        BOARD = None
        OUT = None
        HIGH = 1
        LOW = 0
        def setmode(self, mode): pass
        def setup(self, pin, mode): pass
        def output(self, pin, value): pass

    # Mock SPI
    class MockSPI:
        def openSPI(self, device="/dev/spidev0.0", speed=1000000): pass
        def transfer(self, data): 
            # Return dummy two-byte response
            return [0, 0]

    GPIO = MockGPIO()
    spi = MockSPI()

# ---------------------------
# MFRC522 Class
# ---------------------------
class MFRC522:
    NRSTPD = 22
    MAX_LEN = 16

    # Commands
    PCD_IDLE       = 0x00
    PCD_AUTHENT    = 0x0E
    PCD_RECEIVE    = 0x08
    PCD_TRANSMIT   = 0x04
    PCD_TRANSCEIVE = 0x0C
    PCD_RESETPHASE = 0x0F
    PCD_CALCCRC    = 0x03

    # Mifare card commands
    PICC_REQIDL    = 0x26
    PICC_REQALL    = 0x52
    PICC_ANTICOLL  = 0x93
    PICC_SElECTTAG = 0x93
    PICC_AUTHENT1A = 0x60
    PICC_AUTHENT1B = 0x61
    PICC_READ      = 0x30
    PICC_WRITE     = 0xA0
    PICC_DECREMENT = 0xC0
    PICC_INCREMENT = 0xC1
    PICC_RESTORE   = 0xC2
    PICC_TRANSFER  = 0xB0
    PICC_HALT      = 0x50

    # Status codes
    MI_OK       = 0
    MI_NOTAGERR = 1
    MI_ERR      = 2

    # Registers
    CommandReg     = 0x01
    CommIEnReg     = 0x02
    DivlEnReg      = 0x03
    CommIrqReg     = 0x04
    DivIrqReg      = 0x05
    ErrorReg       = 0x06
    Status1Reg     = 0x07
    Status2Reg     = 0x08
    FIFODataReg    = 0x09
    FIFOLevelReg   = 0x0A
    ControlReg     = 0x0C
    BitFramingReg  = 0x0D
    TxControlReg   = 0x14
    TxAutoReg      = 0x15
    ModeReg        = 0x11
    TModeReg       = 0x2A
    TPrescalerReg  = 0x2B
    TReloadRegH    = 0x2C
    TReloadRegL    = 0x2D
    DivIrqReg      = 0x05
    CRCResultRegL  = 0x22
    CRCResultRegM  = 0x21
    Status2Reg     = 0x08
    ControlReg     = 0x0C
    FIFOLevelReg   = 0x0A
    MAX_LEN        = 16

    def __init__(self, dev='/dev/spidev0.0', spd=1000000):
        # SPI initialization
        spi.openSPI(device=dev, speed=spd)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.NRSTPD, GPIO.OUT)
        GPIO.output(self.NRSTPD, GPIO.HIGH)
        self.MFRC522_Init()

    # ---------------------------
    # Low-level SPI operations
    # ---------------------------
    def Write_MFRC522(self, addr, val):
        spi.transfer(((addr << 1) & 0x7E, val))

    def Read_MFRC522(self, addr):
        val = spi.transfer((((addr << 1) & 0x7E) | 0x80, 0))
        return val[1]

    # ---------------------------
    # Bitmask helpers
    # ---------------------------
    def SetBitMask(self, reg, mask):
        tmp = self.Read_MFRC522(reg)
        self.Write_MFRC522(reg, tmp | mask)

    def ClearBitMask(self, reg, mask):
        tmp = self.Read_MFRC522(reg)
        self.Write_MFRC522(reg, tmp & (~mask))

    # ---------------------------
    # Antenna control
    # ---------------------------
    def AntennaOn(self):
        temp = self.Read_MFRC522(self.TxControlReg)
        if ~(temp & 0x03):
            self.SetBitMask(self.TxControlReg, 0x03)

    def AntennaOff(self):
        self.ClearBitMask(self.TxControlReg, 0x03)

    # ---------------------------
    # Card communication
    # ---------------------------
    def MFRC522_ToCard(self, command, sendData):
        backData = []
        backLen = 0
        status = self.MI_ERR
        irqEn = 0x00
        waitIRq = 0x00

        if command == self.PCD_AUTHENT:
            irqEn = 0x12
            waitIRq = 0x10
        elif command == self.PCD_TRANSCEIVE:
            irqEn = 0x77
            waitIRq = 0x30

        self.Write_MFRC522(self.CommIEnReg, irqEn | 0x80)
        self.ClearBitMask(self.CommIrqReg, 0x80)
        self.SetBitMask(self.FIFOLevelReg, 0x80)
        self.Write_MFRC522(self.CommandReg, self.PCD_IDLE)

        for data in sendData:
            self.Write_MFRC522(self.FIFODataReg, data)

        self.Write_MFRC522(self.CommandReg, command)

        if command == self.PCD_TRANSCEIVE:
            self.SetBitMask(self.BitFramingReg, 0x80)

        i = 2000
        while True:
            n = self.Read_MFRC522(self.CommIrqReg)
            i -= 1
            if not ((i != 0) and not (n & 0x01) and not (n & waitIRq)):
                break

        self.ClearBitMask(self.BitFramingReg, 0x80)

        if i != 0:
            if (self.Read_MFRC522(self.ErrorReg) & 0x1B) == 0x00:
                status = self.MI_OK
                if n & irqEn & 0x01:
                    status = self.MI_NOTAGERR
                n = self.Read_MFRC522(self.FIFOLevelReg)
                lastBits = self.Read_MFRC522(self.ControlReg) & 0x07
                backLen = (n - 1) * 8 + lastBits if lastBits != 0 else n * 8
                if n == 0: n = 1
                if n > self.MAX_LEN: n = self.MAX_LEN
                backData = [self.Read_MFRC522(self.FIFODataReg) for _ in range(n)]

        return status, backData, backLen

    # ---------------------------
    # CRC calculation
    # ---------------------------
    def CalulateCRC(self, data):
        self.ClearBitMask(self.DivIrqReg, 0x04)
        self.SetBitMask(self.FIFOLevelReg, 0x80)
        for byte in data:
            self.Write_MFRC522(self.FIFODataReg, byte)
        self.Write_MFRC522(self.CommandReg, self.PCD_CALCCRC)
        i = 0xFF
        while True:
            n = self.Read_MFRC522(self.DivIrqReg)
            i -= 1
            if not ((i != 0) and not (n & 0x04)):
                break
        return [self.Read_MFRC522(self.CRCResultRegL), self.Read_MFRC522(self.CRCResultRegM)]

    # ---------------------------
    # Initialization
    # ---------------------------
    def MFRC522_Init(self):
        GPIO.output(self.NRSTPD, 1)
        self.Write_MFRC522(self.TModeReg, 0x8D)
        self.Write_MFRC522(self.TPrescalerReg, 0x3E)
        self.Write_MFRC522(self.TReloadRegL, 30)
        self.Write_MFRC522(self.TReloadRegH, 0)
        self.Write_MFRC522(self.TxAutoReg, 0x40)
        self.Write_MFRC522(self.ModeReg, 0x3D)
        self.AntennaOn()
