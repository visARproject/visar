from __future__ import division

import itertools
import math

from autoee import Net, Bus, Interval
from autoee import kicad, bom, easypart, landpattern, model, util, harnesses
from autoee.units import INCH, MM, MIL
from autoee.components import resistor as _resistor, capacitor as _capacitor, inductor

from autoee_components.mounting_hole import mounting_hole
from autoee_components.wire_terminal import wire_terminal
from autoee_components.jumper import trace_jumper, make_jumper_grid
from autoee_components.on_semiconductor import NOIV1SE1300A_QDC, NCP702
from autoee_components.molex import _71430, _1050281001
from autoee_components.sunex import CMT821
from autoee_components.stmicroelectronics.STM32F103TB import STM32F103TB
from autoee_components.texas_instruments.DS10BR150 import DS10BR150TSD
from autoee_components.xilinx.XC2C128 import XC2C128_6VQG100C
from autoee_components.vishay_semiconductors.VSMY7850X01 import VSMY7850X01
from autoee_components.rohm_semiconductor import BUxxTD3WG
from autoee_components.linear_technology.LT3476 import LT3476
from autoee_components.murata_electronics import BLM15G
from autoee_components.measurement_specialties import MS5611_01BA03
from autoee_components.invensense import MPU_9250
from autoee_components.maxim import DS18B20
from autoee_components.diodes_incorporated.DFLS140L import DFLS140L_7
from autoee_components.header import make_header

resistor = lambda *args, **kwargs: _resistor.resistor(*args, packages=frozenset({'0402 '}), **kwargs)
capacitor = lambda *args, **kwargs: _capacitor.capacitor(*args, packages=frozenset({'0402 '}), **kwargs) # might create a problem for power filtering...

digilent_vhdci = _71430._71430_0101('''
    IO1_P GND IO2_P IO3_P GND IO4_P IO5_P GND IO6_P IO7_P GND IO8_P IO9_P GND CLK10_P VCC VU
    VU VCC CLK11_P GND IO12_P IO13_P GND IO14_P IO15_P GND IO16_P IO17_P GND IO18_P IO19_P GND IO20_P
    
    IO1_N GND IO2_N IO3_N GND IO4_N IO5_N GND IO6_N IO7_N GND IO8_N IO9_N GND CLK10_N VCC VU
    VU VCC CLK11_N GND IO12_N IO13_N GND IO14_N IO15_N GND IO16_N IO17_N GND IO18_N IO19_N GND IO20_N
'''.split(), 'SHIELD')

lepton = _1050281001._1050281001('''
    GND GPIO3 GPIO2 GPIO1 GPIO0 GND VDDC GND
    GND GND SPI_MOSI SPI_MISO SPI_CLK SPI_CS_L GND VDDIO
    NC GND VDD GND SCL SDA PWR_DWN_L RESET_L
    GND MASTER_CLK GND MIPI_CLK_N MIPI_CLK_P GND MIPI_DATA_N MIPI_DATA_P
'''.split())

class LeptonHarness(object):
    def __init__(self, prefix,
            gnd=None, vddc=None, vdd=None, vddio=None,
            video_spi_bus=None, video_ss_n=None,
            i2c_bus=None, pwr_dwn_l=None, reset_l=None, master_clk=None):
        self.prefix = prefix
        self.gnd = Net(prefix+'_gnd') if gnd is None else gnd
        self.vddc = Net(prefix+'_vddc') if vddc is None else vddc
        self.vdd = Net(prefix+'_vdd') if vdd is None else vdd
        self.vddio = Net(prefix+'_vddio') if vddio is None else vddio
        self.video_spi_bus = harnesses.SPIBus.new(prefix) if video_spi_bus is None else video_spi_bus
        self.video_ss_n = Net(prefix + '_ss_n') if video_ss_n is None else video_ss_n
        self.i2c_bus = harnesses.I2CBus.new(prefix) if i2c_bus is None else i2c_bus
        self.pwr_dwn_l = Net(prefix+'_pwr_dwn_l') if pwr_dwn_l is None else pwr_dwn_l
        self.reset_l = Net(prefix+'_reset_l') if reset_l is None else reset_l
        self.master_clk = Net(prefix+'_master_clk') if master_clk is None else master_clk
    
    @util.listify
    def make(self):
        yield lepton(self.prefix+'U',
            GND=self.gnd,
            VDDC=self.vddc,
            SPI_MOSI=self.video_spi_bus.MOSI,
            SPI_MISO=self.video_spi_bus.MISO,
            SPI_CLK=self.video_spi_bus.SCLK,
            SPI_CS_L=self.video_ss_n,
            VDDIO=self.vddio,
            VDD=self.vdd,
            SCL=self.i2c_bus.SCL,
            SDA=self.i2c_bus.SDA,
            PWR_DWN_L=self.pwr_dwn_l,
            RESET_L=self.reset_l,
            MASTER_CLK=self.master_clk,
        )

class CameraHarness(object):
    def __init__(self, prefix,
            spi_bus=None, ss_n=None, 
            clock_in=None, clock=None, douts=None, sync=None,
            triggers=None, monitors=None, reset_n=None):
        self.spi_bus = harnesses.SPIBus.new(prefix) if spi_bus is None else spi_bus
        self.ss_n = Net(prefix + '_ss_n') if ss_n is None else ss_n
        self.clock_in = harnesses.LVDSPair.new(prefix + '_clock_in') if clock_in is None else clock_in
        self.clock = harnesses.LVDSPair.new(prefix + '_clock') if clock is None else clock
        self.douts = [harnesses.LVDSPair.new(prefix + '_dout%i' % (i,)) for i in xrange(4)] if douts is None else list(douts)
        assert len(self.douts) == 4
        self.sync = harnesses.LVDSPair.new(prefix + '_sync') if sync is None else sync
        self.triggers = [Net(prefix+'trigger%i' % (i,)) for i in xrange(3)] if triggers is None else list(triggers)
        assert len(self.triggers) == 3
        self.monitors = [Net(prefix+'monitor%i' % (i,)) for i in xrange(2)] if monitors is None else list(monitors)
        assert len(self.monitors) == 2
        self.reset_n = Net(prefix+'reset_n') if reset_n is None else reset_n

@util.listify
def camera(prefix, gnd, vcc3_3, vcc3_3_pix, vcc1_8, harness):
    ibias_master = Net(prefix+'IBIAS')
    yield resistor(47e3)(prefix+'R1', A=ibias_master, B=gnd) # gnd_33
    
    vdd_18 = vcc1_8 # Net(prefix+'vdd_18')
    for i in xrange(3): yield capacitor(100e-9)(prefix+'C1%i' % i, A=vdd_18, B=gnd)
    for i in xrange(2): yield capacitor( 10e-6)(prefix+'C2%i' % i, A=vdd_18, B=gnd)
    
    vdd_33 = vcc3_3 # Net(prefix+'vdd_33')
    for i in xrange(4): yield capacitor(100e-9)(prefix+'C3%i' % i, A=vdd_33, B=gnd)
    for i in xrange(2): yield capacitor(4.7e-6)(prefix+'C4%i' % i, A=vdd_33, B=gnd)
    for i in xrange(2): yield capacitor( 10e-6)(prefix+'C5%i' % i, A=vdd_33, B=gnd)
    
    vdd_pix = Net(prefix+'vdd_pix')
    yield BLM15G.BLM15GG471SN1D(prefix+'FB1', A=vcc3_3_pix, B=vdd_pix)
    for i in xrange(4): yield capacitor(4.7e-6)(prefix+'C6%i' % i, A=vdd_pix, B=gnd)
    for i in xrange(2): yield _capacitor.capacitor(100e-6, voltage=3.3*1.5)(prefix+'C7%i' % i, A=vdd_pix, B=gnd) # not restricted to 0402
    
    yield NOIV1SE1300A_QDC.NOIV1SE1300A_QDC(prefix+'U1',
        vdd_33=vdd_33,
        gnd_33=gnd,
        vdd_pix=vdd_pix,
        gnd_colpc=gnd,
        vdd_18=vdd_18,
        gnd_18=gnd,
        
        mosi=harness.spi_bus.MOSI,
        miso=harness.spi_bus.MISO,
        sck=harness.spi_bus.SCLK,
        ss_n=harness.ss_n,
        
        clock_outn=harness.clock.N,
        clock_outp=harness.clock.P,
        doutn0=harness.douts[0].N,
        doutp0=harness.douts[0].P,
        doutn1=harness.douts[1].N,
        doutp1=harness.douts[1].P,
        doutn2=harness.douts[2].N,
        doutp2=harness.douts[2].P,
        doutn3=harness.douts[3].N,
        doutp3=harness.douts[3].P,
        syncn=harness.sync.N,
        syncp=harness.sync.P,
        
        lvds_clock_inn=harness.clock_in.N,
        lvds_clock_inp=harness.clock_in.P,
        
        clk_pll=gnd,
        
        ibias_master=ibias_master,
        
        trigger0=harness.triggers[0],
        trigger1=harness.triggers[1],
        trigger2=harness.triggers[2],
        monitor0=harness.monitors[0],
        monitor1=harness.monitors[1],
        
        reset_n=harness.reset_n,
    )
    yield CMT821.CMT821(prefix+'M1')
    yield resistor(100, error=0, tolerance=0.01)(prefix+'R2', A=harness.clock_in.P, B=harness.clock_in.N)

@util.listify
def sensors(prefix,
    GND, VCC,
    
    imu_spi_bus,
    imu_spi_nCS,
    imu_FSYNC, imu_INT,
    
    baro_spi_bus,
    baro_spi_nCS,
):
    yield capacitor(100e-9)(prefix+'C0', A=VCC, B=GND)
    yield MS5611_01BA03.MS5611_01BA03(prefix+'U1',
        VDD=VCC,
        PS=GND, # use SPI
        GND=GND,
        CSB=baro_spi_nCS,
        SDO=baro_spi_bus.MISO,
        SDI=baro_spi_bus.MOSI,
        SCLK=baro_spi_bus.SCLK,
    )
    
    
    yield capacitor(10e-9)(prefix+'C3', A=VCC, B=GND) # near VDDIO
    yield capacitor(0.1e-6)(prefix+'C2', A=VCC, B=GND) # near VDD
    
    REGOUT = Net(prefix+'_REGOUT')
    yield capacitor(0.1e-6)(prefix+'C1', A=REGOUT, B=GND)
    
    yield MPU_9250.MPU_9250(prefix+'U2',
        RESV_1=VCC,
        VDDIO=VCC,
        AD0_SDO=imu_spi_bus.MISO,
        REGOUT=REGOUT,
        FSYNC=imu_FSYNC,
        INT=imu_INT,
        VDD=VCC,
        GND=GND,
        RESV_20=GND,
        nCS=imu_spi_nCS,
        SCL_SCLK=imu_spi_bus.SCLK,
        SDA_SDI=imu_spi_bus.MOSI,
    )

@util.listify
def main():
    for i in xrange(4):
        yield mounting_hole('M%i' % (i,))
    
    gnd = Net('gnd')
    
    vcc5in = Net('vcc5in') # specified at 1 A. could supply a lot more at peak if pulsed. used only for LED driver.
    vcc3_3in = Net('vcc3_3in') # specification unclear; around 1 A. used only for LVDS buffers and regulators.
    
    vcc1_2_1 = Net('vcc1_2_1') # thermal 1 (110mA)
    vcc1_2_2 = Net('vcc1_2_2') # thermal 2 (110mA)
    vcc1_8 = Net('vcc1_8') # CPLD (40mA)
    vcc1_8_1 = Net('vcc1_8_1') # CMOS (75mA) - switched
    vcc1_8_1_en = Net('vcc1_8_1_en') # XXX connect to CPLD
    vcc1_8_2 = Net('vcc1_8_2') # CMOS (75mA) - switched
    vcc1_8_2_en = Net('vcc1_8_2_en') # XXX connect to CPLD
    vcc2_8_1 = Net('vcc2_8_1') # thermal (16mA)
    vcc2_8_2 = Net('vcc2_8_2') # thermal (16mA)
    vcc3_0 = Net('vcc3_0') # CPLD, thermal (4mA*2), ARM
    vcc3_0_1a = Net('vcc3_0_1a') # CMOS (130mA) - switched
    vcc3_0_1a_en = Net('vcc3_0_1a_en') # XXX connect to CPLD
    vcc3_0_1b = Net('vcc3_0_1b') # CMOS (2.5mA) - switched
    vcc3_0_1b_en = Net('vcc3_0_1b_en') # XXX connect to CPLD
    vcc3_0_2a = Net('vcc3_0_2a') # CMOS (130mA) - switched
    vcc3_0_2a_en = Net('vcc3_0_2a_en') # XXX connect to CPLD
    vcc3_0_2b = Net('vcc3_0_2b') # CMOS (2.5mA) - switched
    vcc3_0_2b_en = Net('vcc3_0_2b_en') # XXX connect to CPLD
    
    for n, v, en in [
        (vcc1_2_1 , 1.2, None),
        (vcc1_2_2 , 1.2, None),
        (vcc1_8   , 1.8, None),
        (vcc1_8_1 , 1.8, vcc1_8_1_en),
        (vcc1_8_2 , 1.8, vcc1_8_2_en),
        (vcc2_8_1 , 2.8, None),
        (vcc2_8_2 , 2.8, None),
        (vcc3_0   , 3.0, None),
        (vcc3_0_1a, 3.0, vcc3_0_1a_en),
        (vcc3_0_1b, 3.0, vcc3_0_1b_en),
        (vcc3_0_2a, 3.0, vcc3_0_2a_en),
        (vcc3_0_2b, 3.0, vcc3_0_2b_en),
    ]:
        if v != 1.2:
            yield NCP702.by_voltage[v](n.name + 'U',
                IN=vcc3_3in,
                GND=gnd,
                EN=vcc3_3in if en is None else en,
                OUT=n,
                NC=gnd, # thermal
            )
            yield capacitor(1e-6)(n.name + 'C1', A=vcc3_3in, B=gnd)
            yield capacitor(1e-6)(n.name + 'C2', A=n, B=gnd)
        else:
            yield BUxxTD3WG.by_voltage[v](n.name + 'U',
                VIN=vcc3_3in,
                GND=gnd,
                nSTBY=vcc3_3in if en is None else en,
                VOUT=n,
                NC=gnd, # thermal
            )
            yield capacitor(0.47e-6)(n.name + 'C1', A=vcc3_3in, B=gnd)
            yield capacitor(0.47e-6)(n.name + 'C2', A=n, B=gnd)
    
    shield = Net('shield')
    yield _capacitor.capacitor(1e-9, voltage=250)('C2', A=shield, B=gnd)
    yield resistor(1e6)('R2', A=shield, B=gnd)
    
    pairs = {i: harnesses.LVDSPair.new('pair%i' % (i,)) for i in xrange(1, 20+1)}
    yield digilent_vhdci('P1',
        GND=gnd,
        SHIELD=shield,
        VU=vcc5in,
        VCC=vcc3_3in,
        CLK10_P=pairs[10].P, CLK10_N=pairs[10].N,
        CLK11_P=pairs[11].P, CLK11_N=pairs[11].N,
        **dict(
            [('IO%i_P' % (i,), pairs[i].P) for i in range(1, 9+1)+range(12, 20+1)] +
            [('IO%i_N' % (i,), pairs[i].N) for i in range(1, 9+1)+range(12, 20+1)])
    )
    
    bufout = {}
    for i in [2, 3, 4, -5, -6, -10, 11, 15, 16, -17, 18, 19]:
        swap = not (i < 0)
        i = abs(i)
        bufout[i] = harnesses.LVDSPair.new('out%i' % (i,))
        a = bufout[i].swapped if swap else bufout[i]
        b = pairs[i].swapped if swap else pairs[i]
        yield capacitor(100e-9)('B%iC' % (i,), A=vcc3_3in, B=gnd)
        yield DS10BR150TSD('B%i' % (i,),
            GND=gnd,
            INn=a.N,
            INp=a.P,
            VCC=vcc3_3in,
            OUTp=b.P,
            OUTn=b.N,
        )
    
    bufin = {}
    for i in [-1, 20]:
        swap = not (i < 0)
        i = abs(i)
        bufin[i] = harnesses.LVDSPair.new('out%i' % (i,))
        a = pairs[i].swapped if swap else pairs[i]
        b = bufin[i].swapped if swap else bufin[i]
        yield capacitor(100e-9)('B%iC' % (i,), A=vcc3_3in, B=gnd)
        yield DS10BR150TSD('B%i' % (i,),
            GND=gnd,
            INn=a.N,
            INp=a.P,
            VCC=vcc3_3in,
            OUTp=b.P,
            OUTn=b.N,
        )
    
    C1_harness = CameraHarness('C1',
        clock_in=bufin[1].swapped,
        douts=[bufout[6], bufout[5], bufout[4].swapped, bufout[3].swapped],
        sync=bufout[2].swapped,
        clock=bufout[10],
    )
    yield camera('C1',
        gnd=gnd,
        vcc1_8=vcc1_8_1,
        vcc3_3=vcc3_0_1a,
        vcc3_3_pix=vcc3_0_1b,
        harness=C1_harness,
    )
    
    C2_harness = CameraHarness('C2',
        clock_in=bufin[20],
        douts=[bufout[15], bufout[16], bufout[17].swapped, bufout[18]],
        sync=bufout[19],
        clock=bufout[11],
    )
    yield camera('C2',
        gnd=gnd,
        vcc1_8=vcc1_8_2,
        vcc3_3=vcc3_0_2a,
        vcc3_3_pix=vcc3_0_2b,
        harness=C2_harness,
    )
    
    
    lepton1 = LeptonHarness('T1',
        gnd=gnd,
        vddc=vcc1_2_1,
        vdd=vcc2_8_1,
        vddio=vcc3_0,
    )
    yield lepton1.make()
    
    lepton2 = LeptonHarness('T2',
        gnd=gnd,
        vddc=vcc1_2_2,
        vdd=vcc2_8_2,
        vddio=vcc3_0,
    )
    yield lepton2.make()
    
    baro_spi_bus = harnesses.SPIBus.new('baro_') # XXX connect to CPLD
    baro_spi_nCS = Net('baro_spi_nCS') # XXX connect to CPLD
    imu_spi_bus = harnesses.SPIBus.new('imu_') # XXX connect to CPLD
    imu_spi_nCS = Net('imu_spi_nCS') # XXX connect to CPLD
    imu_FSYNC = Net('imu_FSYNC') # XXX connect to CPLD
    imu_INT = Net('imu_INT') # XXX connect to CPLD
    yield sensors('S',
        GND=gnd,
        VCC=vcc3_0,
        baro_spi_bus=baro_spi_bus,
        baro_spi_nCS=baro_spi_nCS,
        imu_spi_bus=imu_spi_bus,
        imu_spi_nCS=imu_spi_nCS,
        imu_FSYNC=imu_FSYNC,
        imu_INT=imu_INT,
    )
    
    led_gnd = Net('led_gnd')
    yield trace_jumper(60*MIL)('J2', A=led_gnd, B=gnd)
    led_pwr = Net('led_pwr')
    yield wire_terminal()('P3', T=led_pwr)
    yield wire_terminal()('P4', T=led_gnd)
    yield make_jumper_grid('J1', [[vcc5in, led_pwr]], grid_size=66*MIL, box_size=60*MIL)
    led_pwm = [Net('led_pwm%i' % (i,)) for i in xrange(4)]
    led_nSHDN = Net('led_nSHDN')
    temp_bus = Net('temp_bus')
    yield leds('I',
        led_gnd=led_gnd,
        led_pwr=vcc5in, # XXX add connector for external higher current 5V power
        pwm=led_pwm,
        nSHDN=led_nSHDN,
        
        temp_gnd=gnd,
        temp_pwr=vcc3_3in,
        temp_bus=temp_bus,
    )
    
    cpld_jtag = harnesses.JTAG.new('cpld_') # XXX make connector for. make sure to use vcc3_0 for power pin
    yield make_header('VREF GND TCK TDO TDI TMS'.split(' '))('P2',
        VREF=vcc3_0,
        GND=gnd,
        TCK=cpld_jtag.TCK,
        TDI=cpld_jtag.TDI,
        TDO=cpld_jtag.TDO,
        TMS=cpld_jtag.TMS,
    )
    
    for i in xrange(6):
        yield capacitor(0.1e-6)('U2C%i' % (i,), A=vcc3_0, B=gnd)
    for i in xrange(2):
        yield capacitor(0.1e-6)('U2C%i' % (10+i,), A=vcc1_8, B=gnd)
    yield XC2C128_6VQG100C('U2',
        GND=gnd,
        VCC=vcc1_8,
        
        VAUX=vcc3_0,
        TDI=cpld_jtag.TDI,
        TDO=cpld_jtag.TDO,
        TCK=cpld_jtag.TCK,
        TMS=cpld_jtag.TMS,
        
        # IO pins can be rearranged any which way, except that GCK pins need
        # to be connected to expansion connector
        VCCIO1=vcc3_0,
        VCCIO2=vcc3_0,
        
        IO1_33=pairs[7].N,
        IO1_32=pairs[7].P,
        IO1_30=pairs[8].N,
        IO1_29=pairs[8].P,
        IO1_28=pairs[9].P,
        IO1_27=pairs[9].N, # GCK
        
        IO1_24=pairs[12].N,
        IO1_23=pairs[12].P, # GCK
        IO1_22=pairs[13].P, # GCK
        IO1_19=pairs[13].N,
        IO1_18=pairs[14].P,
        IO1_17=pairs[14].N,
        
        #IO1_32=temp_bus, # XXX
        #IO1_33=led_pwm[0],
        #IO1_34=led_pwm[1],
        #IO1_35=led_pwm[2],
        #IO1_36=led_pwm[3],
        #IO1_37=led_nSHDN,
        
        
        IO1_39=C1_harness.spi_bus.SCLK,
        IO1_40=C1_harness.spi_bus.MISO,
        IO1_41=C1_harness.spi_bus.MOSI,
        IO1_42=C1_harness.ss_n,
        IO1_43=C1_harness.reset_n,
        IO1_44=C1_harness.monitors[1],
        IO1_46=C1_harness.monitors[0],
        IO1_49=C1_harness.triggers[2],
        IO1_50=C1_harness.triggers[1],
        IO1_52=C1_harness.triggers[0],
        IO1_53=lepton1.master_clk,
        IO1_54=lepton1.pwr_dwn_l,
        IO1_55=lepton1.reset_l,
        IO1_56=lepton1.i2c_bus.SCL,
        IO1_58=lepton1.i2c_bus.SDA,
        IO1_59=lepton1.video_spi_bus.MOSI,
        IO1_60=lepton1.video_spi_bus.MISO,
        IO1_61=lepton1.video_spi_bus.SCLK,
        IO1_63=lepton1.video_ss_n,
        
        
        IO2_10=C2_harness.triggers[0],
        IO2_9=C2_harness.triggers[1],
        IO2_8=C2_harness.triggers[2],
        IO2_7=C2_harness.monitors[0],
        IO2_6=C2_harness.monitors[1],
        IO2_4=C2_harness.reset_n,
        IO2_3=C2_harness.ss_n,
        IO2_2=C2_harness.spi_bus.MOSI,
        IO2_1=C2_harness.spi_bus.MISO,
        IO2_99=C2_harness.spi_bus.SCLK,
        IO2_97=lepton2.reset_l,
        IO2_96=lepton2.pwr_dwn_l,
        IO2_95=lepton2.master_clk,
        IO2_94=lepton2.video_ss_n,
        IO2_93=lepton2.video_spi_bus.SCLK,
        IO2_92=lepton2.video_spi_bus.MISO,
        IO2_91=lepton2.video_spi_bus.MOSI,
        IO2_90=lepton2.i2c_bus.SDA,
        IO2_89=lepton2.i2c_bus.SCL,
    )
    
    yield micro('M',
        gnd=gnd, vcc3_0=vcc3_0,
    )

@util.listify
def leds(prefix, led_gnd, led_pwr, pwm, nSHDN, temp_gnd, temp_pwr, temp_bus):
    # maximum current
    #   driver: > 1 A/channel
    #   LED: 1 A DC, 5 A pulses
    
    ref = Net(prefix+'ref') # 1.05 V
    yield capacitor(0.1e-6)(prefix+'C1', A=ref, B=led_gnd)
    refdiv = Net(prefix+'refdiv') # 1.00 V
    yield resistor(4.99e3)(prefix+'R1', A=ref, B=refdiv)
    yield resistor(100e3)(prefix+'R2', A=refdiv, B=led_gnd)
    
    assert len(pwm) == 4
    cap = [Net(prefix+'cap%i' % (i,)) for i in xrange(4)]
    led = [Net(prefix+'led%i' % (i,)) for i in xrange(4)]
    cat = [Net(prefix+'cat%i' % (i,)) for i in xrange(4)]
    sw = [Net(prefix+'sw%i' % (i,)) for i in xrange(4)]
    vadj = [refdiv for i in xrange(4)]
    vc = [Net(prefix+'vc%i' % (i,)) for i in xrange(4)]
    
    yield resistor(10e3)(prefix+'R3', A=nSHDN, B=led_gnd)
    
    for i in xrange(4):
        yield trace_jumper(5*MIL)(prefix+'D%iJ' % (i,), A=led_pwr, B=cap[i])
        
        yield resistor(100e-3)(prefix+'D%iR' % (i,), A=cap[i], B=led[i]) # refdiv setting & this = 1.00 A thru LED # XXX check power rating
        yield VSMY7850X01(prefix+'D%i' % (i,),
            A=led[i],
            C=cat[i],
        )
        yield capacitor(0.22e-6)(prefix+'D%iC' % (i,), A=led_pwr, B=cat[i])
        yield inductor.inductor(Interval.from_center_and_relative_error(10e-6, 0.3), minimum_current=1, maximum_resistance=100e-3)(prefix+'D%iL' % (i,), A=cat[i], B=sw[i])
        yield DFLS140L_7(prefix+'D%iD' % (i+4,), A=sw[i], C=led_pwr)
        
        yield capacitor(1e-9)(prefix+'D%iC2' % (i,), A=vc[i], B=led_gnd)
        
        yield DS18B20.DS18B20U_('D%iU' % (i,),
            GND=temp_gnd,
            VDD=temp_pwr,
            DQ=temp_bus,
            NC=led[i], # thermal connection
        )
    
    rt = Net(prefix+'rt')
    yield resistor(21e3)(prefix+'RT', A=rt, B=led_gnd) # 1 MHz
    
    yield capacitor(2.2e-6)(prefix+'U3C', A=led_pwr, B=led_gnd)
    yield LT3476(prefix+'U3',
        GND=led_gnd,
        NC=led_gnd, # better heat dissipation
        VIN=led_pwr,
        nSHDN=nSHDN,
        REF=ref,
        RT=rt,
        **util.union_dicts(
            {'PWM%i' % (i+1,): pwm[i] for i in xrange(4)},
            {'SW%i' % (i+1,): sw[i] for i in xrange(4)},
            {'CAP%i' % (i+1,): cap[i] for i in xrange(4)},
            {'LED%i' % (i+1,): led[i] for i in xrange(4)},
            {'VADJ%i' % (i+1,): vadj[i] for i in xrange(4)},
            {'VC%i' % (i+1,): vc[i] for i in xrange(4)},
        ))

@util.listify
def micro(prefix, gnd, vcc3_0):
    # XXX decoupling
    # XXX reset line
    # XXX SWD header
    
    jtag = harnesses.JTAG.new(prefix+'mc_')
    
    yield STM32F103TB(prefix+'U1',
        VSS=gnd,
        BOOT0=gnd,
        NRST=vcc3_0,
        VDD=vcc3_0,
        
        PA13=jtag.TMS,
        PA14=jtag.TCK,
        PA15=jtag.TDI,
        PB3=jtag.TDO,
        PB4=jtag.TRST,
    )

desc = main()
kicad.generate(desc, 'kicad')
bom.generate(desc, 'bom')
