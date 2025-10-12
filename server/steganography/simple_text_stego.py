"""
📝 Simple Text Steganography for 7-Layer Encryption
Hide encrypted messages in innocent-looking text using simple but effective techniques
Focus on reliability and integration with existing 7-layer system
"""

import base64
import hashlib
import random
from content_generator import ContentGenerator

class SimpleTextSteganography:
    """Simple, reliable text steganography for 7-layer encrypted messages"""
    
    def __init__(self):
        self.generator = ContentGenerator()
        self.delimiter = "STEGOMSG"  # Simple delimiter for embedded data
        
    def hide_message_in_text(self, encrypted_data, text_style="mixed"):
        """
        🔒 Hide 7-layer encrypted data in innocent text using base64 + steganography
        
        Args:
            encrypted_data (bytes): The 7-layer encrypted message blob
            text_style (str): Style of cover text to generate
            
        Returns:
            str: Innocent-looking text containing hidden message
        """
        print(f"📝 HIDING MESSAGE IN TEXT")
        print(f"   🔒 Data size: {len(encrypted_data)} bytes")
        print(f"   📝 Text style: {text_style}")
        
        # Step 1: Encode data as base64 for easier handling
        b64_data = base64.b64encode(encrypted_data).decode()
        
        # Step 2: Create checksum for integrity
        checksum = hashlib.md5(encrypted_data).hexdigest()[:8]
        
        # Step 3: Create payload with delimiters
        payload = f"{self.delimiter}:{checksum}:{b64_data}:{self.delimiter}"
        
        print(f"   📦 Payload length: {len(payload)} chars")
        
        # Step 4: Generate innocent cover text
        cover_paragraphs = []
        total_chars = 0
        
        # Generate enough text to hide our payload comfortably
        # Need enough words for each bit in the payload
        target_words = len(payload) * 8 + 50  # 8 bits per char + buffer
        
        while len(' '.join(cover_paragraphs).split()) < target_words:
            if text_style == "mixed":
                style = random.choice(['weather', 'daily_life', 'food', 'technology'])
            else:
                style = text_style
                
            paragraph = self.generator.generate_innocent_text('long', style)
            cover_paragraphs.append(paragraph)
            total_chars += len(paragraph)
        
        cover_text = "\n\n".join(cover_paragraphs)
        
        print(f"   📄 Cover text length: {len(cover_text)} chars")
        
        # Step 5: Hide payload using simple but effective method
        stego_text = self._embed_payload_in_text(cover_text, payload)
        
        print(f"   🎭 STEGANOGRAPHY COMPLETE!")
        print(f"   📝 Final text length: {len(stego_text)} chars")
        
        return stego_text
    
    def extract_message_from_text(self, stego_text):
        """
        🔓 Extract 7-layer encrypted data from steganographic text
        
        Args:
            stego_text (str): Text containing hidden message
            
        Returns:
            bytes: The extracted 7-layer encrypted data
        """
        print(f"🔍 EXTRACTING MESSAGE FROM TEXT")
        print(f"   📄 Text length: {len(stego_text)} chars")
        
        # Step 1: Extract payload from text
        payload = self._extract_payload_from_text(stego_text)
        
        if not payload:
            raise ValueError("❌ No hidden message found in text")
        
        print(f"   📦 Extracted payload: {len(payload)} chars")
        
        # Step 2: Parse payload structure
        try:
            parts = payload.split(':', 3)
            if len(parts) != 4:
                raise ValueError("Invalid payload structure")
                
            start_delimiter, checksum, b64_data, end_delimiter = parts
            
            if start_delimiter != self.delimiter or end_delimiter != self.delimiter:
                raise ValueError("Invalid delimiters")
                
            print("   ✅ Payload structure verified")
            
        except Exception as e:
            raise ValueError(f"❌ Payload parsing failed: {e}")
        
        # Step 3: Decode base64 data
        try:
            encrypted_data = base64.b64decode(b64_data)
        except Exception as e:
            raise ValueError(f"❌ Base64 decoding failed: {e}")
        
        # Step 4: Verify integrity
        calculated_checksum = hashlib.md5(encrypted_data).hexdigest()[:8]
        
        if checksum != calculated_checksum:
            raise ValueError("❌ Data corruption detected - checksum mismatch!")
        
        print("   ✅ Data integrity verified!")
        print(f"   🎭 EXTRACTION COMPLETE!")
        print(f"   📦 Recovered {len(encrypted_data)} bytes of 7-layer encrypted data")
        
        return encrypted_data
    
    def _embed_payload_in_text(self, cover_text, payload):
        """Embed payload using whitespace steganography (simple but reliable)"""
        
        # Method: Use invisible characters between words
        # Normal space = continue, double space = binary 1, single space = binary 0
        
        # Convert payload to binary
        binary_payload = ''.join(format(ord(char), '08b') for char in payload)
        
        print(f"   💾 Binary payload: {len(binary_payload)} bits")
        
        # Split text into words
        words = cover_text.split()
        
        if len(words) < len(binary_payload):
            raise ValueError("❌ Cover text too short for payload")
        
        # Embed binary data between words using space patterns
        result_words = [words[0]]  # Start with first word
        
        for i, bit in enumerate(binary_payload):
            if i + 1 < len(words):
                if bit == '1':
                    # Double space for bit 1
                    result_words.append(' ' + words[i + 1])
                else:
                    # Single space for bit 0  
                    result_words.append(words[i + 1])
        
        # Add remaining words normally
        for i in range(len(binary_payload) + 1, len(words)):
            result_words.append(words[i])
        
        stego_text = ' '.join(result_words)
        
        print(f"   📊 Embedded {len(binary_payload)} bits in text spacing")
        
        return stego_text
    
    def _extract_payload_from_text(self, stego_text):
        """Extract payload from whitespace patterns"""
        
        # Look for our delimiter pattern first
        if self.delimiter not in stego_text:
            # Try extracting from spacing patterns
            binary_bits = self._extract_binary_from_spacing(stego_text)
            
            if not binary_bits:
                return None
            
            # Convert binary back to text
            payload_chars = []
            for i in range(0, len(binary_bits), 8):
                if i + 8 <= len(binary_bits):
                    byte_str = binary_bits[i:i+8]
                    try:
                        payload_chars.append(chr(int(byte_str, 2)))
                    except ValueError:
                        continue
            
            payload = ''.join(payload_chars)
            
            # Look for our delimiter in the reconstructed payload
            start_pos = payload.find(self.delimiter)
            if start_pos == -1:
                return None
                
            end_pos = payload.find(self.delimiter, start_pos + len(self.delimiter))
            if end_pos == -1:
                return None
            
            return payload[start_pos:end_pos + len(self.delimiter)]
        
        else:
            # Direct extraction if delimiters are visible (fallback)
            start_pos = stego_text.find(self.delimiter)
            end_pos = stego_text.find(self.delimiter, start_pos + len(self.delimiter))
            
            if start_pos != -1 and end_pos != -1:
                return stego_text[start_pos:end_pos + len(self.delimiter)]
        
        return None
    
    def _extract_binary_from_spacing(self, text):
        """Extract binary data from spacing patterns between words"""
        
        # Look for double spaces (bit 1) vs single spaces (bit 0)
        binary_bits = []
        
        i = 0
        while i < len(text):
            if text[i] == ' ':
                if i + 1 < len(text) and text[i + 1] == ' ':
                    binary_bits.append('1')  # Double space = 1
                    i += 2  # Skip both spaces
                else:
                    binary_bits.append('0')  # Single space = 0
                    i += 1
            else:
                i += 1
        
        return ''.join(binary_bits)


# Test the simplified text steganography
if __name__ == "__main__":
    # Test with sample 7-layer encrypted data
    text_stego = SimpleTextSteganography()
    
    # Simulate 7-layer encrypted data
    test_message = b"This is a secret message from the 7-layer encryption system!"
    print(f"🧪 TEST MESSAGE: {test_message}")
    print(f"📊 Size: {len(test_message)} bytes")
    
    try:
        print(f"\n{'='*60}")
        print(f"🔒 HIDING MESSAGE IN TEXT")
        print(f"{'='*60}")
        
        # Hide message in text
        stego_text = text_stego.hide_message_in_text(test_message, "daily_life")
        
        print(f"\n📝 STEGANOGRAPHIC TEXT SAMPLE:")
        print(f"{'-'*50}")
        print(f"{stego_text}")
        print(f"{'-'*50}")
        
        print(f"\n{'='*60}")
        print(f"🔍 EXTRACTING MESSAGE FROM TEXT")
        print(f"{'='*60}")
        
        # Extract message back
        recovered_message = text_stego.extract_message_from_text(stego_text)
        
        # Verify results
        print(f"\n🔍 VERIFICATION:")
        print(f"   📝 Original:  {test_message}")
        print(f"   📝 Recovered: {recovered_message}")
        print(f"   ✅ Match: {test_message == recovered_message}")
        
        if test_message == recovered_message:
            print(f"\n🎉 SUCCESS! Text steganography working perfectly!")
        else:
            print(f"\n❌ FAILURE! Data corruption occurred!")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()