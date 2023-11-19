import re
import random
from pwnlib.util import fiddling as bits

from .mutator_base import MutatorBase

class JPEG_Mutator(MutatorBase):
    """
    Mutator that creates altered input on the basis of sample input file
    """
    Markers = {
        # For more info, https://www.disktuna.com/list-of-jpeg-markers/
        "SOI" : b'\xff\xd8', # Start of Image
        "SOF" : b'\xff[\xc0-\xc3\xc5-\xc7\xc9=\xcb\xcd-\xcf]', # Start of Frame (match statement)
        "DHT" : b'\xff\xc4', # Define Huffman Table
        "DQT" : b'\xff\xdb', # Define Quantization Table
        "DRI" : b'\xff\xdd', # Define infotart Interval
        "SOS" : b'\xff\xda', # Start of Scan
        "APP" : b'\xff[\xe0-\xe9\xea-\xef]', # Application specific metadata markers
        "COM" : b'\xff\xfe', # Text Comment
        "EOI" : b'\xff\xd9', # End of Image
    }

    def __init__(self, seed: bytes):
        """
        Initalises the class
        
        Args:
            seed (bytes): Raw bytes of input file
        """
        super().__init__()
        self._seed = seed
        self._dct = ''
        self._body = None
        self._hf_table = list()
        self._shape = [0, 0]
        self._q_table = list()
        self._marker = list()
        self._comments = list()
        self._app_meta = dict()
        self.frame = dict()
        self.scan = dict()
        self._parse(seed)

    def format_output(self, mutable_content: bytes) -> bytes:
        """
        Construct a JPEG file
    
        This function will assembles the JPEG file from the class structure
    
        Args:
            mutable_content (List[bytes]): Raw mutable content

        Returns:
            bytes: A formatted JPEG in byte form.
        """
        
        head = self._asm_app()
        head += self._asm_qt()
        head += self._asm_sof()
        head += self._asm_ht()
        head += self._asm_sos()
        
        self._parse(self._seed)
        
        ret =  self.Markers["SOI"] + head + self._body + self.Markers["EOI"]
        return ret

    def _mutate_qt_new(self):
        """
        This function mutates the input file by adding a quantization table
        with random bytes
    
        Args:
            None

        Returns:
            None
        """

        qt = dict()
        qt['id'] = len(self._q_table) + 1
        qt['table'] = [random.randbytes(8) for _ in range(8)]
        self.q_table.append(qt)

    def _mutate_qt_random(self):
        """
        This function mutates the input file by changing a quantization table
        and replacing it with random bytes
    
        Args:
            None

        Returns:
            None
        """
        tdx = random.randint(0, len(self._q_table) - 1)
        qt = dict()
        qt['id'] = tdx + 1
        qt['table'] = [random.randbytes(8) for _ in range(8)]
        
        self._q_table[tdx](qt)

    def _mutate_hf(self):
        """
        This function mutates the input file by changing a huffman table
        with random bytes
    
        Args:
            None

        Returns:
            None
        """


        new_ht = dict()
        tdx = random.randint(0, len(self._hf_table) - 1)
        new_ht['class'] = random.randint(0, 1)
        new_ht['destination'] = random.randint(0, 1)
        encodings = list()
        for _ in range(16):
            n_encodings = random.randint(1, 0xFF)
            encodings.append(random.randbytes(n_encodings))
        
        new_ht['encodings'] = encodings
        self._hf_table[tdx] = new_ht

    def _mutate_sof(self):
        """
        This function mutates the input file by changing the frame's height and width
        with random bytes
    
        Args:
            None

        Returns:
            None
        """
        
        self._sof_info['height'] = random.randint(0, 0xFFFF)
        self._sof_info['width'] = random.randint(0, 0xFFFF)
    
    def _mutate_body(self):
        """
        This function mutates the input file by swapping the input file's body bits
    
        Args:
            None

        Returns:
            None
        """
        
        data = bits.bits(self._body)
        new_body = list()
        d_length = len(data)
        for _, bdx in data:
            new_body.append(data[d_length - bdx])
        self._body = bits.unbits(new_body)

    def _parse(self, sample: bytes):
        """
        Parses a byte stream from a JPEG file into the class' structure

        Args:
            sample (bytes): Raw bytes of the JPEG file

        Returns:
            null
        """

        head, _, body = sample.partition(self.Markers["SOS"])
        self._body = body[:-2]
        markers = list(self.Markers.values())
        match_expr =  re.compile(b'|'.join(markers), re.MULTILINE)
        matches = re.finditer(match_expr, head)
        for m in matches:
            low, high = m.span()
            field = head[low:high]
            length = None
            content = None
            if content != self.Markers["DRI"]:
                length = int.from_bytes(head[high:high + 2], 'big') - 2
                content = head[high + 2:high + 2 + length]
            
            if re.match(self.Markers["SOF"], field):
                self._sof_info = self._parse_sof(content, field[1])
            elif re.match(self.Markers["APP"], field):
                index = int.from_bytes(field, 'big') - 0xffe0
                self._app_meta[index] = content
               
            elif field == self.Markers["DHT"]:
                table = self._parse_hf(content)
                self._hf_table.append(table)
            elif field == self.Markers["DQT"]:
                table = dict()
                table['id'] = content[0]
                table['table'] = [content[1 + idx * 8:1 + idx * 8 + 8] for idx in range(8)]
                self._q_table.append(table)
            elif field == self.Markers["DRI"]:
                self._infotart_interval = int.from_bytes(head[low + 2:low + 4], 'big')
            elif field == self.Markers["COM"]:
                self._comments.append(content)

        self._sos_info = self._parse_sos(body[2:2 + 10])
        self._body = body[2 + 10:-2]

    def _parse_sof(self, content: bytes, type: bytes) -> dict:
        """
        Parses a content of frame from a JPEG file into the class' structure

        Args:
            content (bytes): Raw bytes of frame of a JPEG file
            type (bytes): type of frame 

        Returns:
            dict: structure contains info on the frame
        """
        
        info = dict()
        info["precision"] = content[0]
        info['n_components'] = content[5]
        info['type'] = type
        info["components"] = self._parse_sof_components(content)
        info['height'] = int.from_bytes(content[1:3], 'big')
        info['width'] = int.from_bytes(content[3:5], 'big')
        
    def _parse_sof_components(self, content: bytes) -> list:
        """
        Parses a content of frame's components from a JPEG file into the class' structure

        Args:
            content (bytes): Raw bytes of frame of a JPEG file

        Returns:
            list: list contains info on the frame's components
        """
        
        components = list()
        colour = content[6:]
        for i in range(content[5]):
            component = {}
            component['id'] = colour[3 * i]
            component['scale'] = [
                colour[1 + 3 * i] >> 4,
                colour[1 + 3 * i] & 0x0f,
            ]
            component['dqt_index'] = colour[2 + 3 * i]
            components.append(component)

        return components
    
    def _parse_hf(self, content: bytes) -> dict:
        """
        Parses a content of huffman table from a JPEG file into the class' structure

        Args:
            content (bytes): Raw bytes of huffman table of a JPEG file

        Returns:
            dict: structure contains info on the huffman table
        """
        
        hf = dict()
        hf['class'] = content[0] >> 4
        hf['destination'] = content[0] & 0x0F
        encode = list()
        encodings = content[17:]
        size = content[1:17]
        lo, hi = 0, 0
        for idx in size:
            if idx == 0:
                encode.append(b'')
            else:
                hi += idx
                encode.append(encodings[lo:hi])
                lo = hi
        hf["encodings"] = encodings
        return hf
    
    def _parse_sos(self, content: bytes) -> dict:
        """
        Parses a content of scan from a JPEG file into the class' structure

        Args:
            content (bytes): Raw bytes of scan of a JPEG file

        Returns:
            dict: structure contains info on the JPEG's scan
        """
        sos = dict()
        sos['n_components'] = content[0]
        sos['components'] = self._parse_sos_components(content)
        sos['spectral_select'] = [content[-3], content[-2]]
        sos['successive_approx'] = content[-1]
        return sos

    def _parse_sos_components(self, content: bytes) -> list:
        """
        Parses a content of scan's components from a JPEG file into the class' structure

        Args:
            content (bytes): Raw bytes of scan of a JPEG file

        Returns:
            list: list contains info on the scan's components
        """
        
        components = list()
        for i in range(content[0]):
            component = dict()
            component['id'] = content[1 + i * 2]
            component['dc'] = content[1 + i * 2 + 1] >> 4
            component['ac'] = content[1 + i * 2 + 1] & 0x0f
            components.append(component)
        
        return components
 
    def _asm_app(self) -> bytes:
        """
        Assembles class structure's application metadata
        into a bytes stream

        Args:
            none

        Returns:
            bytes: byte stream of application metadata
        """
        
        content = bytes()
        for k, v in self.app_meta.items():
            marker = k + 0xffe0
            marker = marker.to_bytes(2, 'big')
            content_len = len(v) + 2
            content += marker + content_len.to_bytes(2, 'big') + v
        return content
    
    def _asm_qt(self) -> bytes:
        """
        Assembles class structure's quantization tables
        into a bytes stream

        Args:
            none

        Returns:
            bytes: byte stream of quantization tables
        """
        
        content = bytes()
        for tbl in self._q_table:
            table = bytes()
            table += tbl['id'].to_bytes(1, 'big')
            table += b''.join(tbl['table'])
            length = len(table) + 2
            content +=  self.Markers["DQT"] + length.to_bytes(2, 'big') + table
        return content

    def _asm_sof(self) -> bytes:
        """
        Assembles class structure's frame
        into a bytes stream

        Args:
            none

        Returns:
            bytes: byte stream of frame
        """
        
        info = bytes()
        info += self._sof_info['precision'].to_bytes(1, 'big')
        info += self._sof_info['height'].to_bytes(2, 'big')
        info += self._sof_info['width'].to_bytes(2, 'big')
        info += self._sof_info['n_components'].to_bytes(1, 'big')
        info += self._asm_comp()

        marker = b'\xff' + self._sof_info['type'].to_bytes(1, 'big')
        length = len(info) + 2
        return marker + length.to_bytes(2, 'big') + info
    
    def _asm_comp(self) -> bytes:
        """
        Assembles class structure frame's components 
        into a bytes stream

        Args:
            none

        Returns:
            bytes: byte stream of frame's components
        """
        
        comps = bytes()
        for i in range(self._sof_info['n_components']):
            comp = self._sof_info['components'][i]
            cBytes = bytes()
            cBytes += comp['id'].to_bytes(1, 'big')
            cBytes += ((comp['scale'][1] << 4) + comp['scale'][0]).to_bytes(1, 'big')
            cBytes += comp['dqt_index'].to_bytes(1, 'big')
            comps += cBytes
        return comp
    
    def _asm_hf(self) -> bytes:
        """
        Assembles class structure's huffman table 
        into a bytes stream

        Args:
            none

        Returns:
            bytes: byte stream of huffman tables
        """
        
        content = bytes()
        for tbl in self._hf_table:
            table = bytes()
            table += ((tbl['class'] << 4) + tbl['destination']).to_bytes(1, 'big')
            size = bytes() 
            encode = bytes()
            for e in tbl['encodings']:
                size += len(e).to_bytes(1, 'big')
                if len(e) > 0:
                    encode += e
            table += size + encode
            length = len(table) + 2
            content +=  self.Markers["DHT"] + length.to_bytes(2, 'big') + table

    def _asm_sos(self) -> bytes:
        """
        Assembles class structure start of scan
        into a bytes stream

        Args:
            none

        Returns:
            bytes: byte stream of start of scan
        """
        
        sos = bytes()
        sos += self._sos_info['n_components'].to_bytes(1, 'big')

        for idx in range(self._sos_info['n_components']):
            component = self._sos_info['components'][idx]
            comp = bytes()
            comp += component['id'].to_bytes(1, 'big')
            comp += ((component['dc'] << 4) + component['ac']).to_bytes(1, 'big')
            
            sos += comp

        content += self._sos_info['spectral_select'][0].to_bytes(1, 'big')
        content += self._sos_info['spectral_select'][1].to_bytes(1, 'big')
        content += self._sos_info['successive_approx'].to_bytes(1, 'big')
        length = len(content) + 2

        return self.Markers["SOS"] + length.to_bytes(2, 'big') + sos





        