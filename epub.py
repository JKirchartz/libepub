#!/usr/bin/env python

# A module to read, write, transform, and generally handle epub format
# thanks to http://www.jedisaber.com/eBooks/tutorial.asp

import zipfile
from lxml import etree

CONTAINER_PATH = "META-INF/container.xml"

class Book:
	
	def __init__(self, path):
		self.archive = zipfile.ZipFile(path, 'r') # read-only for now
		self.opf_path = self._get_opf_path()
		self._parse_opf()
		self.chapters = [Chapter(self.archive.open("OEBPS/" + self.manifest[chapter]['href'])) for chapter in self.spine]
		
	def _get_opf_path(self):
		"""Get the path to the OPF file for this epub"""
		container = self.archive.open(CONTAINER_PATH)
		
		# get the location of the OPF file
		container_etree = etree.parse(container)
		container_root = container_etree.getroot()
		
		base_tag = self._get_base_tag(container_root)
		query_tag = base_tag + "rootfile"
		
		opf_path = container_root.findall(query_tag)[0].get('full-path')
		return opf_path
		
	def _parse_opf(self):
		"""Parse and store the metadata info on this epub"""
		opf = self.archive.open(self.opf_path, "r")
		tree = etree.parse(opf)
		root = tree.getroot()
		
		base_tag = self._get_base_tag(root)
		
		self.book_id = root.get('unique-identifier')
		
		# parse Metadata
		metadata_root = root.find(base_tag + 'metadata')
		self._parse_metadata(metadata_root)
		
		# parse Manifest
		manifest_root = root.find(base_tag + 'manifest')
		self._parse_manifest(manifest_root)
		
		# parse Spine
		spine_root = root.find(base_tag + 'spine')
		self._parse_spine(spine_root)
		
	def _parse_metadata(self, root):
		"""Parse and store the info in the given metadata root"""
		# base_tag = ".//{" + root.nsmap['dc'] + "}"
		self.metadata = {}
		for data in root:
			tag_name = data.tag[data.tag.index('}') + 1:]
			self.metadata[tag_name] = data.text
			
	def _parse_manifest(self, root):
		"""Parse and store the item declarations in given manifest root"""
		self.manifest = {}
		for item in root:
			self.manifest[item.get('id')] = {'href' : item.get('href'),
												'media-type' : item.get('media-type')}
												
	def _parse_spine(self, root):
		"""Parse and store the order in the given spine root"""
		self.spine = []
		for itemref in root:
			self.spine.append(itemref.get('idref'))
		
	def _get_base_tag(self, root):
		"""Return the base tag string for the given root element"""
		base_index = root.tag.index('}')
		base_tag = ".//" + root.tag[:(base_index + 1)]
		return base_tag
		
class Chapter:
	
	def __init__(self, chapter_file):
		self.content = chapter_file.read()
		
		
if __name__ == "__main__":
	b = Book('sample.epub')
	print b.chapters
