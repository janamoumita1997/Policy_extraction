from tika import parser


class TikaExtract:
	def __init__(self, pdffile):
		try:
			self.pdf = pdffile
		except Exception as e:
			print(e)

	def getContent(self):
		try:
			self.raw = parser.from_file(self.pdf)
			return self.raw['content'].splitlines()
		except Exception as e:
			print(e)

	def getValueFromTikaParcer(self, contents, key):
	    try:
	        value = ''
			print("from tiker extract >> ", key)
	        for row in contents:
	            if row.find(key) > -1:
	                value = row[row.find(key) + len(key):]
	                print("in tika parser", value)
	                break
	        return value if value is not None else ''
	    except Exception as e:
	        print(e)
