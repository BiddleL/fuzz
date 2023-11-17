import xml.etree.ElementTree as ET
import random
from .mutator_base import MutatorBase


class XML_Mutator(MutatorBase):

    def __init__(self, seed):
        super().__init__()
        self._content = ET.ElementTree(ET.fromstring(seed))
        self._seed = seed

    def format_output(self, data):
        if not data:
            data = ET.tostring(self._content.getroot(), method='xml')
            self._content = ET.ElementTree(ET.fromstring(self._seed))
        return data

    def _mutate_make_longer_tag(self):
        for node in self._content.iter():
            node.tag = self.pick_from_alphabet(0xff)

    def _recusive_apply(self, node: ET.Element, fn):
        fn(node)
        for child in node:
            self._recusive_apply(child, fn)

    def _mutate_forge_attributes(self):
        new_elements = [ET.Element("h1", {"id": "%s" * 10}) for _ in range(0xff)]
        for element in new_elements:
            self.root.append(element)

    def _mutate_recursion_overflow(self):
        opening_tags = b'<fuz>' * 0xffff
        closing_tags = b'</fuz>' * 0xffff
        return opening_tags + closing_tags

    def _mutate_alter_href(self):
        for node in self._content.iter():
            if 'href' in node.attrib:
                node.set("href", "%s" * 10)

    @property
    def root(self):
        return self._content.getroot()

    def pick_from_alphabet(self, length):
        return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length))
