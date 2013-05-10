# -*- coding: utf-8 -*-



def scale_input(self,Input,scaling):
		sInput = (float(Input)/float(2**scaling.bit))*(scaling.max_value-scaling.min_value)+scaling.min_value
		return sInput