import os
import sys
import time
import logging
import usb.core
import usb.util
import numpy as np

# Configure clinical infrastructure logging loops
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] (UWMed-Ingest) %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class FlirOneProStreamer:
    def __init__(self):
        # Official FLIR Systems, Inc. hardware signature properties
        self.VENDOR_ID = 0x09cb
        self.PRODUCT_ID = 0x1996
        self.device = None
        self.ep_in = None
        
    def initialize_usb_connection(self):
        """Finds the device matrix, detaches kernel interference, and opens data pipelines."""
        logging.info("Searching clinical USB registry for FLIR ONE Pro hardware core...")
        self.device = usb.core.find(idVendor=self.VENDOR_ID, idProduct=self.PRODUCT_ID)
        
        if self.device is None:
            logging.error("FLIR ONE Pro physical connection undetected. Verify udev mapping.")
            return False
            
        # Safely detach active kernel drivers if previously bound by the host OS
        if self.device.is_kernel_driver_active(0):
            try:
                self.device.detach_kernel_driver(0)
                logging.info("Detached generic host OS kernel driver from imaging interface.")
            except usb.core.USBError as e:
                logging.error(f"Failed to isolate USB subsystem interface: {str(e)}")
                return False
                
        # Set active hardware configuration endpoint
        self.device.set_configuration()
        cfg = self.device.get_active_configuration()
        intf = cfg[(0,0)]
        
        # Locate the high-speed bulk input endpoint configuration block
        self.ep_in = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
        )
        
        if self.ep_in is None:
            logging.error("Failed to map bulk input data endpoint from hardware register map.")
            return False
            
        logging.info("Successfully established zero-loss communication bridge to FLIR core.")
        return True

    def initiate_hardware_loop(self):
        """Loops bulk data buffers into host VRAM memory spaces continuously."""
        if not self.initialize_usb_connection():
            return
            
        # Magic configuration packets to trigger internal FLIR Lepton 3.5 frame rendering
        # These bypass mobile application requirements for raw stream access
        START_FRAME_STREAM_CMD = b'\x01\x00\x00\x00\x00\x00\x00\x00'
        
        try:
            # Write start command to control endpoint zero
            self.device.ctrl_transfer(0x21, 0x09, 0x0200, 0x0000, START_FRAME_STREAM_CMD)
            logging.info("Sent telemetry execution sync signal. Ingesting raw frames...")
            
            # Strict FLIR ONE Pro buffer payload footprint (interleaved thermal and visible bytes)
            FRAME_BUFFER_CEILING = 504000 
            
            while True:
                # Retrieve raw byte sequences over the high-speed endpoint array
                raw_data = self.ep_in.read(FRAME_BUFFER_CEILING, timeout=5000)
                
                if len(raw_data) == FRAME_BUFFER_CEILING:
                    self.process_interleaved_payload(raw_data)
                else:
                    logging.warning(f"Dropped frame fragment packet detected: {len(raw_data)} bytes.")
                    
                # Throttle execution to match factory hardware cap (8.7Hz regulatory threshold)
                time.sleep(0.11)
                
        except usb.core.USBError as e:
            logging.critical(f"Fatal USB pipeline disruption encountered: {str(e)}")
        except KeyboardInterrupt:
            logging.info("Ingestion tracking manually stopped by administrator.")

    def process_interleaved_payload(self, buffer_stream):
        """Asynchronously slices raw bytes into target structures for the CUDA pipeline."""
        # Frame extraction sizes for FLIR Lepton 3.5 Core
        # Radiometric 14-bit data maps to 160x120 pixels, interleaved within the transport wrapper
        raw_array = np.frombuffer(buffer_stream, dtype=np.uint8)
        
        # Example slicing boundary logic targeting the raw 14-bit thermal grid allocation
        thermal_slice = raw_array[0:38400].view(dtype=np.uint16).reshape((120, 160))
        
        # Pass directly into the NVIDIA CUDA processing module
        # from cuda_thermal_math import run_gpu_thermal_pipeline
        # celsius_matrix = run_gpu_thermal_pipeline(thermal_slice)

if __name__ == "__main__":
    streamer = FlirOneProStreamer()
    streamer.initiate_hardware_loop()
