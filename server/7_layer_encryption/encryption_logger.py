#!/usr/bin/env python3
"""
🛡️ 7-LAYER ENCRYPTION DETAILED LOGGER
=====================================

This module provides comprehensive logging of the complete 7-layer encryption process.
Logs every key, hash, transformation, and step for both messages and files.
All encryption activities are appended to encryption_log.txt with timestamps.

Author: 7-Layer Military-Grade Encryption System
Date: October 10, 2025
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional


class EncryptionLogger:
    """Comprehensive logger for 7-layer encryption processes"""
    
    def __init__(self, log_file: str = "encryption_log.txt"):
        self.log_file = os.path.join(os.path.dirname(__file__), log_file)
        self.session_start = datetime.now()
        
        # Initialize log file with session header
        self._write_session_header()
    
    def _write_session_header(self):
        """Write session start header to log file"""
        header = f"""
7-LAYER ENCRYPTION SESSION - {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(header)
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    
    def _safe_truncate(self, data: str, max_len: int = 64) -> str:
        """Safely truncate data for display"""
        if len(data) <= max_len:
            return data
        return f"{data[:max_len//2]}...{data[-max_len//2:]}"
    
    def _format_hex_data(self, data: bytes, name: str = "Data") -> str:
        """Format binary data as hex with metadata"""
        hex_data = data.hex()
        return f"""   📊 {name}:
      🔢 Length: {len(data)} bytes
      🔤 Hex: {self._safe_truncate(hex_data, 80)}
      #️⃣ SHA256: {hashlib.sha256(data).hexdigest()[:16]}...
"""

    def log_message_encryption_start(self, original_msg: str, user1: str, user2: str, 
                                   security_profile: str) -> str:
        """Log the start of message encryption process"""
        operation_id = f"MSG_{int(time.time()*1000000)}"
        
        log_entry = f"""
MESSAGE ENCRYPTION - {operation_id}
{'='*50}
Users: {user1} ↔ {user2}
Message: "{original_msg}"
Profile: {security_profile}

"""
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return operation_id
    
    def log_file_encryption_start(self, filename: str, file_size: int, user1: str, user2: str,
                                security_profile: str) -> str:
        """Log the start of file encryption process"""
        operation_id = f"FILE_{int(time.time()*1000000)}"
        
        log_entry = f"""
FILE ENCRYPTION - {operation_id}
{'='*50}
Users: {user1} ↔ {user2}
File: {filename} ({file_size:,} bytes)
Profile: {security_profile}

"""
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        return operation_id
    
    def log_key_generation(self, operation_id: str, master_key: bytes, 
                          derived_keys: Dict[str, bytes], key_material: str):
        """Log master key generation - simplified"""
        
        log_entry = f"""
MASTER KEY GENERATION
{'─'*25}
Material: {key_material}
Master Key: {self._safe_truncate(master_key.hex(), 64)}

"""
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def log_layer_process(self, operation_id: str, layer_num: int, layer_name: str,
                         input_data: bytes, output_data: bytes, 
                         layer_key: bytes, layer_params: Dict[str, Any]):
        """Log individual layer processing details - clean format"""
        
        log_entry = f"""
LAYER {layer_num}: {layer_name}
{'─'*30}
Key:    {self._safe_truncate(layer_key.hex(), 64)}
Input:  {self._safe_truncate(input_data.hex(), 64)} ({len(input_data)} bytes)
Output: {self._safe_truncate(output_data.hex(), 64)} ({len(output_data)} bytes)
Change: {len(input_data)} → {len(output_data)} ({len(output_data)-len(input_data):+d} bytes)

"""
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def log_encryption_complete(self, operation_id: str, original_size: int, 
                              final_size: int, processing_time: float, 
                              final_result: Dict[str, Any]):
        """Log completion of encryption process"""
        
        log_entry = f"""
ENCRYPTION COMPLETE
{'─'*20}
Original: {original_size} bytes → Encrypted: {final_size} bytes
Time: {processing_time:.3f}s
Final: {self._safe_truncate(final_result.get('encrypted_message', ''), 64)}

{'='*60}

"""
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def log_decryption_start(self, operation_id: str, encrypted_data: Dict[str, Any],
                           user1: str, user2: str):
        """Log the start of decryption process"""
        pass  # Simplified - don't log decryption start
    
    def log_decryption_complete(self, operation_id: str, decrypted_size: int,
                              processing_time: float, integrity_verified: bool,
                              final_hash: str):
        """Log completion of decryption process"""
        pass  # Simplified - don't log decryption completion
    
    def log_error(self, operation_id: str, error_stage: str, error_message: str):
        """Log encryption/decryption errors"""
        
        log_entry = f"""
❌ ERROR - {operation_id}
{'─'*30}
⏰ Timestamp: {self._get_timestamp()}
🚨 Stage: {error_stage}
💥 Error: {error_message}

"""
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def get_log_stats(self) -> Dict[str, Any]:
        """Get statistics about logged operations"""
        try:
            if not os.path.exists(self.log_file):
                return {'total_operations': 0, 'file_size': 0}
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            stats = {
                'file_size': len(content),
                'total_operations': content.count('ENCRYPTION STARTED'),
                'message_encryptions': content.count('MESSAGE ENCRYPTION STARTED'),
                'file_encryptions': content.count('FILE ENCRYPTION STARTED'),
                'total_decryptions': content.count('DECRYPTION STARTED'),
                'successful_operations': content.count('SUCCESSFUL!'),
                'errors': content.count('❌ ERROR'),
                'session_start': self.session_start.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}


# Global logger instance
encryption_logger = EncryptionLogger()


def log_message_encryption(original_msg: str, user1: str, user2: str, 
                          security_profile: str) -> str:
    """Convenience function to start message encryption logging"""
    return encryption_logger.log_message_encryption_start(
        original_msg, user1, user2, security_profile
    )


def log_file_encryption(filename: str, file_size: int, user1: str, user2: str,
                       security_profile: str) -> str:
    """Convenience function to start file encryption logging"""
    return encryption_logger.log_file_encryption_start(
        filename, file_size, user1, user2, security_profile
    )


def get_encryption_stats() -> Dict[str, Any]:
    """Get current encryption logging statistics"""
    return encryption_logger.get_log_stats()


if __name__ == "__main__":
    # Test the logger
    print("🛡️ 7-Layer Encryption Logger Test")
    print("=" * 40)
    
    # Simulate a message encryption
    op_id = log_message_encryption("Hello World!", "user1", "user2", "BALANCED")
    print(f"Started logging operation: {op_id}")
    
    # Simulate key generation
    master_key = b"test_master_key_32_bytes_long_123"
    derived_keys = {
        "layer1_key": b"layer1_key_16_bytes",
        "layer2_key": b"layer2_key_24_bytes_123",
        "layer3_key": b"layer3_key_32_bytes_long_test"
    }
    encryption_logger.log_key_generation(op_id, master_key, derived_keys, "test_material")
    
    # Simulate layer processing
    encryption_logger.log_layer_process(
        op_id, 1, "Chaos Theory Layer", 
        b"input_data", b"encrypted_output_data", 
        b"layer_key", {"chaos_param": 3.99, "iterations": 1000}
    )
    
    # Simulate completion
    final_result = {
        "encryption_version": "7LAYER_v1.0",
        "security_profile": "BALANCED",
        "encrypted_message": "base64_encrypted_data_here"
    }
    encryption_logger.log_encryption_complete(op_id, 11, 50, 0.125, final_result)
    
    # Show stats
    stats = get_encryption_stats()
    print(f"Log stats: {stats}")
    print(f"\n📁 Log file: {encryption_logger.log_file}")