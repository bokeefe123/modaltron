"""
Data compressor for efficient transport.
Port of shared/service/Compressor.js
"""


class Compressor:
    """
    Compresses/decompresses floating point numbers for transport.
    """
    
    precision = 100
    
    def compress(self, value: float) -> int:
        """Compress a float into an integer."""
        return int(0.5 + value * self.precision)
    
    def decompress(self, value: int) -> float:
        """Decompress an integer into a float."""
        return value / self.precision

