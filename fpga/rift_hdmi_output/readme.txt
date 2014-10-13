*******************************************************************************
** © Copyright 2010 Xilinx, Inc. All rights reserved.
** This file contains confidential and proprietary information of Xilinx, Inc. and 
** is protected under U.S. and international copyright and other intellectual property laws.
*******************************************************************************
**   ____  ____ 
**  /   /\/   / 
** /___/  \  /   Vendor: Xilinx 
** \   \   \/    
**  \   \        readme.txt Version: 1.0  
**  /   /        Date Last Modified: 11/17/2010 
** /___/   /\    Date Created: 
** \   \  /  \   Associated Filename: xapp495.zip
**  \___\/\___\ 
** 
**  Device: 
**  Purpose:
**  Reference: XAPP495.pdf
**  Revision History: 
**    1.0 - Initial Release
**   
*******************************************************************************
**
**  Disclaimer: 
**
**		This disclaimer is not a license and does not grant any rights to the materials 
**              distributed herewith. Except as otherwise provided in a valid license issued to you 
**              by Xilinx, and to the maximum extent permitted by applicable law: 
**              (1) THESE MATERIALS ARE MADE AVAILABLE "AS IS" AND WITH ALL FAULTS, 
**              AND XILINX HEREBY DISCLAIMS ALL WARRANTIES AND CONDITIONS, EXPRESS, IMPLIED, OR STATUTORY, 
**              INCLUDING BUT NOT LIMITED TO WARRANTIES OF MERCHANTABILITY, NON-INFRINGEMENT, OR 
**              FITNESS FOR ANY PARTICULAR PURPOSE; and (2) Xilinx shall not be liable (whether in contract 
**              or tort, including negligence, or under any other theory of liability) for any loss or damage 
**              of any kind or nature related to, arising under or in connection with these materials, 
**              including for any direct, or any indirect, special, incidental, or consequential loss 
**              or damage (including loss of data, profits, goodwill, or any type of loss or damage suffered 
**              as a result of any action brought by a third party) even if such damage or loss was 
**              reasonably foreseeable or Xilinx had been advised of the possibility of the same.


**  Critical Applications:
**
**		Xilinx products are not designed or intended to be fail-safe, or for use in any application 
**		requiring fail-safe performance, such as life-support or safety devices or systems, 
**		Class III medical devices, nuclear facilities, applications related to the deployment of airbags,
**		or any other applications that could lead to death, personal injury, or severe property or 
**		environmental damage (individually and collectively, "Critical Applications"). Customer assumes 
**		the sole risk and liability of any use of Xilinx products in Critical Applications, subject only 
**		to applicable laws and regulations governing limitations on product liability.

**  THIS COPYRIGHT NOTICE AND DISCLAIMER MUST BE RETAINED AS PART OF THIS FILE AT ALL TIMES.

*******************************************************************************

This readme describes how to use the files that come with XAPP495

*******************************************************************************

** IMPORTANT NOTES **

1) The design files have been tested on Digilent Atlys Board

2) The UCF files are targeted to the Atlys board

*******************************************************************************

Included files:

DVI transmitter

1.  "dvi_demo/rtl/tx/dvi_encoder.v" --- DVI transmitter top module without instantiation of clocking resources
2.  "dvi_demo/rtl/tx/dvi_encoder_top.v" --- DVI transmitter wrapper with instantiation of clocking resources
3.  "dvi_demo/rtl/tx/encode.v" --- DVI encoder
4.  "dvi_demo/rtl/tx/serdes_n_to_1.v" --- configurable to 5:1 serializaer
5.  "dvi_demo/rtl/tx/convert_30to15_fifo.v" --- 30-bit 2:1 gear box
6.  "dvi_demo/rtl/tx/vtc_demo.v" --- Color bar generator with programmable timing controller

DVI Receiver

1.  "dvi_demo/rtl/tx/dvi_decoder.v" --- DVI receiver top wrapper
2.  "dvi_demo/rtl/tx/decode.v"  --- DVI decoder instantiating the CDR and channel de-skew circuits
3.  "dvi_demo/rtl/tx/chnlbond.v"  --- Channel de-skew module
4.  "dvi_demo/rtl/tx/phsaligner.v"  --- Bitslip and TMDS data validation state machine
5.  "dvi_demo/rtl/tx/serdes_1_to_5_diff_data.v" --- 1:5 de-serializer

DVI Common Modules

1.  "dvi_demo/rtl/common/DRAM16XN.v" --- Width configurable distributed RAM
2.  "dvi_demo/rtl/common/timing.v" --- Video Timing Controller
3.  "dvi_demo/rtl/common/hdclrbar.v" --- SMPTE HD color bar generator
4.  "dvi_demo/rtl/common/debnce.v" --- DIP switch debouncer
5.  "dvi_demo/rtl/common/dcmspi.v" --- DCM_CLKGEN SPI controller
6.  "dvi_demo/rtl/common/synchro.v" --- Clock boundary synchronizer

DVI Evaluation

"dvi_demo/rtl/dvi_demo.v" --- 2x2 DVI Matrix design

UCF

"dvi_demo/ucf/vtc_demo.ucf"  --- Transmitter only design with color bar generation and programmable timing controller
"dvi_demo/ucf/dvi_demo.ucf"  --- 2x2 DVI Matrix design
